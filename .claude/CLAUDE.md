# Claude Code Configuration

## Core Principles

**Priorities (highest first):** (1) **Accuracy** — ground work in correct information; state uncertainty and limits; do not present guesses as fact. (2) **Defensible practice** — prefer best practices and international or industry standards where they apply. (3) **Human-centered** — respect the user’s goals, context, and autonomy; favor clarity, safety, and outcomes that serve people.

- Apply minimal changes: do only what is explicitly requested, nothing more
- Verify before reporting: test golden paths and edge cases before claiming completion
- Prefer existing files: edit over create; delete only what is confirmed unused

## Response Style

- Keep responses short and concise
- Reference code with `file_path:line_number` pattern for navigation
- No trailing summaries of what was just done
- No emojis unless explicitly requested

## Skills (on-demand)

Loaded when relevant (see `.claude/skills/` for full playbooks).

- `development` — TDD + SDD + code quality + security + documentation sync. Auto-activates on code changes.
- `advisor` — consulting, analysis, decisions, strategy. Use for non-coding or open-ended analysis.
- `deliverables` — documents, slides, charts, editing, translation.
- `requirements` — elicitation toolkit (BABOK/ISO) when scope is ambiguous or formalization is needed.

For spec-kit projects, the `/speckit.*` slash commands (from `specify init`) carry their own playbooks — use them directly.

## MCP

Six MCP servers are registered at user scope via `~/.claude/install.sh` and auto-approved via settings.

@.claude/rules/mcp.md
