#!/usr/bin/env bash
# Behavior test for the Apple Notes / Reminders operator artifacts.
#
# Verifies the skill+subagent pairing decided in
# docs/adr/0004-distribute-apple-operator-subagents.md:
#   - .claude/skills/apple-{notes,reminders}/  — the standing conventions and
#     the scripts, usable on their own (Codex CLI has no subagent concept).
#   - .claude/agents/apple-{notes,reminders}-operator.md — workers that preload
#     those skills and whose tool allowlist makes "does not modify repository
#     files" a property of the environment rather than an instruction.
#   - the wiring: install.sh distributes both, scrum-master delegates to both,
#     and the always-loaded routing table stays untouched.
#
# Deterministic: inspects repository files only. No network, no `claude` CLI,
# and no macOS -- nothing here executes osascript.
# Usage: bash tests/run-apple-operators.sh

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS="$REPO_ROOT/.claude/skills"
AGENTS="$REPO_ROOT/.claude/agents"
INSTALLER="$REPO_ROOT/install.sh"
SCRUM_MASTER="$SKILLS/scrum-master/SKILL.md"

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

# --- The two skills ---------------------------------------------------------

for app in notes reminders; do
  SKILL="$SKILLS/apple-$app/SKILL.md"

  [ -f "$SKILL" ] && c=1 || c=0
  check "apple-$app skill exists" "$c"

  FM=$(frontmatter "$SKILL")

  echo "$FM" | grep -Eq "^name: *apple-$app *$" && c=1 || c=0
  check "apple-$app skill declares its name" "$c"

  echo "$FM" | grep -Eq '^description: *[^ ]' && c=1 || c=0
  check "apple-$app skill declares a description" "$c"

  # A skill with disable-model-invocation cannot be preloaded into a subagent,
  # which would silently break the `skills:` wiring below.
  echo "$FM" | grep -Eq '^disable-model-invocation: *true' && c=0 || c=1
  check "apple-$app skill stays preloadable (no disable-model-invocation)" "$c"

  # Scripts must resolve at either install scope; a bare relative path breaks
  # once the skill is synced to ~/.claude/skills.
  grep -q 'CLAUDE_SKILL_DIR' "$SKILL" 2>/dev/null && c=1 || c=0
  check "apple-$app skill addresses its scripts by CLAUDE_SKILL_DIR" "$c"

  # Both permission layers fail differently and neither is grantable headlessly.
  grep -qi 'Automation' "$SKILL" 2>/dev/null && c=1 || c=0
  check "apple-$app skill documents the Automation (TCC) grant" "$c"

  # The write paths refuse destructive operations by construction; the skill
  # has to say so, or a reader will route around them with inline AppleScript
  # or their own EventKit code. The two skills word it differently because
  # their backends differ ("cannot delete" vs "no delete command").
  grep -Eqi 'cannot delete|no delete command' "$SKILL" 2>/dev/null && c=1 || c=0
  check "apple-$app skill states that deletion is unavailable" "$c"

  grep -q '## Sources' "$SKILL" 2>/dev/null && c=1 || c=0
  check "apple-$app skill cites its sources" "$c"
done

# --- Scripts ----------------------------------------------------------------

for script in main.swift Info.plist build.sh scrum_block.py; do
  [ -f "$SKILLS/apple-reminders/scripts/$script" ] && c=1 || c=0
  check "apple-reminders ships $script" "$c"
done

# The JXA layer for Reminders was superseded by EventKit; leaving it would give
# two ways to do the same thing and no statement of which is current.
ls "$SKILLS/apple-reminders/scripts/"*.js >/dev/null 2>&1 && c=0 || c=1
check "the superseded JXA Reminders scripts are gone" "$c"

# TCC reads the usage description out of the running binary. Without the
# section, no permission dialog can appear and every call fails as a denial
# the user has no way to reverse -- a build defect that mimics a user choice.
grep -q 'sectcreate' "$SKILLS/apple-reminders/scripts/build.sh" 2>/dev/null &&
  grep -q '__info_plist' "$SKILLS/apple-reminders/scripts/build.sh" 2>/dev/null && c=1 || c=0
check "build.sh links Info.plist into the binary so TCC can prompt" "$c"

grep -q 'NSRemindersFullAccessUsageDescription' \
  "$SKILLS/apple-reminders/scripts/Info.plist" 2>/dev/null && c=1 || c=0
check "Info.plist carries the macOS 14+ Reminders usage description" "$c"

# macOS 14 split Reminders access into full and write-only; this tool reads.
grep -q 'requestFullAccessToReminders' \
  "$SKILLS/apple-reminders/scripts/main.swift" 2>/dev/null && c=1 || c=0
check "main.swift requests full (not write-only) Reminders access" "$c"

# No package manifest, no lockfile: the build is one compiler call.
ls "$SKILLS/apple-reminders/scripts/Package.swift" \
  "$SKILLS/apple-reminders/scripts/"*.lock >/dev/null 2>&1 && c=0 || c=1
check "the EventKit build introduces no package manifest or lockfile" "$c"

# A compiled binary must not reach a diff.
grep -q 'apple-reminders/scripts/remind-cli' "$REPO_ROOT/.gitignore" 2>/dev/null && c=1 || c=0
check "the built remind-cli binary is gitignored" "$c"

# Both identifiers are emitted: local ids do not survive an account move, and
# link markers need the server-provided one.
for field in calendarItemIdentifier calendarItemExternalIdentifier; do
  grep -q "$field" "$SKILLS/apple-reminders/scripts/main.swift" 2>/dev/null && c=1 || c=0
  check "main.swift exposes $field" "$c"
done

for script in list_notes.js write_note.js; do
  [ -f "$SKILLS/apple-notes/scripts/$script" ] && c=1 || c=0
  check "apple-notes ships $script" "$c"
done

# The parsing layer is Python precisely so it can be tested off macOS.
python3 -c "
import importlib.util, sys
spec = importlib.util.spec_from_file_location('sb', '$SKILLS/apple-reminders/scripts/scrum_block.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
sys.exit(0 if m.parse_block('--- scrum ---\nsprint: 7\n---')[0] == {'sprint': '7'} else 1)
" >/dev/null 2>&1 && c=1 || c=0
check "scrum_block.py imports and parses a block" "$c"

# ADR 0001's whole premise: flow_metrics.py runs over Reminders data unforked.
CSV_HEADER=$(echo '[]' | python3 "$SKILLS/apple-reminders/scripts/scrum_block.py" csv 2>/dev/null)
FLOW_HEADER=$(grep -o 'item_id,started_at,completed_at' \
  "$SKILLS/scrum-master/scripts/flow_metrics.py" | head -1)
[ -n "$FLOW_HEADER" ] && [ "$CSV_HEADER" = "$FLOW_HEADER" ] && c=1 || c=0
check "scrum_block.py csv header matches what flow_metrics.py documents" "$c"

# ADR 0001 makes detecting items with no recorded start a required capability.
python3 "$SKILLS/apple-reminders/scripts/scrum_block.py" unstarted --help >/dev/null 2>&1 && c=1 || c=0
check "scrum_block.py exposes the unstarted-item detection" "$c"

# The write paths must not carry a deletion capability at all. Comment lines
# are stripped first: both files discuss deletion at length in order to explain
# why they refuse it, and matching that prose would assert the opposite of the
# code.
code_only() { grep -vE '^\s*//' "$1" 2>/dev/null; }

# EventKit deletes via EKEventStore.remove(_:commit:).
code_only "$SKILLS/apple-reminders/scripts/main.swift" |
  grep -Eq '\.remove\s*\(|\bremoveReminder|EKSpan' && c=0 || c=1
check "main.swift contains no deletion path" "$c"

code_only "$SKILLS/apple-reminders/scripts/main.swift" |
  grep -Eq '"delete"' && c=0 || c=1
check "remind-cli exposes no delete command" "$c"

code_only "$SKILLS/apple-notes/scripts/write_note.js" |
  grep -Eq '\.delete\s*\(|\bdelete\s*\(|\bremove\s*\(' && c=0 || c=1
check "write_note.js contains no deletion path" "$c"

# The same for whole-body replacement in Notes: every assignment to an existing
# note's body must build on its current contents, so append is the only path.
BODY_WRITES=$(code_only "$SKILLS/apple-notes/scripts/write_note.js" | grep -E 'note\.body\s*=')
[ -n "$BODY_WRITES" ] &&
  ! printf '%s\n' "$BODY_WRITES" | grep -qv 'note\.body()' && c=1 || c=0
check "write_note.js only appends, never replaces a body" "$c"

# A note body is HTML: unescaped user text would swallow the rest of the note.
grep -q 'escapeHtml' "$SKILLS/apple-notes/scripts/write_note.js" 2>/dev/null && c=1 || c=0
check "write_note.js escapes text before it enters the HTML body" "$c"

# --- The two operator subagents ---------------------------------------------

for app in notes reminders; do
  AGENT="$AGENTS/apple-$app-operator.md"

  [ -f "$AGENT" ] && c=1 || c=0
  check "apple-$app-operator subagent is defined" "$c"

  FM=$(frontmatter "$AGENT")

  echo "$FM" | grep -Eq "^name: *apple-$app-operator *$" && c=1 || c=0
  check "apple-$app-operator declares its name" "$c"

  echo "$FM" | grep -Eq '^description: *[^ ]' && c=1 || c=0
  check "apple-$app-operator declares a description so Claude can delegate" "$c"

  # The pairing decided in ADR 0004: the skill carries the conventions, the
  # subagent preloads them. Without this the subagent starts cold and blind.
  echo "$FM" | grep -A3 '^skills:' | grep -Eq "^ *- *apple-$app *$" && c=1 || c=0
  check "apple-$app-operator preloads the apple-$app skill" "$c"

  TOOLS=$(echo "$FM" | grep -E '^tools:' || true)
  [ -n "$TOOLS" ] && c=1 || c=0
  check "apple-$app-operator restricts tools via an allowlist" "$c"

  echo "$TOOLS" | grep -q 'Bash' && c=1 || c=0
  check "apple-$app-operator may run Bash (osascript needs it)" "$c"

  # "Changes Reminders/Notes, never the repository" must be structural.
  echo "$TOOLS" | grep -Eq '\bEdit\b' && c=0 || c=1
  check "apple-$app-operator cannot Edit repository files" "$c"

  echo "$TOOLS" | grep -Eq '\bWrite\b' && c=0 || c=1
  check "apple-$app-operator cannot Write repository files" "$c"

  # A subagent has no AskUserQuestion, so ambiguity must stop it, not be guessed.
  grep -qi 'cannot ask' "$AGENT" 2>/dev/null && c=1 || c=0
  check "apple-$app-operator states it cannot ask and must not guess" "$c"

  # Compression is the reason it exists.
  grep -Eqi 'never paste|not the transcript' "$AGENT" 2>/dev/null && c=1 || c=0
  check "apple-$app-operator is told to return the answer, not the dump" "$c"

  grep -qi 'delete' "$AGENT" 2>/dev/null && c=1 || c=0
  check "apple-$app-operator carries the no-delete rule" "$c"
done

# --- Distribution (ADR 0004) ------------------------------------------------

grep -q 'MANAGED_AGENTS' "$INSTALLER" 2>/dev/null && c=1 || c=0
check "install.sh distributes subagents by an explicit name list" "$c"

for agent in apple-notes-operator apple-reminders-operator; do
  grep -q "$agent" "$INSTALLER" 2>/dev/null && c=1 || c=0
  check "install.sh distributes $agent" "$c"
done

# verification-runner drives this repo's own tests/run-*.sh; shipping it
# user-scope would offer it in projects where those files do not exist.
grep -E '^MANAGED_AGENTS=' "$INSTALLER" | grep -q 'verification-runner' && c=0 || c=1
check "install.sh keeps verification-runner project-scoped" "$c"

# sync_path() rm -rf's its target; ~/.claude/agents/ holds the user's own work.
grep -Eq '^\s*sync_path "agents"' "$INSTALLER" && c=0 || c=1
check "install.sh does not wholesale-replace ~/.claude/agents" "$c"

for skill in apple-notes apple-reminders; do
  grep -E '^CUSTOM_SKILLS=' "$INSTALLER" | grep -q "$skill" && c=1 || c=0
  check "install.sh symlinks $skill for Codex CLI" "$c"
done

# --- The scrum-master wiring ------------------------------------------------

for agent in apple-notes-operator apple-reminders-operator; do
  grep -q "$agent" "$SCRUM_MASTER" 2>/dev/null && c=1 || c=0
  check "scrum-master delegates to $agent" "$c"
done

# Delegation is for data access only; the inspection stays in the skill.
grep -q '判断は委譲しない' "$SCRUM_MASTER" 2>/dev/null && c=1 || c=0
check "scrum-master delegates data access but not judgement" "$c"

# Items with no recorded start fall out of Cycle Time; reporting a median
# without saying so is exactly the transparency failure the skill exists to name.
grep -q '着手記録のない項目' "$SCRUM_MASTER" 2>/dev/null && c=1 || c=0
check "scrum-master requires reporting items missing from the flow data" "$c"

# --- The always-loaded routing table stays clean (ADR 0004) -----------------

grep -Eq 'apple-(notes|reminders)' "$REPO_ROOT/.claude/CLAUDE.md" && c=0 || c=1
check "the always-loaded skill list is not widened" "$c"

grep -Eq 'apple-(notes|reminders)' "$REPO_ROOT/.claude/rules/skill-routing.md" && c=0 || c=1
check "the routing rule is not widened" "$c"

# Regression guard for 874475b, which deliberately removed solo/personal
# auto-routing from scrum-master. Its frontmatter must not creep back.
frontmatter "$SCRUM_MASTER" | grep -Eqi 'solo|personal|個人' && c=0 || c=1
check "scrum-master routing still excludes solo/personal Scrum" "$c"

# --- No hook can see an Apple Event; the rule has to be self-applied ---------

grep -qi 'osascript' "$REPO_ROOT/.claude/rules/permissions.md" && c=1 || c=0
check "permissions.md covers destructive osascript use" "$c"

echo
if [ "$FAIL" -eq 0 ]; then
  printf "${GREEN}All %d checks passed.${NC}\n" "$PASS"
  exit 0
else
  printf "${RED}%d passed, %d failed:${NC}" "$PASS" "$FAIL"
  printf "%b\n" "$FAIL_NAMES"
  exit 1
fi
