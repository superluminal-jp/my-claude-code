#!/usr/bin/env bash
# Automated Live Documentation rule test runner
# Usage: bash tests/run-live-documentation.sh

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEST_DIR="$REPO_ROOT/tests/live-documentation"

PASS=0
FAIL=0
FAIL_NAMES=""

GREEN='\033[0;32m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

# Require claude CLI
if ! command -v claude &>/dev/null; then
  echo "Error: 'claude' command not found. Install Claude Code CLI first." >&2
  exit 1
fi

# Extract content between first ``` block under a given section heading
extract_code_block() {
  local file="$1" heading="$2"
  awk -v h="$heading" '
    $0 == h { found=1; next }
    found && /^```/ { in_code=!in_code; next }
    found && in_code { print }
    found && !in_code && /^##/ { exit }
  ' "$file"
}

# Extract first non-empty line under a given section heading (strip backticks and spaces)
extract_first_line() {
  local file="$1" heading="$2"
  awk -v h="$heading" '
    $0 == h { found=1; next }
    found && /^[[:space:]]*$/ { next }
    found {
      gsub(/`/, "")
      sub(/^[[:space:]]*/, ""); sub(/[[:space:]]*$/, "")
      if ($0 != "") { print; exit }
    }
  ' "$file"
}

run_test() {
  local file="$1"

  local name prompt expected exp_norm result pf date_now
  name=$(grep '^# Test:' "$file" | sed 's/^# Test: //')
  prompt=$(extract_code_block "$file" "## Input Prompt")
  expected=$(extract_first_line "$file" "## Expected Behavior")
  exp_norm=$(echo "$expected" | tr '[:upper:]' '[:lower:]')
  date_now=$(date '+%Y-%m-%d')

  # Build Live Documentation evaluation query
  local query
  query="Live Documentation rule evaluation. A developer sent the message below. Apply the Live Documentation rules and output ONLY the keyword that best describes the required response.

Rules:
- drift: code changed but documentation not updated in the same change; flag as Drift violation and block review
- violation: documentation submitted separately from code (doc-only PR for already-shipped code); flag separation
- autogen: documentation artifact can be auto-generated from code; recommend the tool, decline to hand-write
- proximity: documentation proposed for a remote/centralized location; warn and offer co-located alternative
- override-rejected: developer attempts a silent override (no reason stated); reject and request a reason

Developer message:
${prompt}

Output exactly one of: drift | violation | autogen | proximity | override-rejected
No explanation. No other text."

  result=$(printf '%s' "$query" | claude -p 2>/dev/null \
    | tr -d '\n' \
    | sed 's/[[:space:]]//g' \
    | tr '[:upper:]' '[:lower:]')

  if [ "$result" = "$exp_norm" ]; then
    printf "${GREEN}✓ PASS${NC}  %s  (→ %s)\n" "$name" "$result"
    PASS=$((PASS + 1))
    pf="Pass"
  else
    printf "${RED}✗ FAIL${NC}  %s\n" "$name"
    printf "         expected : %s\n" "$exp_norm"
    printf "         got      : %s\n" "$result"
    FAIL=$((FAIL + 1))
    FAIL_NAMES="${FAIL_NAMES}\n  - ${name} (expected: ${exp_norm}, got: ${result})"
    pf="FAIL (got: ${result})"
  fi

  # Update baseline fields in test file (idempotent: only rewrites ___ placeholders)
  sed -i '' \
    -e "s/実行日: ___/実行日: ${date_now}/" \
    -e "s/観察した動作: ___/観察した動作: ${result}/" \
    "$file" 2>/dev/null || true
  sed -i '' \
    -e "s/Pass \/ Fail: ___/Pass \/ Fail: ${pf}/" \
    "$file" 2>/dev/null || true
}

printf "\n${BOLD}Live Documentation Tests${NC}\n"
echo "========================"
echo ""

for f in "$TEST_DIR"/*.md; do
  [ -f "$f" ] || continue
  run_test "$f"
done

echo ""
echo "========================"
printf "Results: ${GREEN}%d passed${NC}, ${RED}%d failed${NC}\n" "$PASS" "$FAIL"

if [ "$FAIL" -gt 0 ]; then
  printf "\nFailed:%b\n" "$FAIL_NAMES"
  exit 1
fi
