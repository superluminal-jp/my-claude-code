#!/usr/bin/env bash
# Behavior test for the isolated verification artifacts (specs/019-verify-fork-test-runner).
#
# Verifies the two artifacts that keep high-volume verification output out of
# the main conversation:
#   - .claude/agents/verification-runner.md — a read-only subagent whose tool
#     allowlist makes "does not modify files" (FR-003, FR-007) a property of the
#     execution environment rather than an instruction.
#   - .claude/skills/verify-config/SKILL.md — the configuration check, forked
#     into that subagent (FR-001) while keeping its checklist contract (FR-002).
#
# Deterministic: inspects repository files only. No network, no `claude` CLI.
# Usage: bash tests/run-verification-agent.sh

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AGENT="$REPO_ROOT/.claude/agents/verification-runner.md"
SKILL="$REPO_ROOT/.claude/skills/verify-config/SKILL.md"
OLD_COMMAND="$REPO_ROOT/.claude/commands/verify-config.md"

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

# Extracts the YAML frontmatter block (between the first two `---` lines).
frontmatter() {
  local file="$1"
  [ -f "$file" ] || return 0
  awk 'NR==1 && $0=="---"{inside=1; next} inside && $0=="---"{exit} inside' "$file"
}

# --- The read-only verification subagent -----------------------------------

[ -f "$AGENT" ] && c=1 || c=0
check "verification-runner subagent is defined" "$c"

AGENT_FM=$(frontmatter "$AGENT")

echo "$AGENT_FM" | grep -Eq '^name: *verification-runner *$' && c=1 || c=0
check "subagent declares its name" "$c"

echo "$AGENT_FM" | grep -Eq '^description: *[^ ]' && c=1 || c=0
check "subagent declares a description so Claude can delegate to it" "$c"

# The tools field is an allowlist. Bash is required to run the checks; Read,
# Grep and Glob to inspect the repository and resolve @-imports.
AGENT_TOOLS=$(echo "$AGENT_FM" | grep -E '^tools:' || true)
[ -n "$AGENT_TOOLS" ] && c=1 || c=0
check "subagent restricts tools via an allowlist" "$c"

echo "$AGENT_TOOLS" | grep -q 'Bash' && c=1 || c=0
check "subagent may run Bash (required by every verification step)" "$c"

echo "$AGENT_TOOLS" | grep -q 'Read' && c=1 || c=0
check "subagent may Read (import-integrity check needs it)" "$c"

# FR-003 / FR-007: not modifying files must not rest on instruction text alone.
echo "$AGENT_TOOLS" | grep -Eq '\bEdit\b' && c=0 || c=1
check "subagent cannot Edit (read-only by construction)" "$c"

echo "$AGENT_TOOLS" | grep -Eq '\bWrite\b' && c=0 || c=1
check "subagent cannot Write (read-only by construction)" "$c"

# FR-006: an unavailable prerequisite is a skip, not a failure.
grep -qi 'skip' "$AGENT" 2>/dev/null && c=1 || c=0
check "subagent body states the skip-when-unavailable contract" "$c"

# FR-007: reporting a failure is the job; fixing it is not.
grep -Eqi 'do not (attempt to )?fix|never fix|not fix' "$AGENT" 2>/dev/null && c=1 || c=0
check "subagent body forbids fixing what it finds" "$c"

# --- The forked configuration check ----------------------------------------

[ -f "$SKILL" ] && c=1 || c=0
check "verify-config skill exists at its documented skill path" "$c"

SKILL_FM=$(frontmatter "$SKILL")

echo "$SKILL_FM" | grep -Eq '^name: *verify-config *$' && c=1 || c=0
check "skill declares its name" "$c"

# FR-001: the raw output must not reach the main conversation.
echo "$SKILL_FM" | grep -Eq '^context: *fork *$' && c=1 || c=0
check "skill runs in a forked context" "$c"

# R3/FR-008: a backgrounded fork gets the reduced background tool set.
echo "$SKILL_FM" | grep -Eq '^background: *false *$' && c=1 || c=0
check "skill waits in the invoking turn, keeping the full tool set" "$c"

echo "$SKILL_FM" | grep -Eq '^agent: *verification-runner *$' && c=1 || c=0
check "skill forks into the read-only verification subagent" "$c"

# R6: the pre-approved Bash patterns must survive the move, or the isolated
# run stalls on approval prompts mid-procedure.
SKILL_ALLOWED=$(echo "$SKILL_FM" | grep -E '^allowed-tools:' || true)
for tool in jq shellcheck shfmt yamllint check-mcp-consistency 'tests/run-'; do
  echo "$SKILL_ALLOWED" | grep -q "$tool" && c=1 || c=0
  check "skill pre-approves $tool" "$c"
done

# FR-002 / R7: relocation only — the six checks and the report format stay.
for step in 'settings.json' 'import' 'shellcheck' 'check-mcp-consistency' 'run-skill-routing' 'run-speckit-update'; do
  grep -q "$step" "$SKILL" 2>/dev/null && c=1 || c=0
  check "skill still performs the $step check" "$c"
done

grep -q '✓' "$SKILL" 2>/dev/null && grep -q '✗' "$SKILL" 2>/dev/null && c=1 || c=0
check "skill still reports a ✓/✗ checklist" "$c"

grep -qi 'do not modify\|never write' "$SKILL" 2>/dev/null && c=1 || c=0
check "skill still states it modifies nothing" "$c"

# --- The move leaves nothing stale -----------------------------------------

[ -f "$OLD_COMMAND" ] && c=0 || c=1
check "the superseded command file is gone" "$c"

# SC-004: no document may point at the former location. This script is exempt —
# it names the old path in order to assert the file is gone. specs/ is exempt
# because superseded feature records are historical and stay as written.
STALE=$(grep -rl --exclude-dir=.git --exclude-dir=specs \
  --exclude="$(basename "${BASH_SOURCE[0]}")" \
  'commands/verify-config' "$REPO_ROOT" 2>/dev/null || true)
[ -z "$STALE" ] && c=1 || c=0
check "no document references the former command path" "$c"

echo
if [ "$FAIL" -eq 0 ]; then
  printf "${GREEN}All %d checks passed.${NC}\n" "$PASS"
  exit 0
else
  printf "${RED}%d passed, %d failed:${NC}" "$PASS" "$FAIL"
  printf "%b\n" "$FAIL_NAMES"
  exit 1
fi
