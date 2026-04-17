#!/usr/bin/env bash
# Register user-scope MCP servers for Claude Code.
# Run once after copying .claude/ to ~/.claude/.
# Requires: claude CLI, uv (for uvx-based servers), and GOOGLE_DEV_KNOWLEDGE_API_KEY.

set -euo pipefail

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
