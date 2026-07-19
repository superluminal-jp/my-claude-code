#!/usr/bin/env bash
# PreToolUse hook: block dangerous Bash commands
# Exit 2 = blocking error (action denied + stderr shown to Claude)
# Exit 0 = allow
#
# Thin wrapper: the actual matching logic lives in scripts/guardrails/
# destructive-command.sh, shared with the Codex CLI adapter at
# .codex/hooks/destructive-command-adapter.sh. See
# specs/013-cross-agent-guardrail-implementation/contracts/guardrail-script-io.md
# for that script's stdin/stdout contract.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Resolve the shared script: prefer the current project's own copy (useful
# when working inside this repo directly, before install.sh has run), then
# the globally-installed copy (deployed by install.sh alongside this hook —
# NOT resolved via CLAUDE_PROJECT_DIR, since once installed this hook runs
# for every project on the machine, most of which aren't this repository),
# then a repo-relative dev fallback for running this script from a plain
# working-tree checkout with neither of the above set up yet.
if [ -n "${CLAUDE_PROJECT_DIR:-}" ] && [ -x "$CLAUDE_PROJECT_DIR/scripts/guardrails/destructive-command.sh" ]; then
  SHARED="$CLAUDE_PROJECT_DIR/scripts/guardrails/destructive-command.sh"
elif [ -x "$HOME/.claude/scripts/guardrails/destructive-command.sh" ]; then
  SHARED="$HOME/.claude/scripts/guardrails/destructive-command.sh"
else
  SHARED="$SCRIPT_DIR/../../scripts/guardrails/destructive-command.sh"
fi

# Fail open if the shared script isn't present (e.g. an older checkout) so a
# missing file never blocks unrelated work; this hook only adds a guardrail,
# it never becomes the reason Bash stops working entirely.
if [ ! -x "$SHARED" ]; then
  exit 0
fi

COMMAND=$(jq -r '.tool_input.command // empty' 2>/dev/null || echo "")

RESULT=$(jq -n --arg command "$COMMAND" '{command:$command}' | bash "$SHARED" 2>/dev/null) || {
  # The shared script itself errored — fail closed, not open.
  echo "Destructive-command guardrail script failed; blocking as a precaution." >&2
  exit 2
}

DECISION=$(echo "$RESULT" | jq -r '.decision // empty')
REASON=$(echo "$RESULT" | jq -r '.reason // empty')

case "$DECISION" in
deny)
  echo "$REASON" >&2
  exit 2
  ;;
ask)
  jq -n --arg reason "$REASON" '{
    continue: true,
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "ask",
      permissionDecisionReason: $reason
    }
  }'
  exit 0
  ;;
allow | "")
  exit 0
  ;;
*)
  # Unrecognized decision — fail closed.
  echo "Destructive-command guardrail returned an unrecognized decision; blocking as a precaution." >&2
  exit 2
  ;;
esac
