#!/usr/bin/env bash
# Deterministic installer contract: isolated HOME, stubbed external CLIs, and
# no network or writes to the operator's real ~/.claude directory.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEST_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/my-claude-code-install.XXXXXX")"
TEST_HOME="$TEST_ROOT/home"
STUB_BIN="$TEST_ROOT/bin"
CLAUDE_LOG="$TEST_ROOT/claude.log"
TARGET="$TEST_HOME/.claude"

cleanup() {
  rm -rf "$TEST_ROOT"
}
trap cleanup EXIT

fail() {
  printf 'FAIL: %s\n' "$1" >&2
  exit 1
}

pass() {
  printf 'PASS: %s\n' "$1"
}

assert_absent() {
  [ ! -e "$1" ] || fail "$2"
  pass "$2"
}

assert_file_equals() {
  cmp -s "$1" "$2" || fail "$3"
  pass "$3"
}

mkdir -p "$STUB_BIN" "$TARGET"

cat >"$STUB_BIN/claude" <<'STUB'
#!/usr/bin/env bash
set -eu
printf '%s\n' "$*" >>"$CLAUDE_LOG"

# Stateful enough to exercise install.sh's own already-registered/
# already-installed branches on a second run: report back only what an
# earlier call in this same log has already logged. Builds the whole
# response into one variable and writes it with a single printf — install.sh
# pipes this into `grep -q`, which closes its end of the pipe as soon as it
# finds a match; a loop of separate printfs risks SIGPIPE on a later line
# once that happens, which (combined with install.sh's own `pipefail`) would
# make an already-successful match look like a pipeline failure.
if [ "${1:-}" = "plugin" ] && [ "${2:-}" = "marketplace" ] && [ "${3:-}" = "list" ]; then
  grep -qx 'plugin marketplace add anthropics/claude-plugins-official' "$CLAUDE_LOG" &&
    printf '%s\n' 'claude-plugins-official'
elif [ "${1:-}" = "plugin" ] && [ "${2:-}" = "list" ]; then
  out=""
  for p in frontend-design code-review skill-creator github deploy-on-aws microsoft-docs; do
    if grep -qx "plugin install ${p}@claude-plugins-official" "$CLAUDE_LOG"; then
      out="${out}${p}@claude-plugins-official
"
    fi
  done
  printf '%s' "$out"
fi
STUB

cat >"$STUB_BIN/uvx" <<'STUB'
#!/usr/bin/env bash
exit 0
STUB

chmod +x "$STUB_BIN/claude" "$STUB_BIN/uvx"

# Seed paths managed by the current repository version. hooks/ and
# scripts/guardrails/ are no longer managed paths (install.sh dropped their
# uninstall-path cleanup once those directories had been gone from this
# repository long enough — see commit 3be3ffa); a leftover copy from a much
# older install is now ordinary user-owned territory, same as any other
# untracked path under ~/.claude, so this test no longer seeds or asserts
# against them.
mkdir -p \
  "$TARGET/rules" \
  "$TARGET/skills/stale-skill" \
  "$TARGET/agents" \
  "$TARGET/commands"
printf '%s\n' stale >"$TARGET/rules/stale.md"
printf '%s\n' stale >"$TARGET/skills/stale-skill/SKILL.md"
printf '%s\n' stale >"$TARGET/agents/stale.md"
printf '%s\n' stale >"$TARGET/commands/stale.md"

# These paths are user-owned because the installer does not declare them.
printf '%s\n' preserve >"$TARGET/user-owned.txt"
printf '%s\n' '{"local":true}' >"$TARGET/settings.local.json"

git_config="$REPO_ROOT/.specify/extensions/git/git-config.yml"
git_config_before="$(cksum <"$git_config")"

install_output="$TEST_ROOT/install.out"
if ! HOME="$TEST_HOME" \
  PATH="$STUB_BIN:/usr/bin:/bin:/usr/sbin:/sbin" \
  CLAUDE_LOG="$CLAUDE_LOG" \
  GOOGLE_DEV_KNOWLEDGE_API_KEY="test-key" \
  bash "$REPO_ROOT/install.sh" >"$install_output" 2>&1; then
  sed 's/^/    /' "$install_output" >&2
  fail "install.sh completes against the isolated home"
fi
pass "install.sh completes against the isolated home"

assert_file_equals "$REPO_ROOT/.claude/CLAUDE.md" "$TARGET/CLAUDE.md" \
  "CLAUDE.md matches the repository"
assert_file_equals "$REPO_ROOT/.claude/settings.json" "$TARGET/settings.json" \
  "settings.json matches the repository"
assert_file_equals "$REPO_ROOT/install.sh" "$TARGET/install.sh" \
  "installed install.sh matches the repository"

diff -r "$REPO_ROOT/.claude/rules" "$TARGET/rules" >/dev/null ||
  fail "rules directory matches the repository"
pass "rules directory matches the repository"

expected_skills="$TEST_ROOT/expected-skills"
cp -R "$REPO_ROOT/.claude/skills" "$expected_skills"
rm -rf "$expected_skills"/speckit-* "$expected_skills/.DS_Store"
diff -r "$expected_skills" "$TARGET/skills" >/dev/null ||
  fail "skills contain only repository-managed shared skills"
pass "skills contain only repository-managed shared skills"

assert_absent "$TARGET/agents" "absent managed agents are removed"
assert_absent "$TARGET/commands" "retired commands are removed"

grep -qx 'preserve' "$TARGET/user-owned.txt" || fail "unrelated user file is preserved"
pass "unrelated user file is preserved"
grep -qx '{"local":true}' "$TARGET/settings.local.json" ||
  fail "unmanaged settings.local.json is preserved"
pass "unmanaged settings.local.json is preserved"

git_config_after="$(cksum <"$git_config")"
[ "$git_config_before" = "$git_config_after" ] ||
  fail "installer does not mutate the source Spec Kit configuration"
pass "installer does not mutate the source Spec Kit configuration"

actual_mcps="$(awk '$1 == "mcp" && $2 == "add" {print $5}' "$CLAUDE_LOG" | sort)"
expected_mcps="$(jq -r '.mcpServers | keys[]' "$REPO_ROOT/.mcp.json" | sort)"
[ "$actual_mcps" = "$expected_mcps" ] || {
  printf 'Expected MCPs:\n%s\nActual MCPs:\n%s\n' "$expected_mcps" "$actual_mcps" >&2
  fail "all and only current MCP servers are upserted"
}
pass "all and only current MCP servers are upserted"

grep -qxF 'plugin marketplace add anthropics/claude-plugins-official' "$CLAUDE_LOG" ||
  fail "official plugin marketplace is added on a fresh environment"
pass "official plugin marketplace is added on a fresh environment"

for official_plugin in frontend-design code-review skill-creator github deploy-on-aws microsoft-docs; do
  grep -qxF "plugin install ${official_plugin}@claude-plugins-official" "$CLAUDE_LOG" ||
    fail "${official_plugin} is installed on a fresh environment"
  grep -qxF "plugin enable ${official_plugin}@claude-plugins-official" "$CLAUDE_LOG" ||
    fail "${official_plugin} is enabled on a fresh environment"
done
pass "official plugins (frontend-design, code-review, skill-creator, github, deploy-on-aws, microsoft-docs) are installed and enabled"

if grep -qE '(^|[^[:alnum:]_])jq([^[:alnum:]_]|$)' "$REPO_ROOT/install.sh"; then
  fail "installer has no unused jq dependency"
fi
pass "installer has no unused jq dependency"

if grep -qF '.specify/extensions/git/git-config.yml' "$REPO_ROOT/install.sh"; then
  fail "installer has no source-tree Spec Kit mutation"
fi
pass "installer has no source-tree Spec Kit mutation"

[ -x "$TARGET/install.sh" ] || fail "installed install.sh is executable"
pass "installed install.sh is executable"

# --- Preflight: missing required commands -----------------------------------
# An empty PATH means `command -v claude` / `command -v uvx` both fail, so
# install.sh must exit 1 with its own diagnostic before touching anything —
# this path was previously dead as far as this suite was concerned.
EMPTY_BIN="$TEST_ROOT/empty-bin"
mkdir -p "$EMPTY_BIN"
# PATH reassignment applies to resolving the `bash` command word itself, not
# just to what install.sh sees — symlink the real interpreter in so `bash` is
# still found, while claude/uvx (elsewhere on the real PATH) are not.
ln -s "$(command -v bash)" "$EMPTY_BIN/bash"
preflight_output="$TEST_ROOT/preflight.out"
if HOME="$TEST_ROOT/unused-home" PATH="$EMPTY_BIN" bash "$REPO_ROOT/install.sh" \
  >"$preflight_output" 2>&1; then
  fail "install.sh exits non-zero when claude/uvx are missing"
fi
grep -q 'Missing required command: claude' "$preflight_output" ||
  fail "install.sh names the missing command in its preflight error"
pass "install.sh fails fast with a clear message when claude/uvx are missing"

# --- Idempotent re-run, and the GOOGLE_DEV_KNOWLEDGE_API_KEY-unset branch ---
# Re-run against the SAME target, appending to the SAME $CLAUDE_LOG (the claude
# stub's `plugin marketplace list` / `plugin list` branches look back through
# that log's full history, so state only carries over if the log is
# continuous — a fresh log for the second run would make every run look like
# a first run). This exercises install.sh's "already present" branches for
# real, not just its "fresh install" branches. `env -u` explicitly removes
# GOOGLE_DEV_KNOWLEDGE_API_KEY rather than merely not re-setting it — an
# ambient value already exported in the *outer* shell running this test would
# otherwise silently leak through and defeat this branch entirely (a prefix
# assignment overrides an inherited value, but the absence of one does not).
lines_before_second_run="$(wc -l <"$CLAUDE_LOG")"
second_output="$TEST_ROOT/install-second.out"
if ! env -u GOOGLE_DEV_KNOWLEDGE_API_KEY \
  HOME="$TEST_HOME" \
  PATH="$STUB_BIN:/usr/bin:/bin:/usr/sbin:/sbin" \
  CLAUDE_LOG="$CLAUDE_LOG" \
  bash "$REPO_ROOT/install.sh" >"$second_output" 2>&1; then
  sed 's/^/    /' "$second_output" >&2
  fail "install.sh is idempotent on a second run"
fi
pass "install.sh is idempotent on a second run"

diff -r "$REPO_ROOT/.claude/rules" "$TARGET/rules" >/dev/null ||
  fail "rules directory still matches the repository after a second run"
pass "rules directory still matches the repository after a second run"

second_run_log="$TEST_ROOT/claude-second-run.log"
tail -n "+$((lines_before_second_run + 1))" "$CLAUDE_LOG" >"$second_run_log"

grep -qxF 'plugin marketplace update claude-plugins-official' "$second_run_log" ||
  fail "second run updates rather than re-adds an already-registered marketplace"
pass "second run updates rather than re-adds an already-registered marketplace"

for official_plugin in frontend-design code-review skill-creator github deploy-on-aws microsoft-docs; do
  grep -qxF "plugin install ${official_plugin}@claude-plugins-official" "$second_run_log" &&
    fail "second run does not re-install already-installed plugin ${official_plugin}"
done
pass "second run does not re-install any already-installed plugin"

grep -qxF 'mcp remove -s user google-developer-knowledge' "$second_run_log" ||
  fail "google-developer-knowledge is removed when its API key is unset"
pass "google-developer-knowledge is removed when its API key is unset"

grep -qF 'mcp add -s user google-developer-knowledge' "$second_run_log" &&
  fail "google-developer-knowledge is not re-added when its API key is unset"
pass "google-developer-knowledge is not re-added when its API key is unset"

printf '%s\n' 'All installer contract checks passed.'
