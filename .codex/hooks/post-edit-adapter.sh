#!/usr/bin/env bash
# Codex CLI PostToolUse adapter (matcher: apply_patch|Edit|Write) for the
# shared post-edit format/lint guardrail (Q7). Translates
# scripts/guardrails/post-edit-format.sh's output into Codex CLI's
# PostToolUse response shape.
#
# NOTE (research.md R1, FR-022): Codex CLI's exact PostToolUse coverage and
# response schema were confirmed via secondary documentation, not a live
# session — this adapter has not yet been re-verified against a real Codex CLI.
#
# Input (Codex CLI PostToolUse): JSON on stdin with .tool_input.path.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -x "$SCRIPT_DIR/../../scripts/guardrails/post-edit-format.sh" ]; then
  SHARED="$SCRIPT_DIR/../../scripts/guardrails/post-edit-format.sh"
else
  SHARED="$HOME/.claude/scripts/guardrails/post-edit-format.sh"
fi

if [ ! -x "$SHARED" ]; then
  jq -n '{continue:true}'
  exit 0
fi

HOOK_INPUT="$(cat 2>/dev/null || true)"
FILE_PATH=$(echo "$HOOK_INPUT" | jq -r '.tool_input.path // .tool_input.file_path // empty' 2>/dev/null || echo "")

[ -z "$FILE_PATH" ] && {
  jq -n '{continue:true}'
  exit 0
}

RESULT=$(jq -n --arg path "$FILE_PATH" '{path:$path}' | bash "$SHARED" 2>/dev/null) || RESULT=""

if [ -n "$RESULT" ]; then
  echo "$RESULT" | jq '{continue: true, systemMessage: (.warnings | join("; "))}' 2>/dev/null || jq -n '{continue:true}'
else
  jq -n '{continue:true}'
fi
