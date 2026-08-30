#!/usr/bin/env bash
# Contract tests for the Digital Agency React/Tailwind frontend skill.
# Usage: bash tests/run-digital-agency-frontend-skill.sh [dads|archive|dashboard|sync]
# Literal backticks and dollar-prefixed skill names are intentional patterns.
# shellcheck disable=SC2016

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL_DIR="$REPO_ROOT/.claude/skills/digital-agency-frontend"
SKILL_FILE="$SKILL_DIR/SKILL.md"
SOURCING_REFERENCE="$SKILL_DIR/references/sourcing-and-licensing.md"
IMPL_REFERENCE="$SKILL_DIR/references/component-implementation.md"
A11Y_REFERENCE="$SKILL_DIR/references/accessibility-gate.md"
DASHBOARD_REFERENCE="$SKILL_DIR/references/dashboard-design.md"
ARCHIVE_DIR="$SKILL_DIR/references/dads-docs"
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

# The skill was restructured to vendor the Digital Agency's official Markdown
# export under references/dads-docs/ and to split the single implementation
# reference into sourcing/licensing, component implementation, and the
# accessibility gate. DADS-12..25 previously asserted against the removed
# references/dads-react-tailwind.md and pinned a DADS version and retrieval
# date; pinning a version is now a regression (see SRC-09), because the skill
# must resolve current versions at task time rather than quote a stale one.

run_dads_contract() {
  check "DADS-01: skill file exists" "$([ -f "$SKILL_FILE" ] && echo 1 || echo 0)"
  check_contains "DADS-02: skill name is canonical" "$SKILL_FILE" '^name:[[:space:]]+digital-agency-frontend$'
  check_contains "DADS-03: description routes React and Tailwind work" "$SKILL_FILE" '^description:.*React.*Tailwind CSS'
  check_contains "DADS-04: description routes DADS and public-service work" "$SKILL_FILE" '^description:.*(Digital Agency Design System|DADS).*(public-service|government|行政|公共)'
  check_contains "DADS-05: description routes dashboard work" "$SKILL_FILE" '^description:.*dashboard'
  check "DADS-06: skill body names no sibling skill (self-contained)" "$([ -f "$SKILL_FILE" ] && ! grep -Eiq '`(coder|clarifier|adr|minto-[a-z]+)`' "$SKILL_FILE" && echo 1 || echo 0)"
  check_contains "DADS-07: workflow states test-first, type-safe, documented practice in its own terms" "$SKILL_FILE" '(failing (behavior|accessibility) test|type-safe|documentation artifact)'
  check_contains "DADS-08: workflow prefers live official sources and discloses drift" "$SKILL_FILE" '(live (official|content)|official live).*(drift|conflict|wins|reachable)'
  check_contains "DADS-09: workflow links implementation reference directly" "$SKILL_FILE" 'references/component-implementation\.md'
  check_contains "DADS-10: workflow links dashboard reference directly" "$SKILL_FILE" 'references/dashboard-design\.md'
  check_contains "DADS-11: workflow includes accessibility release gate" "$SKILL_FILE" '(accessibility|accessible).*(gate|complete|completion|release)'
  check_contains "DADS-12: workflow links sourcing and licensing reference" "$SKILL_FILE" 'references/sourcing-and-licensing\.md'
  check_contains "DADS-13: workflow links accessibility gate reference" "$SKILL_FILE" 'references/accessibility-gate\.md'
  check_contains "DADS-14: skill documents how to look up a page in the archive" "$SKILL_FILE" 'MANIFEST\.md'
  check_contains "DADS-15: skill forbids quoting versions or tokens from memory" "$SKILL_FILE" '(never|not).*(quote|invent).*(version|token)'

  check "SRC-01: sourcing reference exists" "$([ -f "$SOURCING_REFERENCE" ] && echo 1 || echo 0)"
  check_contains "SRC-02: reference links official DADS site" "$SOURCING_REFERENCE" 'https://design\.digital\.go\.jp/dads/'
  check_contains "SRC-03: reference documents how to refresh the archive" "$SOURCING_REFERENCE" '(refresh|再取得|replace).*(archive|dads-docs)|dads-docs.*(replace|refresh)'
  check_contains "SRC-04: reference reads the version from the archive, not from prose" "$SOURCING_REFERENCE" 'grep.*dads-docs/index\.md'
  check_contains "SRC-05: reference states source precedence" "$SOURCING_REFERENCE" '(live official|authoritative|wins)'
  check_contains "SRC-06: reference records MIT code license" "$SOURCING_REFERENCE" 'MIT'
  check_contains "SRC-07: reference records documentation attribution for adapted content" "$SOURCING_REFERENCE" '(attribution|出典).*(modified|adapted|加工)|加工'
  check_contains "SRC-08: reference records Figma CC BY 4.0 and icon carve-out" "$SOURCING_REFERENCE" 'CC BY 4\.0'
  check "SRC-09: no reference pins a DADS version number (must resolve current)" "$(! grep -Eqr 'v2\.1[0-9]\.[0-9]' "$SKILL_FILE" "$SOURCING_REFERENCE" "$IMPL_REFERENCE" "$A11Y_REFERENCE" && echo 1 || echo 0)"

  check "IMPL-01: implementation reference exists" "$([ -f "$IMPL_REFERENCE" ] && echo 1 || echo 0)"
  check_contains "IMPL-02: reference links official React examples" "$IMPL_REFERENCE" 'https://github\.com/digital-go-jp/design-system-example-components-react'
  check_contains "IMPL-03: reference links official Tailwind plugin" "$IMPL_REFERENCE" 'https://github\.com/digital-go-jp/tailwind-theme-plugin'
  check_contains "IMPL-04: reference names the official npm packages" "$IMPL_REFERENCE" '@digital-go-jp/design-tokens'
  check_contains "IMPL-05: reference resolves current versions at task time" "$IMPL_REFERENCE" 'npm view'
  check_contains "IMPL-06: reference records the text-style token vocabulary" "$IMPL_REFERENCE" 'text-std-'
  check_contains "IMPL-07: reference records the brand colour ramp" "$IMPL_REFERENCE" 'key-900'
  check_contains "IMPL-08: reference records DADS border-radius tokens" "$IMPL_REFERENCE" 'rounded-8'
  check_contains "IMPL-09: reference records the DADS breakpoints" "$IMPL_REFERENCE" 'desktop-admin'
  check_contains "IMPL-10: reference records the aria-disabled idiom" "$IMPL_REFERENCE" 'aria-disabled'
  check_contains "IMPL-11: reference records the focus indicator recipe" "$IMPL_REFERENCE" 'focus-visible:ring-yellow-300'
  check_contains "IMPL-12: reference records the 44 px target rule" "$IMPL_REFERENCE" '44'
  check_contains "IMPL-13: reference records forced-colors handling" "$IMPL_REFERENCE" 'forced-colors'
  check_contains "IMPL-14: reference handles Tailwind 3 and 4" "$IMPL_REFERENCE" 'v3.*v4|v4.*v3|Tailwind CSS 3.*Tailwind CSS 4'

  check "A11Y-01: accessibility gate reference exists" "$([ -f "$A11Y_REFERENCE" ] && echo 1 || echo 0)"
  check_contains "A11Y-02: gate requires JIS AA" "$A11Y_REFERENCE" 'JIS X 8341-3:2016.*AA'
  check_contains "A11Y-03: gate requires WCAG 2.2 AA" "$A11Y_REFERENCE" 'WCAG 2\.[12].*AA|WCAG 2\.2'
  check_contains "A11Y-04: gate covers keyboard and focus" "$A11Y_REFERENCE" 'keyboard.*focus|focus.*keyboard'
  check_contains "A11Y-05: gate covers reflow and contrast" "$A11Y_REFERENCE" 'reflow.*contrast|contrast.*reflow'
  check_contains "A11Y-06: gate rejects Storybook as conformance evidence" "$A11Y_REFERENCE" 'Storybook'
  check_contains "A11Y-07: gate blocks completion on undisclosed AA failure" "$A11Y_REFERENCE" '(undisclosed|not report).*(complete|failure)|level A or AA failure'

  # DADS-26..28 asserted against agents/openai.yaml, the last OpenAI/Codex
  # interface descriptor in the skills tree. ADR-0010 removed Codex CLI support
  # entirely, so the file was vestigial and has been deleted; nothing outside
  # the feature 015 planning trail referenced it.
}

run_archive_contract() {
  check "ARCH-01: vendored DADS archive exists" "$([ -f "$ARCHIVE_DIR/index.md" ] && echo 1 || echo 0)"
  check "ARCH-02: archive manifest provides the name-to-path index" "$([ -f "$ARCHIVE_DIR/MANIFEST.md" ] && echo 1 || echo 0)"
  check "ARCH-03: archive carries component specifications" "$([ -f "$ARCHIVE_DIR/components/button/index.md" ] && echo 1 || echo 0)"
  check "ARCH-04: archive carries the accessibility policy" "$([ -f "$ARCHIVE_DIR/webaccessibility/index.md" ] && echo 1 || echo 0)"
  check "ARCH-05: archive carries the foundations" "$([ -f "$ARCHIVE_DIR/foundations/typography/index.md" ] && echo 1 || echo 0)"
  check "ARCH-06: archive is Markdown only (kept verbatim for easy re-sync)" "$([ -d "$ARCHIVE_DIR" ] && [ "$(find "$ARCHIVE_DIR" -type f ! -name '*.md' | wc -l | tr -d ' ')" = "0" ] && echo 1 || echo 0)"
  check_contains "ARCH-07: archive states its own version" "$ARCHIVE_DIR/index.md" '^# .*v[0-9]+\.[0-9]+'
  check_contains "ARCH-08: archive pages carry source_url provenance" "$ARCHIVE_DIR/components/button/index.md" 'source_url:'
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
  check_contains "DASH-13: skill loads dashboard detail conditionally" "$SKILL_FILE" 'references/dashboard-design\.md.*dashboard'
}

run_sync_contract() {
  # Feature 021 removed this repository's former hand-maintained CLI port:
  # the `.agents/skills/` symlinks, the installer's CUSTOM_SKILLS
  # registration, and the generated sync suite are gone, so SYNC-SKILL-01…04,
  # 06, 07 and 10 no longer describe anything that exists — the authored
  # source below is what must stay true.
  check "SYNC-SKILL-02: authored skill exists at the source of truth" "$([ -e "$REPO_ROOT/.claude/skills/digital-agency-frontend/SKILL.md" ] && echo 1 || echo 0)"
  # Feature 035 dropped the hand-maintained skill list from .claude/CLAUDE.md:
  # the harness already injects every skill's name, description and trigger
  # phrases, and the list had drifted (7 named vs 10 present). SYNC-SKILL-05
  # therefore no longer asserts an enumeration — it asserts that CLAUDE.md
  # still points at the rule that does the routing. 05A remains the real
  # check: the composition order that no skill description can express.
  check_contains "SYNC-SKILL-05: Claude routing delegates to the routing rule" "$REPO_ROOT/.claude/CLAUDE.md" 'skill-routing'
  check_contains "SYNC-SKILL-05A: canonical Claude routing composes the skill" "$REPO_ROOT/.claude/rules/skill-routing.md" 'coder.*digital-agency-frontend|digital-agency-frontend.*coder'
  check_contains "SYNC-SKILL-08: English README lists the skill" "$REPO_ROOT/README.md" 'digital-agency-frontend'
  check_contains "SYNC-SKILL-09: Japanese README lists the skill" "$REPO_ROOT/README.ja.md" 'digital-agency-frontend'
}

case "$SELECTOR" in
dads)
  run_dads_contract
  ;;
archive)
  run_archive_contract
  ;;
dashboard)
  run_dashboard_contract
  ;;
sync)
  run_sync_contract
  ;;
all)
  run_dads_contract
  run_archive_contract
  run_dashboard_contract
  run_sync_contract
  ;;
*)
  echo "Usage: $0 [dads|archive|dashboard|sync]" >&2
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
