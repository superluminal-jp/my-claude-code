#!/usr/bin/env bash
# Codex CLI PreToolUse adapter (matcher: Bash) for the shared destructive-
# command guardrail (Q6). Translates scripts/guardrails/destructive-command.sh's
# tool-agnostic decision into Codex CLI's PreToolUse response shape.
#
# Live verification on 2026-07-20 confirmed the current Codex command-hook
# contract: exit 0 with no output allows; exit 2 with a safe stderr reason
# blocks. The older hookSpecificOutput/continue JSON shape is rejected by
# PreToolUse. The shared script's "ask" therefore maps to exit 2 (fail closed).
#
# Input (Codex CLI PreToolUse, matcher Bash): JSON on stdin with at least
# .tool_input.command.

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

if [ ! -x "$SHARED" ]; then
  exit 0
fi

COMMAND=$(jq -r '.tool_input.command // empty' 2>/dev/null || echo "")

RESULT=$(jq -n --arg command "$COMMAND" '{command:$command}' | bash "$SHARED" 2>/dev/null) || {
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
  echo "${REASON:-Requires explicit user approval; the PreToolUse hook fails closed.}" >&2
  exit 2
  ;;
allow | "")
  exit 0
  ;;
*)
  echo "Destructive-command guardrail returned an unrecognized decision; blocking as a precaution." >&2
  exit 2
  ;;
esac
