# MCP servers

Tool search is on: MCP tool **names** are in context, their descriptions and schemas are not. ToolSearch before concluding a capability is missing.

| Server | Covers | Self-describes |
|---|---|---|
| `aws-documentation` | AWS docs: search, read, recommend | yes |
| `aws-knowledge` | AWS docs, regional availability, skill registry | no |
| `bedrock-agentcore` | Bedrock AgentCore: runtime, memory, gateway, browser, code interpreter | yes |
| `strands-agents` | Strands Agents framework docs | no |
| `google-developer-knowledge` | Google developer docs: search, answer | no |
| `microsoft-learn` | Microsoft Learn / Azure docs and code samples | yes |

**yes** → the server's own instructions are already in context; follow them. **no** → ToolSearch its tools first; nothing but the names is loaded.

## AWS skill registry

Before giving freehand AWS advice, check for an official skill: `aws___search_documentation` with `topics: ["agent_skills"]`, then `aws___retrieve_skill` with the **exact** `skill_name` returned — never invent one — for its `SKILL.md` (referenced files via `file`). GCP has no equivalent. Azure is unverified: `microsoft-learn` needs OAuth authorization before its tool set can be checked.

## References

- Claude Code — MCP (tool search, `.mcp.json` fields): <https://code.claude.com/docs/en/mcp>
- MCP specification — Lifecycle, `InitializeResult.instructions`: <https://modelcontextprotocol.io/specification/2025-06-18/basic/lifecycle>
