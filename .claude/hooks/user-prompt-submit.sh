#!/usr/bin/env bash
# UserPromptSubmit hook: block prompts containing obvious secrets
# Exit 2 = blocking error (prompt rejected, stderr shown to Claude)
# Exit 0 = allow
# Grounded in .claude/rules/permissions.md "Credential Safety".

set -euo pipefail

PROMPT=$(jq -r '.prompt // empty' 2>/dev/null || echo "")

if [ -z "$PROMPT" ]; then
  exit 0
fi

# AWS access key ID
if echo "$PROMPT" | grep -qE '\b(AKIA|ASIA)[0-9A-Z]{16}\b'; then
  echo "Blocked: prompt contains an AWS access key ID. Rotate the key and resubmit without it." >&2
  exit 2
fi

# GitHub tokens
if echo "$PROMPT" | grep -qE '\b(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,}\b'; then
  echo "Blocked: prompt contains a GitHub token. Rotate the token and resubmit without it." >&2
  exit 2
fi
if echo "$PROMPT" | grep -qE '\bgithub_pat_[A-Za-z0-9_]{22,}\b'; then
  echo "Blocked: prompt contains a GitHub fine-grained PAT. Rotate the token and resubmit without it." >&2
  exit 2
fi

# Slack tokens
if echo "$PROMPT" | grep -qE '\bxox[abpors]-[A-Za-z0-9-]{10,}\b'; then
  echo "Blocked: prompt contains a Slack token. Rotate the token and resubmit without it." >&2
  exit 2
fi

# Private key headers
if echo "$PROMPT" | grep -qE -- '-----BEGIN ([A-Z]+ )?PRIVATE KEY-----'; then
  echo "Blocked: prompt contains a private key. Remove it and resubmit." >&2
  exit 2
fi

# Google API key
if echo "$PROMPT" | grep -qE '\bAIza[0-9A-Za-z_\-]{35}\b'; then
  echo "Blocked: prompt contains a Google API key. Rotate the key and resubmit without it." >&2
  exit 2
fi

exit 0
