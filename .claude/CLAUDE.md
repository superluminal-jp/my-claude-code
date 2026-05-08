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
- No emojis, ASCII art, or other visual decorations unless explicitly requested
- In internal reasoning, explicitly name the frameworks used (e.g., MECE, SCQA, FURPS+, INVEST) when they are applied.
- In user-facing responses and deliverables (including code comments/docs), apply frameworks implicitly; do not mention framework names unless the user explicitly asks.

## Skills (mandatory routing)

Always load the matching skill before responding (see `.claude/skills/` for full playbooks).

- `coder` — requests involving code implementation, modification, refactoring, testing, or debugging
- `editor` — requests involving documents, slides, charts, translation, or text editing
- `clarifier` — requests with any ambiguity (including gaps in intent, scope, acceptance, or constraints)
- `ubiquitous-language` — active in any project conversation where `.specify/ubiquitous-language/` exists; passively collects domain vocabulary candidates and surfaces them at natural conversation pauses without interrupting ongoing tasks

For mixed requests (both code and documentation): load `coder` first, then `editor`. `/speckit-*` slash commands are excluded (each has its own playbook).

## Response Preflight (before first answer)

- Run the clarification gate first via `rules/clarifier.md` (intent, scope, constraints, acceptance criteria).
- If ambiguity remains, ask clarifying questions before implementation.
- Then choose the minimum relevant skill for the task; avoid loading unrelated skills.
- Use `rules/advisor.md` as concise baseline answer-quality guidance.

@.claude/rules/skill-routing.md

## MCP

Project MCP definitions live in `.mcp.json`. `~/.claude/install.sh` can register matching user-scope defaults.

@.claude/rules/mcp.md
