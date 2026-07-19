# MCP servers catalog

<!--
FR-023/024 fallback (specs/013-cross-agent-guardrail-implementation): this
content is also the source for AGENTS.md's Q4 entry. A `@path` import
pointing at the installed global AGENTS.md (`~/.codex/AGENTS.md`) was the
intended dedup, but whether Claude Code's `@path` import syntax can target a
file outside `.claude/` (via a `$HOME`-relative or absolute path) could not
be verified in the implementing session — spawning a fresh Claude Code
session to test a newly-added import wasn't possible mid-conversation. Per
FR-024, this file keeps its standalone content rather than risk a silently
broken import. Re-verify against a live Claude Code session before adopting
the import; if confirmed, replace this section with the import and delete
this note.
-->

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
