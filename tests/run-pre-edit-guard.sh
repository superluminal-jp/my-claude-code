#!/usr/bin/env bash
# Behavior test for the pre-edit guardrail (Q9/Q10) across the shared script,
# the refactored Claude Code hook, and the Codex CLI adapter. See
# specs/013-cross-agent-guardrail-implementation/contracts/guardrail-script-io.md.
#
# Deterministic: no network, no external tools beyond jq and git.
# Usage: bash tests/run-pre-edit-guard.sh

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SHARED="$REPO_ROOT/scripts/guardrails/pre-edit-block.sh"
CLAUDE_HOOK="$REPO_ROOT/.claude/hooks/pre-edit.sh"
CODEX_ADAPTER="$REPO_ROOT/.codex/hooks/pre-edit-adapter.sh"

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

PASS=0
FAIL=0
FAIL_NAMES=""

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

# Two throwaway project fixtures: one on "main", one on a feature branch.
MAIN_PROJ=$(mktemp -d)
(cd "$MAIN_PROJ" && git init -q -b main && git commit -q --allow-empty -m init)

FEATURE_PROJ=$(mktemp -d)
(cd "$FEATURE_PROJ" && git init -q -b feature/x && git commit -q --allow-empty -m init)

cleanup() { rm -rf "$MAIN_PROJ" "$FEATURE_PROJ"; }
trap cleanup EXIT

# ---------------------------------------------------------------------------
# Part 1: shared script, direct
# ---------------------------------------------------------------------------

shared_decision() {
  local path="$1" proj="$2"
  [ -x "$SHARED" ] || {
    echo "MISSING"
    return
  }
  jq -n --arg path "$path" --arg project_dir "$proj" '{tool_name:"Edit", path:$path, project_dir:$project_dir}' \
    | bash "$SHARED" 2>/dev/null | jq -r '.decision // "PARSE_ERROR"'
}

check "shared: .git/ path denied" "$([ "$(shared_decision '.git/config' "$FEATURE_PROJ")" = "deny" ] && echo 1 || echo 0)"
check "shared: main branch denied" "$([ "$(shared_decision 'foo.txt' "$MAIN_PROJ")" = "deny" ] && echo 1 || echo 0)"
check "shared: feature branch allowed" "$([ "$(shared_decision 'foo.txt' "$FEATURE_PROJ")" = "allow" ] && echo 1 || echo 0)"
check "shared: unknown project_dir allowed (no false positive)" "$([ "$(shared_decision 'foo.txt' '/nonexistent/path')" = "allow" ] && echo 1 || echo 0)"

# ---------------------------------------------------------------------------
# Part 2: Claude Code hook wrapper — exit code contract preserved (FR-018)
# ---------------------------------------------------------------------------

claude_hook_exit() {
  local path="$1" proj="$2"
  [ -x "$CLAUDE_HOOK" ] || {
    echo "MISSING"
    return
  }
  jq -n --arg path "$path" '{tool_name:"Edit", tool_input:{path:$path}}' \
    | CLAUDE_PROJECT_DIR="$proj" bash "$CLAUDE_HOOK" >/dev/null 2>&1
  echo $?
}

check "claude hook: .git/ path exits 2 (block)" "$([ "$(claude_hook_exit '.git/config' "$FEATURE_PROJ")" = "2" ] && echo 1 || echo 0)"
check "claude hook: main branch exits 2 (block)" "$([ "$(claude_hook_exit 'foo.txt' "$MAIN_PROJ")" = "2" ] && echo 1 || echo 0)"
check "claude hook: feature branch exits 0 (allow)" "$([ "$(claude_hook_exit 'foo.txt' "$FEATURE_PROJ")" = "0" ] && echo 1 || echo 0)"

# ---------------------------------------------------------------------------
# Part 3: Codex CLI adapter
# ---------------------------------------------------------------------------

codex_adapter_decision() {
  local path="$1" proj="$2"
  [ -x "$CODEX_ADAPTER" ] || {
    echo "MISSING"
    return
  }
  jq -n --arg path "$path" --arg proj "$proj" \
    '{hook_event_name:"PreToolUse", tool_name:"Edit", tool_input:{path:$path}, cwd:$proj}' \
    | bash "$CODEX_ADAPTER" 2>/dev/null | jq -r '.hookSpecificOutput.permissionDecision // "PARSE_ERROR"'
}

check "codex adapter: .git/ path -> deny" "$([ "$(codex_adapter_decision '.git/config' "$FEATURE_PROJ")" = "deny" ] && echo 1 || echo 0)"
check "codex adapter: main branch -> deny" "$([ "$(codex_adapter_decision 'foo.txt' "$MAIN_PROJ")" = "deny" ] && echo 1 || echo 0)"
check "codex adapter: feature branch -> allow" "$([ "$(codex_adapter_decision 'foo.txt' "$FEATURE_PROJ")" = "allow" ] && echo 1 || echo 0)"

echo ""
echo "===================="
printf "Results: ${GREEN}%d passed${NC}, ${RED}%d failed${NC}\n" "$PASS" "$FAIL"

if [ "$FAIL" -gt 0 ]; then
  printf "\nFailed:%b\n" "$FAIL_NAMES"
  exit 1
fi
