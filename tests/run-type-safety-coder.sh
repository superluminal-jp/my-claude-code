#!/usr/bin/env bash
# Automated Type Safety (coder skill) rule test runner
# Usage: bash tests/run-type-safety-coder.sh
#        TEST_MODEL=opus bash tests/run-type-safety-coder.sh   # override eval model (default: haiku)
#
# Exit codes: 0 = all passed; 1 = at least one assertion failed OR the claude CLI
# errored. CLI errors are reported separately as ERROR, never as a failed assertion.

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEST_DIR="$REPO_ROOT/tests/type-safety-coder"

PASS=0
FAIL=0
ERROR=0
FAIL_NAMES=""
ERROR_NAMES=""

# Model used to evaluate the rule prompts. Overridable: TEST_MODEL=sonnet bash tests/...
TEST_MODEL="${TEST_MODEL:-haiku}"

# Every keyword the evaluation prompt is allowed to return. Anything else means the
# CLI failed (session limit, auth error, crash) rather than the rule being misapplied.
VALID_KEYWORDS="annotate fix-type verify-types validate-boundary"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BOLD='\033[1m'
NC='\033[0m'

# True when the CLI returned one of the keywords the prompt asked for
is_valid_keyword() {
  local candidate="$1" k
  for k in $VALID_KEYWORDS; do
    [ "$candidate" = "$k" ] && return 0
  done
  return 1
}

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

  # Build Type Safety evaluation query
  local query
  query="Type Safety rule evaluation (coder skill). A developer sent the message below. Apply the coder skill's Type Safety instructions and output ONLY the keyword that best describes the required response.

Rules:
- annotate: implementing a new/changed public interface in a typed codebase; add explicit type annotations matching the project's convention, without a separate clarifying question
- fix-type: resolving a type-checking error caused by a genuine type mismatch; correct the type (narrowing, proper typing, small refactor) rather than suppressing the checker
- verify-types: about to report a change done in a project with a configured type checker; run the type checker alongside test/lint/format and resolve any introduced error first
- validate-boundary: consuming data crossing a system boundary (parsed external API/JSON response, user input, deserialized payload); validate or narrow its shape before treating it as a typed internal value

Precedence:
- When a message asks for an implementation and to report when it is done, and names a configured type checker, output verify-types even if the implementation also adds or changes a typed public interface.

Developer message:
${prompt}

Output exactly one of: annotate | fix-type | verify-types | validate-boundary
No explanation. No other text."

  local raw rc
  raw=$(printf '%s' "$query" | claude -p --model "$TEST_MODEL" 2>&1)
  rc=$?
  result=$(printf '%s' "$raw" |
    tr -d '\n' |
    sed 's/[[:space:]]//g' |
    tr '[:upper:]' '[:lower:]')

  # Distinguish infrastructure failure from a genuine rule miss: a CLI error would
  # otherwise be recorded as a failed assertion and written into the baseline file.
  if [ "$rc" -ne 0 ] || ! is_valid_keyword "$result"; then
    printf "${YELLOW}⚠ ERROR${NC}  %s\n" "$name"
    printf "         claude CLI failed or returned no recognized keyword (exit %s)\n" "$rc"
    printf "         output   : %s\n" "${raw:-<empty>}"
    ERROR=$((ERROR + 1))
    ERROR_NAMES="${ERROR_NAMES}\n  - ${name} (exit ${rc}, output: ${result:-<empty>})"
    return
  fi

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

printf "\n${BOLD}Type Safety (coder skill) Tests${NC}  [model: %s]\n" "$TEST_MODEL"
echo "========================"
echo ""

for f in "$TEST_DIR"/*.md; do
  [ -f "$f" ] || continue
  run_test "$f"
done

echo ""
echo "========================"
printf "Results: ${GREEN}%d passed${NC}, ${RED}%d failed${NC}, ${YELLOW}%d errored${NC}\n" "$PASS" "$FAIL" "$ERROR"

if [ "$ERROR" -gt 0 ]; then
  printf "\nErrored (CLI problem, not a rule miss — results are inconclusive):%b\n" "$ERROR_NAMES"
fi

if [ "$FAIL" -gt 0 ]; then
  printf "\nFailed:%b\n" "$FAIL_NAMES"
fi

if [ "$FAIL" -gt 0 ] || [ "$ERROR" -gt 0 ]; then
  exit 1
fi
