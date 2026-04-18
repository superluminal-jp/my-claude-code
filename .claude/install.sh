#!/usr/bin/env bash
# Install this .claude/ tree into the user's ~/.claude/ and register MCP servers.
# Idempotent: re-running refreshes the copy and re-registers MCP servers.
# Requires: claude CLI, uv (for uvx-based servers), GOOGLE_DEV_KNOWLEDGE_API_KEY.
#
# Usage (from the cloned repo):
#   bash path/to/my-claude-code/.claude/install.sh
# Or, after a previous install:
#   ~/.claude/install.sh

set -euo pipefail

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="$HOME/.claude"

# 1. Copy .claude/ contents to ~/.claude/
if [ "$SOURCE_DIR" != "$TARGET_DIR" ]; then
  mkdir -p "$TARGET_DIR"
  cp -R "$SOURCE_DIR"/. "$TARGET_DIR"/
  echo "Copied $SOURCE_DIR -> $TARGET_DIR"
fi

# 2. Ensure hook scripts and this installer are executable
chmod +x "$TARGET_DIR"/hooks/*.sh
chmod +x "$TARGET_DIR"/install.sh

# 3. Register user-scope MCP servers
claude mcp add -s user aws-knowledge \
  --transport http \
  https://knowledge-mcp.global.api.aws

claude mcp add -s user aws-documentation \
  -e FASTMCP_LOG_LEVEL=ERROR \
  -e AWS_DOCUMENTATION_PARTITION=aws \
  -- uvx awslabs.aws-documentation-mcp-server@1.1.20

claude mcp add -s user bedrock-agentcore \
  -e FASTMCP_LOG_LEVEL=ERROR \
  -- uvx awslabs.amazon-bedrock-agentcore-mcp-server@0.0.16

claude mcp add -s user strands-agents \
  -e FASTMCP_LOG_LEVEL=ERROR \
  -- uvx strands-agents-mcp-server@0.2.7

claude mcp add -s user \
  --transport http \
  google-developer-knowledge \
  https://developerknowledge.googleapis.com/mcp \
  --header "X-Goog-Api-Key: ${GOOGLE_DEV_KNOWLEDGE_API_KEY:-}"

claude mcp add -s user microsoft-learn \
  --transport http \
  https://learn.microsoft.com/api/mcp
