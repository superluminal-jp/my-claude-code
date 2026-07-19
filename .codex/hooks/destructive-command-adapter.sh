#!/usr/bin/env bash
# Codex CLI PreToolUse adapter (matcher: Bash) for the shared destructive-
# command guardrail (Q6). Translates scripts/guardrails/destructive-command.sh's
# tool-agnostic decision into Codex CLI's PreToolUse response shape.
#
# NOTE (research.md R1, Medium confidence): Codex CLI's exact PreToolUse
# response schema was confirmed via secondary documentation, not a live
# session (spec FR-010) — this adapter has not yet been re-verified against
# a real Codex CLI. In particular, only "deny" is documented for
# permissionDecision; a three-way "ask" is not confirmed, so per FR-008 this
# adapter maps the shared script's "ask" to "deny" (fail closed).
#
# Input (Codex CLI PreToolUse, matcher Bash): JSON on stdin with at least
# .tool_input.command. Output: JSON with hookSpecificOutput.permissionDecision.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# The shared script lives at $HOME/.claude/scripts/guardrails once installed
# (a single global copy consumed by both Claude Code's hooks and this Codex
# CLI adapter — not duplicated per tool). Fall back to the repo-relative path
# for running this adapter directly from a working-tree checkout.
if [ -x "$SCRIPT_DIR/../../scripts/guardrails/destructive-command.sh" ]; then
  SHARED="$SCRIPT_DIR/../../scripts/guardrails/destructive-command.sh"
else
  SHARED="$HOME/.claude/scripts/guardrails/destructive-command.sh"
fi

deny_response() {
  jq -n --arg reason "$1" '{
    continue: true,
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: $reason
    }
  }'
}

allow_response() {
  jq -n '{
    continue: true,
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "allow"
    }
  }'
}

if [ ! -x "$SHARED" ]; then
  allow_response
  exit 0
fi

COMMAND=$(jq -r '.tool_input.command // empty' 2>/dev/null || echo "")

RESULT=$(jq -n --arg command "$COMMAND" '{command:$command}' | bash "$SHARED" 2>/dev/null) || {
  deny_response "Destructive-command guardrail script failed; blocking as a precaution."
  exit 0
}

DECISION=$(echo "$RESULT" | jq -r '.decision // empty')
REASON=$(echo "$RESULT" | jq -r '.reason // empty')

case "$DECISION" in
deny)
  deny_response "$REASON"
  ;;
ask)
  # No confirmed three-way primitive in Codex CLI's PreToolUse (FR-008): fail closed.
  deny_response "${REASON:-Requires explicit user approval; Codex CLI has no confirmed confirmation primitive, so this is blocked.}"
  ;;
allow | "")
  allow_response
  ;;
*)
  deny_response "Destructive-command guardrail returned an unrecognized decision; blocking as a precaution."
  ;;
esac
