# MCP servers catalog

Single source of truth for the six MCP servers. Runtime definitions: `.mcp.json`. User-scope installation (copy + MCP registration): `~/.claude/install.sh`.

## Catalog

| Server | Transport | Package / URL | Version | Key use cases |
|---|---|---|---|---|
| `aws-knowledge` | HTTP | `https://knowledge-mcp.global.api.aws` | — | AWS knowledge base (remote HTTP, no install) |
| `aws-documentation` | stdio | `awslabs.aws-documentation-mcp-server` | 1.1.20 | AWS official documentation search/fetch |
| `bedrock-agentcore` | stdio | `awslabs.amazon-bedrock-agentcore-mcp-server` | 0.0.16 | Amazon Bedrock AgentCore docs |
| `strands-agents` | stdio | `strands-agents-mcp-server` | 0.2.7 | Strands Agents framework docs |
| `google-developer-knowledge` | HTTP | `https://developerknowledge.googleapis.com/mcp` | — | Google developer knowledge base |
| `microsoft-learn` | HTTP | `https://learn.microsoft.com/api/mcp` | — | Microsoft Learn / Azure official documentation |

## Usage

- Prefer these over general web search for AWS / GCP / Azure questions.
- `aws-documentation` supports `AWS_DOCUMENTATION_PARTITION=aws-cn` for China regions (see `.mcp.json` env).

## Prerequisites

- `uv` — required for the three `uvx` stdio servers. Install: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- `GOOGLE_DEV_KNOWLEDGE_API_KEY` — required for `google-developer-knowledge`.
