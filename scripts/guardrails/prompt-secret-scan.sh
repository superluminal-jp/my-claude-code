#!/usr/bin/env bash
# Shared prompt-secret guardrail (spec 014 FR-011 upgrade, research R4).
# Tool-agnostic: reads {"prompt": "..."} on stdin, writes
# {"decision": "allow"|"deny", "reason": "..."} on stdout. Exit 0 regardless
# of decision; non-zero only on a real script error (caller must treat that
# the same as "deny", per contracts/guardrail-script-io.md). The reason text
# never includes the matched secret value itself.
#
# Extracted from .claude/hooks/user-prompt-submit.sh — detection categories
# and thresholds kept verbatim so both the refactored Claude Code hook and
# the Codex CLI adapter produce identical outcomes to what
# user-prompt-submit.sh already produced.

set -euo pipefail

emit() {
  local decision="$1" reason="$2"
  jq -n --arg decision "$decision" --arg reason "$reason" '{decision:$decision, reason:$reason}'
}

PROMPT=$(jq -r '.prompt // empty' 2>/dev/null || echo "")

if [ -z "$PROMPT" ]; then
  emit "allow" ""
  exit 0
fi

# AWS access key ID
if echo "$PROMPT" | grep -qE '\b(AKIA|ASIA)[0-9A-Z]{16}\b'; then
  emit "deny" "Blocked: prompt contains an AWS access key ID. Rotate the key and resubmit without it."
  exit 0
fi

# GitHub tokens
if echo "$PROMPT" | grep -qE '\b(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,}\b'; then
  emit "deny" "Blocked: prompt contains a GitHub token. Rotate the token and resubmit without it."
  exit 0
fi
if echo "$PROMPT" | grep -qE '\bgithub_pat_[A-Za-z0-9_]{22,}\b'; then
  emit "deny" "Blocked: prompt contains a GitHub fine-grained PAT. Rotate the token and resubmit without it."
  exit 0
fi

# Slack tokens
if echo "$PROMPT" | grep -qE '\bxox[abpors]-[A-Za-z0-9-]{10,}\b'; then
  emit "deny" "Blocked: prompt contains a Slack token. Rotate the token and resubmit without it."
  exit 0
fi

# Private key headers
if echo "$PROMPT" | grep -qE -- '-----BEGIN ([A-Z]+ )?PRIVATE KEY-----'; then
  emit "deny" "Blocked: prompt contains a private key. Remove it and resubmit."
  exit 0
fi

# Google API key
if echo "$PROMPT" | grep -qE '\bAIza[0-9A-Za-z_\-]{35}\b'; then
  emit "deny" "Blocked: prompt contains a Google API key. Rotate the key and resubmit without it."
  exit 0
fi

emit "allow" ""
