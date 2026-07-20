#!/usr/bin/env bash
# Contract tests for the Digital Agency React/Tailwind frontend skill.
# Usage: bash tests/run-digital-agency-frontend-skill.sh [dads|dashboard|sync]

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL_DIR="$REPO_ROOT/.claude/skills/digital-agency-frontend"
SKILL_FILE="$SKILL_DIR/SKILL.md"
DADS_REFERENCE="$SKILL_DIR/references/dads-react-tailwind.md"
DASHBOARD_REFERENCE="$SKILL_DIR/references/dashboard-design.md"
INTERFACE_FILE="$SKILL_DIR/agents/openai.yaml"
SELECTOR="${1:-all}"

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

check_contains() {
  local name="$1" file="$2" pattern="$3"
  check "$name" "$(contains "$file" "$pattern" && echo 1 || echo 0)"
}

run_dads_contract() {
  check "DADS-01: skill file exists" "$([ -f "$SKILL_FILE" ] && echo 1 || echo 0)"
  check_contains "DADS-02: skill name is canonical" "$SKILL_FILE" '^name:[[:space:]]+digital-agency-frontend$'
  check_contains "DADS-03: description routes React and Tailwind work" "$SKILL_FILE" '^description:.*React.*Tailwind CSS'
  check_contains "DADS-04: description routes DADS and public-service work" "$SKILL_FILE" '^description:.*(Digital Agency Design System|DADS).*(public-service|government|行政|公共)'
  check_contains "DADS-05: description routes dashboard work" "$SKILL_FILE" '^description:.*dashboard'
  check_contains "DADS-06: workflow composes with coder" "$SKILL_FILE" '`coder`'
  check_contains "DADS-07: workflow composes with clarifier" "$SKILL_FILE" '`clarifier`'
  check_contains "DADS-08: workflow checks live official source drift" "$SKILL_FILE" '(live official|official live).*(drift|conflict|newer|current)'
  check_contains "DADS-09: workflow links DADS reference directly" "$SKILL_FILE" 'references/dads-react-tailwind\.md'
  check_contains "DADS-10: workflow links dashboard reference directly" "$SKILL_FILE" 'references/dashboard-design\.md'
  check_contains "DADS-11: workflow includes accessibility release gate" "$SKILL_FILE" '(accessibility|accessible).*(gate|complete|completion|release)'

  check "DADS-12: DADS reference exists" "$([ -f "$DADS_REFERENCE" ] && echo 1 || echo 0)"
  check_contains "DADS-13: reference records retrieval date" "$DADS_REFERENCE" '2026-07-20'
  check_contains "DADS-14: reference records DADS version" "$DADS_REFERENCE" 'v2\.16\.0'
  check_contains "DADS-15: reference links official DADS site" "$DADS_REFERENCE" 'https://design\.digital\.go\.jp/dads/'
  check_contains "DADS-16: reference links official React examples" "$DADS_REFERENCE" 'https://github\.com/digital-go-jp/design-system-example-components-react'
  check_contains "DADS-17: reference links official Tailwind plugin" "$DADS_REFERENCE" 'https://github\.com/digital-go-jp/tailwind-theme-plugin'
  check_contains "DADS-18: reference handles React 18 and 19" "$DADS_REFERENCE" 'React 18.*React 19|React 19.*React 18'
  check_contains "DADS-19: reference handles Tailwind 3 and 4" "$DADS_REFERENCE" 'Tailwind CSS 3.*Tailwind CSS 4|Tailwind CSS 4.*Tailwind CSS 3'
  check_contains "DADS-20: reference requires JIS AA" "$DADS_REFERENCE" 'JIS X 8341-3:2016.*AA'
  check_contains "DADS-21: reference requires WCAG 2.2 AA" "$DADS_REFERENCE" 'WCAG 2\.2.*AA'
  check_contains "DADS-22: reference covers keyboard and focus" "$DADS_REFERENCE" 'keyboard.*focus|focus.*keyboard'
  check_contains "DADS-23: reference covers reflow and contrast" "$DADS_REFERENCE" 'reflow.*contrast|contrast.*reflow'
  check_contains "DADS-24: reference records MIT code license" "$DADS_REFERENCE" 'MIT License'
  check_contains "DADS-25: reference records documentation attribution" "$DADS_REFERENCE" '(attribution|出典).*(modified|adapted|加工)'

  check "DADS-26: interface metadata exists" "$([ -f "$INTERFACE_FILE" ] && echo 1 || echo 0)"
  check_contains "DADS-27: interface has display name" "$INTERFACE_FILE" 'display_name:[[:space:]]+"Digital Agency Frontend"'
  check_contains "DADS-28: interface prompt names the skill" "$INTERFACE_FILE" '\$digital-agency-frontend'
}

run_dashboard_contract() {
  check "DASH-01: dashboard reference exists" "$([ -f "$DASHBOARD_REFERENCE" ] && echo 1 || echo 0)"
  check_contains "DASH-02: reference records retrieval date" "$DASHBOARD_REFERENCE" '2026-07-20'
  check_contains "DASH-03: reference records guide update date" "$DASHBOARD_REFERENCE" '2026-07-17'
  check_contains "DASH-04: reference links official guide" "$DASHBOARD_REFERENCE" 'https://www\.digital\.go\.jp/resources/dashboard-guidebook'
  check_contains "DASH-05: requirements capture audience and action" "$DASHBOARD_REFERENCE" 'audience.*(decision|action)|(decision|action).*audience'
  check_contains "DASH-06: workflow distinguishes presentation and exploration" "$DASHBOARD_REFERENCE" 'presentation-oriented.*exploration-oriented|exploration-oriented.*presentation-oriented'
  check_contains "DASH-07: guidance covers information hierarchy" "$DASHBOARD_REFERENCE" 'information hierarchy'
  check_contains "DASH-08: guidance covers layout grid" "$DASHBOARD_REFERENCE" 'layout grid'
  check_contains "DASH-09: guidance covers chart selection" "$DASHBOARD_REFERENCE" 'chart selection'
  check_contains "DASH-10: essential charts have text or table alternatives" "$DASHBOARD_REFERENCE" '(summary|text).*(table|tabular).*(alternative|equivalent)|(alternative|equivalent).*(summary|text).*(table|tabular)'
  check_contains "DASH-11: color is not the only cue" "$DASHBOARD_REFERENCE" 'color.*(only|sole)|not.*color alone'
  check_contains "DASH-12: Power BI artifacts are out of scope" "$DASHBOARD_REFERENCE" 'Power BI.*(out of scope|excluded)|(out of scope|excluded).*Power BI'
  check_contains "DASH-13: skill loads dashboard detail conditionally" "$SKILL_FILE" '(only|when).*(dashboard).*(references/dashboard-design\.md)|references/dashboard-design\.md.*(only|when).*(dashboard)'
}

run_sync_contract() {
  local link="$REPO_ROOT/.agents/skills/digital-agency-frontend"
  local target=""
  [ -L "$link" ] && target=$(readlink "$link")

  check "SYNC-SKILL-01: repository Codex entry is a symlink" "$([ -L "$link" ] && echo 1 || echo 0)"
  check "SYNC-SKILL-02: repository link targets authored skill" "$([ "$target" = '../../.claude/skills/digital-agency-frontend' ] && echo 1 || echo 0)"
  check "SYNC-SKILL-03: repository link resolves" "$([ -e "$link/SKILL.md" ] && echo 1 || echo 0)"
  check_contains "SYNC-SKILL-04: installer registers the skill" "$REPO_ROOT/install.sh" 'CUSTOM_SKILLS=.*digital-agency-frontend'
  check_contains "SYNC-SKILL-05: Claude routing lists the skill" "$REPO_ROOT/.claude/CLAUDE.md" 'digital-agency-frontend'
  check_contains "SYNC-SKILL-05A: canonical Claude routing composes the skill" "$REPO_ROOT/.claude/rules/skill-routing.md" 'coder.*digital-agency-frontend|digital-agency-frontend.*coder'
  check_contains "SYNC-SKILL-06: Codex routing lists the skill" "$REPO_ROOT/.codex/AGENTS.md" '@\.agents/skills/digital-agency-frontend/SKILL\.md'
  check_contains "SYNC-SKILL-07: sync suite expects the skill" "$REPO_ROOT/tests/run-codex-sync.sh" 'for skill_name in .*digital-agency-frontend'
  check_contains "SYNC-SKILL-08: English README lists the skill" "$REPO_ROOT/README.md" 'digital-agency-frontend'
  check_contains "SYNC-SKILL-09: Japanese README lists the skill" "$REPO_ROOT/README.ja.md" 'digital-agency-frontend'
  check_contains "SYNC-SKILL-10: deployment map classifies the skill" "$REPO_ROOT/.codex/README.md" 'digital-agency-frontend'
}

case "$SELECTOR" in
dads)
  run_dads_contract
  ;;
dashboard)
  run_dashboard_contract
  ;;
sync)
  run_sync_contract
  ;;
all)
  run_dads_contract
  run_dashboard_contract
  run_sync_contract
  ;;
*)
  echo "Usage: $0 [dads|dashboard|sync]" >&2
  exit 2
  ;;
esac

echo ""
echo "===================="
printf "Results: ${GREEN}%d passed${NC}, ${RED}%d failed${NC}\n" "$PASS" "$FAIL"

if [ "$FAIL" -gt 0 ]; then
  printf "\nFailed:%b\n" "$FAIL_NAMES"
  exit 1
fi
