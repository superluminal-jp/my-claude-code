#!/usr/bin/env bash
# UserPromptExpansion: before /speckit-* expands, upgrade specify-cli and refresh Spec Kit project files.
# This keeps extensions (including git extension hooks) in sync before each lifecycle command.
# Requires .specify/ in cwd (spec-kit project). Safe for specs/: those dirs are never touched by specify init.
# Integration: override with SPECIFY_INTEGRATION (default: claude). See spec-kit integrations list.

set -uo pipefail

INPUT=$(cat)
CWD=$(echo "$INPUT" | jq -r '.cwd // empty')
COMMAND_NAME=$(echo "$INPUT" | jq -r '.command_name // empty')

case "$COMMAND_NAME" in
  speckit.specify|speckit.clarify|speckit.plan|speckit.tasks|speckit.implement|speckit.checklist|speckit.analyze|speckit.taskstoissues|speckit.constitution) ;;
  *)
    exit 0
    ;;
esac

if [ -z "$CWD" ] || [ ! -d "$CWD" ]; then
  exit 0
fi

INTEGRATION="${SPECIFY_INTEGRATION:-claude}"
UPDATE_INTERVAL_SECONDS="${SPECIFY_AUTO_UPDATE_INTERVAL_SECONDS:-86400}"
FORCE_UPDATE="${SPECIFY_FORCE_AUTO_UPDATE:-0}"
STATE_FILE="$CWD/.specify/.last-auto-update"
LOG=$(mktemp)
trap 'rm -f "$LOG"' EXIT

if [ ! -d "$CWD/.specify" ]; then
  jq -n \
    --arg msg "Spec Kit auto-update skipped: no .specify directory under this workspace. Not a spec-kit project or init not run here." \
    '{hookSpecificOutput: {hookEventName: "UserPromptExpansion", additionalContext: $msg}}'
  exit 0
fi

{
  echo "=== Spec Kit auto-update (before /$COMMAND_NAME) ==="
  echo "cwd=$CWD integration=$INTEGRATION"
  echo "update_interval_seconds=$UPDATE_INTERVAL_SECONDS force_update=$FORCE_UPDATE"
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

  now_epoch=$(date +%s)
  last_update=0
  if [ -f "$STATE_FILE" ]; then
    last_update=$(cat "$STATE_FILE" 2>/dev/null || echo "0")
  fi

  should_run_init=1
  if [ "$FORCE_UPDATE" != "1" ] && [ "$UPDATE_INTERVAL_SECONDS" -gt 0 ] 2>/dev/null; then
    elapsed=$((now_epoch - last_update))
    if [ "$elapsed" -lt "$UPDATE_INTERVAL_SECONDS" ]; then
      should_run_init=0
      echo "SKIP: specify init throttled (elapsed=${elapsed}s < interval=${UPDATE_INTERVAL_SECONDS}s)"
    fi
  fi

  if [ "$should_run_init" -eq 1 ]; then
    echo "--- specify init --here --force ---"
    if command -v specify >/dev/null 2>&1; then
      (cd "$CWD" && specify init --here --force --integration "$INTEGRATION")
      init_exit=$?
      echo "specify init exit: $init_exit"
    elif command -v uv >/dev/null 2>&1; then
      (cd "$CWD" && uvx --from git+https://github.com/github/spec-kit.git specify init --here --force --integration "$INTEGRATION")
      init_exit=$?
      echo "uvx specify init exit: $init_exit"
    else
      init_exit=127
      echo "SKIP: specify not in PATH and uv missing for uvx fallback."
    fi

    if [ "${init_exit:-1}" -eq 0 ]; then
      printf '%s\n' "$now_epoch" > "$STATE_FILE"
      echo "Updated state file: $STATE_FILE"
    fi
  else
    echo "State file unchanged: $STATE_FILE"
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
