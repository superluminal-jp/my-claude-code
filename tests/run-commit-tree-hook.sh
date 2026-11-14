#!/usr/bin/env bash
# Contract for the PreToolUse hook in harness/settings.json that runs the
# sync-docs tree check before Claude runs `git commit` (ADR-0023).
#
# Offline and side-effect free: it reads the settings file, and runs the hook
# command under sh, bash, and (when installed) zsh with a scratch HOME, the
# way Claude Code does, with PreToolUse input on stdin. The hook must only
# warn: it always exits 0, because exit code 2 would block the commit.
#
# What it cannot show: that Claude Code honours the "if" filter and passes
# additionalContext to Claude. That is checked in a new session after
# install.sh.

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SETTINGS="$REPO_ROOT/harness/settings.json"
SKILL="$REPO_ROOT/harness/skills/sync-docs"
STATUS="Checking the documentation tree if this is a commit..."

PASS=0
FAIL=0

check() {
  local name="$1" cond="$2"
  if [ "$cond" = "1" ]; then
    PASS=$((PASS + 1))
    printf 'PASS %s\n' "$name"
  else
    FAIL=$((FAIL + 1))
    printf 'FAIL %s\n' "$name" >&2
  fi
}

for tool in jq python3; do
  command -v "$tool" >/dev/null 2>&1 || {
    echo "run-commit-tree-hook: $tool is required" >&2
    exit 1
  }
done

# --- Wiring ----------------------------------------------------------------

handler='[.hooks.PreToolUse[]? | select(.matcher == "Bash") | .hooks[]? | select(.statusMessage == $m)]'
[ "$(jq --arg m "$STATUS" "$handler | length" "$SETTINGS")" = "1" ] && c=1 || c=0
check "TREE-00 exactly one Bash PreToolUse hook says \"$STATUS\"" "$c"

# The "if" filter is a permission-rule pattern: "Bash(<prefix>*)" runs the hook for a
# command that starts with <prefix>. Every commit form the checker recognises must
# start with it, or Claude Code never runs the hook for that form.
if_rule="$(jq -r --arg m "$STATUS" "$handler | .[0].if // empty" "$SETTINGS")"
prefix="${if_rule#Bash(}"
prefix="${prefix%\*)}"
c=1
case "$if_rule" in Bash\(*\*\)) ;; *) c=0 ;; esac
for form in 'git commit -m x' 'git -C /repo commit -m x' 'git -c user.name=x commit -m x' 'git --no-pager commit -m x'; do
  case "$form" in "$prefix"*) ;; *) c=0; printf '    not covered by %s: %s\n' "$if_rule" "$form" >&2 ;; esac
done
check "TREE-01 the if filter ($if_rule) covers git commit with -C, -c, and other global options" "$c"

timeout="$(jq -r --arg m "$STATUS" "$handler | .[0].timeout // empty" "$SETTINGS")"
[ -n "$timeout" ] && [ "$timeout" -le 30 ] && c=1 || c=0
check "TREE-02 the hook has a timeout of at most 30 seconds" "$c"

cmd="$(jq -r --arg m "$STATUS" "$handler | .[0].command // empty" "$SETTINGS")"

# --- Behavior ----------------------------------------------------------------

SCRATCH="$(mktemp -d "${TMPDIR:-/tmp}/commit-tree-hook.XXXXXX")"
trap 'rm -rf "$SCRATCH"' EXIT
# The interpreter itself, not a shim such as pyenv's, which needs the real HOME.
PY_DIR="$(dirname "$(python3 -c 'import sys; print(sys.executable)')")"

# A project that declares a tree and lacks the README of its feature folder.
PROJECT="$SCRATCH/project"
mkdir -p "$PROJECT/src/features/x"
printf '%s\n' '{"tree": {"features": ["src/features/*"]}}' >"$PROJECT/.living-documentation.json"
printf '# project\n\n- [x](src/features/x/README.md)\n' >"$PROJECT/README.md"
printf 'export {};\n' >"$PROJECT/src/features/x/index.ts"

input() {
  jq -cn --arg c "$1" --arg d "$PROJECT" \
    '{hook_event_name: "PreToolUse", tool_name: "Bash", tool_input: {command: $c}, cwd: $d}'
}

# run_hook SHELL HOME PATH COMMAND-TEXT: run the hook command with only HOME
# and PATH set; prints "<exit code>|<stdout>|<stderr>".
run_hook() {
  local out err code
  out="$(input "$4" | env -i HOME="$2" PATH="$3" PYTHONDONTWRITEBYTECODE=1 "$1" -c "$cmd" 2>"$SCRATCH/err")"
  code=$?
  err="$(cat "$SCRATCH/err")"
  printf '%s|%s|%s' "$code" "$out" "$err"
}

INSTALLED="$SCRATCH/installed"
mkdir -p "$INSTALLED/.claude/skills"
cp -R "$SKILL" "$INSTALLED/.claude/skills/sync-docs"

CRASHING="$SCRATCH/crashing"
mkdir -p "$CRASHING/.claude/skills/sync-docs/scripts"
printf 'import sys\nsys.stderr.write("boom\\n")\nsys.exit(2)\n' >"$CRASHING/.claude/skills/sync-docs/scripts/check_tree.py"

EMPTY="$SCRATCH/empty-home"
mkdir -p "$EMPTY"

SHELLS="sh bash"
if command -v zsh >/dev/null 2>&1; then
  SHELLS="$SHELLS zsh"
else
  echo "    zsh is not installed: its runs are skipped" >&2
fi

for sh_name in $SHELLS; do
  sh_path="$(command -v "$sh_name")"

  result="$(run_hook "$sh_path" "$INSTALLED" "$PY_DIR:/usr/bin:/bin" 'git commit -m change')"
  code="${result%%|*}"
  out="${result#*|}"; out="${out%|*}"
  ctx="$(printf '%s' "$out" | jq -r '.hookSpecificOutput.additionalContext // empty' 2>/dev/null)"
  decision="$(printf '%s' "$out" | jq -r '.hookSpecificOutput.permissionDecision // .decision // empty' 2>/dev/null)"
  case "$ctx" in *"src/features/x: no README.md in this feature folder"*) ok=1 ;; *) ok=0 ;; esac
  [ "$code" = "0" ] && [ "$ok" = "1" ] && [ -z "$decision" ] && c=1 || c=0
  check "TREE-03 [$sh_name] a tree error before git commit reaches Claude as context, with no decision and exit 0" "$c"

  result="$(run_hook "$sh_path" "$INSTALLED" "$PY_DIR:/usr/bin:/bin" 'git status')"
  [ "$result" = "0||" ] && c=1 || c=0
  check "TREE-04 [$sh_name] a command other than git commit adds nothing" "$c"

  result="$(run_hook "$sh_path" "$EMPTY" "$PY_DIR:/usr/bin:/bin" 'git commit -m change')"
  [ "$result" = "0||" ] && c=1 || c=0
  check "TREE-05 [$sh_name] without sync-docs installed the hook adds nothing and exits 0" "$c"

  result="$(run_hook "$sh_path" "$INSTALLED" "$SCRATCH/no-bin" 'git commit -m change')"
  [ "$result" = "0||" ] && c=1 || c=0
  check "TREE-06 [$sh_name] without python3 the hook adds nothing and exits 0" "$c"

  result="$(run_hook "$sh_path" "$CRASHING" "$PY_DIR:/usr/bin:/bin" 'git commit -m change')"
  [ "$result" = "0||" ] && c=1 || c=0
  check "TREE-07 [$sh_name] a checker that exits 2 does not block: exit 0, no output" "$c"
done

echo
if [ "$FAIL" -gt 0 ]; then
  printf 'Results: %d passed, %d failed\n' "$PASS" "$FAIL" >&2
  exit 1
fi
printf 'Results: %d passed, %d failed\n' "$PASS" "$FAIL"
