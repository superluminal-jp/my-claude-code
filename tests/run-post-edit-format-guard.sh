#!/usr/bin/env bash
# Behavior test for the post-edit auto-format guardrail (Q7) across the
# shared script, the refactored Claude Code hook, and the Codex CLI adapter.
# See specs/013-cross-agent-guardrail-implementation/contracts/guardrail-script-io.md.
#
# Deterministic: no network. Skips shfmt/shellcheck/yamllint-specific
# assertions gracefully if those tools aren't installed (matches the
# "missing tools are silently skipped" behavior being tested).
# Usage: bash tests/run-post-edit-format-guard.sh

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SHARED="$REPO_ROOT/scripts/guardrails/post-edit-format.sh"
CLAUDE_HOOK="$REPO_ROOT/.claude/hooks/post-edit-format.sh"
CODEX_ADAPTER="$REPO_ROOT/.codex/hooks/post-edit-adapter.sh"

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

WORK=$(mktemp -d)
cleanup() { rm -rf "$WORK"; }
trap cleanup EXIT

# ---------------------------------------------------------------------------
# Part 1: shared script, direct — reformats a badly-indented .sh file
# ---------------------------------------------------------------------------

if command -v shfmt >/dev/null 2>&1; then
  SH_FILE="$WORK/example.sh"
  printf '#!/usr/bin/env bash\nif true; then\n    echo hi\nfi\n' >"$SH_FILE"
  if [ -x "$SHARED" ]; then
    jq -n --arg path "$SH_FILE" '{path:$path}' | bash "$SHARED" >/dev/null 2>&1
    check "shared: .sh file reformatted to 2-space indent" "$(grep -q '^  echo hi$' "$SH_FILE" && echo 1 || echo 0)"
  else
    check "shared: .sh file reformatted to 2-space indent (MISSING)" 0
  fi
else
  echo "(skipping shfmt-dependent shared-script assertion: shfmt not installed)"
fi

# Malformed JSON should be reported as a warning, not crash the script
JSON_FILE="$WORK/bad.json"
printf '{ invalid' >"$JSON_FILE"
if [ -x "$SHARED" ]; then
  OUT=$(jq -n --arg path "$JSON_FILE" '{path:$path}' | bash "$SHARED" 2>&1)
  RC=$?
  if [ "$RC" -eq 0 ] && echo "$OUT" | grep -qi warning; then
    check "shared: malformed JSON produces a warning, exits 0" 1
  else
    check "shared: malformed JSON produces a warning, exits 0" 0
  fi
else
  check "shared: malformed JSON produces a warning, exits 0 (MISSING)" 0
fi

# ---------------------------------------------------------------------------
# Part 2: Claude Code hook wrapper — never blocks (FR-021)
# ---------------------------------------------------------------------------

TXT_FILE="$WORK/plain.txt"
echo "hello" >"$TXT_FILE"
if [ -x "$CLAUDE_HOOK" ]; then
  jq -n --arg path "$TXT_FILE" '{tool_input:{path:$path}}' | bash "$CLAUDE_HOOK" >/dev/null 2>&1
  check "claude hook: exits 0 for an unrelated file type (never blocks)" "$([ $? -eq 0 ] && echo 1 || echo 0)"
else
  check "claude hook: exits 0 for an unrelated file type (never blocks) (MISSING)" 0
fi

# ---------------------------------------------------------------------------
# Part 3: Codex CLI adapter
# ---------------------------------------------------------------------------

if command -v shfmt >/dev/null 2>&1; then
  SH_FILE2="$WORK/example2.sh"
  printf '#!/usr/bin/env bash\nif true; then\n    echo hi\nfi\n' >"$SH_FILE2"
  if [ -x "$CODEX_ADAPTER" ]; then
    jq -n --arg path "$SH_FILE2" '{hook_event_name:"PostToolUse", tool_input:{path:$path}}' | bash "$CODEX_ADAPTER" >/dev/null 2>&1
    check "codex adapter: .sh file reformatted to 2-space indent" "$(grep -q '^  echo hi$' "$SH_FILE2" && echo 1 || echo 0)"
  else
    check "codex adapter: .sh file reformatted to 2-space indent (MISSING)" 0
  fi
else
  echo "(skipping shfmt-dependent adapter assertion: shfmt not installed)"
fi

if [ -x "$CODEX_ADAPTER" ]; then
  jq -n --arg path "$TXT_FILE" '{hook_event_name:"PostToolUse", tool_input:{path:$path}}' | bash "$CODEX_ADAPTER" >/dev/null 2>&1
  check "codex adapter: exits 0 for an unrelated file type (never blocks)" "$([ $? -eq 0 ] && echo 1 || echo 0)"
else
  check "codex adapter: exits 0 for an unrelated file type (never blocks) (MISSING)" 0
fi

echo ""
echo "===================="
printf "Results: ${GREEN}%d passed${NC}, ${RED}%d failed${NC}\n" "$PASS" "$FAIL"

if [ "$FAIL" -gt 0 ]; then
  printf "\nFailed:%b\n" "$FAIL_NAMES"
  exit 1
fi
