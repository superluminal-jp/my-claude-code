#!/usr/bin/env bash
# Contract tests for the Digital Agency 16:9 slide skill.
# Usage: bash tests/run-digital-agency-slides-skill.sh [skill|assets|tools|unit|lint|e2e]
# Literal backticks and dollar-prefixed skill names are intentional patterns.
# shellcheck disable=SC2016

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL_DIR="$REPO_ROOT/.claude/skills/digital-agency-slides"
SKILL_FILE="$SKILL_DIR/SKILL.md"
DESIGN_REFERENCE="$SKILL_DIR/references/slide-design.md"
CONTRACT_REFERENCE="$SKILL_DIR/references/authoring-contract.md"
CHECKS_REFERENCE="$SKILL_DIR/references/deck-checks.md"
SOURCING_REFERENCE="$SKILL_DIR/references/asset-sourcing.md"
SLIDE_CSS="$SKILL_DIR/assets/slide.css"
DECK_TEMPLATE="$SKILL_DIR/assets/deck-template.html"
DECK_CLI="$SKILL_DIR/scripts/deck.py"
CHECKER="$SKILL_DIR/scripts/check_slides.js"
FETCH_SCRIPT="$SKILL_DIR/scripts/fetch-dads-assets.sh"
SETUP_SCRIPT="$SKILL_DIR/scripts/setup.sh"
FIXTURE_DIR="$REPO_ROOT/tests/fixtures/slides"
LINT_ASSERTS="$REPO_ROOT/tests/assert_lint.py"
UNIT_ASSERTS="$REPO_ROOT/tests/assert_deck_units.py"
SELECTOR="${1:-all}"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m'

PASS=0
FAIL=0
SKIP=0
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

skip() {
  SKIP=$((SKIP + 1))
  printf "${YELLOW}SKIP${NC} %s\n" "$1"
}

contains() {
  local file="$1" pattern="$2"
  [ -f "$file" ] && grep -Eiq -- "$pattern" "$file"
}

check_contains() {
  local name="$1" file="$2" pattern="$3"
  check "$name" "$(contains "$file" "$pattern" && echo 1 || echo 0)"
}

# ---------------------------------------------------------------- the skill --

run_skill_contract() {
  check "SKILL-01: skill file exists" "$([ -f "$SKILL_FILE" ] && echo 1 || echo 0)"
  check_contains "SKILL-02: skill name is canonical" "$SKILL_FILE" '^name:[[:space:]]+digital-agency-slides$'
  check_contains "SKILL-03: description routes 16:9 slide work" "$SKILL_FILE" '^description:.*16:9.*slide'
  check_contains "SKILL-04: description routes DADS official assets" "$SKILL_FILE" '^description:.*Digital Agency Design System'
  check_contains "SKILL-05: description states the deck is delivered as HTML" "$SKILL_FILE" '^description:.*HTML'
  check_contains "SKILL-06: description states the negative boundary" "$SKILL_FILE" '^description:.*Do not use'
  check "SKILL-07: skill body names no sibling skill (self-contained)" \
    "$([ -f "$SKILL_FILE" ] && ! grep -Eq '`(coder|clarifier|adr|git-workflow|meta-spec|minto-[a-z]+|digital-agency-frontend|problem-definition|product-strategy|scrum-master|aws-research)`' "$SKILL_FILE" && echo 1 || echo 0)"
  check_contains "SKILL-08: description excludes PowerPoint files" "$SKILL_FILE" '^description:.*Do not use.*(PowerPoint|\.pptx)'
  check_contains "SKILL-09: skill states the 1280x720 canvas" "$SKILL_FILE" '1280 x 720'
  check_contains "SKILL-10: skill links the design reference" "$SKILL_FILE" 'references/slide-design\.md'
  check_contains "SKILL-11: skill links the authoring contract" "$SKILL_FILE" 'references/authoring-contract\.md'
  check_contains "SKILL-12: skill links the checks reference" "$SKILL_FILE" 'references/deck-checks\.md'
  check_contains "SKILL-13: skill links the sourcing reference" "$SKILL_FILE" 'references/asset-sourcing\.md'
  check_contains "SKILL-14: workflow gates delivery on lint and preview" "$SKILL_FILE" 'deck\.py.*lint'
  check_contains "SKILL-15: workflow orders premises, then the answer, then the tree" "$SKILL_FILE" 'premise.*answer.*(tree|point)'
  check_contains "SKILL-16: guardrail forbids splitting a node across slides" "$SKILL_FILE" '[Nn]ever split'
  check_contains "SKILL-17: guardrail forbids claiming Digital Agency endorsement" "$SKILL_FILE" 'endorsed by the Digital'
  check_contains "SKILL-18: guardrail forbids inventing tokens or versions" "$SKILL_FILE" '[Nn]ever invent.*(token|version)'
  check "SKILL-19: no DADS version number is pinned in prose (must resolve current)" \
    "$(! grep -Eqr 'v2\.[0-9]+\.[0-9]+' "$SKILL_FILE" "$DESIGN_REFERENCE" "$CONTRACT_REFERENCE" "$CHECKS_REFERENCE" "$SOURCING_REFERENCE" && echo 1 || echo 0)"
  check "SKILL-20: no official DADS code is vendored in the skill" \
    "$([ ! -e "$SKILL_DIR/assets/dads" ] && [ ! -e "$SKILL_DIR/references/dads-docs" ] && echo 1 || echo 0)"
  # PowerPoint conversion was removed (ADR-0018). The only mention left is the
  # description's exclusion, which is what routes .pptx work elsewhere.
  check "SKILL-21: nothing in the package converts to or targets PowerPoint" \
    "$(! grep -rIil -- 'pptx\|powerpoint' "$SKILL_DIR" | grep -v "^$SKILL_FILE$" | grep -q . && \
      ! sed '/^description:/d' "$SKILL_FILE" | grep -Eiq 'pptx|powerpoint' && echo 1 || echo 0)"
  check "SKILL-22: the conversion reference is gone" "$([ ! -e "$SKILL_DIR/references/pptx-conversion.md" ] && echo 1 || echo 0)"
  check_contains "SKILL-23: guardrail forbids guessing a classification" "$SKILL_FILE" '[Nn]ever guess.*classification'

  check "DSN-01: design reference exists" "$([ -f "$DESIGN_REFERENCE" ] && echo 1 || echo 0)"
  check_contains "DSN-02: reference requires one assertion per headline" "$DESIGN_REFERENCE" '(headline is an assertion|one assertion)'
  check_contains "DSN-03: reference records the canvas and safe area" "$DESIGN_REFERENCE" 'Safe area'
  check_contains "DSN-04: reference maps roles to the DADS heading sizes" "$DESIGN_REFERENCE" 'data-size="32"'
  check_contains "DSN-05: reference records the DADS colour tokens" "$DESIGN_REFERENCE" '--color-key-900'
  check_contains "DSN-06: reference records the contrast thresholds" "$DESIGN_REFERENCE" '4\.5:1'
  check_contains "DSN-07: reference records the layout catalogue" "$DESIGN_REFERENCE" 'layout catalogue'
  check_contains "DSN-08: reference states reading order is document order" "$DESIGN_REFERENCE" '[Rr]eading order is (DOM|document) order'
  check_contains "DSN-09: reference states the design system removes WCAG's large-text relaxation" "$DESIGN_REFERENCE" 'removes that relaxation'
  check_contains "DSN-10: reference records the non-text contrast rule" "$DESIGN_REFERENCE" '1\.4\.11'
  check_contains "DSN-11: reference branches on delivery mode" "$DESIGN_REFERENCE" 'Projected, distributed, or both'
  check_contains "DSN-12: reference gives a procedure for the argument, not just its vocabulary" "$DESIGN_REFERENCE" 'Write the question each slide answers'
  check_contains "DSN-13: reference maps slides to nodes of the tree" "$DESIGN_REFERENCE" 'one node'
  check_contains "DSN-14: reference derives the slide budget from the tree" "$DESIGN_REFERENCE" 'k \+ 4'
  check_contains "DSN-15: reference sets premises and definitions before the answer" "$DESIGN_REFERENCE" 'premise'
  check_contains "DSN-16: reference forbids explaining by metaphor or analogy" "$DESIGN_REFERENCE" '(metaphor|analogy)'
  check_contains "DSN-17: reference puts the paper's method on the premise slide" "$DESIGN_REFERENCE" '^\| Method.*premise'
  check_contains "DSN-18: reference puts the paper's discussion on the closing slide" "$DESIGN_REFERENCE" '^\| Discussion.*closing'
  check_contains "DSN-19: reference shows where each slide sits in the deck" "$DESIGN_REFERENCE" 'sld-tracker'
  check_contains "DSN-20: reference gives each tree level its own visual treatment" "$DESIGN_REFERENCE" '^### Make the tree visible'
  check_contains "DSN-21: reference places the classification marking on every slide" "$DESIGN_REFERENCE" '機密性.*公開範囲'

  check "CON-01: authoring contract exists" "$([ -f "$CONTRACT_REFERENCE" ] && echo 1 || echo 0)"
  check_contains "CON-02: contract uses the DADS heading with a shoulder" "$CONTRACT_REFERENCE" 'dads-heading__shoulder'
  check_contains "CON-03: contract requires one h1 and no skipped heading level" "$CONTRACT_REFERENCE" '(skip|飛ば).*(level|heading)|(level|heading).*(skip|飛ば)'
  check_contains "CON-04: contract uses the description list for definitions" "$CONTRACT_REFERENCE" 'dads-description-list'
  check_contains "CON-05: contract names the slide roles" "$CONTRACT_REFERENCE" 'data-layout="answer"'
  check_contains "CON-06: contract separates the dads-* and sld-* namespaces" "$CONTRACT_REFERENCE" 'sld-\*'
  check_contains "CON-07: contract gives the marking's markup" "$CONTRACT_REFERENCE" 'sld-marking__scope'

  check "CHK-01: checks reference exists" "$([ -f "$CHECKS_REFERENCE" ] && echo 1 || echo 0)"
  check_contains "CHK-02: reference documents both subcommands" "$CHECKS_REFERENCE" 'deck\.py preview'
  check_contains "CHK-03: reference lists the structure findings" "$CHECKS_REFERENCE" 'late-answer'
  check_contains "CHK-04: reference lists the document findings" "$CHECKS_REFERENCE" 'heading-skip'
  check_contains "CHK-05: reference documents the slide budget option" "$CHECKS_REFERENCE" '--max-slides'
  check_contains "CHK-06: reference lists the tracker findings" "$CHECKS_REFERENCE" 'tracker-missing'
  check_contains "CHK-07: reference lists the marking findings" "$CHECKS_REFERENCE" 'marking-missing'

  check "SRC-01: sourcing reference exists" "$([ -f "$SOURCING_REFERENCE" ] && echo 1 || echo 0)"
  check_contains "SRC-02: reference links the official DADS site" "$SOURCING_REFERENCE" 'https://design\.digital\.go\.jp/dads/'
  check_contains "SRC-03: reference states nothing official is vendored" "$SOURCING_REFERENCE" '[Nn]othing official is vendored'
  check_contains "SRC-04: reference states source precedence" "$SOURCING_REFERENCE" '(live official|authoritative)'
  check_contains "SRC-05: reference resolves package versions at task time" "$SOURCING_REFERENCE" 'npm view'
  check_contains "SRC-06: reference records the MIT code terms" "$SOURCING_REFERENCE" 'MIT'
  check_contains "SRC-07: reference records the Japanese source notice" "$SOURCING_REFERENCE" '出典：デジタル庁デザインシステムウェブサイト'
  check_contains "SRC-08: reference carves out illustrations, icons and Figma data" "$SOURCING_REFERENCE" 'Figma'
}

# ---------------------------------------------------------------- the assets --

run_asset_contract() {
  check "CSS-01: slide layout stylesheet exists" "$([ -f "$SLIDE_CSS" ] && echo 1 || echo 0)"
  check_contains "CSS-02: canvas is 1280px wide" "$SLIDE_CSS" '--sld-w:[[:space:]]*1280px'
  check_contains "CSS-03: canvas is 720px tall" "$SLIDE_CSS" '--sld-h:[[:space:]]*720px'
  check "CSS-04: stylesheet uses DADS tokens only, never a raw hex colour" \
    "$([ -f "$SLIDE_CSS" ] && ! grep -Eq '#[0-9a-fA-F]{3,8}\b' "$SLIDE_CSS" && echo 1 || echo 0)"
  check "CSS-05: stylesheet does not re-implement the DADS heading" \
    "$([ -f "$SLIDE_CSS" ] && ! grep -Eq '^\.sld-(message|eyebrow|rule)\b' "$SLIDE_CSS" && echo 1 || echo 0)"
  check_contains "CSS-06: stylesheet disclaims being a DADS component library" "$SLIDE_CSS" 'NOT[[:space:]]*$|are NOT'
  check_contains "CSS-07: slides clip rather than reflow" "$SLIDE_CSS" 'overflow: hidden'
  check "CSS-08: layout classes stay in the sld-* namespace" \
    "$([ -f "$SLIDE_CSS" ] && ! grep -Eq '^\.dads-' "$SLIDE_CSS" && echo 1 || echo 0)"
  check_contains "CSS-09: stylesheet prints one slide per page" "$SLIDE_CSS" '@page'
  check_contains "CSS-10: stylesheet draws the answer slide's tree" "$SLIDE_CSS" '^\.sld-tree'
  check_contains "CSS-11: stylesheet draws the position tracker" "$SLIDE_CSS" '^\.sld-tracker'
  check_contains "CSS-12: stylesheet draws the classification marking" "$SLIDE_CSS" '^\.sld-marking'

  check "TPL-01: deck template exists" "$([ -f "$DECK_TEMPLATE" ] && echo 1 || echo 0)"
  check_contains "TPL-02: template links the fetched DADS global stylesheet" "$DECK_TEMPLATE" 'dads/global\.css'
  check_contains "TPL-03: template links this skill's layout layer" "$DECK_TEMPLATE" 'slide\.css'
  check_contains "TPL-04: template carries a title layout" "$DECK_TEMPLATE" 'data-layout="title"'
  check_contains "TPL-05: template carries a table using the DADS component" "$DECK_TEMPLATE" 'dads-table__table'
  check_contains "TPL-06: template heads slides with the DADS heading and shoulder" "$DECK_TEMPLATE" 'dads-heading__shoulder'
  check_contains "TPL-07: template sets premises with a DADS description list" "$DECK_TEMPLATE" 'dads-description-list'
  check_contains "TPL-08: figure carries a text alternative" "$DECK_TEMPLATE" 'aria-labelledby|aria-label|<title'
  check_contains "TPL-09: template carries a premise slide" "$DECK_TEMPLATE" 'data-layout="premise"'
  check_contains "TPL-10: template carries an answer slide with the tree" "$DECK_TEMPLATE" 'class="sld-tree"'
  check "TPL-11: template has no section divider slides" \
    "$([ -f "$DECK_TEMPLATE" ] && ! grep -q 'data-layout="section"' "$DECK_TEMPLATE" && echo 1 || echo 0)"
  check_contains "TPL-13: template's premise slide states how the evidence was gathered" "$DECK_TEMPLATE" '調べ方：'
  check_contains "TPL-14: template's closing slide states the conclusion's limits" "$DECK_TEMPLATE" '限界：'
  check_contains "TPL-15: template shows each slide's place in the deck" "$DECK_TEMPLATE" 'class="sld-tracker[ "]'
  check_contains "TPL-16: the tracker marks the current part for assistive technology" "$DECK_TEMPLATE" 'aria-current="step"'
  check_contains "TPL-17: main slides number themselves against the whole" "$DECK_TEMPLATE" '<span>4 / 7</span>'
  check "TPL-19: the marking writes the level as 機密性n情報" \
    "$([ -f "$DECK_TEMPLATE" ] && grep -q 'sld-marking__level">機密性[123]情報<' "$DECK_TEMPLATE" && ! grep -q 'sld-marking__level">機密性[123]<' "$DECK_TEMPLATE" && echo 1 || echo 0)"
  check "TPL-18: every slide carries the classification marking" \
    "$([ -f "$DECK_TEMPLATE" ] && [ "$(grep -c 'class="sld-marking' "$DECK_TEMPLATE")" -eq "$(grep -c 'class="sld-slide"' "$DECK_TEMPLATE")" ] && echo 1 || echo 0)"
  check "TPL-12: template has exactly one h1" \
    "$([ -f "$DECK_TEMPLATE" ] && [ "$(grep -o '<h1' "$DECK_TEMPLATE" | wc -l)" -eq 1 ] && echo 1 || echo 0)"
}

# ----------------------------------------------------------------- the tools --

run_tool_contract() {
  check "TOOL-01: deck CLI exists and is executable" "$([ -x "$DECK_CLI" ] && echo 1 || echo 0)"
  check "TOOL-02: checker exists" "$([ -f "$CHECKER" ] && echo 1 || echo 0)"
  check "TOOL-03: asset fetch script exists and is executable" "$([ -x "$FETCH_SCRIPT" ] && echo 1 || echo 0)"
  check "TOOL-04: setup script exists and is executable" "$([ -x "$SETUP_SCRIPT" ] && echo 1 || echo 0)"
  check "TOOL-05: requirements are declared" "$([ -f "$SKILL_DIR/scripts/requirements.txt" ] && echo 1 || echo 0)"

  if command -v python3 >/dev/null 2>&1; then
    check "TOOL-06: deck CLI parses" "$(python3 -c "import ast,sys;ast.parse(open(sys.argv[1]).read())" "$DECK_CLI" >/dev/null 2>&1 && echo 1 || echo 0)"
  else
    skip "TOOL-06: python3 not available"
  fi

  if command -v node >/dev/null 2>&1; then
    check "TOOL-08: checker parses" "$(node --check "$CHECKER" >/dev/null 2>&1 && echo 1 || echo 0)"
  else
    skip "TOOL-08: node not available"
  fi

  check "TOOL-09: shell scripts parse" \
    "$(bash -n "$FETCH_SCRIPT" >/dev/null 2>&1 && bash -n "$SETUP_SCRIPT" >/dev/null 2>&1 && echo 1 || echo 0)"
  check_contains "TOOL-10: CLI exposes exactly lint and preview" "$DECK_CLI" 'choices=\["lint", "preview"\]'
  check_contains "TOOL-11: lint can report machine-readable findings" "$DECK_CLI" '"--json"'
  check "TOOL-07: requirements carry no PowerPoint library" \
    "$([ -f "$SKILL_DIR/scripts/requirements.txt" ] && ! grep -qi 'pptx' "$SKILL_DIR/scripts/requirements.txt" && echo 1 || echo 0)"
  check_contains "TOOL-12: checker emits findings for clipped text" "$CHECKER" "'clipped'"
  check_contains "TOOL-13: checker checks contrast" "$CHECKER" 'contrastRatio'
  check_contains "TOOL-14: checker checks the heading outline" "$CHECKER" "'heading-skip'"
  check_contains "TOOL-19: checker checks each slide's tracker against its position" "$CHECKER" "'tracker'"
  check_contains "TOOL-20: checker checks each slide's classification marking" "$CHECKER" "'marking'"
  check_contains "TOOL-17: checker compares tags case-insensitively (SVG reports lower case)" "$CHECKER" 'const tagOf'
  check "TOOL-18: the conversion extractor is gone" "$([ ! -e "$SKILL_DIR/scripts/extract_slides.js" ] && echo 1 || echo 0)"
  check_contains "TOOL-15: fetch script records upstream provenance" "$FETCH_SCRIPT" 'Commit'
  check "TOOL-16: repository root scripts/ stays removed (ADR-0007)" "$([ ! -e "$REPO_ROOT/scripts" ] && echo 1 || echo 0)"
}

# ---------------------------------------------------------------- behaviour --

# Everything above greps files. These run the checker and assert against what
# it actually reports — deck.py's own functions, self-contained fixtures that
# need no network, and the shipped template against freshly fetched assets —
# because a string in a document proves nothing about behaviour.

find_python() {
  local candidate
  if [ -n "${DECK_PYTHON:-}" ]; then
    printf '%s' "$DECK_PYTHON"
    return
  fi
  for candidate in "$REPO_ROOT/.venv/bin/python" "$(command -v python3 || true)"; do
    if [ -n "$candidate" ] && "$candidate" -c 'import playwright' >/dev/null 2>&1; then
      printf '%s' "$candidate"
      return
    fi
  done
  printf ''
}

run_unit_contract() {
  local python_bin
  python_bin="$(find_python)"
  if [ -z "$python_bin" ]; then
    skip "UNIT-*: playwright not installed (run scripts/setup.sh, then set DECK_PYTHON)"
    return
  fi
  check "UNIT-00: unit assertions exist" "$([ -f "$UNIT_ASSERTS" ] && echo 1 || echo 0)"
  if "$python_bin" "$UNIT_ASSERTS" "$DECK_CLI" >"$REPO_ROOT/.unit.log" 2>&1; then
    check "UNIT: deck.py unit assertions pass" "1"
  else
    check "UNIT: deck.py unit assertions pass" "0"
    sed 's/^/      /' "$REPO_ROOT/.unit.log" >&2
  fi
  rm -f "$REPO_ROOT/.unit.log"
}

run_lint_contract() {
  local python_bin
  python_bin="$(find_python)"
  if [ -z "$python_bin" ]; then
    skip "LINT-*: playwright not installed"
    return
  fi
  check "LINT-00: lint fixtures exist" \
    "$([ -f "$FIXTURE_DIR/structure.html" ] && [ -f "$FIXTURE_DIR/document.html" ] && [ -f "$FIXTURE_DIR/clean.html" ] && [ -f "$FIXTURE_DIR/tracker.html" ] && [ -f "$FIXTURE_DIR/marking.html" ] && echo 1 || echo 0)"
  if "$python_bin" "$LINT_ASSERTS" "$python_bin" "$DECK_CLI" "$FIXTURE_DIR" >"$REPO_ROOT/.lint.log" 2>&1; then
    check "LINT: findings match each fixture" "1"
  else
    check "LINT: findings match each fixture" "0"
    sed 's/^/      /' "$REPO_ROOT/.lint.log" >&2
  fi
  rm -f "$REPO_ROOT/.lint.log"
}

# ------------------------------------------------------------------ end-to-end --

run_e2e_contract() {
  local python_bin
  python_bin="$(find_python)"

  if [ -z "$python_bin" ]; then
    skip "E2E-01..03: playwright not installed (run scripts/setup.sh, then set DECK_PYTHON)"
    return
  fi

  local work
  work="$(mktemp -d)"
  trap 'rm -rf "$work"' RETURN

  cp "$DECK_TEMPLATE" "$work/deck.html"
  cp "$SLIDE_CSS" "$work/slide.css"

  if ! bash "$FETCH_SCRIPT" "$work" >/dev/null 2>&1; then
    skip "E2E-01..03: could not fetch official DADS assets (network required)"
    return
  fi
  check "E2E-01: official assets fetched with provenance" "$([ -f "$work/dads/global.css" ] && [ -f "$work/dads/SOURCE.md" ] && echo 1 || echo 0)"

  "$python_bin" "$DECK_CLI" lint "$work/deck.html" --json >"$work/lint.json" 2>"$work/lint.txt"
  check "E2E-02: the shipped template lints with no error and no warning" \
    "$("$python_bin" - "$work/lint.json" <<'PY' >/dev/null 2>&1 && echo 1 || echo 0
import json, sys
report = json.load(open(sys.argv[1], encoding="utf-8"))
assert report["findings"] == [], report["findings"]
PY
)"
  [ -s "$work/lint.txt" ] && sed 's/^/      /' "$work/lint.txt" >&2
  check "E2E-03: the template's main deck is seven slides with the answer third" \
    "$("$python_bin" - "$work/lint.json" <<'PY' >/dev/null 2>&1 && echo 1 || echo 0
import json, sys
slides = json.load(open(sys.argv[1], encoding="utf-8"))["slides"]
layouts = [s["layout"] for s in slides]
main = [l for l in layouts if l != "appendix"]
assert len(main) == 7, layouts
assert layouts[2] == "answer", layouts
assert layouts[0] == "title" and layouts[1] == "premise", layouts
PY
)"

  if "$python_bin" "$DECK_CLI" preview "$work/deck.html" -o "$work/preview" >"$work/preview.txt" 2>&1; then
    check "E2E-04: preview writes one PNG per slide" \
      "$([ "$(find "$work/preview" -name 'slide-*.png' | wc -l)" -eq "$(grep -c 'class="sld-slide"' "$work/deck.html")" ] && echo 1 || echo 0)"
  else
    check "E2E-04: preview writes one PNG per slide" "0"
    sed 's/^/      /' "$work/preview.txt" >&2
  fi
}

case "$SELECTOR" in
skill) run_skill_contract ;;
assets) run_asset_contract ;;
tools) run_tool_contract ;;
unit) run_unit_contract ;;
lint) run_lint_contract ;;
e2e) run_e2e_contract ;;
all)
  run_skill_contract
  run_asset_contract
  run_tool_contract
  run_unit_contract
  run_lint_contract
  run_e2e_contract
  ;;
*)
  echo "Usage: $0 [skill|assets|tools|unit|lint|e2e]" >&2
  exit 2
  ;;
esac

echo ""
echo "===================="
printf "Results: ${GREEN}%d passed${NC}, ${RED}%d failed${NC}, ${YELLOW}%d skipped${NC}\n" "$PASS" "$FAIL" "$SKIP"

if [ "$FAIL" -gt 0 ]; then
  printf "\nFailed:%b\n" "$FAIL_NAMES"
  exit 1
fi
