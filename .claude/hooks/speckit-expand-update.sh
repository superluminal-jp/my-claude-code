#!/usr/bin/env bash
# UserPromptExpansion: before /speckit.specify expands, upgrade specify-cli and refresh Spec Kit project files.
# Requires .specify/ in cwd (spec-kit project). Safe for specs/: those dirs are never touched by specify init.
# Integration: override with SPECIFY_INTEGRATION (default: claude). See spec-kit integrations list.

set -uo pipefail

INPUT=$(cat)
CWD=$(echo "$INPUT" | jq -r '.cwd // empty')
COMMAND_NAME=$(echo "$INPUT" | jq -r '.command_name // empty')

case "$COMMAND_NAME" in
  speckit.specify) ;;
  *)
    exit 0
    ;;
esac

if [ -z "$CWD" ] || [ ! -d "$CWD" ]; then
  exit 0
fi

INTEGRATION="${SPECIFY_INTEGRATION:-claude}"
LOG=$(mktemp)
trap 'rm -f "$LOG"' EXIT

if [ ! -d "$CWD/.specify" ]; then
  jq -n \
    --arg msg "Spec Kit auto-update skipped: no .specify directory under this workspace. Not a spec-kit project or init not run here." \
    '{hookSpecificOutput: {hookEventName: "UserPromptExpansion", additionalContext: $msg}}'
  exit 0
fi

{
  echo "=== Spec Kit auto-update (before /speckit.specify) ==="
  echo "cwd=$CWD integration=$INTEGRATION"
  set +e
  if command -v uv >/dev/null 2>&1; then
    echo "--- uv tool install specify-cli ---"
    uv tool install specify-cli --force --from git+https://github.com/github/spec-kit.git
    echo "uv tool install exit: $?"
  elif command -v pipx >/dev/null 2>&1; then
    echo "--- pipx install specify-cli ---"
    pipx install --force git+https://github.com/github/spec-kit.git
    echo "pipx install exit: $?"
  else
    echo "SKIP: neither uv nor pipx in PATH; CLI not upgraded."
  fi

  echo "--- specify init --here --force ---"
  if command -v specify >/dev/null 2>&1; then
    (cd "$CWD" && specify init --here --force --integration "$INTEGRATION")
    echo "specify init exit: $?"
  elif command -v uv >/dev/null 2>&1; then
    (cd "$CWD" && uvx --from git+https://github.com/github/spec-kit.git specify init --here --force --integration "$INTEGRATION")
    echo "uvx specify init exit: $?"
  else
    echo "SKIP: specify not in PATH and uv missing for uvx fallback."
  fi
} >>"$LOG" 2>&1 || true

NOTE=$'\n\nNote: specify init --here --force may replace the default template for .specify/memory/constitution.md. Restore from git if you customized it (see Spec Kit upgrade guide).'

BODY=$(jq -n \
  --rawfile log "$LOG" \
  --arg note "$NOTE" \
  --arg hook "UserPromptExpansion" \
  '($log | if length > 8800 then .[0:8800] + "\n...(truncated)\n" else . end) as $text |
  {
    hookSpecificOutput: {
      hookEventName: $hook,
      additionalContext: ("Spec Kit auto-update output:\n\n" + $text + $note)
    }
  }')

echo "$BODY"
exit 0
