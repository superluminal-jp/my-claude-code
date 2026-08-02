# Phase 0 Research: Where the delegation rule belongs, and what it may claim

**Feature**: `020-subagent-delegation-rule`

**Date**: 2026-08-02

## R1. Placement — the question the user asked

**Decision**: A new always-on rule at `.claude/rules/subagent-delegation.md`, imported from `.claude/CLAUDE.md`. The guidance itself does **not** go in `.claude/CLAUDE.md`.

**Rationale**: This repository has an established shape, and the candidate homes fail on it in different ways.

| Candidate | Verdict |
|---|---|
| `.claude/CLAUDE.md` body | ✗ The file is a **routing and principles index**, not a playbook. Every substantive procedure it references — clarification, skill routing, live documentation, MCP — lives in `.claude/rules/` behind an `@`-import, with at most a short orienting sentence left inline. Putting a full decision procedure in the body breaks the pattern the other four already set. |
| `.claude/skills/<name>/SKILL.md` | ✗ Skills load **on demand, by relevance**. The delegation decision is made when planning *any* task, including tasks that match no skill. A skill would be consulted exactly when it is least needed. |
| `.claude/rules/subagent-delegation.md` | ✅ Matches what `.claude/rules/` is for: always-applicable, cross-cutting, sourced. |
| `coder` skill | ✗ Delegation applies to research, review, and document work too, not only code. |

**The cost this decision has to answer for**: `.claude/rules/` is always loaded. The existing always-on set — `.claude/CLAUDE.md` plus its four imports plus `permissions.md` and `git-workflow.md` — measures ~31 KB. A rule about spending context frugally that itself bloats every turn would be self-defeating, so the rule is written as decision criteria, not as an explanation of the subagent feature. Terse is a requirement here, not a style preference.

**Alternative considered and rejected**: leaving the guidance implicit and relying on the harness's own system prompt. Rejected because the harness prompt is not version-controlled by this repository, is not visible to contributors, and cannot be cited in review — the same reasons `.claude/CLAUDE.md` prefers repo documentation over agent-only memory.

## R2. Reconciling the overlap with the existing "Execution" section

`.claude/CLAUDE.md` § "Execution: parallelize whenever valid" already says independent subagent launches go in one message. That is a **parallelism** rule, not a **delegation** rule: it governs how to issue calls once you have decided to make them.

Per `rules/live-documentation.md` § 5 (No Redundancy), the two must not both state the same thing. Resolution: the parallelism section keeps ownership of "issue independent calls together" and gains a pointer to the new rule for "should this be a subagent at all". The new rule does not restate the parallelism guidance.

## R3. What the rule is allowed to claim

Every behavioural claim traces to the official documentation. Sources are the Claude Code documentation pages `code.claude.com/docs/en/sub-agents` and `code.claude.com/docs/en/skills`, read on 2026-08-02.

| Claim in the rule | Supporting text |
|---|---|
| Isolating high-volume output is the primary use | "One of the most effective uses for subagents is isolating operations that produce large amounts of output. Running tests, fetching documentation, or processing log files can consume significant context." |
| Delegate when output is verbose / constraints must be enforced / work is self-contained | The documentation's "Use **subagents** when" list. |
| Stay inline for back-and-forth, shared multi-phase context, quick edits, latency | The documentation's "Use the **main conversation** when" list, including "Subagents start fresh and may need time to gather context". |
| A subagent sees none of the conversation | "Each subagent starts with a fresh, isolated context window. It doesn't see your conversation history, the skills you've already invoked, or the files Claude has already read." |
| A subagent cannot ask the operator | `AskUserQuestion` appears in the list of tools removed from every subagent regardless of the `tools` field. |
| Delegation is not free | "When subagents complete, their results return to your main conversation. Running many subagents that each return detailed results can consume significant context." |
| Delegating after exploring pays twice | The fork-vs-named-subagent comparison: a named subagent has a "Separate cache", where a fork "Shared with main session"; plus the fresh-context statement above. |
| A guidelines-only skill must not be forked | "`context: fork` only makes sense for skills with explicit instructions. If your skill contains guidelines like 'use these API conventions' without a task, the subagent receives the guidelines but no actionable prompt, and returns without meaningful output." |
| Two mechanisms, opposite directions | The skills page's comparison of "Skill with `context: fork`" against "Subagent with `skills` field". |
| Spawn limits exist | Session limit of 200 per session; concurrent limit of 20. Both are defaults with environment-variable overrides. |

**Deliberately excluded**: version-gated details (`min-version` notes), environment-variable names, and the exact tool lists for background subagents. They are accurate today but churn with releases, and an always-loaded rule that goes stale is worse than one that stays general. The rule points at the documentation for specifics.

## R4. Citation form

`.claude/rules/*.md` files end with a `## References` section listing sources as `Author/Publisher, *Title*, year — <URL>`. The new rule follows that form. Unlike the existing rules, whose sources are books and ISO standards, this rule's sources are living documentation pages, so each citation carries the date it was read — the same discipline the repository applies elsewhere to distinguish fact from inference.

## R5. Cross-agent parity

`tests/run-codex-sync.sh` SYNC-08 walks `find .claude -type f` and requires each path to appear literally in `.codex/README.md`; `.claude/rules/*` has no blanket exemption (only `.claude/skills/*` does). A new rule file therefore **requires** a deployment-map row.

The row is `対象外`: Codex CLI has no subagent mechanism, so there is nothing to map the guidance onto. This differs from the other `.claude/rules/*` entries, which are all `本機能で移植(014)` into `.codex/AGENTS.md` sections. Recording it as intentionally-not-ported with a stated reason is what the map's own legend requires.

SYNC-03 checks `.codex/AGENTS.md` for four specific headings; none is added or removed here, so it is unaffected.
