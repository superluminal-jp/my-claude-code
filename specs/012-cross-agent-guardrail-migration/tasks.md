---

description: "Task list for the Cross-Agent Guardrail & Rule Migration Decision Record"
---

# Tasks: Cross-Agent Guardrail & Rule Migration Decision Record

**Input**: Design documents from `/specs/012-cross-agent-guardrail-migration/`

**Prerequisites**: plan.md (required, done), spec.md (required, done — 14/14 Clarifications recorded), research.md, data-model.md, quickstart.md

**Tests**: Not requested for this feature (spec.md's Testing = "N/A — validation is a manual read-through against Success Criteria"). No test tasks are generated; `quickstart.md`'s checklist substitutes for automated tests in the Polish phase.

**Organization**: Tasks are grouped by user story (P1/P2/P3 from spec.md), each producing its slice of the single output file, `decision-record.md`. All tasks write to the same file, so — unlike a typical multi-file feature — none are marked `[P]`: same-file edits cannot safely run in parallel even though the user stories are logically independent (per spec.md's Independent Test criteria).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies) — not used in this feature; see Organization above.
- **[Story]**: Which user story this task belongs to (US1/US2/US3)
- Include exact file paths in descriptions

## Path Conventions

Single documentation artifact: `specs/012-cross-agent-guardrail-migration/decision-record.md`. No `src/`/`tests/` involved (see plan.md's Project Structure).

---

## Phase 1: Setup

**Purpose**: Create the output file and its top-level structure.

- [ ] T001 Create `specs/012-cross-agent-guardrail-migration/decision-record.md` with a title, a one-paragraph intro linking back to `spec.md`, and three empty section headers ("P1 — Low-Cost Unification", "P2 — Per-Tool Tradeoff", "P3 — No Cross-Agent Hook Equivalent"), per `data-model.md`'s Decision Record entity.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Define the shared per-item write-up format before any item is written, so all three story phases stay consistent (this is what makes SC-002 — independent readability — achievable).

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T002 In `specs/012-cross-agent-guardrail-migration/decision-record.md`, write the shared per-item entry template as a short explanatory note (fields: current Claude Code behavior, options considered, recorded verdict — labeled per-tool when it differs, rationale, unconfirmed-dependency flag), derived from `data-model.md`'s Decision Verdict entity and `research.md`'s R1–R5.

**Checkpoint**: Foundation ready — item write-ups can now begin.

---

## Phase 3: User Story 1 - Low-cost, low-risk unification items (Priority: P1) 🎯 MVP

**Goal**: Record the four items that unify into `AGENTS.md` with zero enforcement loss.

**Independent Test**: Reviewing just the "P1" section of `decision-record.md` is sufficient to confirm all four items have a verdict and rationale, without reading the P2/P3 sections.

### Implementation for User Story 1

- [ ] T003 [US1] Write the Q1 entry (`pre-edit.sh` CI/settings/production warnings) in `specs/012-cross-agent-guardrail-migration/decision-record.md`, sourced from `spec.md`'s Clarifications Q1 and User Story 1 Acceptance Scenario 4.
- [ ] T004 [US1] Write the Q2 entry (`tools.md` dedicated-tools/parallel-calls principles) in `specs/012-cross-agent-guardrail-migration/decision-record.md`, sourced from `spec.md`'s Clarifications Q2 and Acceptance Scenario 3; note the tool-name genericization.
- [ ] T005 [US1] Write the Q3 entry (`skill-routing.md` routing table) in `specs/012-cross-agent-guardrail-migration/decision-record.md`, sourced from `spec.md`'s Clarifications Q3 and Acceptance Scenario 2; include the SKILL.md-discoverability precondition and flag it against `research.md` R5 (unify_full but the routing table's *usefulness* depends on R2/R1-level, Medium-confidence skill-loading claims).
- [ ] T006 [US1] Write the Q4 entry (`mcp.md` catalog + usage rule) in `specs/012-cross-agent-guardrail-migration/decision-record.md`, sourced from `spec.md`'s Clarifications Q4 and Acceptance Scenario 1.

**Checkpoint**: P1 section of `decision-record.md` complete and independently readable.

---

## Phase 4: User Story 2 - Per-tool tradeoff items (Priority: P2)

**Goal**: Record the four items where Cursor and Codex CLI warrant different (or jointly downgraded) treatment.

**Independent Test**: Reviewing just the "P2" section confirms each of the four items states its per-tool verdict split (or explains why both tools got the same downgraded treatment), without needing the P1/P3 sections.

### Implementation for User Story 2

- [ ] T007 [US2] Write the Q5 entry (`user-prompt-submit.sh` secret detection) in `specs/012-cross-agent-guardrail-migration/decision-record.md`, sourced from `spec.md`'s Clarifications Q5 and Acceptance Scenario 1 (US2); explicitly state that Cursor's `beforeSubmitPrompt` was a viable option that was declined, per FR-007/SC-003, and flag `research.md` R2 as the unconfirmed dependency.
- [ ] T008 [US2] Write the Q6 entry (`pre-bash.sh` destructive-command blocking) in `specs/012-cross-agent-guardrail-migration/decision-record.md`, sourced from `spec.md`'s Clarifications Q6 and Acceptance Scenario 2 (US2); mark this as the highest-priority follow-up implementation item (real enforcement across all three tools) and flag `research.md` R1–R3 as unconfirmed dependencies.
- [ ] T009 [US2] Write the Q7 entry (`post-edit-format.sh` auto-formatting) in `specs/012-cross-agent-guardrail-migration/decision-record.md`, sourced from `spec.md`'s Clarifications Q7 and Acceptance Scenario 3 (US2); explicitly state that Cursor's `afterFileEdit` was viable but declined, per FR-007/SC-003.
- [ ] T010 [US2] Write the Q8 entry (`recommend-speckit.sh` nudge) in `specs/012-cross-agent-guardrail-migration/decision-record.md`, sourced from `spec.md`'s Clarifications Q8 and Acceptance Scenario 4 (US2); note the accepted throttle-cache degradation.

**Checkpoint**: P1 and P2 sections both complete and independently readable.

---

## Phase 5: User Story 3 - Items with no cross-agent hook equivalent (Priority: P3)

**Goal**: Record the six items (across five spec.md acceptance scenarios — Q13/Q14 share one scenario) that have no viable pre-action hook in either target tool today.

**Independent Test**: Reviewing just the "P3" section confirms all six items have a verdict, and that the main/master item (Q9) explicitly names GitHub Branch Protection as the declined alternative.

### Implementation for User Story 3

- [ ] T011 [US3] Write the Q9 entry (`pre-edit.sh` main/master-branch block) in `specs/012-cross-agent-guardrail-migration/decision-record.md`, sourced from `spec.md`'s Clarifications Q9; explicitly name GitHub Branch Protection as the recommended-but-declined alternative, per Acceptance Scenario 1 (US3)'s requirement to name the chosen control.
- [ ] T012 [US3] Write the Q10 entry (`pre-edit.sh` `.git/`-direct-edit block) in `specs/012-cross-agent-guardrail-migration/decision-record.md`, sourced from `spec.md`'s Clarifications Q10 and Acceptance Scenario 2 (US3).
- [ ] T013 [US3] Write the Q11 entry (`session-start.sh` lint-toolchain bootstrap) in `specs/012-cross-agent-guardrail-migration/decision-record.md`, sourced from `spec.md`'s Clarifications Q11 and Acceptance Scenario 3 (US3); note that the resulting `AGENTS.md` text is documentation of an assumption, not an actionable instruction (no execution trigger exists).
- [ ] T014 [US3] Write the Q12 entry (`speckit-expand-update.sh` Spec Kit CLI auto-update) in `specs/012-cross-agent-guardrail-migration/decision-record.md`, sourced from `spec.md`'s Clarifications Q12 and Acceptance Scenario 4 (US3).
- [ ] T015 [US3] Write the Q13 entry (`tools.md` Memory section) in `specs/012-cross-agent-guardrail-migration/decision-record.md`, sourced from `spec.md`'s Clarifications Q13 and the Memory half of Acceptance Scenario 5 (US3); confirm no reference to the Claude Memory tool leaks into the mechanism-agnostic phrasing.
- [ ] T016 [US3] Write the Q14 entry (`tools.md` Subagents section) in `specs/012-cross-agent-guardrail-migration/decision-record.md`, sourced from `spec.md`'s Clarifications Q14 and the Subagents half of Acceptance Scenario 5 (US3); confirm no reference to Claude Code-specific mechanism names (`Agent` tool, `subagent_type`) leaks into the phrasing.

**Checkpoint**: All 14 items now recorded; `decision-record.md` is content-complete.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validate the finished record against `spec.md`'s Success Criteria and commit it.

- [ ] T017 Run the `specs/012-cross-agent-guardrail-migration/quickstart.md` validation checklist (SC-001–SC-004, FR-009) against `specs/012-cross-agent-guardrail-migration/decision-record.md`.
- [ ] T018 Cross-check the verdict-class distribution in `specs/012-cross-agent-guardrail-migration/decision-record.md` against the table in `specs/012-cross-agent-guardrail-migration/data-model.md` (expect 6 `unify_full`, 8 `unify_weak`, 0 dropped).
- [ ] T019 Commit `specs/012-cross-agent-guardrail-migration/decision-record.md` and push to the current branch.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately.
- **Foundational (Phase 2)**: Depends on Setup (T001) — BLOCKS all user story phases.
- **User Stories (Phase 3–5)**: All depend on Foundational (T002). Logically independent per spec.md, but execute sequentially (T003→...→T016) since every task edits the same file.
- **Polish (Phase 6)**: Depends on all three user stories being complete (T003–T016).

### Parallel Opportunities

None. Every task in this feature edits the single file `decision-record.md`; parallelizing would produce edit conflicts regardless of the tasks' logical independence. Execute T001 through T019 in strict numeric order.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001)
2. Complete Phase 2: Foundational (T002)
3. Complete Phase 3: User Story 1 (T003–T006)
4. **STOP and VALIDATE**: the P1 section alone already delivers value — four cheap `AGENTS.md` transcriptions ready to act on — even before P2/P3 are written.

### Incremental Delivery

1. Setup + Foundational → template ready (T001–T002)
2. User Story 1 → P1 section done, reviewable independently (T003–T006)
3. User Story 2 → P2 section done (T007–T010)
4. User Story 3 → P3 section done (T011–T016)
5. Polish → validated and committed (T017–T019)

---

## Notes

- No `[P]` tasks in this feature — see Organization and Parallel Opportunities above.
- `[Story]` label maps each task to its user story for traceability back to `spec.md`.
- This feature produces no source code; "implementation" means authoring Markdown sections from already-decided content in `spec.md`'s Clarifications.
- Commit after Phase 6 (T019), not after every task — the individual entries are not independently useful commits (unlike the Clarifications answers, which were committed per-question during `/speckit-clarify`).
