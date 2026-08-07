# MCP servers catalog

Purpose: know which MCP server answers which cloud-docs question, and when calling one is mandatory. Applies when a request concerns AWS, GCP, or Azure. Also lists non-docs tool servers (e.g. `drawio`) for completeness, since `scripts/check-mcp-consistency.sh` requires every `.mcp.json` entry to appear here — their usage rules live with the skill that uses them, not in this file, to avoid duplication.

Runtime definitions are in `.mcp.json`. Optional user-scope defaults are installed by `~/.claude/install.sh` (Google MCP requires `GOOGLE_DEV_KNOWLEDGE_API_KEY`).

## Catalog

| Server | Transport | Endpoint / package | Key use cases |
|---|---|---|---|
| `aws-knowledge` | HTTP | `https://knowledge-mcp.global.api.aws` | AWS knowledge base; also the only server here exposing AWS's official guided-skill registry (see below) |
| `aws-documentation` | stdio | `awslabs.aws-documentation-mcp-server` | AWS official documentation search/fetch |
| `bedrock-agentcore` | stdio | `awslabs.amazon-bedrock-agentcore-mcp-server` | Amazon Bedrock AgentCore docs |
| `strands-agents` | stdio | `strands-agents-mcp-server` | Strands Agents framework docs |
| `google-developer-knowledge` | HTTP | `https://developerknowledge.googleapis.com/mcp` | Google developer knowledge base |
| `microsoft-learn` | HTTP | `https://learn.microsoft.com/api/mcp` | Microsoft Learn / Azure docs |
| `drawio` | stdio | `@drawio/mcp` | draw.io diagram generation (`create_diagram`, `search_shapes`) — not a docs source; usage governed by the `drawio` skill, not the rule below |

## Usage rule

When a question directly concerns AWS, GCP, or Azure services, features, or documentation, you MUST invoke the matching MCP server before answering:

- AWS question → `aws-knowledge` or `aws-documentation`
- GCP question → `google-developer-knowledge`
- Azure question → `microsoft-learn`

If the MCP server is unreachable, warn the user that live documentation is unavailable, then answer from training knowledge.

Incidental mentions of AWS/GCP/Azure in otherwise generic questions (e.g., "I'm deployed on AWS but my question is about Python loops") do not require an MCP call.

This mandatory-invoke rule does not apply to `drawio` — it is a generation tool, not a documentation source. See the `drawio` skill for when and how to use it.

## Official provider skill registries

Beyond plain docs lookup, prefer a provider's own guided skill over ad-hoc guidance when one exists for the task:

- **AWS**: `aws-knowledge` exposes AWS's official skill registry. Call `aws___search_documentation` with `topics: ["agent_skills"]` to find a matching skill, then `aws___retrieve_skill` with the exact `skill_name` returned (never invent or guess one) to fetch its `SKILL.md` (and any referenced file via the `file` param). Use this for AWS workflows/patterns it covers, in place of freehand advice.
- **GCP**: no equivalent found. `google-developer-knowledge`'s tools (`search_documents`, `answer_query`, `get_documents`) are docs search/answer only — no skill-retrieval tool exists in its schema.
- **Azure**: unverified. `microsoft-learn` requires OAuth authorization; until it's authorized, its tool set — and whether it offers an equivalent — cannot be checked. Re-check once authorized rather than assuming either way.
