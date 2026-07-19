#!/usr/bin/env bash
# PreToolUse hook: validate Edit/Write/Delete operations
# Exit 2 = block (stderr shown to Claude); exit 0 = allow
#
# Thin wrapper: the .git/ and main/master-branch block logic lives in
# scripts/guardrails/pre-edit-block.sh, shared with the Codex CLI adapter at
# .codex/hooks/pre-edit-adapter.sh. See
# specs/013-cross-agent-guardrail-implementation/contracts/guardrail-script-io.md.
# The CI/settings/production-path warnings below are Claude Code-specific
# prose reminders (Q1 — AGENTS.md carries the Codex CLI equivalent) and stay
# here unchanged, since they were never part of the shared script's contract.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# See pre-bash.sh for why this isn't resolved via CLAUDE_PROJECT_DIR alone.
if [ -n "${CLAUDE_PROJECT_DIR:-}" ] && [ -x "$CLAUDE_PROJECT_DIR/scripts/guardrails/pre-edit-block.sh" ]; then
  SHARED="$CLAUDE_PROJECT_DIR/scripts/guardrails/pre-edit-block.sh"
elif [ -x "$HOME/.claude/scripts/guardrails/pre-edit-block.sh" ]; then
  SHARED="$HOME/.claude/scripts/guardrails/pre-edit-block.sh"
else
  SHARED="$SCRIPT_DIR/../../scripts/guardrails/pre-edit-block.sh"
fi

FILE_PATH=""
TOOL_NAME=""
if [ ! -t 0 ]; then
    HOOK_INPUT="$(cat 2>/dev/null || true)"
    if [ -n "$HOOK_INPUT" ] && command -v jq >/dev/null 2>&1; then
        TOOL_NAME="$(echo "$HOOK_INPUT" | jq -r '.tool_name // empty' 2>/dev/null || true)"
        FILE_PATH="$(echo "$HOOK_INPUT" | jq -r '.tool_input.path // .tool_input.file_path // empty' 2>/dev/null || true)"
    fi
fi
[ -z "$TOOL_NAME" ] && TOOL_NAME="${CLAUDE_TOOL_NAME:-}"
[ -z "$FILE_PATH" ] && FILE_PATH="${CLAUDE_TOOL_INPUT_PATH:-}"

if [ -x "$SHARED" ]; then
    RESULT=$(jq -n --arg tool_name "$TOOL_NAME" --arg path "$FILE_PATH" --arg project_dir "${CLAUDE_PROJECT_DIR:-}" \
        '{tool_name:$tool_name, path:$path, project_dir:$project_dir}' | bash "$SHARED" 2>/dev/null) || {
        echo "Pre-edit guardrail script failed; blocking as a precaution." >&2
        exit 2
    }
    DECISION=$(echo "$RESULT" | jq -r '.decision // empty')
    REASON=$(echo "$RESULT" | jq -r '.reason // empty')
    if [ "$DECISION" = "deny" ]; then
        echo "$REASON" >&2
        exit 2
    fi
fi

# Warn for sensitive file paths
if [ -n "$FILE_PATH" ]; then
    case "$FILE_PATH" in
        .github/workflows/*|.gitlab-ci.yml|.circleci/*)
            echo "Warning: editing CI/CD configuration ($FILE_PATH) — test in a feature branch first." >&2
            ;;
        .claude/settings.json|.claude/settings.local.json)
            echo "Warning: editing Claude Code settings ($FILE_PATH) — verify hook paths and permission rules." >&2
            ;;
        *.prod.*|*production.*|*.env.production)
            echo "Warning: editing production configuration ($FILE_PATH) — ensure changes are tested." >&2
            ;;
    esac
fi

exit 0
