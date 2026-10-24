#!/usr/bin/env bash
# Contract tests for the secure-logging skill: structure, scope text, the
# sourcing rules of its checklist, and its plugin packaging. They do not exercise how the skill behaves
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

last_field() {
  # last_field <row>: trimmed last column, which is the basis in every item table
  printf '%s\n' "$1" | awk -F'|' '{ gsub(/^ +| +$/, "", $(NF - 1)); print $(NF - 1) }'
}

# Short names in the first column of the Sources table.
source_names() {
  awk '/^## Sources/ { on = 1; next } /^## / { on = 0 } on && /^\| [^-|]/' "$CHECKLIST" 2>/dev/null |
    awk -F'|' 'NR > 1 { gsub(/^ +| +$/, "", $2); print $2 }'
}

run_skill_contract() {
  check "SL-01: SKILL.md and checklist exist" "$([ -f "$SKILL_FILE" ] && [ -f "$CHECKLIST" ] && echo 1 || echo 0)"
  check_contains "SL-02: front matter names the skill" "$SKILL_FILE" '^name: secure-logging$'
  check_contains "SL-03: description is a domain overlay used alongside other work" "$SKILL_FILE" '^description:.*overlay.*alongside.*supplements'
  check_contains "SL-04: description excludes log infrastructure operations" "$SKILL_FILE" '^description:.*(Do not use|not for).*(SIEM|infrastructure)'
  check_contains "SL-05: description excludes unrelated observability" "$SKILL_FILE" '^description:.*(Do not use|not for).*observability'
  check_contains "SL-06: description excludes changes that touch no logging" "$SKILL_FILE" '^description:.*(Do not use|not for).*touch no logging'
  check "SL-07: SKILL.md stays under 200 lines" "$([ "$(wc -l <"$SKILL_FILE")" -lt 200 ] && echo 1 || echo 0)"
  check_contains "SL-10: description covers logging practice from official stack documentation" "$SKILL_FILE" '^description:.*logging practices?.*official documentation'
  check_contains "SL-11: description covers logging resources in CDK, Terraform, and Bicep" "$SKILL_FILE" '^description:.*infrastructure code.*CDK.*Terraform.*Bicep'
  check_contains "SL-12: description covers serverless runtimes and AI inference services" "$SKILL_FILE" '^description:.*Cloud Run functions.*Azure Functions.*AI inference'
  check_contains "SL-13: description covers GitHub Actions workflow logs" "$SKILL_FILE" '^description:.*GitHub Actions'

  # The checklist is the single source of requirements: SKILL.md cites items
  # by ID instead of restating them, and every cited ID must exist.
  local completion_ids cited_ids unknown_ids="" id
  completion_ids="$(sed -n '/^## Completion check/,$p' "$SKILL_FILE" 2>/dev/null | grep -oE 'LOG-[A-Z]+-[0-9]+' || true)"
  check "SL-08: the completion check cites checklist items by ID" "$([ -n "$completion_ids" ] && echo 1 || echo 0)"
  cited_ids="$(grep -oE 'LOG-[A-Z]+-[0-9]+' "$SKILL_FILE" 2>/dev/null | sort -u || true)"
  for id in $cited_ids; do
    rows | grep -q "^| $id |" || unknown_ids="$unknown_ids $id"
  done
  check "SL-09: every item ID cited in SKILL.md exists in the checklist" "$([ -n "$cited_ids" ] && [ -z "$unknown_ids" ] && echo 1 || echo 0)"
}

run_checklist_contract() {
  local all_rows bad_basis dup ops_pass nist_in_item cwe_unread
  all_rows="$(rows)"
  check "CL-01: checklist has items" "$([ -n "$all_rows" ] && echo 1 || echo 0)"

  bad_basis=0
  while IFS= read -r row; do
    [ -z "$row" ] && continue
    basis="$(last_field "$row")"
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

  for group in INV EVT ATT DATA INJ ERR CFG TST OPS PRC; do
    check "CL-11: group $group has at least one item" "$(printf '%s\n' "$all_rows" | grep -q "^| LOG-$group-" && echo 1 || echo 0)"
  done

  # Practice items rest on a stack's official documentation: each names the
  # stack it applies to and cites a listed source with a section after it.
  local prc_rows names bad_prc=0 applies cited name
  prc_rows="$(printf '%s\n' "$all_rows" | grep -E '^\| LOG-PRC-' || true)"
  names="$(source_names)"
  while IFS= read -r row; do
    [ -z "$row" ] && continue
    applies="$(field "$row" 3)"
    basis="$(last_field "$row")"
    cited=0
    while IFS= read -r name; do
      [ -z "$name" ] && continue
      case "$basis" in "$name "?*) cited=1 ;; esac
    done <<<"$names"
    { [ -z "$applies" ] || [ "$applies" = "$basis" ] || [ "$cited" -eq 0 ]; } && bad_prc=$((bad_prc + 1))
  done <<<"$prc_rows"
  check "CL-12: every practice item names its stack and cites a listed source section" "$([ -n "$prc_rows" ] && [ "$bad_prc" -eq 0 ] && echo 1 || echo 0)"

  # A practice item's security impact is "none" or the security items a Fail
  # would also violate; those items must exist and must not be practice items.
  local bad_impact=0 impact
  while IFS= read -r row; do
    [ -z "$row" ] && continue
    impact="$(field "$row" 4)"
    if [ -z "$impact" ] || [ "$impact" = "$(last_field "$row")" ]; then
      bad_impact=$((bad_impact + 1))
      continue
    fi
    [ "$impact" = "none" ] && continue
    for id in $(printf '%s\n' "$impact" | tr ',' ' '); do
      case "$id" in LOG-PRC-*) bad_impact=$((bad_impact + 1)); continue ;; esac
      printf '%s\n' "$all_rows" | grep -q "^| $id |" || bad_impact=$((bad_impact + 1))
    done
  done <<<"$prc_rows"
  check "CL-14: every practice item states its security impact as none or existing security items" "$([ -n "$prc_rows" ] && [ "$bad_impact" -eq 0 ] && echo 1 || echo 0)"

  # Evidence rows map an existing group B item to infrastructure-code
  # attributes; their ID is backquoted so they are not read as items.
  local evidence_rows bad_evidence=0 id
  evidence_rows="$(grep -E '^\| `LOG-OPS-[0-9]+` \|' "$CHECKLIST" 2>/dev/null || true)"
  while IFS= read -r row; do
    [ -z "$row" ] && continue
    id="$(field "$row" 1 | tr -d '`')"
    basis="$(last_field "$row")"
    cited=0
    while IFS= read -r name; do
      [ -z "$name" ] && continue
      case "$basis" in "$name "?*) cited=1 ;; esac
    done <<<"$names"
    { printf '%s\n' "$all_rows" | grep -q "^| $id |" && [ "$cited" -eq 1 ]; } || bad_evidence=$((bad_evidence + 1))
  done <<<"$evidence_rows"
  check "CL-13: infrastructure-code evidence maps existing group B items and cites listed sources" "$([ -n "$evidence_rows" ] && [ "$bad_evidence" -eq 0 ] && echo 1 || echo 0)"
}

# Heading levels in document order, skipping fenced code blocks.
heading_levels() {
  awk '/^```/ { fenced = !fenced; next } !fenced && /^#+ / { print substr($0, 1, index($0, " ") - 1) }' "$1"
}

run_plugin_contract() {
  local manifest="$SKILL_DIR/.claude-plugin/plugin.json"
  local readme="$SKILL_DIR/README.md" readme_ja="$SKILL_DIR/README.ja.md"

  check "PL-01: plugin manifest names the skill and describes it" \
    "$([ -f "$manifest" ] && jq -e '.name == "secure-logging" and (.description | length > 0)' "$manifest" >/dev/null 2>&1 && echo 1 || echo 0)"
  check "PL-02: README.md and README.ja.md share one heading structure" \
    "$([ -f "$readme" ] && [ -f "$readme_ja" ] && [ -n "$(heading_levels "$readme")" ] && [ "$(heading_levels "$readme")" = "$(heading_levels "$readme_ja")" ] && echo 1 || echo 0)"

  if ! command -v claude >/dev/null 2>&1; then
    printf "SKIP PL-03, PL-04: Claude Code CLI not installed\n"
    return
  fi
  check "PL-03: claude plugin validate --strict accepts the plugin" \
    "$(claude plugin validate --strict "$SKILL_DIR" >/dev/null 2>&1 && echo 1 || echo 0)"
  # The manifest check does not read SKILL.md; validate it as a skills directory.
  local tmp
  tmp="$(mktemp -d)"
  mkdir -p "$tmp/skills"
  cp -R "$SKILL_DIR" "$tmp/skills/secure-logging"
  rm -rf "$tmp/skills/secure-logging/.claude-plugin"
  check "PL-04: claude plugin validate --strict accepts SKILL.md as a skill" \
    "$(claude plugin validate --strict "$tmp/skills" >/dev/null 2>&1 && echo 1 || echo 0)"
  rm -rf "$tmp"
}

run_skill_contract
run_checklist_contract
run_plugin_contract

echo ""
echo "===================="
printf "Results: ${GREEN}%d passed${NC}, ${RED}%d failed${NC}\n" "$PASS" "$FAIL"

if [ "$FAIL" -gt 0 ]; then
  printf "\nFailed:%b\n" "$FAIL_NAMES"
  exit 1
fi
