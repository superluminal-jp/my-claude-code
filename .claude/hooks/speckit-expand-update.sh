#!/usr/bin/env bash
# UserPromptExpansion + SessionStart: keep this workspace's Spec Kit current.
# Fires (a) before any /speckit-* command expands, and (b) at every session
# start for a workspace that already has `.specify/` — so a project that
# adopted Spec Kit stays current even in sessions where no /speckit-* command
# is invoked. Upgrades specify-cli via `specify self upgrade` (resolves latest
# stable via GitHub Releases, reinstalls in place) when specify-cli is already
# on PATH; otherwise bootstraps an initial install from an HTTPS release tarball.
# speckit-specify always runs specify init (bypasses throttle) and protects modified constitution.md.
# All other triggers (including SessionStart) throttle specify init to once per UPDATE_INTERVAL_SECONDS.
# Spec Kit is opt-in per project (`specify init`); this hook only refreshes the
# current workspace's own .specify/ and .claude/skills/speckit-* — it never
# touches any other project or the user-scope ~/.claude install.
# Integration: override with SPECIFY_INTEGRATION (default: claude). See spec-kit integrations list.

set -uo pipefail

INPUT=$(cat)
CWD=$(echo "$INPUT" | jq -r '.cwd // empty')
COMMAND_NAME=$(echo "$INPUT" | jq -r '.command_name // empty')
HOOK_EVENT_NAME=$(echo "$INPUT" | jq -r '.hook_event_name // empty')

# On SessionStart there is no command_name to gate on — proceed straight to
# the .specify/ presence check below. On every other trigger (UserPromptExpansion),
# only the specific speckit.* commands wired in settings.json's matcher apply.
if [ "$HOOK_EVENT_NAME" != "SessionStart" ]; then
  case "$COMMAND_NAME" in
    speckit.specify|speckit.clarify|speckit.plan|speckit.tasks|speckit.implement|speckit.checklist|speckit.analyze|speckit.taskstoissues|speckit.constitution|speckit.converge) ;;
    *)
      exit 0
      ;;
  esac
fi

if [ -z "$CWD" ] || [ ! -d "$CWD" ]; then
  exit 0
fi

INTEGRATION="${SPECIFY_INTEGRATION:-claude}"
UPDATE_INTERVAL_SECONDS="${SPECIFY_AUTO_UPDATE_INTERVAL_SECONDS:-86400}"
FORCE_UPDATE="${SPECIFY_FORCE_AUTO_UPDATE:-0}"
STATE_FILE="$CWD/.specify/.last-auto-update"
LOG=$(mktemp)
trap 'rm -f "$LOG"' EXIT

EFFECTIVE_HOOK_EVENT_NAME="${HOOK_EVENT_NAME:-UserPromptExpansion}"

if [ ! -d "$CWD/.specify" ]; then
  # On SessionStart this is the common case (most projects haven't opted into
  # Spec Kit) — stay silent rather than reporting a "skip" every session.
  if [ "$HOOK_EVENT_NAME" = "SessionStart" ]; then
    exit 0
  fi
  jq -n \
    --arg msg "Spec Kit auto-update skipped: no .specify directory under this workspace. Not a spec-kit project or init not run here." \
    --arg hook "$EFFECTIVE_HOOK_EVENT_NAME" \
    '{hookSpecificOutput: {hookEventName: $hook, additionalContext: $msg}}'
  exit 0
fi

{
  if [ -n "$COMMAND_NAME" ]; then
    echo "=== Spec Kit auto-update (before /$COMMAND_NAME) ==="
  else
    echo "=== Spec Kit auto-update ($HOOK_EVENT_NAME refresh) ==="
  fi
  echo "cwd=$CWD integration=$INTEGRATION"
  echo "update_interval_seconds=$UPDATE_INTERVAL_SECONDS force_update=$FORCE_UPDATE"
  set +e

  # Steady state: specify-cli >=0.10 ships its own updater (`specify self
  # upgrade`), which resolves the latest stable release via GitHub Releases
  # and reinstalls in place for uv-tool/pipx installs. Prefer it over
  # hand-rolled tag resolution so we don't duplicate spec-kit's own logic.
  SRC_DIR=""
  if command -v specify >/dev/null 2>&1; then
    echo "--- specify self upgrade ---"
    specify self upgrade
    upgrade_exit=$?
    echo "specify self upgrade exit: $upgrade_exit"
    if [ "$upgrade_exit" -ne 0 ]; then
      echo "WARN: specify self upgrade failed (exit $upgrade_exit); continuing with the currently installed specify-cli."
    fi
  else
    echo "specify-cli not on PATH; bootstrapping initial install from the latest stable release."

    # Resolve latest stable release tag from GitHub. releases/latest excludes
    # drafts and prereleases by definition, so prefer it (curl-only, no gh
    # dependency); fall back to gh with the same exclusions if curl/jq are
    # unavailable. Only needed for this one-time bootstrap — once installed,
    # `specify self upgrade` resolves it internally on every later run.
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
        echo "--- uv tool install specify-cli (tag unresolved, using default branch) ---"
        uv tool install specify-cli --force --from "git+https://github.com/github/spec-kit.git"
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
        echo "--- pipx install specify-cli (tag unresolved, using default branch) ---"
        pipx install --force "git+https://github.com/github/spec-kit.git"
      fi
      echo "pipx exit: $?"
    else
      echo "SKIP: neither uv nor pipx in PATH; specify-cli not installed."
    fi
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
    fi
  else
    echo "State file unchanged: $STATE_FILE"
  fi

  [ -n "$SRC_DIR" ] && rm -rf "$SRC_DIR"
} >>"$LOG" 2>&1 || true

# On SessionStart, a throttled no-op run (the common case once a project has
# adopted Spec Kit) has nothing worth surfacing every session — stay silent.
if [ "$HOOK_EVENT_NAME" = "SessionStart" ] && [ "${should_run_init:-0}" -ne 1 ]; then
  exit 0
fi

if [ "$COMMAND_NAME" = "speckit.specify" ]; then
  NOTE=$'\n\nNote: speckit-specify always runs specify init --here --force. Modified .specify/memory/constitution.md is protected from overwrite.'
else
  NOTE=$'\n\nNote: specify init --here --force may replace the default template for .specify/memory/constitution.md. Restore from git if you customized it (see Spec Kit upgrade guide).'
fi

BODY=$(jq -n \
  --rawfile log "$LOG" \
  --arg note "$NOTE" \
  --arg hook "$EFFECTIVE_HOOK_EVENT_NAME" \
  '($log | if length > 8800 then .[0:8800] + "\n...(truncated)\n" else . end) as $text |
  {
    hookSpecificOutput: {
      hookEventName: $hook,
      additionalContext: ("Spec Kit auto-update output:\n\n" + $text + $note)
    }
  }')

echo "$BODY"
exit 0
