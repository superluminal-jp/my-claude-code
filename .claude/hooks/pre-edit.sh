#!/usr/bin/env bash
# PreToolUse hook: validate Edit/Write/Delete operations
# Exit 2 = block (stderr shown to Claude); exit 0 = allow

set -euo pipefail

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

# Block direct edits to .git internals
if [ -n "$FILE_PATH" ] && echo "$FILE_PATH" | grep -qE '(^|/)\.git/'; then
    echo "Direct modification of .git/ is not allowed." >&2
    exit 2
fi

# Block edits on main/master (only when project dir is known to avoid false positives)
if [ -n "${CLAUDE_PROJECT_DIR:-}" ] && [ -d "$CLAUDE_PROJECT_DIR" ]; then
    if (cd "$CLAUDE_PROJECT_DIR" && git rev-parse --git-dir >/dev/null 2>&1); then
        CURRENT_BRANCH=$(cd "$CLAUDE_PROJECT_DIR" && git branch --show-current 2>/dev/null || echo "")
        if [ "$CURRENT_BRANCH" = "main" ] || [ "$CURRENT_BRANCH" = "master" ]; then
            echo "Cannot $TOOL_NAME on $CURRENT_BRANCH branch. Create a feature branch first: git checkout -b feature/your-feature" >&2
            exit 2
        fi
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
