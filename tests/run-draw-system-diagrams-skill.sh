#!/usr/bin/env bash
# Offline contract suite for the checker bundled in the draw-system-diagrams skill:
# its acceptance tests, the bundled example set, and the templates the skill
# tells the model to copy. Python standard library only; writes nothing in the
# repository.

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TOOL_DIR="$REPO_ROOT/harness/skills/draw-system-diagrams"
CHECKER="$TOOL_DIR/scripts/check_diagrams.py"
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

check_exit "DIAG-01: checker acceptance tests pass" 0 \
  python3 -B -m unittest discover -s "$TOOL_DIR/tests"
check_exit "DIAG-02: the bundled example set passes the checker" 0 \
  python3 -B "$CHECKER" "$TOOL_DIR/examples/library-reservation"
check_exit "DIAG-03: the bundled templates pass the checker" 0 \
  python3 -B "$CHECKER" "$TOOL_DIR/assets/templates/view-page.md" \
  "$TOOL_DIR/assets/templates/view.drawio" "$TOOL_DIR/assets/templates/workspace.dsl"

# A page with no legend and an unlabelled line must fail, so a checker that
# accepts everything cannot pass this suite.
tmp="$(mktemp -d "${TMPDIR:-/tmp}/draw-system-diagrams.XXXXXX")"
trap 'rm -rf "$tmp"' EXIT
cat >"$tmp/bad.md" <<'EOF'
# Container view: Example

The API stores orders.

```mermaid
flowchart LR
  accTitle: Container view: Example
  accDescr: The API stores orders in the database.
  api["API<br/>[Container: Python]<br/>Accepts orders"]
  db[("Database<br/>[Container: PostgreSQL]<br/>Stores orders")]
  api --> db
```
EOF
check_exit "DIAG-04: an unlabelled line and a missing legend fail the checker" 1 \
  python3 -B "$CHECKER" "$tmp/bad.md"

printf '\nsystem-diagrams: %d passed, %d failed\n' "$PASS" "$FAIL"
if [ "$FAIL" -ne 0 ]; then
  printf 'Failed:%b\n' "$FAIL_NAMES" >&2
  exit 1
fi
