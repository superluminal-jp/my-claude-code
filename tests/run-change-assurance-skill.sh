#!/usr/bin/env bash
# Offline contract suite for the change-assurance skill
# (specs/061-change-assurance): the bundled checker's acceptance tests, its
# example manifest, and its JUnit import. The tests include the four that
# specs/059 deferred: T-04 (a failed parent check is not complete), T-05 (an
# AI claim is not evidence), T-06 (stale evidence), and T-10 (unclassified
# risk stops).

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL="$REPO_ROOT/.claude/skills/change-assurance"
CHECKER="$SKILL/scripts/assure.py"
export PYTHONDONTWRITEBYTECODE=1

PASS=0
FAIL=0
FAIL_NAMES=""

check() {
  local name="$1" condition="$2"
  if [ "$condition" = "1" ]; then
    PASS=$((PASS + 1))
    printf 'PASS %s\n' "$name"
  else
    FAIL=$((FAIL + 1))
    FAIL_NAMES="$FAIL_NAMES\n  - $name"
    printf 'FAIL %s\n' "$name" >&2
  fi
}

check_exit() {
  local name="$1" expected="$2" out status
  shift 2
  out="$("$@" 2>&1)"
  status=$?
  [ "$status" -ne "$expected" ] && printf '%s\n' "$out" | sed 's/^/    /' >&2
  check "$name" "$([ "$status" -eq "$expected" ] && echo 1 || echo 0)"
}

if ! command -v python3 >/dev/null 2>&1; then
  echo "Missing required command: python3" >&2
  exit 1
fi

out="$(python3 -B -m unittest discover -s "$SKILL/tests" -t "$SKILL/tests" 2>&1)"
status=$?
summary="$(printf '%s\n' "$out" | grep -E '^Ran [0-9]+ tests?' | tail -n 1)"
[ "$status" -ne 0 ] && printf '%s\n' "$out" | sed 's/^/    /' >&2
check "CA-01: acceptance tests pass (${summary:-no tests ran})" "$([ "$status" -eq 0 ] && echo 1 || echo 0)"

check_exit "CA-02: the example manifest passes its own rules" 0 \
  python3 -B "$CHECKER" check "$SKILL/examples/verification-manifest.example.json"
check_exit "CA-03: the example graph and manifest pass the gate" 0 \
  python3 -B "$CHECKER" gate "$SKILL/examples/requirements-graph.example.json" "$SKILL/examples/verification-manifest.example.json"

echo
if [ "$FAIL" -gt 0 ]; then
  printf 'Results: %d passed, %d failed\n' "$PASS" "$FAIL" >&2
  printf 'Failed:%b\n' "$FAIL_NAMES" >&2
  exit 1
fi
printf 'Results: %d passed, %d failed\n' "$PASS" "$FAIL"
