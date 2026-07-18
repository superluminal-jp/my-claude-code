#!/usr/bin/env bash
# Install this .claude/ tree into the user's ~/.claude/ and sync MCP servers.
# Idempotent: re-running refreshes hooks/rules/skills/settings and upserts MCP servers.
# Requires: claude CLI, uvx, jq. Optional: GOOGLE_DEV_KNOWLEDGE_API_KEY.
#
# Usage (from the cloned repo):
#   bash path/to/my-claude-code/install.sh
# Or, after a previous install:
#   ~/.claude/install.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="$SCRIPT_DIR/.claude"
TARGET_DIR="$HOME/.claude"

upsert_user_mcp() {
  local name="$1"
  shift

  # Ensure repo values win on re-install.
  claude mcp remove -s user "$name" >/dev/null 2>&1 || true
  claude mcp add -s user "$name" "$@"
}

sync_path() {
  local rel="$1"
  local src="$SOURCE_DIR/$rel"
  local dst="$TARGET_DIR/$rel"

  # Make target match source exactly for managed paths.
  rm -rf "$dst"
  if [ -d "$src" ]; then
    mkdir -p "$(dirname "$dst")"
    cp -R "$src" "$dst"
  elif [ -f "$src" ]; then
    mkdir -p "$(dirname "$dst")"
    cp "$src" "$dst"
  fi
}

# 0. Preflight checks
for cmd in claude uvx jq; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Missing required command: $cmd" >&2
    exit 1
  fi
done

# 1. Sync managed .claude paths (prevents stale skills/rules/hooks)
if [ "$SCRIPT_DIR" != "$TARGET_DIR" ]; then
  mkdir -p "$TARGET_DIR"
  sync_path "hooks"
  sync_path "rules"
  sync_path "skills"
  sync_path "commands"
  sync_path "CLAUDE.md"
  sync_path "settings.json"
  cp "$SCRIPT_DIR/install.sh" "$TARGET_DIR/install.sh"
  echo "Synced managed paths from $SOURCE_DIR -> $TARGET_DIR"
fi

# 2. Ensure hook scripts and this installer are executable
chmod +x "$TARGET_DIR"/hooks/*.sh
chmod +x "$TARGET_DIR"/install.sh

# 3. Upsert user-scope MCP servers to match this repository
upsert_user_mcp aws-knowledge \
  --transport http \
  https://knowledge-mcp.global.api.aws

upsert_user_mcp aws-documentation \
  -e FASTMCP_LOG_LEVEL=ERROR \
  -e AWS_DOCUMENTATION_PARTITION=aws \
  -- uvx awslabs.aws-documentation-mcp-server@1.1.20

upsert_user_mcp bedrock-agentcore \
  -e FASTMCP_LOG_LEVEL=ERROR \
  -- uvx awslabs.amazon-bedrock-agentcore-mcp-server@0.0.16

upsert_user_mcp strands-agents \
  -e FASTMCP_LOG_LEVEL=ERROR \
  -- uvx strands-agents-mcp-server@0.2.7

if [ -n "${GOOGLE_DEV_KNOWLEDGE_API_KEY:-}" ]; then
  upsert_user_mcp google-developer-knowledge \
    --transport http \
    https://developerknowledge.googleapis.com/mcp \
    --header "X-Goog-Api-Key: ${GOOGLE_DEV_KNOWLEDGE_API_KEY}"
else
  claude mcp remove -s user google-developer-knowledge >/dev/null 2>&1 || true
  echo "Skipping google-developer-knowledge MCP: GOOGLE_DEV_KNOWLEDGE_API_KEY is not set" >&2
fi

upsert_user_mcp microsoft-learn \
  --transport http \
  https://learn.microsoft.com/api/mcp

# 4. Configure Spec Kit git extension (enable auto-commit if .specify is present)
# Spec Kit is opt-in per project (`specify init`); this only tunes this repo's
# own local .specify/, it does not propagate to ~/.claude or any other project.
SPECKIT_GIT_CONFIG="$SCRIPT_DIR/.specify/extensions/git/git-config.yml"
if [ -f "$SPECKIT_GIT_CONFIG" ]; then
  python3 - "$SPECKIT_GIT_CONFIG" <<'PYEOF'
import sys, re

path = sys.argv[1]
with open(path) as f:
    content = f.read()

content = re.sub(r'^( *default: )false', r'\1true', content, flags=re.MULTILINE)
content = re.sub(r'^( *enabled: )false', r'\1true', content, flags=re.MULTILINE)

with open(path, 'w') as f:
    f.write(content)

print(f"[install] Spec Kit git auto-commit enabled: {path}")
PYEOF
fi

# 5. Install codex-plugin-cc (Codex review/rescue from Claude Code)
if ! claude plugin marketplace list 2>/dev/null | grep -q "openai-codex"; then
  claude plugin marketplace add openai/codex-plugin-cc
else
  claude plugin marketplace update openai-codex >/dev/null 2>&1 || true
fi
if ! claude plugin list 2>/dev/null | grep -q "codex@openai-codex"; then
  claude plugin install codex@openai-codex
fi

echo "Done. ~/.claude and user-scope MCP are synced to this repository state."
