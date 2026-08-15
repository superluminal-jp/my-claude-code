#!/usr/bin/env bash
# Behavior test for the pre-edit guardrail (Q9/Q10) against the shared
# script. See
# specs/013-cross-agent-guardrail-implementation/contracts/guardrail-script-io.md.
#
# Deterministic: no network, no external tools beyond jq and git.
# Usage: bash tests/run-pre-edit-guard.sh

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SHARED="$REPO_ROOT/scripts/guardrails/pre-edit-block.sh"

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
  jq -n --arg path "$path" --arg project_dir "$proj" '{tool_name:"Edit", path:$path, project_dir:$project_dir}' |
    bash "$SHARED" 2>/dev/null | jq -r '.decision // "PARSE_ERROR"'
}

check "shared: .git/ path denied" "$([ "$(shared_decision '.git/config' "$FEATURE_PROJ")" = "deny" ] && echo 1 || echo 0)"
check "shared: main branch denied" "$([ "$(shared_decision 'foo.txt' "$MAIN_PROJ")" = "deny" ] && echo 1 || echo 0)"
check "shared: feature branch allowed" "$([ "$(shared_decision 'foo.txt' "$FEATURE_PROJ")" = "allow" ] && echo 1 || echo 0)"
check "shared: unknown project_dir allowed (no false positive)" "$([ "$(shared_decision 'foo.txt' '/nonexistent/path')" = "allow" ] && echo 1 || echo 0)"

# ---------------------------------------------------------------------------
# Part 2: Codex CLI adapter — removed by feature 021.
# ---------------------------------------------------------------------------
# This repository no longer ships a Codex adapter for this guard. Codex fires
# PreToolUse for shell commands only, so an edit-protection hook cannot run
# there at all; README.md § "Codex CLI support" documents the absence.
# The shared decision script (Part 1) above is unaffected. See
# specs/021-codex-official-import/.

echo ""
echo "===================="
printf "Results: ${GREEN}%d passed${NC}, ${RED}%d failed${NC}\n" "$PASS" "$FAIL"

if [ "$FAIL" -gt 0 ]; then
  printf "\nFailed:%b\n" "$FAIL_NAMES"
  exit 1
fi
