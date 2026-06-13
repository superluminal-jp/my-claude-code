#!/usr/bin/env bash
# PostToolUse hook: format and lint edited files
# Silently formats; writes warnings to stderr on errors

set -euo pipefail

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

case "$FILE_PATH" in
    *.json)
        if command -v jq >/dev/null 2>&1; then
            if ! jq empty "$FILE_PATH" 2>/dev/null; then
                echo "Warning: JSON syntax error in $FILE_PATH" >&2
            fi
        fi
        ;;
    *.sh)
        if command -v shfmt >/dev/null 2>&1; then
            # Pin 2-space indent to match repo scripts; shfmt defaults to tabs,
            # which would reformat every space-indented script on next edit.
            shfmt -w -i 2 "$FILE_PATH" 2>/dev/null || true
        fi
        if command -v shellcheck >/dev/null 2>&1; then
            shellcheck "$FILE_PATH" || true
        fi
        ;;
    *.yaml|*.yml)
        if command -v yamllint >/dev/null 2>&1; then
            yamllint "$FILE_PATH" 2>/dev/null || true
        fi
        ;;
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
