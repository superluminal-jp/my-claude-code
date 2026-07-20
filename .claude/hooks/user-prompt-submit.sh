#!/usr/bin/env bash
# UserPromptSubmit hook: block prompts containing obvious secrets.
# Thin wrapper around scripts/guardrails/prompt-secret-scan.sh, shared with
# Codex's UserPromptSubmit adapter.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -n "${CLAUDE_PROJECT_DIR:-}" ] && [ -x "$CLAUDE_PROJECT_DIR/scripts/guardrails/prompt-secret-scan.sh" ]; then
  SHARED="$CLAUDE_PROJECT_DIR/scripts/guardrails/prompt-secret-scan.sh"
elif [ -x "$HOME/.claude/scripts/guardrails/prompt-secret-scan.sh" ]; then
  SHARED="$HOME/.claude/scripts/guardrails/prompt-secret-scan.sh"
else
  SHARED="$SCRIPT_DIR/../../scripts/guardrails/prompt-secret-scan.sh"
fi

# Match the established wrappers: a missing optional guardrail must not break
# all prompts, while an installed scanner that errors fails closed.
if [ ! -x "$SHARED" ]; then
  exit 0
fi

HOOK_INPUT="$(cat 2>/dev/null || true)"
RESULT=$(printf '%s' "$HOOK_INPUT" | bash "$SHARED" 2>/dev/null) || {
  echo "Prompt-secret guardrail script failed; blocking as a precaution." >&2
  exit 2
}

DECISION=$(printf '%s' "$RESULT" | jq -r '.decision // empty')
REASON=$(printf '%s' "$RESULT" | jq -r '.reason // empty')

case "$DECISION" in
deny)
  echo "$REASON" >&2
  exit 2
  ;;
allow | "")
  exit 0
  ;;
*)
  echo "Prompt-secret guardrail returned an unrecognized decision; blocking as a precaution." >&2
  exit 2
  ;;
esac
