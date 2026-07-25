#!/usr/bin/env bash
# Destructive-test acceptance for run-codex-sync.sh. All mutations happen in
# an isolated temporary copy and a fake HOME; the working tree and real user
# configuration remain read-only.

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FIXTURE_ROOT=$(mktemp -d)
FIXTURE_REPO="$FIXTURE_ROOT/repo"
FIXTURE_HOME="$FIXTURE_ROOT/home"
FIXTURE_BIN="$FIXTURE_ROOT/bin"

cleanup() { rm -rf "$FIXTURE_ROOT"; }
trap cleanup EXIT

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'
PASS=0
FAIL=0

check() {
  local name="$1" cond="$2"
  if [ "$cond" = "1" ]; then
    PASS=$((PASS + 1))
    printf "${GREEN}PASS${NC} %s\n" "$name"
  else
    FAIL=$((FAIL + 1))
    printf "${RED}FAIL${NC} %s\n" "$name"
  fi
}

cp -R "$REPO_ROOT" "$FIXTURE_REPO"
mkdir -p "$FIXTURE_HOME/.codex" "$FIXTURE_BIN"

# A user-owned MCP definition with the same logical name as a catalog entry
# must survive installation without creating an invalid duplicate TOML table.
printf '[mcp_servers."strands-agents"]\ncommand = "existing-strands"\n' >"$FIXTURE_HOME/.codex/config.toml"

# install.sh only needs these commands to exist for this isolated deployment;
# no external CLI or network action is part of the fixture.
printf '#!/usr/bin/env bash\nexit 0\n' >"$FIXTURE_BIN/claude"
printf '#!/usr/bin/env bash\nexit 0\n' >"$FIXTURE_BIN/uvx"
chmod +x "$FIXTURE_BIN/claude" "$FIXTURE_BIN/uvx"

INSTALL_OUTPUT=$(PATH="$FIXTURE_BIN:$PATH" HOME="$FIXTURE_HOME" bash "$FIXTURE_REPO/install.sh" 2>&1)
INSTALL_EXIT=$?

run_sync() {
  CODEX_SYNC_REPO_ROOT_OVERRIDE="$FIXTURE_REPO" \
    CODEX_SYNC_HOME_OVERRIDE="$FIXTURE_HOME" \
    bash "$FIXTURE_REPO/tests/run-codex-sync.sh" 2>&1
}

assert_only_failure() {
  local name="$1" expected_id="$2" output unexpected
  output=$(run_sync)
  if printf '%s\n' "$output" | grep -q "FAIL.*$expected_id"; then
    unexpected=$(printf '%s\n' "$output" | grep 'FAIL.*SYNC-' | grep -v "$expected_id" || true)
    check "$name" "$([ -z "$unexpected" ] && echo 1 || echo 0)"
  else
    check "$name" 0
  fi
}

baseline=$(run_sync)
BASELINE_EXIT=$?
check "baseline fixture is fully synchronized" \
  "$([ "$INSTALL_EXIT" -eq 0 ] && [ "$BASELINE_EXIT" -eq 0 ] && echo 1 || echo 0)"
check "installer explains the required Codex hook trust step" \
  "$(printf '%s' "$INSTALL_OUTPUT" | grep -Fq '/hooks' && echo 1 || echo 0)"
preserved_strands_count=$(grep -Ec '^\[mcp_servers\.("strands-agents"|strands-agents)\]$' "$FIXTURE_HOME/.codex/config.toml")
preserved_strands_command=$(grep -Ec '^command = "existing-strands"$' "$FIXTURE_HOME/.codex/config.toml")
check "installer preserves a non-managed MCP definition without duplication" \
  "$([ "$preserved_strands_count" -eq 1 ] && [ "$preserved_strands_command" -eq 1 ] && echo 1 || echo 0)"

mv "$FIXTURE_HOME/.agents/skills/digital-agency-frontend" "$FIXTURE_ROOT/digital-agency-frontend-link"
assert_only_failure "missing deployed custom skill triggers only SYNC-02" "SYNC-02"
mv "$FIXTURE_ROOT/digital-agency-frontend-link" "$FIXTURE_HOME/.agents/skills/digital-agency-frontend"

mv "$FIXTURE_REPO/.claude/skills/adr" "$FIXTURE_REPO/.claude/skills/adr.disabled"
assert_only_failure "skill target deletion triggers only SYNC-01" "SYNC-01"
mv "$FIXTURE_REPO/.claude/skills/adr.disabled" "$FIXTURE_REPO/.claude/skills/adr"

cp "$FIXTURE_REPO/.mcp.json" "$FIXTURE_ROOT/mcp.json"
jq '.mcpServers["drift-fixture"] = {"type":"http","url":"https://example.invalid/mcp"}' \
  "$FIXTURE_ROOT/mcp.json" >"$FIXTURE_REPO/.mcp.json"
assert_only_failure "MCP server addition triggers only SYNC-04" "SYNC-04"
cp "$FIXTURE_ROOT/mcp.json" "$FIXTURE_REPO/.mcp.json"

cp "$FIXTURE_REPO/.codex/AGENTS.md" "$FIXTURE_ROOT/agents.md"
cp "$FIXTURE_HOME/.codex/AGENTS.md" "$FIXTURE_ROOT/home-agents.md"
dd if=/dev/zero bs=1024 count=34 2>/dev/null | tr '\0' x >>"$FIXTURE_REPO/.codex/AGENTS.md"
cp "$FIXTURE_REPO/.codex/AGENTS.md" "$FIXTURE_HOME/.codex/AGENTS.md"
assert_only_failure "oversized guidance triggers only SYNC-03" "SYNC-03"
cp "$FIXTURE_ROOT/agents.md" "$FIXTURE_REPO/.codex/AGENTS.md"
cp "$FIXTURE_ROOT/home-agents.md" "$FIXTURE_HOME/.codex/AGENTS.md"

mv "$FIXTURE_REPO/.codex/hooks/pre-edit-adapter.sh" "$FIXTURE_REPO/.codex/hooks/pre-edit-adapter.disabled"
assert_only_failure "adapter rename triggers only SYNC-05" "SYNC-05"
mv "$FIXTURE_REPO/.codex/hooks/pre-edit-adapter.disabled" "$FIXTURE_REPO/.codex/hooks/pre-edit-adapter.sh"

printf '\nlocal drift\n' >>"$FIXTURE_HOME/.codex/AGENTS.md"
assert_only_failure "deployed guidance edit triggers only SYNC-06" "SYNC-06"

echo ""
echo "===================="
printf "Results: ${GREEN}%d passed${NC}, ${RED}%d failed${NC}\n" "$PASS" "$FAIL"

if [ "$FAIL" -gt 0 ]; then
  exit 1
fi
