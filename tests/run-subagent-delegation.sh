#!/usr/bin/env bash
# Behavior test for .claude/rules/subagent-delegation.md (specs/020-subagent-delegation-rule).
#
# The rule is always loaded, so its contract is structural: it must state both
# halves of the decision (delegate / stay inline), name the capabilities a
# subagent lacks so those conditions are derivable, warn that delegation moves
# context cost rather than removing it, cover both delegation mechanisms, and
# cite its sources. It must also not duplicate the parallelism guidance that
# .claude/CLAUDE.md already owns.
#
# Deterministic: inspects repository files only. No network, no `claude` CLI.
# Usage: bash tests/run-subagent-delegation.sh

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RULE="$REPO_ROOT/.claude/rules/subagent-delegation.md"
CLAUDE_MD="$REPO_ROOT/.claude/CLAUDE.md"
AGENTS_MD="$REPO_ROOT/AGENTS.md"

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

PASS=0
FAIL=0
FAIL_NAMES=""

check() {
  local name="$1" cond="$2"
  if [ "$cond" = "1" ]; then
    PASS=$((PASS + 1))
    printf "${GREEN}PASS${NC} %s\n" "$name"
  else
    FAIL=$((FAIL + 1))
    FAIL_NAMES="$FAIL_NAMES\n  - $name"
    printf "${RED}FAIL${NC} %s\n" "$name"
  fi
}

# Case-insensitive fixed-string presence in the rule.
rule_has() {
  grep -qiF "$1" "$RULE" 2>/dev/null
}

# --- House conventions for a rules file ------------------------------------

[ -f "$RULE" ] && c=1 || c=0
check "the delegation rule exists in .claude/rules/" "$c"

grep -q '^Purpose:' "$RULE" 2>/dev/null && c=1 || c=0
check "rule opens with the house 'Purpose:' line" "$c"

grep -q '^## References' "$RULE" 2>/dev/null && c=1 || c=0
check "rule carries a References section" "$c"

# FR-006: sources must be reachable, not just named.
grep -q 'https://code.claude.com/docs/en/sub-agents' "$RULE" 2>/dev/null && c=1 || c=0
check "rule cites the sub-agents documentation by URL" "$c"

grep -q 'https://code.claude.com/docs/en/skills' "$RULE" 2>/dev/null && c=1 || c=0
check "rule cites the skills documentation by URL" "$c"

# R4: living documentation is cited with the date it was read.
grep -Eq '20[0-9]{2}-[0-9]{2}-[0-9]{2}' "$RULE" 2>/dev/null && c=1 || c=0
check "rule dates its documentation citations" "$c"

# --- FR-001: when to delegate ----------------------------------------------

rule_has 'large amounts of output' && c=1 || c=0
check "rule names high-volume output as the primary delegation trigger" "$c"

rule_has 'self-contained' && c=1 || c=0
check "rule requires the work to be self-contained" "$c"

grep -qi 'parallel' "$RULE" 2>/dev/null && c=1 || c=0
check "rule covers independent investigations in parallel" "$c"

# --- FR-002: when to stay inline -------------------------------------------

grep -qi 'back-and-forth\|iterative' "$RULE" 2>/dev/null && c=1 || c=0
check "rule keeps back-and-forth work in the main conversation" "$c"

grep -qi 'latency' "$RULE" 2>/dev/null && c=1 || c=0
check "rule accounts for latency" "$c"

# --- FR-003: why those conditions hold -------------------------------------

grep -qi 'AskUserQuestion\|cannot ask\|can.t ask' "$RULE" 2>/dev/null && c=1 || c=0
check "rule states a subagent cannot ask the operator" "$c"

grep -qi 'conversation history' "$RULE" 2>/dev/null && c=1 || c=0
check "rule states a subagent does not see the conversation" "$c"

grep -qi 'cache' "$RULE" 2>/dev/null && c=1 || c=0
check "rule explains why delegating after exploring pays twice" "$c"

# --- FR-005: delegation is not free ----------------------------------------

grep -qi 'return to your main conversation\|returns to the main conversation\|results return' "$RULE" 2>/dev/null && c=1 || c=0
check "rule warns that returned results consume main-conversation context" "$c"

# --- FR-004: both mechanisms -----------------------------------------------

rule_has 'context: fork' && c=1 || c=0
check "rule covers the forked-skill mechanism" "$c"

rule_has 'skills:' && c=1 || c=0
check "rule covers the preloaded-skills mechanism" "$c"

grep -qi 'without a task\|no actionable\|guidelines' "$RULE" 2>/dev/null && c=1 || c=0
check "rule warns against forking guidance that carries no task" "$c"

# --- FR-007 / FR-008: wiring and no duplication ----------------------------

grep -q '@.claude/rules/subagent-delegation.md' "$CLAUDE_MD" 2>/dev/null && c=1 || c=0
check "CLAUDE.md imports the rule" "$c"

grep -q 'subagent-delegation' "$CLAUDE_MD" 2>/dev/null &&
  grep -c 'subagent-delegation' "$CLAUDE_MD" >/dev/null && c=1 || c=0
check "CLAUDE.md references the rule from its execution guidance" "$c"

# FR-008: the parallelism rule stays in CLAUDE.md and is not restated here.
rule_has 'go in one message' && c=0 || c=1
check "rule does not restate CLAUDE.md's parallelism instruction" "$c"

# SC-006: the guidance itself must not be copied into the always-loaded index.
grep -qi 'large amounts of output' "$CLAUDE_MD" 2>/dev/null && c=0 || c=1
check "CLAUDE.md carries a pointer, not a second copy of the guidance" "$c"

# --- R5: cross-agent parity -------------------------------------------------

# Feature 021 retired the deployment map (.codex/README.md) along with the rest
# of the hand-maintained Codex port. The cross-agent question it answered —
# "is the subagent-delegation rule ported to Codex?" — is now answered in the
# root AGENTS.md, which is what Codex actually reads. ADR-0004 records why the
# exclusion still stands: Codex custom agents set defaults rather than
# isolating context from the parent turn.
grep -Fq 'subagent' "$AGENTS_MD" 2>/dev/null && c=1 || c=0
check "root AGENTS.md addresses delegation for Codex" "$c"

# --- Always-loaded size discipline -----------------------------------------

# plan.md holds this to the mid-sized rules, not the largest (live-documentation
# is ~9.0 KB). A generous ceiling: exceeding it means the rule drifted into
# documenting the feature rather than stating the decision.
if [ -f "$RULE" ]; then
  size=$(wc -c <"$RULE")
  [ "$size" -le 7000 ] && c=1 || c=0
else
  c=0
fi
check "rule stays within the always-loaded size budget (<= 7000 bytes)" "$c"

echo
if [ "$FAIL" -eq 0 ]; then
  printf "${GREEN}All %d checks passed.${NC}\n" "$PASS"
  exit 0
else
  printf "${RED}%d passed, %d failed:${NC}" "$PASS" "$FAIL"
  printf "%b\n" "$FAIL_NAMES"
  exit 1
fi
