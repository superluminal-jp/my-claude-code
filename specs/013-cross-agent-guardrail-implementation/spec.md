# Feature Specification: Cross-Agent Guardrail Implementation (AGENTS.md Rollout)

**Feature Branch**: `013-cross-agent-guardrail-implementation`

**Created**: 2026-07-19

**Status**: Draft

**Input**: User description: "`.claude`のスキルやルールをOpenAI Codexも参照できるようにする" (make `.claude`'s skills and rules referenceable by OpenAI Codex too). Scoped, on confirmation, to implementing the decisions already recorded in `specs/012-cross-agent-guardrail-migration/decision-record.md`: publish a shared `AGENTS.md` at the repository root carrying the 13 prose-appropriate items, and reproduce real destructive-command enforcement (Q6) for Codex CLI and Cursor via a shared script with thin per-tool adapters. No re-litigation of the 14 verdicts already decided in spec 012 is in scope.

**Follow-up correction 1 (same session)**: The maintainer identified, via [learn.chatgpt.com/docs/build-skills](https://learn.chatgpt.com/docs/build-skills), that Codex CLI natively scans `.agents/skills/<name>/SKILL.md` from the current directory up to the repository root — a real skill-discovery mechanism distinct from `AGENTS.md` prose, and already in active use in this repository for the 15 `speckit-*` skills (synced there by the existing `speckit-expand-update.sh` hook). This repository's 9 other, hand-authored skills (`adr`, `advisor`, `clarifier`, `coder`, `domain-model`, `minto-builder`, `minto-reviewer`, `minto-rewriter`, `ubiquitous-language`) are not synced anywhere outside `.claude/skills/`. On confirmation, Q3's `AGENTS.md`-prose treatment (a routing-table transcription) is superseded, for Codex CLI, by native sync into `.agents/skills/` — a stronger, zero-drift mechanism the original spec 012 decision did not have evidence for.

**Follow-up correction 2 (same session)**: The maintainer identified, via [learn.chatgpt.com/docs/hooks](https://learn.chatgpt.com/docs/hooks), that Codex CLI's `PreToolUse`/`PostToolUse` hooks cover `apply_patch`/`Edit`/`Write` (file-edit tools), not just Bash — contradicting `specs/012-cross-agent-guardrail-migration/research.md`'s R4 ("no tool has a pre-edit... file-write block") for Codex CLI specifically, and matching `.claude/hooks/pre-edit.sh`'s and `post-edit-format.sh`'s own stdin/stdout contract closely enough that reuse is straightforward. On confirmation, Q9 (main/master block) and Q10 (`.git/` block) are upgraded from `unify_weak` (prose-only) to real enforcement for Codex CLI, and Q7 (post-edit auto-format) is upgraded the same way for Codex CLI — in each case, **Cursor's treatment is unchanged** from spec 012's original recorded verdict (still prose-only; this correction's source did not cover Cursor).

Spec 012's own decision record is not rewritten by either correction (already committed); this spec absorbs both since it is still in Draft.

## Overview

Spec 012 answered, for each of 14 Claude Code-specific `.claude/` hooks and rules, whether it should be unified for OpenAI Codex CLI and Cursor compatibility — and if so, at what strength (full enforcement vs. prose-only note). That decision record is final and committed; **this feature is the follow-up build that turns those decisions into files that actually exist**: today there is no `AGENTS.md` in the repository, and `.claude/hooks/pre-bash.sh`'s destructive-command blocking has no Codex CLI or Cursor counterpart.

This specification defines what must exist for a maintainer working in this repository through Codex CLI or Cursor to receive (a) the same baseline guidance Claude Code sessions already get, (b) the same destructive-command protection Claude Code sessions already get, (c) native discovery of this repository's own skills for Codex CLI, and (d) the same pre-edit blocking and post-edit formatting Claude Code sessions already get, for Codex CLI. It does not redefine which items are unified or at what strength — those are fixed inputs from `specs/012-cross-agent-guardrail-migration/decision-record.md`, except where explicitly superseded above (Q3, Q7, Q9, Q10 — each for Codex CLI only; Cursor's treatment of every item is unchanged from spec 012).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Shared baseline guidance via AGENTS.md (Priority: P1)

A maintainer opens this repository in Codex CLI or Cursor instead of Claude Code. They want the same baseline guidance Claude Code sessions get from `.claude/rules/*` — the 13 items spec 012 decided to unify (6 full, 7 weak; Q6 is excluded here because its unification is a real hook, not prose, and is covered by User Stories 2–3) — available to them without opening `.claude/` at all.

**Why this priority**: This is the highest-value, lowest-risk deliverable — it is markdown content only, requires no new hook mechanism, and depends on nothing else in this feature. It alone gives Codex CLI and Cursor sessions parity with Claude Code's non-enforcement guidance.

**Independent Test**: With only `AGENTS.md` created (no adapters yet), a reviewer opens the file and confirms all 13 items from the decision record are present, each phrased at the strength (full vs. weak) that record specifies, independent of whether User Story 2 or 3 has shipped.

**Acceptance Scenarios**:

1. **Given** decision-record.md's `unify_full` verdicts for Q1, Q2, Q4, and Q14, **When** `AGENTS.md` is created, **Then** it contains an entry for each, with Q2's tool references genericized (no `Read`/`Edit`/`Grep`-style Claude Code tool names). Q3 (skill routing) is **not** carried as `AGENTS.md` prose in this feature — see User Story 4, which supersedes the original prose-transcription treatment for Codex CLI; `AGENTS.md` still names the underlying principle (which category of request routes to which skill) only for tools where no native skill-file discovery is confirmed (currently: Cursor, per the open dependency in Acceptance Scenario 2 of User Story 4).
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

---

### User Story 4 - Native skill discovery for Codex CLI via .agents/skills (Priority: P1)

A maintainer working in Codex CLI wants this repository's own skills (`adr`, `advisor`, `clarifier`, `coder`, `domain-model`, `minto-builder`, `minto-reviewer`, `minto-rewriter`, `ubiquitous-language`) to trigger the same way they do in Claude Code — not as a lossy prose summary, but as the real `SKILL.md` files, discovered the same way Codex CLI already discovers this repository's 15 `speckit-*` skills today.

**Why this priority**: Codex CLI natively scans `.agents/skills/<name>/SKILL.md` from the working directory up to the repository root (confirmed via [learn.chatgpt.com/docs/build-skills](https://learn.chatgpt.com/docs/build-skills)); this repository already relies on that exact mechanism for its 15 `speckit-*` skills via the existing `speckit-expand-update.sh` sync. Extending the same, already-proven mechanism to the 9 remaining skills is zero-drift and lower-risk than the prose-routing-table approach Q3 originally specified, so it supersedes that approach for Codex CLI and ranks at P1 alongside User Story 1.

**Independent Test**: With this story implemented alone (no `AGENTS.md`, no destructive-command adapters), a reviewer runs a request in a Codex CLI session that should trigger one of the 9 custom skills (e.g. a decision/trade-off request that should trigger `advisor`) and confirms Codex CLI reads that skill's real `SKILL.md` from `.agents/skills/advisor/SKILL.md`, independent of User Stories 1–3.

**Acceptance Scenarios**:

1. **Given** the 9 custom-authored skills currently exist only under `.claude/skills/`, **When** this story is implemented, **Then** each of the 9 also exists under `.agents/skills/<name>/SKILL.md`, matching the directory-per-skill structure Codex CLI's documentation specifies (a directory containing `SKILL.md` plus any optional scripts/references).
2. **Given** Cursor's own skill-discovery mechanism (if any) was not confirmed by the source consulted for this story, **When** `AGENTS.md` is written (User Story 1), **Then** it does not claim skill-file discoverability for Cursor — that remains an open, unconfirmed dependency, distinct from Codex CLI's now-confirmed mechanism.
3. **Given** a custom skill's `.claude/skills/<name>/SKILL.md` is edited after this story ships, **When** the next sync point is reached, **Then** `.agents/skills/<name>/SKILL.md` reflects the same content — the two must not be allowed to silently drift apart.

---

### User Story 5 - Real pre-edit blocking for Codex CLI (Priority: P2)

A maintainer working in Codex CLI attempts to edit a file directly under `.git/`, or attempts any edit while the current branch is `main`/`master`. Today nothing stops them — only Claude Code has this protection (`.claude/hooks/pre-edit.sh`). They want the same block Claude Code already gives, since Codex CLI's `PreToolUse` hook has now been confirmed to intercept `apply_patch`/`Edit`/`Write` calls before they complete — the exact "before the fact" coverage `specs/012-cross-agent-guardrail-migration/research.md`'s R4 assumed did not exist for any tool.

**Why this priority**: This upgrades two items (Q9, Q10) from documentation-only notes to real enforcement at comparatively low cost, since Codex CLI's `PreToolUse` input/output contract (JSON stdin with `tool_name`/`tool_input`, exit-code/JSON-based block) closely mirrors `.claude/hooks/pre-edit.sh`'s own contract. Ranked P2 — same tier as the other real-enforcement work (User Story 2) — because, unlike User Story 1's zero-risk documentation win, this requires new adapter code and the re-verification FR-024 requires.

**Independent Test**: With `.claude/hooks/pre-edit.sh`'s `.git/`-path and main/master-branch matching logic extracted into a shared script and a Codex CLI `PreToolUse` adapter (scoped to `apply_patch`/`Edit`/`Write`) wired to it, attempt an edit under `.git/` and an edit while on `main` through a Codex CLI session, and confirm both are denied before the edit completes — independent of User Story 6.

**Acceptance Scenarios**:

1. **Given** a file path under `.git/`, **When** an edit is attempted through the Codex CLI adapter, **Then** the edit is denied before it completes, matching `.claude/hooks/pre-edit.sh`'s current behavior.
2. **Given** the current branch is `main` or `master`, **When** any edit is attempted through the Codex CLI adapter, **Then** the edit is denied before it completes, matching `.claude/hooks/pre-edit.sh`'s current behavior.
3. **Given** a file path not under `.git/` and a non-`main`/`master` branch, **When** an edit is attempted, **Then** it is allowed (no false-positive blocking).
4. **Given** Cursor's `afterFileEdit` hook fires only after an edit completes (per `research.md` R2/R4, unaffected by this correction), **When** this story is implemented, **Then** Cursor's `AGENTS.md` treatment of Q9/Q10 remains prose-only, unchanged from spec 012's original recorded verdict.
5. **Given** [learn.chatgpt.com/docs/hooks](https://learn.chatgpt.com/docs/hooks)'s claim that `PreToolUse` covers `apply_patch`/`Edit`/`Write` is a secondary confirmation gathered mid-session, **When** the adapter is implemented, **Then** the claim is re-verified against a live Codex CLI session before the adapter is considered complete (FR-024).

---

### User Story 6 - Real post-edit auto-format for Codex CLI (Priority: P3)

A maintainer edits a `.sh`, `.yaml`/`.yml`, or `.json` file through Codex CLI. Today nothing runs `shfmt`/`shellcheck`/`yamllint`/`jq` afterward — only Claude Code sessions get that via `.claude/hooks/post-edit-format.sh`. They want the same automatic formatting/linting, since Codex CLI's `PostToolUse` hook has now been confirmed to cover the same edit tools as `PreToolUse`.

**Why this priority**: Lower priority than User Story 5 because it is automation quality-of-life (silent formatting), not a security guardrail — no destructive action is prevented if this story is deferred. It depends on nothing this feature hasn't already built (the shared-script extraction pattern from User Stories 2 and 5).

**Independent Test**: With `.claude/hooks/post-edit-format.sh`'s per-extension formatting logic extracted into a shared script and a Codex CLI `PostToolUse` adapter wired to it, edit a `.sh` file through a Codex CLI session and confirm `shfmt`/`shellcheck` ran against it, independent of User Story 5.

**Acceptance Scenarios**:

1. **Given** a `.sh` file is edited through the Codex CLI adapter, **When** the edit completes, **Then** `shfmt -w -i 2` and `shellcheck` run against it, matching `.claude/hooks/post-edit-format.sh`'s current behavior.
2. **Given** a `.yaml`/`.yml` or `.json` file is edited, **When** the edit completes, **Then** `yamllint` or a JSON syntax check runs respectively, matching current Claude Code behavior.
3. **Given** Cursor's `afterFileEdit` hook was confirmed viable for this exact purpose but the maintainer declined to implement it in spec 012's Q7 verdict, **When** this story is implemented, **Then** Cursor's `AGENTS.md` treatment of Q7 remains prose-only, unchanged — this feature does not silently reopen that specific per-tool decision.

### Edge Cases

- What happens if a destructive-command category's decision is "ask" but the target tool's hook contract only supports a binary allow/deny? The adapter MUST default to deny (fail-safe default), never allow.
- What happens if the shared script itself errors (crashes, times out, unexpected input)? Each adapter MUST treat a script error the same way it treats a "deny" decision, not an "allow" — a broken guardrail must fail closed, not fail open.
- What happens if `.claude/hooks/pre-bash.sh`'s behavior changes in the future (a new destructive-command category is added)? Because the matching logic is extracted into one shared script that all three tools' adapters call, a future addition made once in the shared script propagates to all three automatically — this is a design property to preserve, not a scenario requiring new tests today.
- What happens if Codex CLI's or Cursor's actual hook behavior (once re-verified per FR-011) turns out to differ from `research.md`'s R1/R2/R3 assumptions? The adapter for that tool MUST be adjusted to match the verified behavior before being considered complete; the acceptance scenarios in User Stories 2–3 that cite re-verification are blocking, not advisory.
- What happens to Claude Code's own `pre-bash.sh` behavior during this refactor? It MUST produce identical outcomes before and after the shared-script extraction — this feature must not regress the one guardrail that already works.
- What happens to Claude Code's own `pre-edit.sh` and `post-edit-format.sh` behavior during their respective refactors (User Stories 5–6)? Both MUST produce identical outcomes before and after — no regression, mirroring the `pre-bash.sh` requirement above.
- What happens if Codex CLI's `PreToolUse`/`PostToolUse` file-edit coverage, once re-verified per FR-024, turns out narrower than documented (e.g. covers `apply_patch` but not a raw `Write` tool call)? The Codex CLI adapters for User Stories 5–6 MUST be scoped to whatever is actually verified, and any gap MUST be documented rather than assumed closed.
- What happens if this feature's upgrade of Q7/Q9/Q10 for Codex CLI creates an inconsistency with `AGENTS.md`'s prose note for the same item (which still exists for Cursor)? `AGENTS.md`'s entry for each upgraded item MUST state plainly that Codex CLI enforces it via hook while other tools receive the prose note only — the entry must not read as if the same (weak) treatment applies to all tools.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a root-level `AGENTS.md` file containing one entry for each of the 13 non-Q6 items recorded in `specs/012-cross-agent-guardrail-migration/decision-record.md` (Q1–Q5, Q7–Q14).
- **FR-002**: For each `unify_weak` item still prose-only for every tool (Q5, Q8, Q11, Q12, Q13), the `AGENTS.md` wording MUST NOT imply the enforcement guarantee the original Claude Code mechanism had — phrased as a note or request, per that item's decision-record rationale. For Q7, Q9, and Q10 — upgraded to real enforcement for Codex CLI per FR-017–FR-022 — the `AGENTS.md` entry MUST state that Codex CLI enforces the item via hook while other tools (Cursor) receive the prose note only; it MUST NOT read as uniformly weak across tools.
- **FR-003**: Q2's `AGENTS.md` entry MUST use tool-agnostic vocabulary (no Claude Code-specific tool names).
- **FR-004** (revised — supersedes the original Q3 prose-transcription treatment for Codex CLI): `AGENTS.md` MUST NOT carry Q3's skill-routing table as a prose transcription. Instead, `AGENTS.md` MAY name the underlying routing principle only for tools with no confirmed native skill-file discovery (currently Cursor); for Codex CLI, skill discoverability is solved natively per FR-014, not documented as an open dependency.
- **FR-005**: Q13's and Q14's `AGENTS.md` entries MUST NOT name a Claude Code-specific mechanism (Claude Memory, the `Agent` tool, `subagent_type` values).
- **FR-006**: The system MUST provide one shared script encoding `.claude/hooks/pre-bash.sh`'s destructive-command matching logic (force push, `git reset --hard`, `git clean -f`, `rm -rf` against root/home/cwd, other `rm -rf`, `mkfs`/`dd`/fork-bomb, `curl|bash`, non-HTTPS request, credential-path read, credential-path write, global package installs, `sudo`), exposing one tool-agnostic decision (allow / deny / ask) plus a human-readable reason per invocation.
- **FR-007**: The system MUST provide a Codex CLI adapter that invokes the shared script from a `PreToolUse` hook scoped to Bash tool calls and translates its decision into Codex CLI's expected hook response.
- **FR-008**: The system MUST provide a Cursor adapter that invokes the shared script from a `beforeShellExecution` hook with `failClosed: true` and translates its decision into Cursor's `{permission, user_message, agent_message}` response shape.
- **FR-009**: Where the shared script's decision is "ask" and a target tool's hook contract has no three-way primitive, that tool's adapter MUST default to deny rather than allow.
- **FR-010**: `.claude/hooks/pre-bash.sh` MUST continue to produce identical allow/deny/ask outcomes for every existing test case after being refactored to call the shared script — zero behavior regression for Claude Code.
- **FR-011**: Before the Codex CLI and Cursor adapters are considered complete, the implementation MUST re-verify `research.md`'s R1 (Codex CLI `PreToolUse` Bash-only scope and response shape) and R2/R3 (Cursor `beforeShellExecution` shape, `failClosed` behavior, and `permissions.json` non-guarantee) against each vendor's primary documentation, since the decision record flags both as Medium-confidence.
- **FR-012**: If `AGENTS.md` already exists at the time this feature is implemented, the system MUST surface its current content to the maintainer before any content is overwritten.
- **FR-013**: The system MUST provide an automated test suite covering every destructive-command category in FR-006, run against the shared script directly and against each of the three integration points (Claude Code hook, Codex CLI adapter, Cursor adapter).
- **FR-014**: The system MUST make each of this repository's 9 custom-authored skills (`adr`, `advisor`, `clarifier`, `coder`, `domain-model`, `minto-builder`, `minto-reviewer`, `minto-rewriter`, `ubiquitous-language`) available under `.agents/skills/<name>/SKILL.md`, using the same directory-per-skill structure Codex CLI's documentation specifies, mirroring the sync mechanism already used for the 15 `speckit-*` skills.
- **FR-015**: `.agents/skills/<name>/SKILL.md` content for each of the 9 custom skills MUST remain equivalent to its `.claude/skills/<name>/SKILL.md` source — the two MUST NOT be allowed to silently drift apart after either is edited.
- **FR-016**: The system MUST NOT claim skill-file discoverability for Cursor without separate, primary-source confirmation — `AGENTS.md` and this feature's other artifacts MUST treat Cursor's skill-discovery mechanism as unconfirmed, distinct from Codex CLI's now-confirmed `.agents/skills` mechanism.
- **FR-017**: The system MUST provide one shared script encoding `.claude/hooks/pre-edit.sh`'s block logic (deny edits under `.git/`; deny edits when the current branch is `main`/`master`), exposing a tool-agnostic allow/deny decision plus reason, reused by both Claude Code's existing hook and a new Codex CLI adapter.
- **FR-018**: The system MUST provide a Codex CLI adapter that invokes FR-017's shared script from a `PreToolUse` hook scoped to `apply_patch`/`Edit`/`Write`, translating the decision into Codex CLI's expected response format.
- **FR-019**: `.claude/hooks/pre-edit.sh`'s block behavior (Q9, Q10) MUST continue to produce identical outcomes for every existing test case after being refactored to call the shared script — zero regression for Claude Code.
- **FR-020**: The system MUST provide one shared script encoding `.claude/hooks/post-edit-format.sh`'s per-extension formatting behavior (`shfmt`/`shellcheck` for `.sh`, `yamllint` for `.yaml`/`.yml`, JSON syntax check for `.json`), reused by both Claude Code's existing hook and a new Codex CLI adapter.
- **FR-021**: The system MUST provide a Codex CLI adapter that invokes FR-020's shared logic from a `PostToolUse` hook scoped to `apply_patch`/`Edit`/`Write`.
- **FR-022**: `.claude/hooks/post-edit-format.sh`'s behavior MUST continue to produce identical outcomes for every existing test case after being refactored to call the shared script — zero regression for Claude Code.
- **FR-023**: For Cursor, Q7, Q9, and Q10 MUST remain prose-only in `AGENTS.md`, exactly as spec 012 originally recorded — this feature MUST NOT extend real enforcement to Cursor for these three items, since spec 012 already recorded the maintainer explicitly declining Cursor's viable `afterFileEdit` hook for Q7, and Cursor's pre-edit-block capability (Q9/Q10) remains unconfirmed by any source consulted in this feature.
- **FR-024**: Before the Codex CLI pre-edit and post-edit adapters (User Stories 5–6) are considered complete, the implementation MUST re-verify [learn.chatgpt.com/docs/hooks](https://learn.chatgpt.com/docs/hooks)'s claims — specifically that `PreToolUse`/`PostToolUse` cover `apply_patch`/`Edit`/`Write` and that a deny decision blocks the edit before completion — against a live Codex CLI session, mirroring FR-011's re-verification requirement for Q6.

### Key Entities

- **AGENTS.md**: Shared, tool-agnostic instruction file at the repository root; the carrier of the 12 remaining prose-appropriate decision-record items (Q1, Q2, Q4, Q5, Q7–Q14; Q3's routing-table content is carried natively per FR-014 for Codex CLI, and only as an unconfirmed-dependency note for Cursor). For Q7, Q9, Q10, its entry additionally notes the Codex CLI real-enforcement split introduced by this feature. Read natively by Codex CLI and Cursor without additional per-tool configuration.
- **Shared destructive-command script**: Single source of truth for `pre-bash.sh`'s matching logic (Q6), tool-agnostic in its inputs (a shell command string) and outputs (allow/deny/ask + reason).
- **Shared pre-edit script**: Single source of truth for `pre-edit.sh`'s block logic (Q9, Q10 — `.git/` paths, `main`/`master` branch), tool-agnostic in its inputs (tool name + file path) and outputs (allow/deny + reason).
- **Shared post-edit script**: Single source of truth for `post-edit-format.sh`'s per-extension formatting logic (Q7), tool-agnostic in its inputs (a file path).
- **Codex CLI `PreToolUse` adapter (Bash)**: Thin translation layer between the shared destructive-command script's decision and Codex CLI's `PreToolUse` hook contract, scoped to Bash.
- **Codex CLI `PreToolUse` adapter (edit)**: Thin translation layer between the shared pre-edit script's decision and Codex CLI's `PreToolUse` hook contract, scoped to `apply_patch`/`Edit`/`Write`.
- **Codex CLI `PostToolUse` adapter**: Thin translation layer between the shared post-edit script and Codex CLI's `PostToolUse` hook contract, scoped to `apply_patch`/`Edit`/`Write`.
- **Cursor `beforeShellExecution` adapter**: Thin translation layer between the shared destructive-command script's decision and Cursor's `beforeShellExecution` hook contract.
- **`.agents/skills/` sync**: The mechanism (mirroring the existing `speckit-expand-update.sh` pattern) that keeps this repository's 9 custom-authored skills discoverable by Codex CLI's native `.agents/skills` scan, without content drift from their `.claude/skills/` source.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All 12 remaining prose-appropriate decision-record items (Q1, Q2, Q4, Q5, Q7–Q14) have a corresponding, verifiable entry in `AGENTS.md` (12/12, checked by a reviewer against `decision-record.md`); Q3 and Q6 are verified instead by SC-006 and SC-002 respectively.
- **SC-002**: Every destructive-command test case that currently passes against `.claude/hooks/pre-bash.sh` produces the identical allow/deny/ask outcome when run through the Codex CLI adapter and the Cursor adapter (100% parity across all three entry points).
- **SC-003**: `.claude/hooks/pre-bash.sh`'s own existing behavior shows zero regressions after the shared-script refactor (100% of its current test cases still pass).
- **SC-004**: A maintainer working from a fresh Codex CLI or Cursor session (no prior context of spec 012) can, by reading only `AGENTS.md`, correctly state for any of the 13 items whether it is enforced or advisory-only.
- **SC-005**: Attempting a hard-blocked destructive command from a Codex CLI or Cursor session in this repository is denied before execution, with no successful execution path found during testing.
- **SC-006**: All 9 custom-authored skills exist under `.agents/skills/<name>/SKILL.md` with content matching their `.claude/skills/<name>/SKILL.md` source (9/9, verified by diff), and a representative request routed through a Codex CLI session triggers the correct skill.
- **SC-007**: Attempting to edit a file under `.git/`, or any file while on the `main`/`master` branch, from a Codex CLI session in this repository is denied before the edit completes, with no successful edit path found during testing (Q9, Q10).
- **SC-008**: Editing a `.sh`, `.yaml`/`.yml`, or `.json` file from a Codex CLI session in this repository results in the same formatting/lint pass Claude Code already applies, verified for each extension category (Q7).
- **SC-009**: `.claude/hooks/pre-edit.sh` and `.claude/hooks/post-edit-format.sh` show zero regressions after their respective shared-script refactors (100% of their current test cases still pass).

## Assumptions

- Codex CLI and Cursor are both actively used to work in this repository going forward — the premise of the original request and confirmed by the maintainer during scoping.
- `specs/012-cross-agent-guardrail-migration/research.md`'s R1–R5 findings are the accepted starting point for design, but R1–R3 (Medium/Medium-high confidence) must be re-verified against primary vendor documentation before the Codex CLI and Cursor adapters ship (FR-011) — R4 and R5 need no re-verification here since neither is load-bearing for this feature's scope (R4 concerns the pre-edit items already resolved as prose-only in spec 012; R5 is already High confidence).
- No test suite currently exists for `.claude/hooks/pre-bash.sh`'s destructive-command categories (confirmed: `tests/` has no `pre-bash`-related suite); one must be created as part of this feature rather than merely extended.
- `AGENTS.md` is the single shared file for both target tools, per R5 — this feature does not introduce a per-tool `CODEX.md` or `.cursor/rules` split.
- Where the shared script returns "ask" and a target tool's hook has no three-way decision primitive, the fail-safe default (deny) applies, consistent with this repository's existing least-privilege / fail-safe-default permission philosophy.
- Codex CLI's `.agents/skills` discovery mechanism, as described by [learn.chatgpt.com/docs/build-skills](https://learn.chatgpt.com/docs/build-skills), applies to this repository's `SKILL.md` files without modification (same `name`/`description` YAML-frontmatter shape already used by the existing `speckit-*` skills). This claim is treated as sufficiently confirmed for planning (a documented, named source, consistent with this repository's own existing `.agents/skills/speckit-*` usage) but should still be spot-checked against a live Codex CLI session before User Story 4 is considered complete.
- Cursor's equivalent skill-discovery mechanism (if any) was not covered by the source consulted for User Story 4 and is out of scope for this feature; FR-016 governs how that gap must be represented rather than assumed away.
- Codex CLI's `PreToolUse`/`PostToolUse` coverage of `apply_patch`/`Edit`/`Write`, as described by [learn.chatgpt.com/docs/hooks](https://learn.chatgpt.com/docs/hooks), is treated as sufficiently confirmed for planning (a documented, named source with a field-level contract closely matching `.claude/hooks/pre-edit.sh`'s own) but must still be re-verified against a live Codex CLI session before User Stories 5–6 are considered complete (FR-024) — the same standard already applied to Q6's Codex adapter (FR-011).
- This correction is scoped to Codex CLI only. Cursor's treatment of Q7, Q9, and Q10 is unchanged from spec 012's original recorded verdicts (prose-only) — no source consulted in this feature revisited Cursor's `beforeShellExecution`/`afterFileEdit` capability for these items.
- No test suite currently exists for `.claude/hooks/pre-edit.sh` or `.claude/hooks/post-edit-format.sh` (mirroring the `pre-bash.sh` gap already noted below); test suites for both must be created as part of this feature.
