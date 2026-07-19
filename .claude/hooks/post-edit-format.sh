#!/usr/bin/env bash
# PostToolUse hook: format and lint edited files
# Silently formats; writes warnings to stderr on errors
#
# Thin wrapper: the .sh/.yaml/.yml/.json formatting logic lives in
# scripts/guardrails/post-edit-format.sh, shared with the Codex CLI adapter
# at .codex/hooks/post-edit-adapter.sh. See
# specs/013-cross-agent-guardrail-implementation/contracts/guardrail-script-io.md.
# The */CLAUDE.md @import check below is Claude Code-specific and stays
# here unchanged, since Codex CLI has no CLAUDE.md.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# See pre-bash.sh for why this isn't resolved via CLAUDE_PROJECT_DIR alone.
if [ -n "${CLAUDE_PROJECT_DIR:-}" ] && [ -x "$CLAUDE_PROJECT_DIR/scripts/guardrails/post-edit-format.sh" ]; then
    SHARED="$CLAUDE_PROJECT_DIR/scripts/guardrails/post-edit-format.sh"
elif [ -x "$HOME/.claude/scripts/guardrails/post-edit-format.sh" ]; then
    SHARED="$HOME/.claude/scripts/guardrails/post-edit-format.sh"
else
    SHARED="$SCRIPT_DIR/../../scripts/guardrails/post-edit-format.sh"
fi

FILE_PATH=""
if [ ! -t 0 ]; then
    HOOK_INPUT="$(cat 2>/dev/null || true)"
    if [ -n "$HOOK_INPUT" ] && command -v jq >/dev/null 2>&1; then
        FILE_PATH="$(echo "$HOOK_INPUT" | jq -r '.tool_input.path // .tool_input.file_path // empty' 2>/dev/null || true)"
    fi
fi
[ -z "$FILE_PATH" ] && FILE_PATH="${CLAUDE_TOOL_INPUT_PATH:-}"

[ -z "$FILE_PATH" ] && exit 0
[ -f "$FILE_PATH" ] || exit 0

if [ -x "$SHARED" ]; then
    RESULT=$(jq -n --arg path "$FILE_PATH" '{path:$path}' | bash "$SHARED" 2>/dev/null) || RESULT=""
    if [ -n "$RESULT" ]; then
        echo "$RESULT" | jq -r '.warnings[]? // empty' | while IFS= read -r w; do
            [ -n "$w" ] && echo "Warning: $w" >&2
        done
    fi
fi

case "$FILE_PATH" in
    */CLAUDE.md)
        # Fast, offline guard against broken standing context: every @-import
        # must resolve. Paths are written relative to the repo root.
        ROOT="${CLAUDE_PROJECT_DIR:-$(git -C "$(dirname "$FILE_PATH")" rev-parse --show-toplevel 2>/dev/null || true)}"
        if [ -n "$ROOT" ]; then
            while IFS= read -r imp; do
                [ -z "$imp" ] && continue
                [ -f "$ROOT/$imp" ] || echo "Warning: broken @-import in $FILE_PATH: $imp" >&2
            done < <(grep -oE '^@[^[:space:]]+' "$FILE_PATH" 2>/dev/null | sed 's/^@//')
        fi
        ;;
esac

exit 0
