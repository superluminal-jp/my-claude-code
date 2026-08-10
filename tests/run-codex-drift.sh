#!/usr/bin/env bash
# Upstream-drift suite for the Codex documentation (feature 021).
#
# Everything README.md § "Codex CLI support" says about Codex is a measurement
# of software that changes underneath us. This suite re-derives the small set
# of upstream facts those claims rest on, so staleness surfaces on its own
# instead of waiting for someone to notice.
#
# It SKIPs — never fails — when the Codex CLI or the migrate-to-codex skill is
# absent, so contributors without Codex are not blocked and CI stays green.
# A drift warning is a prompt to re-measure (specs/021-codex-official-import/
# quickstart.md Steps 4-5), not a defect to suppress.
#
# Contract: specs/021-codex-official-import/contracts/codex-setup-procedure.md
# § G3 (DRIFT-01 … DRIFT-06).
#
# Usage: bash tests/run-codex-drift.sh

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m'

PASS=0
FAIL=0
SKIP=0
FAIL_NAMES=""

# The version every stamped claim in README.md was measured against. Update
# this together with the "measured on" stamp when re-measuring.
REFERENCE_CODEX_VERSION="0.147.0"

# Documented cache location of the curated skill (README.md § Codex CLI support).
MIGRATE_SKILL_DIR="$HOME/.codex/vendor_imports/skills/skills/.curated/migrate-to-codex"

check() {
  local name="$1" cond="$2"
  if [ "$cond" = "0" ]; then
    PASS=$((PASS + 1))
    printf "${GREEN}PASS${NC} %s\n" "$name"
  else
    FAIL=$((FAIL + 1))
    FAIL_NAMES="$FAIL_NAMES\n  - $name"
    printf "${RED}FAIL${NC} %s\n" "$name"
  fi
}

skip() {
  local name="$1" reason="$2"
  SKIP=$((SKIP + 1))
  printf "${YELLOW}SKIP${NC} %s (%s)\n" "$name" "$reason"
}

cd "$REPO_ROOT" || exit 1

HAVE_CODEX=0
if command -v codex >/dev/null 2>&1 && codex --version >/dev/null 2>&1; then
  HAVE_CODEX=1
fi

# --- DRIFT-01: CLI version matches what the documentation was measured on ---
if [ "$HAVE_CODEX" = "1" ]; then
  CURRENT_VERSION="$(codex --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)"
  if [ "$CURRENT_VERSION" = "$REFERENCE_CODEX_VERSION" ]; then
    check "DRIFT-01: Codex CLI is the measured version ($REFERENCE_CODEX_VERSION)" 0
  else
    # Deliberately a SKIP, not a FAIL: a newer Codex is normal and expected.
    # It means the stamped claims need re-measuring, not that anything broke.
    skip "DRIFT-01: Codex CLI version" \
      "found $CURRENT_VERSION, docs measured on $REFERENCE_CODEX_VERSION — re-run quickstart Steps 4-5 and update the stamp"
  fi
else
  skip "DRIFT-01: Codex CLI version" "codex not installed"
fi

# --- DRIFT-02 / DRIFT-03: the hooks feature flag ----------------------------
if [ "$HAVE_CODEX" = "1" ]; then
  FEATURES="$(codex features list 2>/dev/null)"
  if [ -n "$FEATURES" ]; then
    hooks_enabled="$(printf '%s\n' "$FEATURES" | awk '$1 == "hooks" && $NF == "true" {print "yes"}')"
    check "DRIFT-02: feature 'hooks' exists and is enabled" \
      "$([ "$hooks_enabled" = "yes" ] && echo 0 || echo 1)"

    # The procedure explicitly tells developers NOT to set this. If it ever
    # appears upstream, that instruction has to be revisited.
    codex_hooks_present="$(printf '%s\n' "$FEATURES" | awk '$1 == "codex_hooks" {print "yes"}')"
    check "DRIFT-03: no 'codex_hooks' feature exists (docs tell developers not to set it)" \
      "$([ -z "$codex_hooks_present" ] && echo 0 || echo 1)"
  else
    skip "DRIFT-02: feature 'hooks' enabled" "codex features list produced no output"
    skip "DRIFT-03: no 'codex_hooks' feature" "codex features list produced no output"
  fi
else
  skip "DRIFT-02: feature 'hooks' enabled" "codex not installed"
  skip "DRIFT-03: no 'codex_hooks' feature" "codex not installed"
fi

# --- DRIFT-04: /import remains TUI-only -------------------------------------
if [ "$HAVE_CODEX" = "1" ]; then
  import_subcmd="$(codex --help 2>/dev/null | awk '/^Commands:/,/^$/' | grep -cE '^[[:space:]]+import([[:space:]]|$)')"
  check "DRIFT-04: no 'codex import' subcommand (docs say /import is TUI-only)" \
    "$([ "$import_subcmd" = "0" ] && echo 0 || echo 1)"
else
  skip "DRIFT-04: no 'codex import' subcommand" "codex not installed"
fi

# --- DRIFT-05: the curated skill is where the docs say it is ----------------
if [ -f "$MIGRATE_SKILL_DIR/scripts/migrate-to-codex.py" ]; then
  check "DRIFT-05: migrate-to-codex skill is at the documented cache path" 0
  checked="$(grep -hoE 'Docs last checked: [0-9]{4}-[0-9]{2}-[0-9]{2}' \
    "$MIGRATE_SKILL_DIR/references/differences.md" 2>/dev/null | head -1)"
  [ -n "$checked" ] && printf "     converter reference file self-reports: %s\n" "$checked"
else
  skip "DRIFT-05: migrate-to-codex skill at documented path" \
    "not found at $MIGRATE_SKILL_DIR — README's inspection commands need updating"
fi

# --- DRIFT-06: the AGENTS.md symlink hazard still exists --------------------
# README warns that the converter's write mode symlinks AGENTS.md to CLAUDE.md.
# If that behaviour ever changes, the warning becomes misinformation.
if [ -f "$MIGRATE_SKILL_DIR/scripts/migrate-to-codex.py" ] && command -v python3 >/dev/null 2>&1; then
  dry="$(python3 "$MIGRATE_SKILL_DIR/scripts/migrate-to-codex.py" \
    --source ./.claude/ --target ./.codex/ --dry-run 2>/dev/null)"
  if [ -n "$dry" ]; then
    hazard="$(printf '%s\n' "$dry" | grep -c 'symlinked: AGENTS.md')"
    check "DRIFT-06: converter still symlinks AGENTS.md (README's warning is still true)" \
      "$([ "$hazard" -ge 1 ] && echo 0 || echo 1)"
  else
    skip "DRIFT-06: converter AGENTS.md symlink hazard" "dry-run produced no output"
  fi
else
  skip "DRIFT-06: converter AGENTS.md symlink hazard" "migrate-to-codex or python3 unavailable"
fi

echo ""
echo "===================="
printf "Results: ${GREEN}%d passed${NC}, ${RED}%d failed${NC}, ${YELLOW}%d skipped${NC}\n" "$PASS" "$FAIL" "$SKIP"

if [ "$SKIP" -gt 0 ]; then
  printf "%bNote%b: skips are expected without Codex installed. A DRIFT-01 skip means the\n" "$YELLOW" "$NC"
  printf "      documentation's measured-on stamp is older than the installed CLI — re-run\n"
  printf "      specs/021-codex-official-import/quickstart.md Steps 4-5 and update it.\n"
fi

if [ "$FAIL" -gt 0 ]; then
  printf "\nFailed:%b\n" "$FAIL_NAMES"
  exit 1
fi
