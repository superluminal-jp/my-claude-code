#!/usr/bin/env bash
# Codex CLI PreToolUse adapter (matcher: apply_patch|Edit|Write) for the
# shared pre-edit guardrail (Q9/Q10). Translates
# scripts/guardrails/pre-edit-block.sh's tool-agnostic decision into Codex
# CLI's PreToolUse response shape.
#
# Live verification on 2026-07-20 confirmed the current command-hook contract:
# exit 0 with no output allows and exit 2 with stderr blocks. The older
# hookSpecificOutput/continue JSON shape is rejected by PreToolUse.
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

if [ ! -x "$SHARED" ]; then
  exit 0
fi

HOOK_INPUT="$(cat 2>/dev/null || true)"
TOOL_NAME=$(echo "$HOOK_INPUT" | jq -r '.tool_name // empty' 2>/dev/null || echo "")
FILE_PATH=$(echo "$HOOK_INPUT" | jq -r '.tool_input.path // .tool_input.file_path // empty' 2>/dev/null || echo "")
PROJECT_DIR=$(echo "$HOOK_INPUT" | jq -r '.cwd // empty' 2>/dev/null || echo "")

RESULT=$(jq -n --arg tool_name "$TOOL_NAME" --arg path "$FILE_PATH" --arg project_dir "$PROJECT_DIR" \
  '{tool_name:$tool_name, path:$path, project_dir:$project_dir}' | bash "$SHARED" 2>/dev/null) || {
  echo "Pre-edit guardrail script failed; blocking as a precaution." >&2
  exit 2
}

DECISION=$(echo "$RESULT" | jq -r '.decision // empty')
REASON=$(echo "$RESULT" | jq -r '.reason // empty')

case "$DECISION" in
deny)
  echo "$REASON" >&2
  exit 2
  ;;
allow | "")
  exit 0
  ;;
*)
  echo "Pre-edit guardrail returned an unrecognized decision; blocking as a precaution." >&2
  exit 2
  ;;
esac
