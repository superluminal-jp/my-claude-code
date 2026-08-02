# Phase 0 Research: Isolating verification output

**Feature**: `019-verify-fork-test-runner`

**Date**: 2026-08-02

Sources are the official Claude Code documentation at `code.claude.com/docs/en/skills` and `code.claude.com/docs/en/sub-agents`, read during this feature's investigation. Quoted text is from those pages.

## R1. Which isolation mechanism fits the configuration check

**Decision**: Run it as a skill with `context: fork`.

**Rationale**: Two mechanisms exist, and they differ in where the task comes from.

| Approach | System prompt | Task |
|---|---|---|
| Skill with `context: fork` | From the agent type | The SKILL.md content |
| Subagent with `skills:` field | The subagent's body | The delegating message |

The documentation warns that the first only works for skills that carry an actionable task:

> `context: fork` only makes sense for skills with explicit instructions. If your skill contains guidelines like "use these API conventions" without a task, the subagent receives the guidelines but no actionable prompt, and returns without meaningful output.

The existing `verify-config` body is a six-step numbered procedure ending in "Report each step as ✓/✗ … End with the overall verdict." That is an actionable task, so `context: fork` applies cleanly.

**Alternatives rejected**:

- *Leave it as-is in `.claude/commands/`* — does not isolate anything; the raw output keeps landing in the main conversation. This is the status quo the feature exists to change.
- *A subagent with `skills: [verify-config]`* — inverts the relationship: the procedure would become reference material rather than the task, and would need a delegating message to restate it. Redundant.

## R2. Why the file must move out of `.claude/commands/`

**Decision**: Migrate `.claude/commands/verify-config.md` to `.claude/skills/verify-config/SKILL.md`.

**Rationale**: The documentation states that commands and skills both produce `/name` and "work the same way", and that existing `.claude/commands/` files keep working, but it scopes the added capabilities to skills:

> Skills add optional features: a directory for supporting files, frontmatter to control whether you or Claude invokes them, and the ability for Claude to load them automatically when relevant.

`context: fork` is documented only as a SKILL.md frontmatter field. Rather than depend on unverified behaviour of that field inside `.claude/commands/`, the file moves to the documented location. The invocation path `/verify-config` is unchanged by the move.

## R3. Foreground vs background for the fork

**Decision**: Set `background: false`.

**Rationale**: Two documented reasons.

1. Tool set. A backgrounded fork runs with the reduced built-in tool set that applies to background subagents; the documentation instructs: "If your skill's steps depend on a tool outside that set, set `background: false` to keep the full tool set." This satisfies FR-008 without having to reason about which filter applies.
2. Concurrency. Verification is something an operator waits on — a verdict that arrives detached from the request is of little use, and the spec's concurrent-invocation edge case is avoided outright because the result is consumed in the invoking turn.

The documentation also notes Claude Code waits for a forked skill regardless in non-interactive mode (`-p` / Agent SDK), so `background: false` makes interactive and non-interactive behaviour agree rather than diverge.

**Trade-off accepted**: the operator's turn blocks for the duration of the run. This is the intended behaviour for a verification gate.

## R4. Which agent type executes the fork

**Decision**: A new project subagent, read-only by construction, named in the skill's `agent` field. The same subagent serves the behaviour-suite runs.

**Rationale**: The `agent` field "determines the execution environment (model, tools, and permissions)", defaulting to `general-purpose` when omitted. The candidates:

- `general-purpose` (the default) — carries `Edit`/`Write`. FR-003 and FR-007 ("MUST NOT modify any file") would rest on instruction text alone.
- `Explore` — read-only and has `Bash`, but it skips CLAUDE.md, is one-shot and cannot be resumed, and its prompt is oriented to codebase search rather than executing a numbered procedure.
- A project subagent with `tools` restricted to `Read, Grep, Glob, Bash` — makes "does not modify files" a property of the execution environment rather than a request. The documentation presents `tools` as an allowlist for exactly this: "The subagent can't edit files, write files, or use any MCP tools."

The third makes FR-003/FR-007 structurally enforced, and it is the artifact the behaviour-suite delegation needs anyway. One subagent serves both stories, so no duplicate definition is introduced.

**Note on the residual risk**: `Bash` can still write (`>`, `sed -i`). The tool restriction removes the accidental path, not every path; the instruction to report diffs only remains necessary. The repository's `pre-bash.sh` hook is the backstop for destructive commands.

## R5. What the fork does *not* inherit

**Constraint recorded, not a decision.** A fork of this kind starts without the parent's conversation:

> Add `context: fork` to your frontmatter when you want a skill to run in isolation. The skill content becomes the prompt that drives the subagent. It won't have access to your conversation history.

Two consequences shape the design:

1. The SKILL.md body must be self-sufficient — every path, command, and reporting rule stated inline. It already is. This is FR-010.
2. `AskUserQuestion` is removed from every subagent, so the run cannot ask the operator anything. Verification is non-interactive by nature, which is what makes this safe; the spec records it as a constraint (Edge Cases) rather than leaving it implicit.

CLAUDE.md *is* loaded for a forked skill except when the agent is `Explore` or `Plan`, so the repository's rules still reach the run under R4's decision.

## R6. Preserving the existing permission grants

**Decision**: Carry the existing `allowed-tools` frontmatter across the move verbatim.

**Rationale**: The current command pre-approves the exact Bash patterns it needs (`jq`, `shellcheck`, `shfmt`, `yamllint`, `scripts/check-mcp-consistency.sh`, `tests/run-*.sh`). Dropping it would make the isolated run hit approval prompts mid-procedure. The documentation notes a background subagent surfaces permission prompts in the main session and that a denial fails only that call — which for a verification run would be misreported as a failed check. The spec calls this out as an edge case; preserving `allowed-tools` is the mitigation.

## R7. Scope boundary

The checks themselves — which tools run, in what order, what counts as a hard failure — are carried over unchanged. This feature relocates execution. Any change to *what* is verified is out of scope and would be a separate spec.
