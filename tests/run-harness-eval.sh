#!/usr/bin/env bash
# Offline checks for the whole-harness behavior baseline
# (specs/066-harness-behavior-baseline): the unit tests of
# tests/harness-eval/harness_eval.py, then the capability map and scenario
# suite against the working tree. Calls no model; the billed baseline run is
# `python3 tests/harness-eval/harness_eval.py run --max-cost-usd N`.

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONDONTWRITEBYTECODE=1
status=0

python3 -B -m unittest discover -s "$REPO_ROOT/tests/harness-eval" -v || status=1
python3 -B "$REPO_ROOT/tests/harness-eval/harness_eval.py" check || status=1

if [ "$status" -eq 0 ]; then
  echo "harness-eval: passed"
else
  echo "harness-eval: FAILED" >&2
fi
exit "$status"
