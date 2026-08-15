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

if [ "${1:-}" = "plugin" ] && [ "${2:-}" = "marketplace" ] && [ "${3:-}" = "list" ]; then
  printf '%s\n' 'openai-codex'
elif [ "${1:-}" = "plugin" ] && [ "${2:-}" = "list" ]; then
  printf '%s\n' 'codex@openai-codex'
fi
STUB

cat >"$STUB_BIN/uvx" <<'STUB'
#!/usr/bin/env bash
exit 0
STUB

chmod +x "$STUB_BIN/claude" "$STUB_BIN/uvx"

# Seed paths managed by current and earlier repository versions.
mkdir -p \
  "$TARGET/hooks" \
  "$TARGET/rules" \
  "$TARGET/skills/stale-skill" \
  "$TARGET/agents" \
  "$TARGET/commands" \
  "$TARGET/scripts/guardrails"
printf '%s\n' stale >"$TARGET/hooks/stale.sh"
printf '%s\n' stale >"$TARGET/rules/stale.md"
printf '%s\n' stale >"$TARGET/skills/stale-skill/SKILL.md"
printf '%s\n' stale >"$TARGET/agents/stale.md"
printf '%s\n' stale >"$TARGET/commands/stale.md"
printf '%s\n' stale >"$TARGET/scripts/guardrails/stale.sh"

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

assert_absent "$TARGET/hooks" "retired hooks are removed"
assert_absent "$TARGET/agents" "absent managed agents are removed"
assert_absent "$TARGET/commands" "retired commands are removed"
assert_absent "$TARGET/scripts/guardrails" "retired guardrails are removed"

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

if grep -qE '(^|[^[:alnum:]_])jq([^[:alnum:]_]|$)' "$REPO_ROOT/install.sh"; then
  fail "installer has no unused jq dependency"
fi
pass "installer has no unused jq dependency"

if grep -qF '.specify/extensions/git/git-config.yml' "$REPO_ROOT/install.sh"; then
  fail "installer has no source-tree Spec Kit mutation"
fi
pass "installer has no source-tree Spec Kit mutation"

printf '%s\n' 'All installer contract checks passed.'
