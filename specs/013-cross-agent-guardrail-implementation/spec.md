# Feature Specification: Cross-Agent Guardrail Implementation (AGENTS.md Rollout)

**Feature Branch**: `013-cross-agent-guardrail-implementation`

**Created**: 2026-07-19

**Status**: Draft

**Input**: User description: "`.claude`のスキルやルールをOpenAI Codexも参照できるようにする" (make `.claude`'s skills and rules referenceable by OpenAI Codex too). Scoped, on confirmation, to implementing the decisions already recorded in `specs/012-cross-agent-guardrail-migration/decision-record.md`: publish a shared `AGENTS.md` at the repository root carrying the 13 prose-appropriate items, and reproduce real destructive-command enforcement (Q6) for Codex CLI and Cursor via a shared script with thin per-tool adapters. No re-litigation of the 14 verdicts already decided in spec 012 is in scope.

## Overview

Spec 012 answered, for each of 14 Claude Code-specific `.claude/` hooks and rules, whether it should be unified for OpenAI Codex CLI and Cursor compatibility — and if so, at what strength (full enforcement vs. prose-only note). That decision record is final and committed; **this feature is the follow-up build that turns those decisions into files that actually exist**: today there is no `AGENTS.md` in the repository, and `.claude/hooks/pre-bash.sh`'s destructive-command blocking has no Codex CLI or Cursor counterpart.

This specification defines what must exist for a maintainer working in this repository through Codex CLI or Cursor to receive (a) the same baseline guidance Claude Code sessions already get, and (b) the same destructive-command protection Claude Code sessions already get. It does not redefine which items are unified or at what strength — those are fixed inputs from `specs/012-cross-agent-guardrail-migration/decision-record.md`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Shared baseline guidance via AGENTS.md (Priority: P1)

A maintainer opens this repository in Codex CLI or Cursor instead of Claude Code. They want the same baseline guidance Claude Code sessions get from `.claude/rules/*` — the 13 items spec 012 decided to unify (6 full, 7 weak; Q6 is excluded here because its unification is a real hook, not prose, and is covered by User Stories 2–3) — available to them without opening `.claude/` at all.

**Why this priority**: This is the highest-value, lowest-risk deliverable — it is markdown content only, requires no new hook mechanism, and depends on nothing else in this feature. It alone gives Codex CLI and Cursor sessions parity with Claude Code's non-enforcement guidance.

**Independent Test**: With only `AGENTS.md` created (no adapters yet), a reviewer opens the file and confirms all 13 items from the decision record are present, each phrased at the strength (full vs. weak) that record specifies, independent of whether User Story 2 or 3 has shipped.

**Acceptance Scenarios**:

1. **Given** decision-record.md's `unify_full` verdicts for Q1, Q2, Q3, Q4, and Q14, **When** `AGENTS.md` is created, **Then** it contains an entry for each, with Q2's tool references genericized (no `Read`/`Edit`/`Grep`-style Claude Code tool names) and Q3's SKILL.md-discoverability precondition stated as an explicit open dependency rather than assumed.
2. **Given** decision-record.md's `unify_weak` verdicts for Q5, Q7, Q8, Q9, Q10, Q11, Q12, and Q13, **When** `AGENTS.md` is created, **Then** it contains a prose-only entry for each, worded as a note or request rather than a guarantee, and Q13's entry names no Claude Code-specific mechanism (e.g. does not say "Claude Memory").
3. **Given** `AGENTS.md` does not exist yet in this repository, **When** it is created, **Then** it is a new file at the repository root (not nested under `.claude/`, `.codex/`, or `.cursor/`), matching the shared-file premise `specs/012-cross-agent-guardrail-migration/research.md`'s R5 finding relies on.
4. **Given** a hypothetical future run where `AGENTS.md` already exists with unrelated maintainer content, **When** this feature's rollout runs, **Then** the existing content is surfaced to the maintainer before any overwrite, not silently replaced.

---

### User Story 2 - Real destructive-command blocking for Codex CLI (Priority: P2)

A maintainer runs a destructive shell command (force push, `rm -rf ~`, `curl | bash`, etc.) from a Codex CLI session in this repository. Today nothing stops them — only Claude Code has this protection. They want the same block/ask outcome Claude Code already gives.

**Why this priority**: Decision-record.md flags Q6 as "the only item, of all 14, where real enforcement can be reproduced across all three tools" — this is the highest-security-value item in the whole feature, but it requires new code (a shared matcher script plus a tool adapter), so it ranks below the zero-risk documentation win in User Story 1.

**Independent Test**: With `.claude/hooks/pre-bash.sh`'s matching logic extracted into a shared script and a Codex CLI adapter wired to it, run each destructive-command category (force push, `git reset --hard`, `git clean -f`, `rm -rf` against root/home/cwd, other `rm -rf`, `mkfs`/`dd`/fork-bomb, `curl|bash`, non-HTTPS request, credential-path read, credential-path write, global package install, `sudo`) through a Codex CLI session and confirm the same allow/deny/ask outcome Claude Code produces for that same command — independent of whether User Story 3 (Cursor) has shipped.

**Acceptance Scenarios**:

1. **Given** a command matching a currently-hard-blocked category (e.g. `git push --force`, `rm -rf /`), **When** it is run through the Codex CLI adapter, **Then** the command is denied before execution.
2. **Given** a command matching a currently-"ask"-routed category (`rm -rf` outside root/home/cwd, `sudo`), **When** it is run through the Codex CLI adapter, **Then** the adapter either routes it to confirmation (if Codex CLI's hook contract supports a three-way decision) or denies it by default (if it does not) — never silently allows it.
3. **Given** a benign command matching none of the categories, **When** it is run through the Codex CLI adapter, **Then** it is allowed.
4. **Given** `research.md`'s R1 (Codex CLI `PreToolUse` Bash-only scope) is flagged Medium-confidence, **When** the adapter is implemented, **Then** R1's claim is re-verified against Codex CLI's primary documentation before the adapter is considered complete.

---

### User Story 3 - Real destructive-command blocking for Cursor (Priority: P3)

The same protection as User Story 2, delivered for Cursor sessions via its `beforeShellExecution` hook.

**Why this priority**: Same shared script as User Story 2, but a distinct per-tool adapter and a distinct config surface (Cursor hook registration, not Codex CLI's). Ranked after Codex CLI only because the two are independently deployable and Codex CLI was named first in the originating request; there is no technical dependency forcing this order beyond both depending on the shared script existing.

**Independent Test**: With the same shared script from User Story 2 and a Cursor `beforeShellExecution` adapter (`failClosed: true`) wired to it, run the same destructive-command categories through a Cursor session and confirm the same allow/deny/ask outcome, independent of Codex CLI's adapter status.

**Acceptance Scenarios**:

1. **Given** a command matching a currently-hard-blocked category, **When** it is run through the Cursor adapter, **Then** the command is denied before execution, and `failClosed: true` ensures a hook error or timeout also denies rather than allows.
2. **Given** a command matching a currently-"ask"-routed category, **When** it is run through the Cursor adapter, **Then** it is routed to Cursor's `ask` permission (per `research.md` R2's `{permission: allow|deny|ask}` shape).
3. **Given** `research.md`'s R2/R3 (Cursor's hook shape and its `permissions.json` allowlist being explicitly not a security guarantee) are flagged Medium/Medium-high confidence, **When** the adapter is implemented, **Then** both claims are re-verified against Cursor's primary documentation before the adapter is considered complete, and the adapter uses the `beforeShellExecution` hook rather than `permissions.json` regardless (per R3's rationale).

### Edge Cases

- What happens if a destructive-command category's decision is "ask" but the target tool's hook contract only supports a binary allow/deny? The adapter MUST default to deny (fail-safe default), never allow.
- What happens if the shared script itself errors (crashes, times out, unexpected input)? Each adapter MUST treat a script error the same way it treats a "deny" decision, not an "allow" — a broken guardrail must fail closed, not fail open.
- What happens if `.claude/hooks/pre-bash.sh`'s behavior changes in the future (a new destructive-command category is added)? Because the matching logic is extracted into one shared script that all three tools' adapters call, a future addition made once in the shared script propagates to all three automatically — this is a design property to preserve, not a scenario requiring new tests today.
- What happens if Codex CLI's or Cursor's actual hook behavior (once re-verified per FR-011) turns out to differ from `research.md`'s R1/R2/R3 assumptions? The adapter for that tool MUST be adjusted to match the verified behavior before being considered complete; the acceptance scenarios in User Stories 2–3 that cite re-verification are blocking, not advisory.
- What happens to Claude Code's own `pre-bash.sh` behavior during this refactor? It MUST produce identical outcomes before and after the shared-script extraction — this feature must not regress the one guardrail that already works.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a root-level `AGENTS.md` file containing one entry for each of the 13 non-Q6 items recorded in `specs/012-cross-agent-guardrail-migration/decision-record.md` (Q1–Q5, Q7–Q14).
- **FR-002**: For each `unify_weak` item (Q5, Q7, Q8, Q9, Q10, Q11, Q12, Q13), the `AGENTS.md` wording MUST NOT imply the enforcement guarantee the original Claude Code mechanism had — phrased as a note or request, per that item's decision-record rationale.
- **FR-003**: Q2's `AGENTS.md` entry MUST use tool-agnostic vocabulary (no Claude Code-specific tool names).
- **FR-004**: Q3's `AGENTS.md` entry MUST state the SKILL.md cross-tool discoverability precondition explicitly as an open, unconfirmed dependency.
- **FR-005**: Q13's and Q14's `AGENTS.md` entries MUST NOT name a Claude Code-specific mechanism (Claude Memory, the `Agent` tool, `subagent_type` values).
- **FR-006**: The system MUST provide one shared script encoding `.claude/hooks/pre-bash.sh`'s destructive-command matching logic (force push, `git reset --hard`, `git clean -f`, `rm -rf` against root/home/cwd, other `rm -rf`, `mkfs`/`dd`/fork-bomb, `curl|bash`, non-HTTPS request, credential-path read, credential-path write, global package installs, `sudo`), exposing one tool-agnostic decision (allow / deny / ask) plus a human-readable reason per invocation.
- **FR-007**: The system MUST provide a Codex CLI adapter that invokes the shared script from a `PreToolUse` hook scoped to Bash tool calls and translates its decision into Codex CLI's expected hook response.
- **FR-008**: The system MUST provide a Cursor adapter that invokes the shared script from a `beforeShellExecution` hook with `failClosed: true` and translates its decision into Cursor's `{permission, user_message, agent_message}` response shape.
- **FR-009**: Where the shared script's decision is "ask" and a target tool's hook contract has no three-way primitive, that tool's adapter MUST default to deny rather than allow.
- **FR-010**: `.claude/hooks/pre-bash.sh` MUST continue to produce identical allow/deny/ask outcomes for every existing test case after being refactored to call the shared script — zero behavior regression for Claude Code.
- **FR-011**: Before the Codex CLI and Cursor adapters are considered complete, the implementation MUST re-verify `research.md`'s R1 (Codex CLI `PreToolUse` Bash-only scope and response shape) and R2/R3 (Cursor `beforeShellExecution` shape, `failClosed` behavior, and `permissions.json` non-guarantee) against each vendor's primary documentation, since the decision record flags both as Medium-confidence.
- **FR-012**: If `AGENTS.md` already exists at the time this feature is implemented, the system MUST surface its current content to the maintainer before any content is overwritten.
- **FR-013**: The system MUST provide an automated test suite covering every destructive-command category in FR-006, run against the shared script directly and against each of the three integration points (Claude Code hook, Codex CLI adapter, Cursor adapter).

### Key Entities

- **AGENTS.md**: Shared, tool-agnostic instruction file at the repository root; the single carrier of all 13 prose-appropriate decision-record items, read natively by Codex CLI and Cursor without additional per-tool configuration.
- **Shared guardrail script**: Single source of truth for destructive-command matching logic, tool-agnostic in its inputs (a shell command string) and outputs (allow/deny/ask + reason).
- **Codex CLI adapter**: Thin translation layer between the shared script's decision and Codex CLI's `PreToolUse` hook contract.
- **Cursor adapter**: Thin translation layer between the shared script's decision and Cursor's `beforeShellExecution` hook contract.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All 13 non-Q6 decision-record items have a corresponding, verifiable entry in `AGENTS.md` (13/13, checked by a reviewer against `decision-record.md`).
- **SC-002**: Every destructive-command test case that currently passes against `.claude/hooks/pre-bash.sh` produces the identical allow/deny/ask outcome when run through the Codex CLI adapter and the Cursor adapter (100% parity across all three entry points).
- **SC-003**: `.claude/hooks/pre-bash.sh`'s own existing behavior shows zero regressions after the shared-script refactor (100% of its current test cases still pass).
- **SC-004**: A maintainer working from a fresh Codex CLI or Cursor session (no prior context of spec 012) can, by reading only `AGENTS.md`, correctly state for any of the 13 items whether it is enforced or advisory-only.
- **SC-005**: Attempting a hard-blocked destructive command from a Codex CLI or Cursor session in this repository is denied before execution, with no successful execution path found during testing.

## Assumptions

- Codex CLI and Cursor are both actively used to work in this repository going forward — the premise of the original request and confirmed by the maintainer during scoping.
- `specs/012-cross-agent-guardrail-migration/research.md`'s R1–R5 findings are the accepted starting point for design, but R1–R3 (Medium/Medium-high confidence) must be re-verified against primary vendor documentation before the Codex CLI and Cursor adapters ship (FR-011) — R4 and R5 need no re-verification here since neither is load-bearing for this feature's scope (R4 concerns the pre-edit items already resolved as prose-only in spec 012; R5 is already High confidence).
- No test suite currently exists for `.claude/hooks/pre-bash.sh`'s destructive-command categories (confirmed: `tests/` has no `pre-bash`-related suite); one must be created as part of this feature rather than merely extended.
- `AGENTS.md` is the single shared file for both target tools, per R5 — this feature does not introduce a per-tool `CODEX.md` or `.cursor/rules` split.
- Where the shared script returns "ask" and a target tool's hook has no three-way decision primitive, the fail-safe default (deny) applies, consistent with this repository's existing least-privilege / fail-safe-default permission philosophy.
