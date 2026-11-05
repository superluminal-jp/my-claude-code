#!/usr/bin/env bash
# Offline contract suite for tools/refinement-checker
# (specs/059-refinement-graph-checker): the checker's acceptance tests, its two
# example declarations, and this repository's own skills read in
# compatibility mode. Tests the spec defers to a later phase are printed as
# NOT RUN and never counted as passed.

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TOOL_DIR="$REPO_ROOT/tools/refinement-checker"
CHECKER="$TOOL_DIR/check_graph.py"
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

# check_exit <name> <expected exit code> <command...>: shows the command's
# output only when the exit code differs.
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

out="$(python3 -B -m unittest discover -s "$TOOL_DIR/tests" -t "$TOOL_DIR/tests" 2>&1)"
status=$?
summary="$(printf '%s\n' "$out" | grep -E '^Ran [0-9]+ tests?' | tail -n 1)"
[ "$status" -ne 0 ] && printf '%s\n' "$out" | sed 's/^/    /' >&2
check "RC-01: acceptance tests pass (${summary:-no tests ran})" "$([ "$status" -eq 0 ] && echo 1 || echo 0)"

check_exit "RC-02: the requirements example passes" 0 \
  python3 -B "$CHECKER" "$TOOL_DIR/examples/requirements-graph.example.json"
check_exit "RC-03: the skills example passes" 0 \
  python3 -B "$CHECKER" "$TOOL_DIR/examples/skills-graph.example.json"
check_exit "RC-04: this repository's skills pass in compatibility mode" 0 \
  python3 -B "$CHECKER" --skills-dir "$REPO_ROOT/.claude/skills"

# Deferred to Phase 3 (spec "後の Phase へ送るテスト"): they need an evidence
# record format that does not exist yet. Listed so they are never mistaken
# for passing checks.
printf 'NOT RUN T-04: a failed parent verification keeps the change incomplete (Phase 3)\n'
printf 'NOT RUN T-05: an AI completion claim without evidence is not_run or blocked (Phase 3)\n'
printf 'NOT RUN T-06: evidence for another commit is rejected as stale (Phase 3)\n'
printf 'NOT RUN T-10: an unknown risk class stops instead of counting as low risk (Phase 3)\n'

echo
if [ "$FAIL" -gt 0 ]; then
  printf 'Results: %d passed, %d failed, 4 not run\n' "$PASS" "$FAIL" >&2
  printf 'Failed:%b\n' "$FAIL_NAMES" >&2
  exit 1
fi
printf 'Results: %d passed, %d failed, 4 not run\n' "$PASS" "$FAIL"
