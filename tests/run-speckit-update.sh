#!/usr/bin/env bash
# Behavior test for .claude/hooks/speckit-expand-update.sh.
# Verifies the hook's per-project refresh behavior (init runs, throttling,
# constitution protection) and — the invariant this repo now enforces after
# removing vendored speckit-* skills (docs/adr/0001) — that the hook never
# touches any path outside the invoking project's own workspace, in
# particular $HOME/.claude/skills.
#
# Deterministic: specify/uv/gh/curl are stubbed on PATH; no network is used.
# Usage: bash tests/run-speckit-update.sh

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOOK="$REPO_ROOT/.claude/hooks/speckit-expand-update.sh"

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

PASS=0
FAIL=0
FAIL_NAMES=""

CURL_STUB='#!/usr/bin/env bash
for a in "$@"; do
  [ "$a" = "-o" ] && exit 1
done
case "$*" in
  *releases/latest*) echo "{\"tag_name\":\"v0.0.0-stub\"}" ;;
  *) exit 1 ;;
esac'

if ! command -v jq >/dev/null 2>&1; then
  echo "Error: 'jq' is required for this test." >&2
  exit 1
fi

check() {
  local name="$1" cond="$2"
  if [ "$cond" = "1" ]; then
    PASS=$((PASS + 1))
    printf "${GREEN}PASS${NC} %s\n" "$name"
  else
    FAIL=$((FAIL + 1))
    FAIL_NAMES="$FAIL_NAMES\n  - $name"
    printf "${RED}FAIL${NC} %s\n" "$name"
  fi
}

# Sets up an isolated $HOME + project + stubbed toolchain under "$1".
# "$2" controls whether ~/.claude/skills pre-exists, so we can assert the
# hook never writes into it.
setup_workspace() {
  local work="$1" seed_user_skills="$2"
  local home="$work/home" proj="$work/proj" bin="$work/bin"

  if [ "$seed_user_skills" = "1" ]; then
    mkdir -p "$home/.claude/skills/speckit-foo"
    printf 'UNTOUCHED\n' >"$home/.claude/skills/speckit-foo/SKILL.md"
  fi

  mkdir -p "$proj/.specify" "$proj/.claude/skills/speckit-foo"
  printf 'FRESH-foo\n' >"$proj/.claude/skills/speckit-foo/SKILL.md"

  mkdir -p "$bin"
  local init_count_file="$work/init_count"
  printf '0\n' >"$init_count_file"
  cat >"$bin/specify" <<EOF
#!/usr/bin/env bash
if [ "\$1" = "init" ]; then
  c=\$(cat "$init_count_file")
  echo \$((c + 1)) >"$init_count_file"
fi
exit 0
EOF
  printf '#!/usr/bin/env bash\nexit 0\n' >"$bin/uv"
  printf '#!/usr/bin/env bash\nexit 1\n' >"$bin/gh"
  printf '%s\n' "$CURL_STUB" >"$bin/curl"
  chmod +x "$bin/specify" "$bin/uv" "$bin/gh" "$bin/curl"
}

run_hook() {
  local proj="$1" home="$2" bin="$3"
  shift 3
  local input
  input=$(jq -n --arg cwd "$proj" '{cwd:$cwd, command_name:"speckit.plan"}')
  HOME="$home" PATH="$bin:$PATH" "$@" bash "$HOOK" <<<"$input" >/dev/null 2>&1
}

# Same as run_hook but fires a SessionStart event (no command_name) and
# echoes stdout, so callers can assert on the additionalContext body.
run_session_start() {
  local proj="$1" home="$2" bin="$3"
  shift 3
  local input
  input=$(jq -n --arg cwd "$proj" '{cwd:$cwd, hook_event_name:"SessionStart"}')
  HOME="$home" PATH="$bin:$PATH" "$@" bash "$HOOK" <<<"$input" 2>/dev/null
}

# --- Test 1: init runs and the throttle state file is updated ---
WORK1=$(mktemp -d)
setup_workspace "$WORK1" "0"
run_hook "$WORK1/proj" "$WORK1/home" "$WORK1/bin" env SPECIFY_FORCE_AUTO_UPDATE=1
[ -f "$WORK1/proj/.specify/.last-auto-update" ] && c=1 || c=0
check "specify init runs and records the throttle state file" "$c"
rm -rf "$WORK1"

# --- Test 2: a second call within the throttle window skips init ---
WORK2=$(mktemp -d)
setup_workspace "$WORK2" "0"
run_hook "$WORK2/proj" "$WORK2/home" "$WORK2/bin" env SPECIFY_FORCE_AUTO_UPDATE=1
run_hook "$WORK2/proj" "$WORK2/home" "$WORK2/bin" env SPECIFY_AUTO_UPDATE_INTERVAL_SECONDS=86400
got=$(cat "$WORK2/init_count" 2>/dev/null || echo 0)
[ "$got" = "1" ] && c=1 || c=0
check "second call within the throttle window does not re-run init" "$c"
rm -rf "$WORK2"

# --- Test 3: a customized constitution.md survives the refresh ---
WORK3=$(mktemp -d)
setup_workspace "$WORK3" "0"
mkdir -p "$WORK3/proj/.specify/memory" "$WORK3/proj/.specify/templates"
printf 'TEMPLATE\n' >"$WORK3/proj/.specify/templates/constitution-template.md"
printf 'CUSTOMIZED\n' >"$WORK3/proj/.specify/memory/constitution.md"
run_hook "$WORK3/proj" "$WORK3/home" "$WORK3/bin" env SPECIFY_FORCE_AUTO_UPDATE=1
got=$(cat "$WORK3/proj/.specify/memory/constitution.md" 2>/dev/null || echo MISSING)
[ "$got" = "CUSTOMIZED" ] && c=1 || c=0
check "customized constitution.md is preserved across the refresh" "$c"
rm -rf "$WORK3"

# --- Test 4: hook never writes to $HOME/.claude/skills (no global propagation) ---
WORK4=$(mktemp -d)
setup_workspace "$WORK4" "1"
run_hook "$WORK4/proj" "$WORK4/home" "$WORK4/bin" env SPECIFY_FORCE_AUTO_UPDATE=1
got=$(cat "$WORK4/home/.claude/skills/speckit-foo/SKILL.md" 2>/dev/null || echo MISSING)
[ "$got" = "UNTOUCHED" ] && c=1 || c=0
check "pre-existing user-scope speckit skill is left untouched" "$c"
[ ! -d "$WORK4/home/.claude/skills/speckit-bar" ] && c=1 || c=0
check "no new skill is created under the user-scope install" "$c"
rm -rf "$WORK4"

# --- Test 5: no .specify directory -> no-op, no crash ---
WORK5=$(mktemp -d)
mkdir -p "$WORK5/home" "$WORK5/proj" "$WORK5/bin"
printf '#!/usr/bin/env bash\nexit 0\n' >"$WORK5/bin/specify"
printf '#!/usr/bin/env bash\nexit 0\n' >"$WORK5/bin/uv"
printf '#!/usr/bin/env bash\nexit 1\n' >"$WORK5/bin/gh"
printf '%s\n' "$CURL_STUB" >"$WORK5/bin/curl"
chmod +x "$WORK5/bin/specify" "$WORK5/bin/uv" "$WORK5/bin/gh" "$WORK5/bin/curl"
input5=$(jq -n --arg cwd "$WORK5/proj" '{cwd:$cwd, command_name:"speckit.plan"}')
HOME="$WORK5/home" PATH="$WORK5/bin:$PATH" SPECIFY_FORCE_AUTO_UPDATE=1 \
  bash "$HOOK" <<<"$input5" >/dev/null 2>&1
rc=$?
[ "$rc" -eq 0 ] && [ ! -d "$WORK5/home/.claude" ] && c=1 || c=0
check "no .specify directory: hook exits cleanly, touches nothing under HOME" "$c"
rm -rf "$WORK5"

# --- Test 6: SessionStart refreshes a project that already adopted Spec Kit ---
WORK6=$(mktemp -d)
setup_workspace "$WORK6" "0"
out6=$(run_session_start "$WORK6/proj" "$WORK6/home" "$WORK6/bin" env SPECIFY_FORCE_AUTO_UPDATE=1)
[ -f "$WORK6/proj/.specify/.last-auto-update" ] && c=1 || c=0
check "SessionStart runs the refresh for a project with .specify/" "$c"
echo "$out6" | jq -e '.hookSpecificOutput.hookEventName == "SessionStart"' >/dev/null 2>&1 && c=1 || c=0
check "SessionStart output reports hookEventName SessionStart" "$c"
rm -rf "$WORK6"

# --- Test 7: SessionStart stays silent once throttled (no per-session noise) ---
WORK7=$(mktemp -d)
setup_workspace "$WORK7" "0"
run_session_start "$WORK7/proj" "$WORK7/home" "$WORK7/bin" env SPECIFY_FORCE_AUTO_UPDATE=1 >/dev/null
out7=$(run_session_start "$WORK7/proj" "$WORK7/home" "$WORK7/bin")
[ -z "$out7" ] && c=1 || c=0
check "throttled SessionStart run stays silent" "$c"
rm -rf "$WORK7"

# --- Test 8: SessionStart in a project without .specify/ stays silent ---
WORK8=$(mktemp -d)
mkdir -p "$WORK8/home" "$WORK8/proj" "$WORK8/bin"
printf '#!/usr/bin/env bash\nexit 0\n' >"$WORK8/bin/specify"
printf '#!/usr/bin/env bash\nexit 0\n' >"$WORK8/bin/uv"
printf '#!/usr/bin/env bash\nexit 1\n' >"$WORK8/bin/gh"
printf '%s\n' "$CURL_STUB" >"$WORK8/bin/curl"
chmod +x "$WORK8/bin/specify" "$WORK8/bin/uv" "$WORK8/bin/gh" "$WORK8/bin/curl"
out8=$(run_session_start "$WORK8/proj" "$WORK8/home" "$WORK8/bin" env SPECIFY_FORCE_AUTO_UPDATE=1)
[ -z "$out8" ] && c=1 || c=0
check "SessionStart in a non-spec-kit project stays silent" "$c"
rm -rf "$WORK8"

echo
if [ "$FAIL" -eq 0 ]; then
  printf "${GREEN}All %d checks passed.${NC}\n" "$PASS"
  exit 0
else
  printf "${RED}%d passed, %d failed:${NC}" "$PASS" "$FAIL"
  printf "%b\n" "$FAIL_NAMES"
  exit 1
fi
