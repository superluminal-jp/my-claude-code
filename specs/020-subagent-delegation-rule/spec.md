# Feature Specification: A grounded rule for when to delegate work to a subagent

**Feature Branch**: `020-subagent-delegation-rule`

**Created**: 2026-08-02

**Status**: Draft

**Input**: User description: "効率的なサブエージェント委譲のプラクティスを適切な指示に追加。引用元を明記して。CLAUDE.md に追記が適切か？"

## Context

This repository instructs an agent on how to work, but says almost nothing about *where* work should run. `.claude/CLAUDE.md` § "Execution: parallelize whenever valid" mentions subagent launches only as an example of parallelism — it says to launch independent research tracks together, not when a subagent is the right vehicle at all.

Delegation is therefore decided ad hoc, and two failure modes follow: verbose, self-contained work stays in the main conversation and consumes context that is never referenced again; and interactive or iterative work gets delegated to a subagent that cannot ask a question and cannot see the conversation.

Feature 019 acted on this reasoning for one case (`/verify-config`) without writing the reasoning down. This feature records the general rule.

### The placement question

The user asks whether `.claude/CLAUDE.md` is the right home. It is not, and the spec treats placement as a requirement rather than an implementation detail, because the wrong placement carries a measurable cost: `.claude/CLAUDE.md` and its imports load on **every** turn. A rule about conserving context must not itself be careless with context.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The agent delegates verbose, self-contained work instead of absorbing it (Priority: P1)

An operator asks for something whose execution produces far more output than its conclusion needs — running a full test suite, processing logs, sweeping many files for one answer. The agent recognises the shape, runs it in a subagent, and brings back the conclusion rather than the transcript.

**Why this priority**: This is the case the official documentation names as the single most effective use of subagents, and the case this repository currently leaves to chance.

**Independent Test**: Issue a request whose work is high-volume and self-contained, and confirm the agent delegates rather than running it inline.

**Acceptance Scenarios**:

1. **Given** a request whose execution produces large volumes of output not needed afterwards, **When** the agent plans the work, **Then** it delegates that work to a subagent and reports only the result.
2. **Given** several independent investigations, **When** the agent plans them, **Then** it delegates them in parallel rather than sequentially.

---

### User Story 2 - The agent keeps interactive and iterative work in the main conversation (Priority: P1)

An operator asks for something that needs their input, or that will proceed in rounds informed by what came before. The agent keeps that work inline instead of delegating it into a context that cannot ask questions and cannot see the conversation.

**Why this priority**: Equal to Story 1 and the more damaging failure. Over-delegation does not merely waste effort — a subagent that meets an ambiguity has no way to resolve it and will guess, silently.

**Independent Test**: Issue a request with an unresolved decision in it and confirm the agent does not delegate it away.

**Acceptance Scenarios**:

1. **Given** a request that will need a decision from the operator mid-flight, **When** the agent plans the work, **Then** it keeps that work in the main conversation.
2. **Given** work that depends on context the main conversation has already established, **When** the agent plans it, **Then** it either keeps the work inline or restates the needed context in the delegation.
3. **Given** guidance material with no actionable task, **When** the agent considers running it in a forked context, **Then** it does not, because the forked run would have nothing to execute.

---

### User Story 3 - A reader can check the guidance against its source (Priority: P2)

A contributor who doubts a claim in the rule can follow it to the official documentation that supports it, in the same way every other rule in this repository can be checked.

**Why this priority**: Lower than P1 because the rule functions without it, but this repository's first Core Principle is grounding claims in verifiable sources, and every existing file in `.claude/rules/` carries a References section. A rule about agent behaviour that could not be checked against the tool's own documentation would be the only unsourced rule in the set.

**Independent Test**: Read the rule's References section and confirm each substantive claim traces to a cited source.

**Acceptance Scenarios**:

1. **Given** the new rule, **When** a reader reaches the end, **Then** a References section lists the official documentation pages the guidance is drawn from.
2. **Given** a claim in the rule about how subagents behave, **When** a reader checks the cited source, **Then** the source supports the claim.

---

### Edge Cases

- **The guidance contradicts a direct instruction.** An operator who explicitly asks for work to run inline, or in a subagent, overrides the heuristic. The rule advises; it does not override the operator.
- **Delegation is possible but pointless.** Work whose output *is* the deliverable gains nothing from isolation, because the deliverable returns to the main conversation either way. The rule must not push delegation in that case.
- **The main conversation has already done the exploration.** Delegating afterwards pays for the same discovery twice, since a subagent starts fresh and does not share the parent's prompt cache. Timing is part of the decision, not just suitability.
- **Many subagents each return a detailed report.** Delegation moves context cost; it does not eliminate it. The rule must say so rather than presenting subagents as free.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The guidance MUST state the conditions under which work is delegated to a subagent.
- **FR-002**: The guidance MUST state the conditions under which work stays in the main conversation.
- **FR-003**: The guidance MUST name the capabilities a subagent does not have, so that FR-001 and FR-002 are derivable rather than arbitrary.
- **FR-004**: The guidance MUST distinguish the available delegation mechanisms and state which situation each fits.
- **FR-005**: The guidance MUST state that a subagent's returned result consumes main-conversation context, so delegation is not presented as free.
- **FR-006**: The guidance MUST cite the official documentation it is drawn from, in the same form as the other rule files in this repository.
- **FR-007**: The guidance MUST live in the location this repository's own conventions dictate for always-applicable rules, and MUST NOT duplicate content that already exists elsewhere in the repository.
- **FR-008**: Existing text that overlaps the new guidance MUST be reconciled — either narrowed to point at the new rule, or left as the single source with the new rule pointing back — never both stating the same thing.
- **FR-009**: The addition MUST NOT break the repository's cross-agent drift checks, and any element with no counterpart in another harness MUST be recorded as such with a reason.

### Key Entities

- **Delegation decision**: the per-task choice between running work in the main conversation and running it in a subagent.
- **Delegation mechanism**: the concrete means of delegating — a forked skill, a subagent with preloaded skills, or a direct task handoff.
- **Rule file**: an always-applicable instruction document in `.claude/rules/`, carrying a purpose, its scope, its guidance, and its sources.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Given a request whose work is high-volume and self-contained, the agent delegates it rather than running it inline.
- **SC-002**: Given a request requiring operator input mid-flight, the agent does not delegate it.
- **SC-003**: Every behavioural claim in the new guidance traces to a cited source; a reader can verify each without consulting the author.
- **SC-004**: No statement in the new guidance is duplicated verbatim elsewhere in the repository.
- **SC-005**: The repository's existing test suites pass unchanged after the addition.
- **SC-006**: The always-loaded instruction set grows by the rule itself and nothing more — no second copy of the guidance is added to another always-loaded file.

## Assumptions

- The official Claude Code documentation is the authoritative source for how subagents behave. Where this repository's experience differs, the documentation wins and the difference is worth reporting, not encoding.
- The guidance targets an agent reading it as instructions, not a human reading it as a tutorial. It is therefore written as decision criteria, not as an explanation of the feature.
- Codex CLI has no subagent equivalent, so this rule is expected to be Claude-specific and to be recorded as intentionally not ported.
- The project constitution (`.specify/memory/constitution.md`) remains an unfilled template, so no constitutional gate applies beyond `.claude/CLAUDE.md` and `.claude/rules/`.
