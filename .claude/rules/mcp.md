# MCP servers catalog

Purpose: know which MCP server answers which cloud-docs question, and when calling one is mandatory. Applies when a request concerns AWS, GCP, or Azure.

Runtime definitions are in `.mcp.json`. Optional user-scope defaults are installed by `~/.claude/install.sh` (Google MCP requires `GOOGLE_DEV_KNOWLEDGE_API_KEY`).

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

When a question directly concerns AWS, GCP, or Azure services, features, or documentation, you MUST invoke the matching MCP server before answering:

- AWS question → `aws-knowledge` or `aws-documentation`
- GCP question → `google-developer-knowledge`
- Azure question → `microsoft-learn`

If the MCP server is unreachable, warn the user that live documentation is unavailable, then answer from training knowledge.

Incidental mentions of AWS/GCP/Azure in otherwise generic questions (e.g., "I'm deployed on AWS but my question is about Python loops") do not require an MCP call.
