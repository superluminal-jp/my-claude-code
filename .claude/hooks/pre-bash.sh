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
if echo "$COMMAND" | grep -qE 'git push.*(-f|--force)'; then
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

# Block curl | bash / wget | bash patterns
if echo "$COMMAND" | grep -qE '(curl|wget).*\|.*(bash|sh|zsh)'; then
  echo "Piping remote scripts to shell is blocked by policy." >&2
  exit 2
fi

exit 0
