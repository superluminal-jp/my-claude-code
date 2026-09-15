#!/usr/bin/env bash
# Contract tests for the Digital Agency 16:9 slide skill.
# Usage: bash tests/run-digital-agency-slides-skill.sh [skill|assets|tools|e2e]
# Literal backticks and dollar-prefixed skill names are intentional patterns.
# shellcheck disable=SC2016

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL_DIR="$REPO_ROOT/.claude/skills/digital-agency-slides"
SKILL_FILE="$SKILL_DIR/SKILL.md"
JA_SKILL_FILE="$REPO_ROOT/.claude-ja/skills/digital-agency-slides/SKILL.md"
DESIGN_REFERENCE="$SKILL_DIR/references/slide-design.md"
CONTRACT_REFERENCE="$SKILL_DIR/references/authoring-contract.md"
CONVERSION_REFERENCE="$SKILL_DIR/references/pptx-conversion.md"
SOURCING_REFERENCE="$SKILL_DIR/references/asset-sourcing.md"
SLIDE_CSS="$SKILL_DIR/assets/slide.css"
DECK_TEMPLATE="$SKILL_DIR/assets/deck-template.html"
DECK_CLI="$SKILL_DIR/scripts/deck.py"
EXTRACTOR="$SKILL_DIR/scripts/extract_slides.js"
FETCH_SCRIPT="$SKILL_DIR/scripts/fetch-dads-assets.sh"
SETUP_SCRIPT="$SKILL_DIR/scripts/setup.sh"
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
  check_contains "SKILL-05: description routes PowerPoint conversion" "$SKILL_FILE" '^description:.*(PowerPoint|\.pptx)'
  check_contains "SKILL-06: description states the negative boundary" "$SKILL_FILE" '^description:.*Do not use'
  check "SKILL-07: skill body names no sibling skill (self-contained)" \
    "$([ -f "$SKILL_FILE" ] && ! grep -Eq '`(coder|clarifier|adr|git-workflow|meta-spec|minto-[a-z]+|digital-agency-frontend|problem-definition|product-strategy|scrum-master|cloud-platform-research)`' "$SKILL_FILE" && echo 1 || echo 0)"
  check_contains "SKILL-08: skill states the exact px/pt/EMU invariant" "$SKILL_FILE" '9525 EMU'
  check_contains "SKILL-09: skill states the 1280x720 canvas" "$SKILL_FILE" '1280 x 720'
  check_contains "SKILL-10: skill links the design reference" "$SKILL_FILE" 'references/slide-design\.md'
  check_contains "SKILL-11: skill links the authoring contract" "$SKILL_FILE" 'references/authoring-contract\.md'
  check_contains "SKILL-12: skill links the conversion reference" "$SKILL_FILE" 'references/pptx-conversion\.md'
  check_contains "SKILL-13: skill links the sourcing reference" "$SKILL_FILE" 'references/asset-sourcing\.md'
  check_contains "SKILL-14: workflow gates conversion on lint and preview" "$SKILL_FILE" 'deck\.py.*lint'
  check_contains "SKILL-15: guardrail forbids rasterizing a whole slide" "$SKILL_FILE" '[Nn]ever rasterize a whole slide'
  check_contains "SKILL-16: guardrail records the font dependency" "$SKILL_FILE" '(font|Fonts).*(metrics|install|remap)'
  check_contains "SKILL-17: guardrail forbids claiming Digital Agency endorsement" "$SKILL_FILE" 'endorsed by the Digital'
  check_contains "SKILL-18: guardrail forbids inventing tokens or versions" "$SKILL_FILE" '[Nn]ever invent.*(token|version)'
  check "SKILL-19: no DADS version number is pinned in prose (must resolve current)" \
    "$(! grep -Eqr 'v2\.[0-9]+\.[0-9]+' "$SKILL_FILE" "$DESIGN_REFERENCE" "$CONTRACT_REFERENCE" "$CONVERSION_REFERENCE" "$SOURCING_REFERENCE" && echo 1 || echo 0)"
  check "SKILL-20: no official DADS code is vendored in the skill" \
    "$([ ! -e "$SKILL_DIR/assets/dads" ] && [ ! -e "$SKILL_DIR/references/dads-docs" ] && echo 1 || echo 0)"
  check "SKILL-21: Japanese mirror exists" "$([ -f "$JA_SKILL_FILE" ] && echo 1 || echo 0)"
  check_contains "SKILL-22: Japanese mirror carries the canonical name" "$JA_SKILL_FILE" '^name:[[:space:]]+digital-agency-slides$'

  check "DSN-01: design reference exists" "$([ -f "$DESIGN_REFERENCE" ] && echo 1 || echo 0)"
  check_contains "DSN-02: reference requires one assertion per slide" "$DESIGN_REFERENCE" '(headline is an assertion|one assertion)'
  check_contains "DSN-03: reference records the canvas and safe area" "$DESIGN_REFERENCE" 'Safe area'
  check_contains "DSN-04: reference records the DADS type scale classes" "$DESIGN_REFERENCE" 'dads-u-std-32B-150'
  check_contains "DSN-05: reference records the DADS colour tokens" "$DESIGN_REFERENCE" '--color-key-900'
  check_contains "DSN-06: reference records the contrast thresholds" "$DESIGN_REFERENCE" '4\.5:1'
  check_contains "DSN-07: reference records the layout catalogue" "$DESIGN_REFERENCE" 'layout catalogue'
  check_contains "DSN-08: reference states reading order is document order" "$DESIGN_REFERENCE" '[Rr]eading order is DOM order'

  check "CON-01: authoring contract exists" "$([ -f "$CONTRACT_REFERENCE" ] && echo 1 || echo 0)"
  check_contains "CON-02: contract documents the data-pptx overrides" "$CONTRACT_REFERENCE" 'data-pptx'
  check_contains "CON-03: contract documents the raster escape hatch" "$CONTRACT_REFERENCE" '`raster`'
  check_contains "CON-04: contract explains why a flex gap splits a text box" "$CONTRACT_REFERENCE" '(flex|grid).*gap.*not a margin|gap. is not a margin'
  check_contains "CON-05: contract states pseudo-elements do not convert" "$CONTRACT_REFERENCE" '::before'
  check_contains "CON-06: contract separates the dads-* and sld-* namespaces" "$CONTRACT_REFERENCE" 'sld-\*'

  check "CNV-01: conversion reference exists" "$([ -f "$CONVERSION_REFERENCE" ] && echo 1 || echo 0)"
  check_contains "CNV-02: reference states the exact EMU factor" "$CONVERSION_REFERENCE" '9525 EMU'
  check_contains "CNV-03: reference states the exact slide EMU size" "$CONVERSION_REFERENCE" '12192000 x 6858000'
  check_contains "CNV-04: reference documents every subcommand" "$CONVERSION_REFERENCE" 'deck\.py ir'
  check_contains "CNV-05: reference lists the finding codes" "$CONVERSION_REFERENCE" 'pseudo-decoration'
  check_contains "CNV-06: reference separates exact from approximate fidelity" "$CONVERSION_REFERENCE" '\*\*Exact\.\*\*'
  check_contains "CNV-07: reference records the font-substitution failure mode" "$CONVERSION_REFERENCE" 'Font substitution'

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
  # A ::before/::after *selector* is the regression; naming them in a comment is not.
  check "CSS-05: stylesheet paints no decoration in a pseudo-element" \
    "$([ -f "$SLIDE_CSS" ] && ! grep -Eq '::(before|after)[^{;]*\{' "$SLIDE_CSS" && echo 1 || echo 0)"
  check_contains "CSS-06: stylesheet disclaims being a DADS component library" "$SLIDE_CSS" 'NOT[[:space:]]*$|are NOT'
  check_contains "CSS-07: slides clip rather than reflow" "$SLIDE_CSS" 'overflow: hidden'
  check "CSS-08: layout classes stay in the sld-* namespace" \
    "$([ -f "$SLIDE_CSS" ] && ! grep -Eq '^\.dads-' "$SLIDE_CSS" && echo 1 || echo 0)"

  check "TPL-01: deck template exists" "$([ -f "$DECK_TEMPLATE" ] && echo 1 || echo 0)"
  check_contains "TPL-02: template links the fetched DADS global stylesheet" "$DECK_TEMPLATE" 'dads/global\.css'
  check_contains "TPL-03: template links this skill's layout layer" "$DECK_TEMPLATE" 'slide\.css'
  check_contains "TPL-04: template carries a title layout" "$DECK_TEMPLATE" 'data-layout="title"'
  check_contains "TPL-05: template carries a table layout using the DADS component" "$DECK_TEMPLATE" 'dads-table__table'
  check_contains "TPL-06: template demonstrates the raster escape hatch" "$DECK_TEMPLATE" 'data-pptx="raster"'
  check_contains "TPL-07: template demonstrates speaker notes" "$DECK_TEMPLATE" 'data-pptx="notes"'
  check_contains "TPL-08: rasterized figure carries a text alternative" "$DECK_TEMPLATE" 'aria-labelledby|aria-label|<title'
  check "TPL-09: template draws its rules as real elements, not pseudo-elements" \
    "$([ -f "$DECK_TEMPLATE" ] && grep -q 'sld-rule' "$DECK_TEMPLATE" && echo 1 || echo 0)"
}

# ----------------------------------------------------------------- the tools --

run_tool_contract() {
  check "TOOL-01: deck CLI exists and is executable" "$([ -x "$DECK_CLI" ] && echo 1 || echo 0)"
  check "TOOL-02: extractor exists" "$([ -f "$EXTRACTOR" ] && echo 1 || echo 0)"
  check "TOOL-03: asset fetch script exists and is executable" "$([ -x "$FETCH_SCRIPT" ] && echo 1 || echo 0)"
  check "TOOL-04: setup script exists and is executable" "$([ -x "$SETUP_SCRIPT" ] && echo 1 || echo 0)"
  check "TOOL-05: requirements are declared" "$([ -f "$SKILL_DIR/scripts/requirements.txt" ] && echo 1 || echo 0)"

  if command -v python3 >/dev/null 2>&1; then
    check "TOOL-06: deck CLI parses" "$(python3 -c "import ast,sys;ast.parse(open(sys.argv[1]).read())" "$DECK_CLI" >/dev/null 2>&1 && echo 1 || echo 0)"
    check "TOOL-07: px-to-EMU and px-to-pt factors are exact" \
      "$(python3 - "$DECK_CLI" <<'PY' >/dev/null 2>&1 && echo 1 || echo 0
import importlib.util, sys
spec = importlib.util.spec_from_file_location("deck", sys.argv[1])
deck = importlib.util.module_from_spec(spec)
sys.modules["deck"] = deck  # dataclasses resolves annotations through sys.modules
spec.loader.exec_module(deck)
assert deck.EMU_PER_PX == 9525, deck.EMU_PER_PX
assert deck.PT_PER_PX == 0.75, deck.PT_PER_PX
assert deck.px_to_emu(1280) == 12192000
assert deck.px_to_emu(720) == 6858000
assert deck.px_to_pt(32) == 24.0
PY
)"
  else
    skip "TOOL-06/07: python3 not available"
  fi

  if command -v node >/dev/null 2>&1; then
    check "TOOL-08: extractor parses" "$(node --check "$EXTRACTOR" >/dev/null 2>&1 && echo 1 || echo 0)"
  else
    skip "TOOL-08: node not available"
  fi

  check "TOOL-09: shell scripts parse" \
    "$(bash -n "$FETCH_SCRIPT" >/dev/null 2>&1 && bash -n "$SETUP_SCRIPT" >/dev/null 2>&1 && echo 1 || echo 0)"
  check_contains "TOOL-10: CLI exposes lint, preview, pptx and ir" "$DECK_CLI" '"lint", "preview", "pptx", "ir"'
  check_contains "TOOL-11: CLI refuses to convert a deck with errors by default" "$DECK_CLI" 'Refusing to convert a deck with errors'
  check_contains "TOOL-12: extractor emits findings for clipped text" "$EXTRACTOR" "'clipped'"
  check_contains "TOOL-13: extractor checks contrast" "$EXTRACTOR" 'contrastRatio'
  check_contains "TOOL-14: extractor flags unreachable pseudo-element decoration" "$EXTRACTOR" 'pseudo-decoration'
  check_contains "TOOL-15: fetch script records upstream provenance" "$FETCH_SCRIPT" 'Commit'
  check "TOOL-16: repository root scripts/ stays removed (ADR-0007)" "$([ ! -e "$REPO_ROOT/scripts" ] && echo 1 || echo 0)"
}

# ------------------------------------------------------------------ end-to-end --

run_e2e_contract() {
  local python_bin="${DECK_PYTHON:-}"
  if [ -z "$python_bin" ]; then
    for candidate in "$REPO_ROOT/.venv/bin/python" "$(command -v python3 || true)"; do
      if [ -n "$candidate" ] && "$candidate" -c 'import pptx, playwright' >/dev/null 2>&1; then
        python_bin="$candidate"
        break
      fi
    done
  fi

  if [ -z "$python_bin" ]; then
    skip "E2E-01..03: python-pptx and playwright not installed (run scripts/setup.sh, then set DECK_PYTHON)"
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

  if ! "$python_bin" "$DECK_CLI" lint "$work/deck.html" >"$work/lint.txt" 2>&1; then
    check "E2E-02: the shipped template lints clean" "0"
    sed 's/^/      /' "$work/lint.txt" >&2
  else
    check "E2E-02: the shipped template lints clean" "1"
  fi

  if "$python_bin" "$DECK_CLI" pptx "$work/deck.html" -o "$work/deck.pptx" >"$work/pptx.txt" 2>&1; then
    check "E2E-03: conversion produces a 16:9 deck of native shapes" \
      "$("$python_bin" - "$work/deck.pptx" <<'PY' >/dev/null 2>&1 && echo 1 || echo 0
import sys
from pptx import Presentation
prs = Presentation(sys.argv[1])
assert prs.slide_width == 12192000, prs.slide_width
assert prs.slide_height == 6858000, prs.slide_height
assert len(prs.slides) >= 9, len(prs.slides)
pictures = sum(1 for s in prs.slides for sh in s.shapes if sh.shape_type is not None and "PICTURE" in str(sh.shape_type))
shapes = sum(len(s.shapes) for s in prs.slides)
assert pictures <= 2, f"{pictures} pictures — the deck is being rasterized"
assert shapes - pictures > 50, shapes
assert any(s.has_table for s in prs.slides for s in s.shapes if hasattr(s, "has_table"))
PY
)"
  else
    check "E2E-03: conversion produces a 16:9 deck of native shapes" "0"
    sed 's/^/      /' "$work/pptx.txt" >&2
  fi
}

case "$SELECTOR" in
skill) run_skill_contract ;;
assets) run_asset_contract ;;
tools) run_tool_contract ;;
e2e) run_e2e_contract ;;
all)
  run_skill_contract
  run_asset_contract
  run_tool_contract
  run_e2e_contract
  ;;
*)
  echo "Usage: $0 [skill|assets|tools|e2e]" >&2
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
