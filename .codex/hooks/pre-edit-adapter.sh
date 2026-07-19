#!/usr/bin/env bash
# Codex CLI PreToolUse adapter (matcher: apply_patch|Edit|Write) for the
# shared pre-edit guardrail (Q9/Q10). Translates
# scripts/guardrails/pre-edit-block.sh's tool-agnostic decision into Codex
# CLI's PreToolUse response shape.
#
# NOTE (research.md R1, FR-022): Codex CLI's exact coverage of apply_patch/
# Edit/Write under PreToolUse was confirmed via secondary documentation, not
# a live session — this adapter has not yet been re-verified against a real
# Codex CLI.
#
# Input (Codex CLI PreToolUse): JSON on stdin with .tool_input.path and .cwd
# (Codex CLI's documented common field for the working directory).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -x "$SCRIPT_DIR/../../scripts/guardrails/pre-edit-block.sh" ]; then
  SHARED="$SCRIPT_DIR/../../scripts/guardrails/pre-edit-block.sh"
else
  SHARED="$HOME/.claude/scripts/guardrails/pre-edit-block.sh"
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

HOOK_INPUT="$(cat 2>/dev/null || true)"
TOOL_NAME=$(echo "$HOOK_INPUT" | jq -r '.tool_name // empty' 2>/dev/null || echo "")
FILE_PATH=$(echo "$HOOK_INPUT" | jq -r '.tool_input.path // .tool_input.file_path // empty' 2>/dev/null || echo "")
PROJECT_DIR=$(echo "$HOOK_INPUT" | jq -r '.cwd // empty' 2>/dev/null || echo "")

RESULT=$(jq -n --arg tool_name "$TOOL_NAME" --arg path "$FILE_PATH" --arg project_dir "$PROJECT_DIR" \
  '{tool_name:$tool_name, path:$path, project_dir:$project_dir}' | bash "$SHARED" 2>/dev/null) || {
  deny_response "Pre-edit guardrail script failed; blocking as a precaution."
  exit 0
}

DECISION=$(echo "$RESULT" | jq -r '.decision // empty')
REASON=$(echo "$RESULT" | jq -r '.reason // empty')

case "$DECISION" in
deny)
  deny_response "$REASON"
  ;;
allow | "")
  allow_response
  ;;
*)
  deny_response "Pre-edit guardrail returned an unrecognized decision; blocking as a precaution."
  ;;
esac
