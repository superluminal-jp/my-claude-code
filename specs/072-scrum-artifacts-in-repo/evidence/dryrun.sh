#!/usr/bin/env bash
# AC-ROOT-1: place, extend, and check Scrum artifacts for two products in a
# fresh Git repository under $TMPDIR, using only the commands SKILL.md gives.
# Usage: bash specs/072-scrum-artifacts-in-repo/evidence/dryrun.sh
# Exit 0 when every expectation holds, 1 otherwise.
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
CLAUDE_SKILL_DIR="$REPO_ROOT/harness/skills/manage-scrum-artifacts"
: "${TMPDIR:?TMPDIR must be set}"
WORK="$(mktemp -d "$TMPDIR/scrum-dryrun.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT
CLAUDE_PROJECT_DIR="$WORK/repo"
export PYTHONDONTWRITEBYTECODE=1
FAIL=0

expect() { # name, expected exit code, command...
  local name="$1" want="$2"; shift 2
  "$@" >"$WORK/out.txt" 2>&1; local got=$?
  sed "s#$WORK#\$WORK#g; s/^/    /" "$WORK/out.txt"
  if [ "$got" -eq "$want" ]; then printf 'PASS %s (exit %s)\n' "$name" "$got"
  else printf 'FAIL %s (exit %s, expected %s)\n' "$name" "$got" "$want"; FAIL=1; fi
}

mkdir -p "$CLAUDE_PROJECT_DIR/products/a"
git -C "$CLAUDE_PROJECT_DIR" init -q

echo "== 1. init for the root product and for products/a"
expect "init root" 0 python3 "${CLAUDE_SKILL_DIR}/scripts/scaffold.py" init --root "${CLAUDE_PROJECT_DIR}"
expect "init products/a" 0 python3 "${CLAUDE_SKILL_DIR}/scripts/scaffold.py" init --root "${CLAUDE_PROJECT_DIR}" --product products/a

echo "== 2. two sprints for products/a"
expect "sprint 1" 0 python3 "${CLAUDE_SKILL_DIR}/scripts/scaffold.py" sprint --root "${CLAUDE_PROJECT_DIR}" --product products/a --start 2026-11-16
expect "sprint 2" 0 python3 "${CLAUDE_SKILL_DIR}/scripts/scaffold.py" sprint --root "${CLAUDE_PROJECT_DIR}" --product products/a --start 2026-11-30

echo "== 3. the check passes for both products"
expect "check root" 0 python3 "${CLAUDE_SKILL_DIR}/scripts/check_artifacts.py" --root "${CLAUDE_PROJECT_DIR}"
expect "check products/a" 0 python3 "${CLAUDE_SKILL_DIR}/scripts/check_artifacts.py" --root "${CLAUDE_PROJECT_DIR}" --product products/a

echo "== files placed"
(cd "$CLAUDE_PROJECT_DIR" && find . -path ./.git -prune -o -type f -print | sort | sed 's/^/    /')

echo "== 4. a copy of the Product Backlog inside a sprint folder is an error"
cp "$CLAUDE_PROJECT_DIR/products/a/scrum/product-backlog.md" "$CLAUDE_PROJECT_DIR/products/a/scrum/sprints/002-2026-11-30/"
expect "check products/a with a second Product Backlog" 1 python3 "${CLAUDE_SKILL_DIR}/scripts/check_artifacts.py" --root "${CLAUDE_PROJECT_DIR}" --product products/a

echo
[ "$FAIL" -eq 0 ] && echo "dryrun: passed" || echo "dryrun: FAILED"
exit "$FAIL"
