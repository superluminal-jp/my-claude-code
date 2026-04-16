# Claude Code Best Practices Configuration

This configuration enforces the official Claude Code specifications and best practices
from https://code.claude.com/docs/.

## Core Principles

- Apply minimal changes: do only what is explicitly requested, nothing more
- Verify before reporting: test golden paths and edge cases before claiming completion
- Prefer existing files: edit over create; delete only what is confirmed unused

## Code Quality

- Write no speculative abstractions: complexity should match the task, not hypothetical future needs
- Add no error handling for impossible scenarios: trust framework guarantees; validate only at system boundaries
- Add no unsolicited improvements: no cleanup, refactoring, or enhancements beyond scope
- Add no docstrings, comments, or type annotations to untouched code
- Three similar lines are better than a premature abstraction

## Security

- Never introduce command injection, XSS, SQL injection, or OWASP Top 10 vulnerabilities
- Validate input at system boundaries (user input, external APIs) only
- If insecure code is written, fix it immediately before proceeding

## Response Style

- Keep responses short and concise
- Reference code with `file_path:line_number` pattern for navigation
- No trailing summaries of what was just done
- No emojis unless explicitly requested

## MCP Servers

Four MCP servers are configured in `.mcp.json` and auto-approved via settings.

| Server              | Key use cases                                                    |
|---------------------|------------------------------------------------------------------|
| `aws-knowledge`     | Search authoritative AWS knowledge base (remote HTTP, no install) |
| `aws-documentation` | Fetch and search AWS official documentation pages                |
| `bedrock-agentcore` | Search and fetch Amazon Bedrock AgentCore docs                   |
| `strands-agents`    | Search and fetch Strands Agents framework docs                   |

- Prefer these tools over general web search when answering AWS or Strands questions
- `aws-documentation` supports `AWS_DOCUMENTATION_PARTITION=aws-cn` for China regions
- All `uvx`-based servers require `uv` to be installed: `curl -LsSf https://astral.sh/uv/install.sh | sh`

## Rules

Rules are auto-loaded from `.claude/rules/`. See `permissions.md`, `tools.md`,
`advisor.md`, and `development.md` in that directory.
