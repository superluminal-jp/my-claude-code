#!/usr/bin/env bash
# Codex UserPromptSubmit adapter for the shared prompt-secret scanner.
# UserPromptSubmit has no matcher and uses common hook output fields:
# continue=false blocks the prompt and stopReason records the safe reason.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK_INPUT="$(cat 2>/dev/null || true)"
CWD=$(printf '%s' "$HOOK_INPUT" | jq -r '.cwd // empty' 2>/dev/null || true)

if [ -n "$CWD" ] && [ -x "$CWD/scripts/guardrails/prompt-secret-scan.sh" ]; then
  SHARED="$CWD/scripts/guardrails/prompt-secret-scan.sh"
elif [ -x "$HOME/.claude/scripts/guardrails/prompt-secret-scan.sh" ]; then
  SHARED="$HOME/.claude/scripts/guardrails/prompt-secret-scan.sh"
else
  SHARED="$SCRIPT_DIR/../../scripts/guardrails/prompt-secret-scan.sh"
fi

allow_response() {
  jq -n '{continue:true}'
}

deny_response() {
  jq -n --arg reason "$1" '{continue:false, stopReason:$reason}'
}

if [ ! -x "$SHARED" ]; then
  allow_response
  exit 0
fi

RESULT=$(printf '%s' "$HOOK_INPUT" | bash "$SHARED" 2>/dev/null) || {
  deny_response "Prompt-secret guardrail script failed; blocking as a precaution."
  exit 0
}

DECISION=$(printf '%s' "$RESULT" | jq -r '.decision // empty')
REASON=$(printf '%s' "$RESULT" | jq -r '.reason // empty')

case "$DECISION" in
deny)
  deny_response "$REASON"
  ;;
allow | "")
  allow_response
  ;;
*)
  deny_response "Prompt-secret guardrail returned an unrecognized decision; blocking as a precaution."
  ;;
esac
