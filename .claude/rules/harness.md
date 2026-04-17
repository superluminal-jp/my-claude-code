# Harness Design Rules

Applies three patterns from *Harnessing Claude's Intelligence*
(https://claude.com/blog/harnessing-claudes-intelligence) to any
application, agent, or tool surface built on top of Claude.

## 1. Use What Claude Already Knows

Prefer tools and formats the model has seen at scale over bespoke ones.

- Default to **bash** and a **text editor** surface for file and process work;
  do not invent custom replacements unless a capability gap is proven
- Default to **widely-used file formats and CLIs** (POSIX utilities, `git`,
  language-native REPLs) over project-specific DSLs
- Before adding a new tool, state the concrete capability it unlocks that an
  existing, well-known tool cannot provide

## 2. Ask What You Can Stop Doing

Harness scaffolding accrues to compensate for old limitations. When the model
improves, that scaffolding becomes dead weight that bottlenecks the new model.

- When upgrading Claude models, audit the harness and ask: *what can I stop
  doing?* Remove prompts, resets, reminders, or retries that existed only to
  work around prior-model behavior
- Examples of scaffolding to reassess on each model bump:
  - Context resets / summarization passes introduced for "context anxiety"
  - Step-by-step reminders the new model no longer needs
  - Retry loops covering failures the new model no longer produces
  - Hand-written planners that duplicate the model's own planning
- Removal requires the same rigor as addition: show the before/after behavior
  on a representative task before deleting scaffolding

## 3. Set Boundaries With the Harness — Carefully

Dedicated tools are for **UX, observability, and security** boundaries — not
for micromanaging Claude's reasoning.

- **Promote to a dedicated tool** when the action needs:
  - A security boundary (typed args the harness can gate, audit, or deny)
  - An observability hook (structured logs, metrics, traces)
  - A UX affordance (render, confirm, stream to the user)
- **Do not** promote an action to a dedicated tool just to constrain *how*
  Claude reasons about it
- **Do not** force every tool result back through the context window. Give
  Claude a code execution surface (bash, REPL) so it can filter, pipe, or
  transform tool output without spending context tokens on data it does not
  need to read
- Keep tool schemas stable across turns to maximize prompt cache hits; churn
  in tool definitions invalidates the cache

## Review Triggers

Revisit this file and the harness when any of these change:

- Claude model version (new Opus / Sonnet / Haiku release)
- Tool surface area (adding, removing, or renaming tools)
- Reports of the agent "giving up early," looping, or ignoring context
- Latency or token-cost regressions tied to tool-result handling
