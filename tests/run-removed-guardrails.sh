#!/usr/bin/env bash
# Regression guard for three "removed with no replacement" decisions:
# ADR-0005 (.claude/hooks/), ADR-0006 (settings.json's permissions block),
# and ADR-0007 (scripts/). Each ADR's own dedicated verification suite was
# deleted along with the thing it verified (that is the point — there is
# nothing left to test in depth), but nothing was left behind to catch a
# regression if one of these three were silently reintroduced later. This
# suite is that catch, kept deliberately small: one assertion per decision.

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

PASS=0
FAIL=0

check() {
  local name="$1" cond="$2"
  if [ "$cond" = "1" ]; then
    PASS=$((PASS + 1))
    printf 'PASS %s\n' "$name"
  else
    FAIL=$((FAIL + 1))
    printf 'FAIL %s\n' "$name" >&2
  fi
}

[ ! -e "$REPO_ROOT/.claude/hooks" ] && c=1 || c=0
check "ADR-0005: .claude/hooks/ stays removed" "$c"

[ ! -e "$REPO_ROOT/scripts" ] && c=1 || c=0
check "ADR-0007: scripts/ stays removed" "$c"

if command -v jq >/dev/null 2>&1; then
  jq -e 'has("permissions") | not' "$REPO_ROOT/.claude/settings.json" >/dev/null 2>&1 && c=1 || c=0
else
  grep -q '"permissions"' "$REPO_ROOT/.claude/settings.json" && c=0 || c=1
fi
check "ADR-0006: settings.json carries no permissions block" "$c"

echo
if [ "$FAIL" -gt 0 ]; then
  printf 'Results: %d passed, %d failed\n' "$PASS" "$FAIL" >&2
  exit 1
fi
printf 'Results: %d passed, %d failed\n' "$PASS" "$FAIL"
