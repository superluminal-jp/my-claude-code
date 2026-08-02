# Subagent Delegation Rules

Purpose: decide **where** a piece of work runs — in this conversation, or in a subagent with its own context. Applies when planning any non-trivial task, before starting it. Composes with `.claude/CLAUDE.md` § Execution, which governs *how* to issue calls once delegation is decided; this file governs *whether* to delegate at all. Grounded in the official Claude Code documentation (see [References](#references)).

The operator's explicit instruction always wins. This file decides the default when they have not said.

## Delegate when

- **The work produces far more output than its conclusion needs.** This is the primary case: *"One of the most effective uses for subagents is isolating operations that produce large amounts of output. Running tests, fetching documentation, or processing log files can consume significant context."* Broad file sweeps, log processing, and full-suite runs qualify.
- **The work is self-contained and can return a summary** — the caller needs the finding, not the trail that produced it.
- **Tool or permission restrictions should be enforced** rather than requested. A subagent's `tools` allowlist makes a constraint structural instead of an instruction.
- **Several investigations are independent.** Delegate them in parallel; they do not queue behind each other.

Delegate **before** exploring, not after. A subagent starts fresh and keeps a separate prompt cache, so work delegated once the conversation has already read the files pays for that discovery twice.

## Stay in the main conversation when

- The task needs **back-and-forth or iterative refinement**.
- Multiple phases **share significant context** — planning, implementation, and testing on one thread.
- The change is **quick and targeted**; the handoff would cost more than the work.
- **Latency matters.** A subagent starts cold and spends time gathering context the conversation already has.
- The **deliverable itself is the output.** Isolation saves nothing when the full result must return regardless.

## What a subagent does not have

These are the reasons behind the two lists above, not separate advice:

- **No conversation history.** *"It doesn't see your conversation history, the skills you've already invoked, or the files Claude has already read."* Everything it needs goes in the delegation message, restated.
- **No way to ask.** `AskUserQuestion` is removed from every subagent regardless of its `tools` field. Work carrying an unresolved decision must not be delegated — the subagent cannot surface it and will resolve it silently. Clarify first (`rules/clarifier.md`), then delegate.
- **No free lunch.** *"When subagents complete, their results return to your main conversation. Running many subagents that each return detailed results can consume significant context."* Delegation moves context cost; it does not remove it. Ask for a compact report, and prefer one well-scoped subagent to several overlapping ones.

Spawn counts are capped per session and per concurrent run, so treat subagents as a budgeted resource rather than a reflex.

## Choosing the mechanism

| Situation | Mechanism |
|---|---|
| A repeatable procedure that *is* the task | Skill with `context: fork` — the skill body becomes the prompt |
| A worker that needs standing conventions, with the task supplied per call | Subagent with a `skills:` field — preloads that guidance at startup |
| A one-off bounded task | Direct delegation with an explicit prompt; no new artifact |

Never fork guidance that carries no task: *"`context: fork` only makes sense for skills with explicit instructions. If your skill contains guidelines like 'use these API conventions' without a task, the subagent receives the guidelines but no actionable prompt, and returns without meaningful output."* Standing conventions belong in a `skills:` preload, not a fork.

## Reporting back

A delegated result is a claim the conversation did not witness. Report what the subagent found as its finding, verify anything load-bearing before acting on it, and never present a still-running subagent's result as complete.

## References

Living documentation — cited with the date read, since these pages change.

- Anthropic, *Create custom subagents* (Claude Code documentation), read 2026-08-02 — <https://code.claude.com/docs/en/sub-agents>
- Anthropic, *Extend Claude with skills* (Claude Code documentation), read 2026-08-02 — <https://code.claude.com/docs/en/skills>
