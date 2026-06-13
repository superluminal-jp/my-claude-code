#!/usr/bin/env bash
# statusLine: render "<model> | <dir> | <git-branch>" for the Claude Code TUI.
#
# Receives a JSON status payload on stdin; every field is optional, so each
# lookup falls back gracefully. Read-only and never fatal: a failure here must
# not disrupt the session, so unresolved fields degrade to sensible defaults.

set -uo pipefail

input="$(cat 2>/dev/null || true)"

field() { printf '%s' "$input" | jq -r "$1 // empty" 2>/dev/null || true; }

model="$(field '.model.display_name')"
[ -z "$model" ] && model="$(field '.model.id')"
[ -z "$model" ] && model="claude"

dir="$(field '.workspace.current_dir')"
[ -z "$dir" ] && dir="$(field '.cwd')"
[ -z "$dir" ] && dir="$PWD"

branch=""
if command -v git >/dev/null 2>&1; then
  branch="$(git -C "$dir" branch --show-current 2>/dev/null || true)"
fi

out="$model | $(basename "$dir")"
[ -n "$branch" ] && out="$out | $branch"
printf '%s' "$out"
