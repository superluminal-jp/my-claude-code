#!/usr/bin/env bash
# Offline checks of the rebuilt skill tree (harness/skills): the skill
# contract, and the unit tests of the bundled checker scripts. Everything
# runs inside the Claude Code Bash sandbox: no network, no write outside the
# repository, temporary files only under $TMPDIR (Python's tempfile honors it).

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS="${1:-$REPO_ROOT/harness/skills}"
export PYTHONDONTWRITEBYTECODE=1

PASS=0
FAIL=0

check() {
  local name="$1" status="$2"
  if [ "$status" -eq 0 ]; then
    PASS=$((PASS + 1))
    printf 'PASS %s\n' "$name"
  else
    FAIL=$((FAIL + 1))
    printf 'FAIL %s\n' "$name" >&2
  fi
}

if ! command -v python3 >/dev/null 2>&1; then
  echo "Missing required command: python3" >&2
  exit 1
fi

out="$(cd "$REPO_ROOT" && python3 -B -m unittest tests/test_skill_contract.py 2>&1)"
status=$?
summary="$(printf '%s\n' "$out" | grep -E '^Ran [0-9]+ tests?' | tail -n 1)"
[ "$status" -ne 0 ] && printf '%s\n' "$out" | tail -n 40 | sed 's/^/    /' >&2
check "HS-00: every rule of the contract is shown able to fail (${summary:-no tests ran})" "$status"

out="$(python3 -B "$REPO_ROOT/tests/assert_skill_contract.py" "$SKILLS" 2>&1)"
status=$?
[ "$status" -ne 0 ] && printf '%s\n' "$out" | grep '^FAIL' | sed 's/^/    /' >&2
check "HS-01: every skill meets the contract ($(printf '%s\n' "$out" | tail -n 1))" "$status"

for skill in specify-requirements verify-change draw-system-diagrams structure-document sync-docs; do
  out="$(python3 -B -m unittest discover -s "$SKILLS/$skill/tests" -t "$SKILLS/$skill/tests" 2>&1)"
  status=$?
  summary="$(printf '%s\n' "$out" | grep -E '^Ran [0-9]+ tests?' | tail -n 1)"
  [ "$status" -ne 0 ] && printf '%s\n' "$out" | tail -n 40 | sed 's/^/    /' >&2
  check "HS-02: $skill script tests pass (${summary:-no tests ran})" "$status"
done

echo
printf 'Results: %d passed, %d failed\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ]
