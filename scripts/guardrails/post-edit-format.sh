#!/usr/bin/env bash
# Shared post-edit format/lint guardrail (Q7). Tool-agnostic: reads
# {"path": "..."} on stdin, writes {"warnings": [...]} on stdout. Never
# blocks (no "decision" field — this is automation, not a gate). Exit 0
# always, unless the script itself errors (caller treats that the same as a
# script error per contracts/guardrail-script-io.md, though nothing here
# should ever cause a caller to deny an action).
#
# Extracted from .claude/hooks/post-edit-format.sh — logic kept verbatim for
# .sh/.yaml/.yml/.json (FR-021). The */CLAUDE.md @import check is
# Claude Code-specific (Codex CLI has no CLAUDE.md) and stays in the Claude
# Code wrapper, not here — same treatment as Q1's warnings in pre-edit.sh.

set -euo pipefail

WARNINGS=()

FILE_PATH=$(jq -r '.path // empty' 2>/dev/null || echo "")

emit() {
  printf '%s\n' "${WARNINGS[@]:-}" | jq -R . | jq -s '{warnings: map(select(length > 0))}'
}

if [ -z "$FILE_PATH" ] || [ ! -f "$FILE_PATH" ]; then
  emit
  exit 0
fi

case "$FILE_PATH" in
*.json)
  if command -v jq >/dev/null 2>&1; then
    if ! jq empty "$FILE_PATH" 2>/dev/null; then
      WARNINGS+=("JSON syntax error in $FILE_PATH")
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
    SC_OUT=$(shellcheck "$FILE_PATH" 2>&1) || WARNINGS+=("$SC_OUT")
  fi
  ;;
*.yaml | *.yml)
  if command -v yamllint >/dev/null 2>&1; then
    YL_OUT=$(yamllint "$FILE_PATH" 2>&1) || WARNINGS+=("$YL_OUT")
  fi
  ;;
esac

emit
