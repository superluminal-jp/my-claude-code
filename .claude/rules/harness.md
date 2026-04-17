# Harness Design Rules

Three patterns from [Harnessing Claude's Intelligence](https://claude.com/blog/harnessing-claudes-intelligence) applied to any agent/tool surface built on Claude.

## 1. Use what Claude already knows

Prefer tools and formats the model has seen at scale.

- Default to **bash** + a **text editor** surface for files and processes.
- Prefer **POSIX utilities, `git`, language-native REPLs** over project-specific DSLs.
- Before adding a new tool, state the concrete capability existing well-known tools cannot provide.

## 2. Ask what you can stop doing

Old scaffolding becomes dead weight on better models. On every model bump, audit and remove what no longer helps.

- Candidates to reassess: context resets / summarization passes, step-by-step reminders, retry loops, hand-written planners duplicating the model's planning.
- Removal requires the same rigor as addition — show before/after on a representative task before deleting.

## 3. Set boundaries carefully

Dedicated tools are for **UX, observability, security** — not for micromanaging reasoning.

- Promote to a tool only when it needs: typed args to gate/audit/deny (security), structured logs/metrics/traces (observability), or render/confirm/stream (UX).
- Do **not** promote to constrain *how* Claude reasons.
- Do **not** force every tool result through the context window — give Claude a code execution surface (bash, REPL) to filter/pipe/transform output.
- Keep tool schemas stable across turns (churn invalidates prompt cache).

## Review triggers

Revisit this file and the harness when any change:

- Claude model version (Opus / Sonnet / Haiku)
- Tool surface (adding, removing, renaming)
- Agent "gives up early," loops, or ignores context
- Latency or token-cost regression tied to tool-result handling
