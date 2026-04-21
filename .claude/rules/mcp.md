# MCP servers catalog

Six MCP servers are registered at user scope. Runtime definitions: `.mcp.json`. Installation: `~/.claude/install.sh`.

## Catalog

| Server | Transport | Endpoint / package | Key use cases |
|---|---|---|---|
| `aws-knowledge` | HTTP | `https://knowledge-mcp.global.api.aws` | AWS knowledge base |
| `aws-documentation` | stdio | `awslabs.aws-documentation-mcp-server` | AWS official documentation search/fetch |
| `bedrock-agentcore` | stdio | `awslabs.amazon-bedrock-agentcore-mcp-server` | Amazon Bedrock AgentCore docs |
| `strands-agents` | stdio | `strands-agents-mcp-server` | Strands Agents framework docs |
| `google-developer-knowledge` | HTTP | `https://developerknowledge.googleapis.com/mcp` | Google developer knowledge base |
| `microsoft-learn` | HTTP | `https://learn.microsoft.com/api/mcp` | Microsoft Learn / Azure docs |

## Usage rule

Prefer these MCP servers over `WebSearch` / `WebFetch` for AWS, GCP, or Azure questions — they return first-party documentation and avoid drift from cached search results.
