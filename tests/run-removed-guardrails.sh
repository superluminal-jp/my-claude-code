#!/usr/bin/env bash
# Regression guard for the "removed with no replacement" decisions:
# ADR-0005 (the hooks directory) and ADR-0007 (scripts/), plus the narrowed
# permissions decision, and for the move of the managed configuration from
# this repository's .claude/ to harness/. Each ADR's own dedicated verification suite was
# deleted along with the thing it verified (that is the point — there is
# nothing left to test in depth), but nothing was left behind to catch a
# regression if one of these were silently reintroduced later. This suite is
# that catch, kept deliberately small: one assertion per decision.
#
# ADR-0006 removed settings.json's permissions block entirely; ADR-0014
# restored only the credential-safety deny list, leaving allow/ask absent.
# So the assertion is no longer "no permissions block" — it is "deny only".
# A reintroduced allow or ask array still fails here.

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

[ ! -e "$REPO_ROOT/harness/hooks" ] && [ ! -e "$REPO_ROOT/.claude/hooks" ] && c=1 || c=0
check "ADR-0005: no hooks directory, in harness/ or in .claude/" "$c"

# The managed configuration moved from this repository's .claude/ to harness/.
# A copy left behind would load a second time as project configuration, and
# would be the copy a reader edits by mistake. The check looks for files: an
# empty directory holds no configuration, Git does not track one, and Claude
# Code itself leaves empty working directories under .claude/.
legacy=""
for path in CLAUDE.md rules skills agents settings.json commands; do
  if [ -n "$(find "$REPO_ROOT/.claude/$path" -type f 2>/dev/null | head -n 1)" ]; then
    legacy="$legacy .claude/$path"
  fi
done
[ -n "$legacy" ] && printf '    still present:%s\n' "$legacy" >&2
[ -z "$legacy" ] && c=1 || c=0
check "SRC-01: this repository's own .claude/ holds no managed configuration" "$c"

[ ! -e "$REPO_ROOT/scripts" ] && c=1 || c=0
check "ADR-0007: scripts/ stays removed" "$c"

if command -v jq >/dev/null 2>&1; then
  jq -e '(.permissions // {}) | has("allow") or has("ask") | not' \
    "$REPO_ROOT/harness/settings.json" >/dev/null 2>&1 && c=1 || c=0
else
  grep -qE '"(allow|ask)"' "$REPO_ROOT/harness/settings.json" && c=0 || c=1
fi
check "ADR-0006/0014: settings.json permissions carries no allow/ask tier" "$c"

# ADR-0014: every deny entry must be a Read rule anchored with ~/ or **/ —
# a single-leading-slash pattern resolves differently once install.sh copies
# this file to user scope, so one would silently protect the wrong path.
if command -v jq >/dev/null 2>&1; then
  jq -e '[(.permissions.deny // [])[]
          | select((startswith("Read(") | not) or test("\\(/[^/]"))]
         | length == 0' \
    "$REPO_ROOT/harness/settings.json" >/dev/null 2>&1 && c=1 || c=0
else
  c=1  # skipped without jq
fi
check "ADR-0014: deny entries are Read rules with portable anchors" "$c"

echo
if [ "$FAIL" -gt 0 ]; then
  printf 'Results: %d passed, %d failed\n' "$PASS" "$FAIL" >&2
  exit 1
fi
printf 'Results: %d passed, %d failed\n' "$PASS" "$FAIL"
