#!/usr/bin/env bash
# PreToolUse hook: block dangerous Bash commands
# Exit 2 = blocking error (action denied + stderr shown to Claude)
# Exit 0 = allow

set -euo pipefail

COMMAND=$(jq -r '.tool_input.command // empty' 2>/dev/null || echo "")

if [ -z "$COMMAND" ]; then
  exit 0
fi

# Block force push
if echo "$COMMAND" | grep -qE 'git push.*(\s-f(\s|$)|--force)'; then
  echo "Force push is blocked by policy. Use a normal push or get explicit user approval." >&2
  exit 2
fi

# Block hard reset
if echo "$COMMAND" | grep -qE 'git reset.*--hard'; then
  echo "git reset --hard is blocked by policy. Confirm with user before discarding changes." >&2
  exit 2
fi

# Block git clean -f (force delete untracked files)
if echo "$COMMAND" | grep -qE 'git clean.*-[a-zA-Z]*f'; then
  echo "git clean -f is blocked by policy. Confirm with user before deleting untracked files." >&2
  exit 2
fi

# Handle recursive force delete
# Match rm only when it is a command token (start of string or after ;, &&, ||, |, &, ()
# This avoids false positives from rm appearing inside quoted arguments (e.g., heredoc PR bodies)
if echo "$COMMAND" | grep -qE '(^|;|&&|\|\||[|(&])\s*rm\s+-[a-zA-Z]*r[a-zA-Z]*f|(^|;|&&|\|\||[|(&])\s*rm\s+-[a-zA-Z]*f[a-zA-Z]*r'; then
  # Always block: filesystem root (/), home (~), current directory (.), or $HOME
  if echo "$COMMAND" | grep -qE '(^|;|&&|\|\||[|(&])\s*rm\s+(-[a-zA-Z]+\s+)*(\/|~\/?|\.\/?|\/\*)(\s|$)' || \
     echo "$COMMAND" | grep -qE '(^|;|&&|\|\||[|(&])\s*rm\s+(-[a-zA-Z]+\s+)*\$HOME'; then
    echo "rm -rf targeting root, home, or current directory is permanently blocked by policy." >&2
    exit 2
  fi
  # All other rm -rf: route through user confirmation
  cat <<'JSON'
{
  "continue": true,
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "ask",
    "permissionDecisionReason": "rm -rf requires explicit user approval before deleting directories"
  }
}
JSON
  exit 0
fi

# Block system-destructive commands (device overwrite, filesystem format, fork bomb)
if echo "$COMMAND" | grep -qE '>\s*/dev/sd[a-z]' || \
   echo "$COMMAND" | grep -qE '(^|[;&|[:space:]])mkfs(\s|$)' || \
   echo "$COMMAND" | grep -qF 'dd if=/dev/zero' || \
   echo "$COMMAND" | grep -qF ':(){ :|:& };:'; then
  echo "System-destructive command blocked by policy." >&2
  exit 2
fi

# Block curl | bash / wget | bash patterns
if echo "$COMMAND" | grep -qE '(curl|wget).*\|.*(bash|sh|zsh)'; then
  echo "Piping remote scripts to shell is blocked by policy." >&2
  exit 2
fi

# Block non-HTTPS http:// for curl/wget except localhost / 127.0.0.1 (per URL)
if echo "$COMMAND" | grep -qE '(curl|wget)'; then
  while IFS= read -r url; do
    [ -z "$url" ] && continue
    if echo "$url" | grep -qE '^http://(localhost|127\.0\.0\.1)(/|:|$)'; then
      continue
    fi
    echo "Non-HTTPS HTTP requests are blocked by policy (except localhost)." >&2
    exit 2
  done < <(echo "$COMMAND" | grep -oE 'http://[^[:space:]]+' 2>/dev/null || true)
fi

# Block reading credential paths or key material via common shell read commands
# Exclude heredoc usage (cat << / cat <<'EOF') which is not a file read
READ_CMD_RE='(cat|less|more|head|tail|od|hexdump)'
if echo "$COMMAND" | grep -qE "${READ_CMD_RE}\s+" && \
   ! echo "$COMMAND" | grep -qE "${READ_CMD_RE}\s*<<"; then
  # Phase 1: strong structural patterns — unambiguously credential paths anywhere in command
  if echo "$COMMAND" | grep -qE '(/\.ssh/|/\.aws/|~/\.ssh|~/\.aws|\.env(\s|$|\.)|secrets/|credentials/|\.pem(\s|$)|\.p12(\s|$)|\.pfx(\s|$))'; then
    echo "Reading credential paths or key material via shell is blocked by policy." >&2
    exit 2
  fi
  # Phase 2: broad keywords — restrict to the file argument following the read command
  # to avoid false positives from commit messages, PR bodies, or pipe targets
  FILE_ARG=$(echo "$COMMAND" | grep -oE "${READ_CMD_RE}(\s+-\S+)*\s+\S+" | grep -oE '\s\S+$' | tr -d ' ' | head -1)
  if [ -n "$FILE_ARG" ] && echo "$FILE_ARG" | grep -qE '(secret|credential|token|key)'; then
    echo "Reading credential paths or key material via shell is blocked by policy." >&2
    exit 2
  fi
fi

# Block writing to credential paths (redirection or tee)
if echo "$COMMAND" | grep -qE '(>|>>|\|\s*tee(\s|$))'; then
  if echo "$COMMAND" | grep -qE '(/\.ssh/|/\.aws/|~/\.ssh|~/\.aws|\.env(\s|$|\.)|\.pem(\s|$)|\.p12(\s|$)|\.pfx(\s|$))'; then
    echo "Writing to credential paths or key material is blocked by policy." >&2
    exit 2
  fi
fi

# Route sudo through user confirmation via JSON permission decision
if echo "$COMMAND" | grep -qE '(^|[;&|[:space:]])sudo(\s|$)'; then
  cat <<'JSON'
{
  "continue": true,
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "ask",
    "permissionDecisionReason": "sudo requires explicit user approval"
  }
}
JSON
  exit 0
fi

exit 0
