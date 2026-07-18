#!/usr/bin/env bash
# Automated skill routing test runner
# Usage: bash tests/run-skill-routing.sh

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEST_DIR="$REPO_ROOT/tests/skill-routing"

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
      gsub(/ → /, "→")
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
  expected=$(extract_first_line "$file" "## Expected Skill")
  exp_norm=$(echo "$expected" | tr '[:upper:]' '[:lower:]')
  date_now=$(date '+%Y-%m-%d')

  # Build routing evaluation query
  local query
  query="Routing evaluation. Apply rules below and output ONLY the skill name.

Rules:
- coder: code implementation, modification, refactoring, tests, debugging
- minto-reviewer: diagnose or critique the structure of an existing document, outline, or slide storyline
- minto-rewriter: rewrite, restructure, polish, or finalize an existing draft or document
- minto-builder: build a document through dialogue from a topic, notes, or incomplete material
- clarifier: ambiguity in intent, scope, acceptance criteria, or constraints (what to build is unclear)
- advisor: decision, trade-off, recommendation, compare options (goal clear enough to choose a path)
- coder→minto-rewriter: request requires both code changes AND updating an existing document

User request: ${prompt}

Output exactly one of: coder | minto-reviewer | minto-rewriter | minto-builder | clarifier | advisor | coder→minto-rewriter
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

printf "\n${BOLD}Skill Routing Tests${NC}\n"
echo "===================="
echo ""

for f in "$TEST_DIR"/*.md; do
  [ -f "$f" ] || continue
  run_test "$f"
done

echo ""
echo "===================="
printf "Results: ${GREEN}%d passed${NC}, ${RED}%d failed${NC}\n" "$PASS" "$FAIL"

if [ "$FAIL" -gt 0 ]; then
  printf "\nFailed:%b\n" "$FAIL_NAMES"
  exit 1
fi
