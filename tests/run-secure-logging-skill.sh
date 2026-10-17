#!/usr/bin/env bash
# Contract tests for the secure-logging skill: structure, scope text, and the
# sourcing rules of its checklist. They do not exercise how the skill behaves
# when a model follows it; that is checked by hand (see
# specs/050-secure-logging-skill/quickstart.md).
# Usage: bash tests/run-secure-logging-skill.sh

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL_DIR="$REPO_ROOT/.claude/skills/secure-logging"
SKILL_FILE="$SKILL_DIR/SKILL.md"
CHECKLIST="$SKILL_DIR/references/logging-checklist.md"

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

PASS=0
FAIL=0
FAIL_NAMES=""

check() {
  local name="$1" condition="$2"
  if [ "$condition" = "1" ]; then
    PASS=$((PASS + 1))
    printf "${GREEN}PASS${NC} %s\n" "$name"
  else
    FAIL=$((FAIL + 1))
    FAIL_NAMES="$FAIL_NAMES\n  - $name"
    printf "${RED}FAIL${NC} %s\n" "$name"
  fi
}

contains() {
  local file="$1" pattern="$2"
  [ -f "$file" ] && grep -Eiq -- "$pattern" "$file"
}

# Like contains, but joins lines first so a sentence wrapped across lines matches.
contains_flat() {
  local file="$1" pattern="$2"
  [ -f "$file" ] && tr '\n' ' ' <"$file" | grep -Eiq -- "$pattern"
}

check_contains() {
  local name="$1" file="$2" pattern="$3"
  check "$name" "$(contains "$file" "$pattern" && echo 1 || echo 0)"
}

check_contains_flat() {
  local name="$1" file="$2" pattern="$3"
  check "$name" "$(contains_flat "$file" "$pattern" && echo 1 || echo 0)"
}

# Checklist rows look like: | LOG-INJ-1 | requirement | basis |
rows() {
  grep -E '^\| LOG-[A-Z]+-[0-9]+ \|' "$CHECKLIST" 2>/dev/null
}

field() {
  # field <row> <n>: trimmed n-th pipe-delimited column (1 = id)
  printf '%s\n' "$1" | awk -F'|' -v n="$2" '{ gsub(/^ +| +$/, "", $(n + 1)); print $(n + 1) }'
}

run_skill_contract() {
  check "SL-01: SKILL.md and checklist exist" "$([ -f "$SKILL_FILE" ] && [ -f "$CHECKLIST" ] && echo 1 || echo 0)"
  check_contains "SL-02: front matter names the skill" "$SKILL_FILE" '^name: secure-logging$'
  check_contains "SL-03: description is a domain overlay used alongside other work" "$SKILL_FILE" '^description:.*overlay.*alongside.*supplements'
  check_contains "SL-04: description excludes log infrastructure operations" "$SKILL_FILE" '^description:.*(Do not use|not for).*(SIEM|infrastructure)'
  check_contains "SL-05: description excludes unrelated observability" "$SKILL_FILE" '^description:.*(Do not use|not for).*observability'
  check_contains "SL-06: description excludes changes that touch no logging" "$SKILL_FILE" '^description:.*(Do not use|not for).*touch no logging'
  check "SL-07: SKILL.md stays under 200 lines" "$([ "$(wc -l <"$SKILL_FILE")" -lt 200 ] && echo 1 || echo 0)"
}

run_checklist_contract() {
  local all_rows bad_basis dup ops_pass nist_in_item cwe_unread
  all_rows="$(rows)"
  check "CL-01: checklist has items" "$([ -n "$all_rows" ] && echo 1 || echo 0)"

  bad_basis=0
  while IFS= read -r row; do
    [ -z "$row" ] && continue
    basis="$(field "$row" 3)"
    # A basis must name a source and a section or requirement id, never a bare source.
    case "$basis" in
      "" | CS | ASVS | Top10 | Vocab | OTel) bad_basis=$((bad_basis + 1)) ;;
    esac
  done <<<"$all_rows"
  check "CL-02: every item has a basis with a section or requirement id" "$([ -n "$all_rows" ] && [ "$bad_basis" -eq 0 ] && echo 1 || echo 0)"

  dup="$(printf '%s\n' "$all_rows" | awk -F'|' '{gsub(/ /, "", $2); print $2}' | sort | uniq -d)"
  check "CL-03: item ids are unique" "$([ -n "$all_rows" ] && [ -z "$dup" ] && echo 1 || echo 0)"

  cwe_unread="$(printf '%s\n' "$all_rows" | grep -E 'CWE-22[13]' || true)"
  check "CL-04: no item rests on a CWE whose text was not read (221, 223)" "$([ -z "$cwe_unread" ] && echo 1 || echo 0)"

  nist_in_item="$(printf '%s\n' "$all_rows" | grep -E '\bNIST\b|800-92' || true)"
  check "CL-05: no item cites NIST as a requirement" "$([ -z "$nist_in_item" ] && echo 1 || echo 0)"
  check_contains_flat "CL-06: NIST SP 800-92 is marked as a draft for background" "$CHECKLIST" '800-92.*draft.*Background|Background only.*draft'

  check_contains_flat "CL-07: ISO/IEC 27002 is declared excluded" "$CHECKLIST" 'excluded.*ISO/IEC 27002|ISO/IEC 27002.*excluded|Deliberately excluded[^|]*ISO/IEC 27002'
  check_contains_flat "CL-08: PCI DSS is declared excluded" "$CHECKLIST" 'Deliberately excluded[^|]*PCI DSS|PCI DSS[^|]*(excluded|no primary text)'
  check_contains_flat "CL-09: NIST SP 800-53 is declared excluded" "$CHECKLIST" 'Deliberately excluded[^|]*800-53|800-53[^|]*(excluded|no primary text)'

  ops_pass="$(printf '%s\n' "$all_rows" | grep -E '^\| LOG-OPS-' | grep -Ei '\bpass(es|ed)?\b' || true)"
  check "CL-10: group B items never read as passable from code" "$([ -z "$ops_pass" ] && printf '%s\n' "$all_rows" | grep -q '^| LOG-OPS-' && echo 1 || echo 0)"

  for group in INV EVT ATT DATA INJ ERR CFG TST OPS; do
    check "CL-11: group $group has at least one item" "$(printf '%s\n' "$all_rows" | grep -q "^| LOG-$group-" && echo 1 || echo 0)"
  done
}

run_skill_contract
run_checklist_contract

echo ""
echo "===================="
printf "Results: ${GREEN}%d passed${NC}, ${RED}%d failed${NC}\n" "$PASS" "$FAIL"

if [ "$FAIL" -gt 0 ]; then
  printf "\nFailed:%b\n" "$FAIL_NAMES"
  exit 1
fi
