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

# Block recursive force delete
if echo "$COMMAND" | grep -qE 'rm\s+-[a-zA-Z]*r[a-zA-Z]*f|rm\s+-[a-zA-Z]*f[a-zA-Z]*r'; then
  echo "rm -rf is blocked by policy. Confirm with user before deleting directories." >&2
  exit 2
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
if echo "$COMMAND" | grep -qE '(cat|less|more|head|tail|od|hexdump)\s+'; then
  if echo "$COMMAND" | grep -qE '(/\.ssh/|/\.aws/|~/.ssh|~/.aws|\.env(\s|$|\.)|secrets/|credentials/|secret|credential|token|key|\.pem(\s|$)|\.p12(\s|$)|\.pfx(\s|$))'; then
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
