---
description: "Task list for Live Documentation Enforcement rule implementation"
---

# Tasks: Live Documentation Enforcement

**Input**: Design documents from `specs/009-live-doc-enforcement/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/rule-behavior.md ✓

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1–US4)
- Tests are part of this feature's scope (specified in plan.md T003–T008)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create directory structure and verify prerequisites

- [x] T001 Create `tests/live-documentation/` directory for test scenarios

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core rule file and CLAUDE.md integration — MUST complete before any user story test can pass

**⚠️ CRITICAL**: No test scenario can be verified until T002 and T003 are complete

- [x] T002 Create the Live Documentation rule file at `.claude/rules/live-documentation.md` with six enforcement sections (Drift Detection, Separate-PR Detection, Auto-generation Recommendation, Proximity Enforcement, No Redundancy, Override Handling) per `contracts/rule-behavior.md`; ≤ 150 lines; imperative language ("When X, Claude MUST Y")
- [x] T003 Add `@.claude/rules/live-documentation.md` import to `.claude/CLAUDE.md` after the existing rule imports; verify file stays under 200 lines

**Checkpoint**: Rule file loaded — Claude Code now enforces Live Documentation in every session

---

## Phase 3: User Story 1 — Catch Documentation Drift at Review Time (Priority: P1) 🎯 MVP

**Goal**: Claude detects and flags drift when code changes but documentation does not, blocking review until resolved or overridden.

**Independent Test**: Present a diff where a public function signature changed but its docstring is unchanged → Claude MUST flag Drift and refuse to pass the review.

### Implementation for User Story 1

- [x] T004 [US1] Write test scenario `tests/live-documentation/001-drift-detection.md` — scenario: code diff changes a public API; its docstring is unchanged; expected: Claude flags Drift and blocks review completion; format matches `tests/skill-routing/001-code-implement.md` exactly (sections: `# Test:`, `## Input Prompt`, `## Expected Behavior`, `## Pass Criteria`, `## Baseline`)

**Checkpoint**: US1 independently testable — run `claude -p` against the drift-detection scenario to verify

---

## Phase 4: User Story 2 — Block Separate Documentation PRs (Priority: P2)

**Goal**: Claude identifies documentation-only PRs that cover already-shipped code, flags the violation, and recommends amending the original commit.

**Independent Test**: Present a PR diff containing only README updates for a module shipped last week → Claude MUST flag the separation as a Live Documentation violation.

### Implementation for User Story 2

- [x] T005 [US2] Write test scenario `tests/live-documentation/002-separate-doc-pr.md` — scenario: PR contains only README changes for a feature committed a week ago; expected: Claude flags separation violation and recommends amending the original commit; format matches `tests/skill-routing/001-code-implement.md`

**Checkpoint**: US2 independently testable — run scenario against the loaded rule

---

## Phase 5: User Story 3 — Identify Auto-Generatable Documentation (Priority: P3)

**Goal**: When asked to write documentation that can be derived from code, Claude recommends the automated path and declines to hand-write the content.

**Independent Test**: Ask Claude "write the API docs for this fully-annotated function" → Claude MUST recommend using the project's doc-generation tool instead of producing the hand-written artifact.

### Implementation for User Story 3

- [x] T006 [P] [US3] Write test scenario `tests/live-documentation/003-autogen-recommendation.md` — scenario: developer asks Claude to document a function that has complete type annotations; expected: Claude identifies auto-generation opportunity and recommends the tool path; format matches `tests/skill-routing/001-code-implement.md`

**Checkpoint**: US3 independently testable

---

## Phase 6: User Story 4 — Enforce Proximity of Documentation (Priority: P3)

**Goal**: When placing documentation, Claude always co-locates it with the code it describes, and warns when a remote location is proposed.

**Independent Test**: Ask Claude to "document the authentication module and put it in docs/" → Claude MUST warn that remote placement violates Proximity and propose a co-located alternative.

### Implementation for User Story 4

- [x] T007 [P] [US4] Write test scenario `tests/live-documentation/004-proximity-enforcement.md` — scenario: developer asks Claude to document a module and place it in a top-level `docs/` directory; expected: Claude warns about proximity violation and offers a co-located path; format matches `tests/skill-routing/001-code-implement.md`

**Checkpoint**: US4 independently testable

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Override handling, test runner, agent context update, and quickstart validation

- [x] T008 Write test scenario `tests/live-documentation/005-override-acceptance.md` — scenario part A: developer says "skip the doc check, this is an emergency hotfix" (no reason stated); expected: Claude rejects the silent override and requests a reason; scenario part B: developer provides a reason; expected: Claude accepts and records the acknowledgment; format matches `tests/skill-routing/001-code-implement.md`
- [x] T009 Write bash test runner `tests/run-live-documentation.sh` modeled on `tests/run-skill-routing.sh`: iterates over `tests/live-documentation/*.md`, calls `claude -p` with a structured evaluation query per scenario, compares output to expected behavior, reports PASS/FAIL with counts, exits non-zero on any failure; make executable with `chmod +x`
- [x] T010 Update root `CLAUDE.md` `<!-- SPECKIT START --> … <!-- SPECKIT END -->` block to reference `specs/009-live-doc-enforcement/plan.md`
- [x] T011 Run `quickstart.md` validation steps 1–4 and confirm: rule is loaded, drift detection fires, auto-generation is recommended, and `bash tests/run-live-documentation.sh` exits 0

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 — **BLOCKS all test phases**
- **User Stories (Phases 3–6)**: All depend on Phase 2 completion; can then run in parallel
- **Polish (Phase 7)**: T008 can start after Phase 2; T009 depends on T004–T008 all being written; T010 is independent; T011 depends on T009

### User Story Dependencies

- **US1 (P1)**: Can start after Phase 2 — no dependency on other stories
- **US2 (P2)**: Can start after Phase 2 — independent of US1
- **US3 (P3)**: Can start after Phase 2 — independent of US1/US2
- **US4 (P3)**: Can start after Phase 2 — independent of US1/US2/US3

### Within Each Phase

- T002 → T003 (register import after file exists)
- T004, T005, T006, T007 → can all run in parallel (different files)
- T009 → depends on T004, T005, T006, T007, T008 (all scenario files must exist)
- T011 → depends on T009 (runner must exist to run)

---

## Parallel Execution Examples

### User Stories (Phases 3–6) in Parallel

```
# After T003 completes, launch all four test scenarios simultaneously:
Task: T004 — write 001-drift-detection.md
Task: T005 — write 002-separate-doc-pr.md
Task: T006 — write 003-autogen-recommendation.md
Task: T007 — write 004-proximity-enforcement.md
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (`tests/live-documentation/` directory)
2. Complete Phase 2: Foundational (rule file + CLAUDE.md import)
3. Complete Phase 3: US1 drift-detection test scenario
4. **STOP and VALIDATE**: Manually run the 001-drift-detection.md scenario against Claude
5. If Claude correctly flags drift → US1 is done; proceed to US2

### Incremental Delivery

1. Phase 1 + Phase 2 → Rule live in all sessions
2. Phase 3 → US1 verified (drift detection working)
3. Phase 4 → US2 verified (separate-PR detection working)
4. Phases 5–6 → US3/US4 verified (auto-gen + proximity working)
5. Phase 7 → Full test runner passing; all contracts verified

---

## Notes

- [P] tasks = different files, no blocking dependencies between them
- [Story] label maps each task to its user story for traceability
- Each user story (US1–US4) is independently verifiable by running its scenario against Claude
- Test scenarios follow the exact format of `tests/skill-routing/001-code-implement.md` for consistency with the existing test infrastructure
- Commit after Phase 2 completes (rule live) and after Phase 7 T011 passes (all tests green)
- No new external dependencies required — only Claude Code CLI (`claude -p`) which already exists
