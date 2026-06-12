#!/usr/bin/env bash
# SessionStart hook: ensure the lint toolchain used by post-edit-format.sh is
# available in fresh Claude Code on the web containers.
#
# Without this, shfmt/shellcheck/yamllint are absent in remote sessions, so
# .claude/hooks/post-edit-format.sh silently skips all shell/YAML linting.
#
# Web-only, synchronous, idempotent, non-interactive, and never fatal: a failed
# install must not block session startup. Status is written to stderr only.

set -uo pipefail

# Only run in Claude Code on the web; local machines manage their own toolchain.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

log() { echo "[session-start] $*" >&2; }

have() { command -v "$1" >/dev/null 2>&1; }

apt_install() {
  # Best-effort apt install; refresh package lists at most once.
  if ! have apt-get; then
    return 1
  fi
  if [ -z "${_APT_UPDATED:-}" ]; then
    apt-get update -qq >/dev/null 2>&1 || true
    _APT_UPDATED=1
  fi
  DEBIAN_FRONTEND=noninteractive apt-get install -y -qq "$1" >/dev/null 2>&1
}

pip_install() {
  if ! have python3; then
    return 1
  fi
  python3 -m pip install --quiet "$1" >/dev/null 2>&1 ||
    python3 -m pip install --quiet --break-system-packages "$1" >/dev/null 2>&1
}

# jq: required by post-edit-format.sh and check-mcp-consistency.sh.
if ! have jq; then
  apt_install jq || true
fi

# Shell static analysis (the shellcheck tool) for *.sh edits.
if ! have shellcheck; then
  apt_install shellcheck || true
fi

# yamllint: YAML linting for *.yml/*.yaml edits. pip is the most portable path.
if ! have yamllint; then
  pip_install yamllint || apt_install yamllint || true
fi

# shfmt: shell formatter. Try the distro package, then a Go toolchain build.
# Avoid curl-pipe-bash installs (blocked by pre-bash.sh and against repo policy).
if ! have shfmt; then
  if ! apt_install shfmt; then
    if have go; then
      go install mvdan.cc/sh/v3/cmd/shfmt@latest >/dev/null 2>&1 || true
      if [ -x "$HOME/go/bin/shfmt" ] && [ -n "${CLAUDE_ENV_FILE:-}" ]; then
        # Literal line is expanded when the session sources CLAUDE_ENV_FILE.
        # shellcheck disable=SC2016
        echo 'export PATH="$HOME/go/bin:$PATH"' >>"$CLAUDE_ENV_FILE"
      fi
    fi
  fi
fi

# Report readiness without blocking the session.
missing=""
for tool in jq shellcheck shfmt yamllint; do
  have "$tool" || missing="$missing $tool"
done
if [ -n "$missing" ]; then
  log "lint toolchain incomplete; still missing:$missing (post-edit linting will skip these)"
else
  log "lint toolchain ready: jq shellcheck shfmt yamllint"
fi

exit 0
