#!/usr/bin/env bash
# UserPromptExpansion: before /speckit-* expands, upgrade specify-cli and refresh Spec Kit project files.
# speckit-specify always runs specify init (bypasses throttle) and protects modified constitution.md.
# All other commands throttle specify init to once per UPDATE_INTERVAL_SECONDS.
# After a successful init, freshly regenerated speckit-* skills are synced to the
# user-scope install (~/.claude/skills) so imported skills stay current; opt out
# with SPECIFY_SYNC_USER_SKILLS=0.
# Integration: override with SPECIFY_INTEGRATION (default: claude). See spec-kit integrations list.

set -uo pipefail

INPUT=$(cat)
CWD=$(echo "$INPUT" | jq -r '.cwd // empty')
COMMAND_NAME=$(echo "$INPUT" | jq -r '.command_name // empty')

case "$COMMAND_NAME" in
  speckit.specify|speckit.clarify|speckit.plan|speckit.tasks|speckit.implement|speckit.checklist|speckit.analyze|speckit.taskstoissues|speckit.constitution|speckit.converge) ;;
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

  # Resolve latest stable release tag from GitHub. releases/latest excludes drafts
  # and prereleases by definition, so prefer it (curl-only, no gh dependency);
  # fall back to gh with the same exclusions if curl/jq are unavailable.
  LATEST_TAG=""
  if command -v curl >/dev/null 2>&1 && command -v jq >/dev/null 2>&1; then
    LATEST_TAG=$(curl -fsSL "https://api.github.com/repos/github/spec-kit/releases/latest" 2>/dev/null | jq -r '.tag_name // empty' 2>/dev/null || true)
  fi
  if [ -z "$LATEST_TAG" ] && command -v gh >/dev/null 2>&1; then
    LATEST_TAG=$(gh release list --repo github/spec-kit --exclude-drafts --exclude-pre-releases --limit 1 --json tagName --jq '.[0].tagName' 2>/dev/null || true)
  fi
  echo "Latest stable tag: ${LATEST_TAG:-unknown}"

  # Fetch the tagged source as an HTTPS tarball rather than `git+https://...`:
  # some network policies allow plain HTTPS downloads but reject the git
  # smart-HTTP protocol, so this path is more portable for `uv`/`pipx --from`.
  SRC_DIR=""
  if [ -n "$LATEST_TAG" ] && command -v curl >/dev/null 2>&1 && command -v tar >/dev/null 2>&1; then
    TARBALL=$(mktemp)
    if curl -fsSL -o "$TARBALL" "https://codeload.github.com/github/spec-kit/tar.gz/refs/tags/${LATEST_TAG}"; then
      SRC_DIR=$(mktemp -d)
      if tar xzf "$TARBALL" -C "$SRC_DIR" --strip-components=1; then
        echo "Downloaded spec-kit@${LATEST_TAG} tarball to $SRC_DIR"
      else
        rm -rf "$SRC_DIR"
        SRC_DIR=""
        echo "WARN: failed to extract spec-kit@${LATEST_TAG} tarball"
      fi
    else
      echo "WARN: failed to download spec-kit@${LATEST_TAG} tarball"
    fi
    rm -f "$TARBALL"
  fi

  if command -v uv >/dev/null 2>&1; then
    if [ -n "$SRC_DIR" ]; then
      echo "--- uv tool install specify-cli from tarball ($LATEST_TAG) ---"
      uv tool install specify-cli --force --from "$SRC_DIR"
    elif [ -n "$LATEST_TAG" ]; then
      echo "--- uv tool install specify-cli @ $LATEST_TAG (git) ---"
      uv tool install specify-cli --force --from "git+https://github.com/github/spec-kit.git@${LATEST_TAG}"
    else
      echo "--- uv tool upgrade specify-cli (latest tag unresolved, using cached source) ---"
      uv tool upgrade specify-cli
    fi
    echo "uv exit: $?"
  elif command -v pipx >/dev/null 2>&1; then
    if [ -n "$SRC_DIR" ]; then
      echo "--- pipx install specify-cli from tarball ($LATEST_TAG) ---"
      pipx install --force "$SRC_DIR"
    elif [ -n "$LATEST_TAG" ]; then
      echo "--- pipx install specify-cli @ $LATEST_TAG (git) ---"
      pipx install --force "git+https://github.com/github/spec-kit.git@${LATEST_TAG}"
    else
      echo "--- pipx upgrade specify-cli (latest tag unresolved) ---"
      pipx upgrade specify-cli
    fi
    echo "pipx exit: $?"
  else
    echo "SKIP: neither uv nor pipx in PATH; CLI not upgraded."
  fi

  now_epoch=$(date +%s)
  last_update=0
  if [ -f "$STATE_FILE" ]; then
    last_update=$(cat "$STATE_FILE" 2>/dev/null || echo "0")
  fi

  # speckit.specify always runs init; all other commands are throttled
  should_run_init=1
  if [ "$COMMAND_NAME" != "speckit.specify" ] && [ "$FORCE_UPDATE" != "1" ] && [ "$UPDATE_INTERVAL_SECONDS" -gt 0 ] 2>/dev/null; then
    elapsed=$((now_epoch - last_update))
    if [ "$elapsed" -lt "$UPDATE_INTERVAL_SECONDS" ]; then
      should_run_init=0
      echo "SKIP: specify init throttled (elapsed=${elapsed}s < interval=${UPDATE_INTERVAL_SECONDS}s)"
    fi
  fi

  if [ "$should_run_init" -eq 1 ]; then
    # Constitution protection: backup if modified from template
    CONSTITUTION_FILE="$CWD/.specify/memory/constitution.md"
    CONSTITUTION_TEMPLATE="$CWD/.specify/templates/constitution-template.md"
    CONSTITUTION_BACKUP=""
    if [ -f "$CONSTITUTION_FILE" ] && [ -f "$CONSTITUTION_TEMPLATE" ]; then
      if ! diff -q "$CONSTITUTION_FILE" "$CONSTITUTION_TEMPLATE" >/dev/null 2>&1; then
        CONSTITUTION_BACKUP=$(mktemp)
        cp "$CONSTITUTION_FILE" "$CONSTITUTION_BACKUP"
        echo "constitution.md differs from template; backed up before init."
      fi
    fi

    echo "--- specify init --here --force ---"
    if command -v specify >/dev/null 2>&1; then
      (cd "$CWD" && specify init --here --force --integration "$INTEGRATION")
      init_exit=$?
      echo "specify init exit: $init_exit"
    elif command -v uv >/dev/null 2>&1; then
      if [ -n "$SRC_DIR" ]; then
        (cd "$CWD" && uvx --from "$SRC_DIR" specify init --here --force --integration "$INTEGRATION")
      else
        (cd "$CWD" && uvx --from git+https://github.com/github/spec-kit.git specify init --here --force --integration "$INTEGRATION")
      fi
      init_exit=$?
      echo "uvx specify init exit: $init_exit"
    else
      init_exit=127
      echo "SKIP: specify not in PATH and uv missing for uvx fallback."
    fi

    # Restore constitution if it was backed up
    if [ -n "$CONSTITUTION_BACKUP" ] && [ -f "$CONSTITUTION_BACKUP" ]; then
      cp "$CONSTITUTION_BACKUP" "$CONSTITUTION_FILE"
      rm -f "$CONSTITUTION_BACKUP"
      echo "constitution.md restored (protected from template overwrite)."
    fi

    if [ "${init_exit:-1}" -eq 0 ]; then
      printf '%s\n' "$now_epoch" > "$STATE_FILE"
      echo "Updated state file: $STATE_FILE"

      # Propagate the freshly regenerated speckit skills to the user-scope
      # install so skills imported into ~/.claude (via install.sh) stay in
      # lockstep with the project update. Opt out with SPECIFY_SYNC_USER_SKILLS=0.
      SYNC_USER_SKILLS="${SPECIFY_SYNC_USER_SKILLS:-1}"
      USER_CLAUDE="$HOME/.claude"
      if [ "$SYNC_USER_SKILLS" = "1" ] && [ -d "$USER_CLAUDE/skills" ] && [ "$USER_CLAUDE" != "$CWD/.claude" ]; then
        synced=0
        for src in "$CWD"/.claude/skills/speckit-*/; do
          [ -d "$src" ] || continue
          name=$(basename "$src")
          dst="$USER_CLAUDE/skills/$name"
          rm -rf "$dst"
          cp -R "$src" "$dst"
          synced=$((synced + 1))
        done
        echo "Synced $synced speckit skill(s) to user scope: $USER_CLAUDE/skills"
      else
        echo "User-scope skill sync skipped (disabled, no ~/.claude/skills, or cwd is the user install)."
      fi
    fi
  else
    echo "State file unchanged: $STATE_FILE"
  fi

  [ -n "$SRC_DIR" ] && rm -rf "$SRC_DIR"
} >>"$LOG" 2>&1 || true

if [ "$COMMAND_NAME" = "speckit.specify" ]; then
  NOTE=$'\n\nNote: speckit-specify always runs specify init --here --force. Modified .specify/memory/constitution.md is protected from overwrite.'
else
  NOTE=$'\n\nNote: specify init --here --force may replace the default template for .specify/memory/constitution.md. Restore from git if you customized it (see Spec Kit upgrade guide).'
fi

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
