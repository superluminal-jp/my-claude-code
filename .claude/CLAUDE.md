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
- `ubiquitous-language` — activate when conversation contains business event expressions (past/passive verb+noun: e.g., 「注文が確定された」) or domain vocabulary candidates; passively queues candidates without interrupting; surfaces them at natural pauses (no new candidates in preceding turn)
- `domain-model` — activate when conversation contains DDD structural patterns (aggregates, entities, value objects, domain events, invariants) or when user asks to create/update a domain model; passively queues candidates; surfaces at natural pauses

For mixed requests (both code and documentation): load `coder` first, then `editor`. `/speckit-*` slash commands are excluded (each has its own playbook).

## Response Preflight (before first answer)

- Run the clarification gate — `rules/clarifier.md` is the canonical source for when to ask vs proceed (do not restate its triggers here). If ambiguity remains, ask before implementing.
- Choose the minimum relevant skill (`rules/skill-routing.md`); avoid loading unrelated skills.
- Use `rules/advisor.md` as baseline answer-quality guidance.

### Pre-execution discipline (non-Spec-Kit tasks)

For non-trivial work that does not use a `/speckit-*` command, run a lightweight internal design→plan→task pass before editing — the same discipline Spec Kit formalizes, applied proportionately:

- **Non-trivial** = touches multiple files, adds or changes observable behavior, or is hard to reverse. Internally state the **approach** (scope + design, via the clarifier gate), a **short plan** (ordered steps, via `rules/advisor.md`), and a **task breakdown** before making changes. Surface it to the user only when the task warrants it; otherwise keep it internal.
- **Trivial** = single file, reversible, ≤1 logical step (typo, one-line fix). Skip the ceremony and act.

When in doubt, prefer the lighter path; do not let planning add friction to small reversible changes.

@.claude/rules/skill-routing.md
@.claude/rules/live-documentation.md

## MCP

Project MCP definitions live in `.mcp.json`. `~/.claude/install.sh` can register matching user-scope defaults.

@.claude/rules/mcp.md
