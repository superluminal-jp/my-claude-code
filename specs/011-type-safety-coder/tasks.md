---

description: "Task list template for feature implementation"
---

# Tasks: Type Safety Enforcement in Coder Skill

**Input**: Design documents from `/specs/011-type-safety-coder/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/type-safety-behavior.md, quickstart.md

**Tests**: Behavioral scenario files are included as part of implementation (not a pre-implementation TDD gate) — they validate the instruction text's observable effect, mirroring the existing `tests/live-documentation/` pattern, per the Phase 1 design decision in `research.md` (Decision 4).

**Organization**: Tasks are grouped by user story (US1–US4, P1/P2/P2/P3 per spec.md) to enable independent validation of each story's behavior.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- Skill file lives outside the repo: `/Users/taikiogihara/.claude/skills/coder/SKILL.md`
- Tests live in-repo: `tests/type-safety-coder/`, `tests/run-type-safety-coder.sh`
- No `src/` tree — this feature delivers an instruction-document change, not application code

---

## Phase 1: Setup

**Purpose**: Confirm the exact insertion point in the existing skill file before editing it

- [ ] T001 Read `/Users/taikiogihara/.claude/skills/coder/SKILL.md` in full and confirm the insertion point for a new "Type Safety" section (after "Documentation Sync", before "Code quality and security", per plan.md's Summary) does not collide with existing headings

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add the section scaffold and the cross-cutting guardrail (FR-007) that every user story's instructions must respect

**⚠️ CRITICAL**: No user-story instruction bullets are added until this phase is complete — all stories edit the same section of the same file

- [ ] T002 Add the "Type Safety" section heading, one-sentence framing (ties to the existing "run the repository's configured linter, formatter, type-checker, and test runner" line already in "Language and stack conventions"), and the FR-007 guardrail ("follow the existing repo convention; do not introduce a new typing system, annotate untouched code, or perform unrelated typing refactors beyond the agreed task") to `/Users/taikiogihara/.claude/skills/coder/SKILL.md`

**Checkpoint**: Section scaffold exists — user story instruction bullets can now be added in priority order

---

## Phase 3: User Story 1 - Type-Annotated Public Interfaces by Default (Priority: P1) 🎯 MVP

**Goal**: Claude adds type annotations to new/changed public interfaces by default, matching the repo's existing typing convention (FR-001, FR-002)

**Independent Test**: Ask Claude to add a new function to a typed codebase and verify the signature carries matching type annotations without a separate "add types" request

### Implementation for User Story 1

- [ ] T003 [US1] Add FR-001/FR-002 instruction bullets (annotate new/changed public interfaces; update annotations when inputs/outputs change) to the "Type Safety" section in `/Users/taikiogihara/.claude/skills/coder/SKILL.md`
- [ ] T004 [P] [US1] Create behavioral test scenario `tests/type-safety-coder/001-typed-public-interface.md` per Contract 1 in `contracts/type-safety-behavior.md`, following the `tests/live-documentation/001-drift-detection.md` format (`# Test:`, `## Input Prompt`, `## Expected Behavior`, `## Pass Criteria`, `## Baseline`)

**Checkpoint**: User Story 1 behavior is instructed and independently testable

---

## Phase 4: User Story 2 - No Unsafe Type Escapes Without Justification (Priority: P2)

**Goal**: Claude fixes underlying type mismatches instead of silencing the type checker, and justifies any unavoidable escape (FR-003, FR-004)

**Independent Test**: Ask Claude to resolve a type error and verify it narrows/corrects the type rather than suppressing the checker, except with a stated, justified escape

### Implementation for User Story 2

- [ ] T005 [US2] Add FR-003/FR-004 instruction bullets (prefer correcting the type mismatch over suppression; justify and surface any unavoidable escape with a comment) to the "Type Safety" section in `/Users/taikiogihara/.claude/skills/coder/SKILL.md` (after T002)
- [ ] T006 [P] [US2] Create behavioral test scenario `tests/type-safety-coder/002-no-unsafe-escape.md` per Contract 2 in `contracts/type-safety-behavior.md`, same format as T004

**Checkpoint**: User Stories 1 and 2 both instructed and independently testable

---

## Phase 5: User Story 3 - Type Checker Runs Before Work Is Reported Done (Priority: P2)

**Goal**: Claude runs the project's configured type checker as part of pre-completion verification and resolves errors it introduced (FR-005)

**Independent Test**: Make a change that introduces a type error and confirm Claude's own verification step catches it before declaring the task done

### Implementation for User Story 3

- [ ] T007 [US3] Add FR-005 instruction bullet (run the configured type checker alongside test/lint/format before reporting done; resolve or surface introduced errors) to the "Type Safety" section in `/Users/taikiogihara/.claude/skills/coder/SKILL.md` (after T002)
- [ ] T008 [P] [US3] Create behavioral test scenario `tests/type-safety-coder/003-type-checker-verification.md` per Contract 3 in `contracts/type-safety-behavior.md`, same format as T004

**Checkpoint**: User Stories 1–3 instructed and independently testable

---

## Phase 6: User Story 4 - Validate and Narrow Types at System Boundaries (Priority: P3)

**Goal**: Claude validates/narrows boundary-crossing data (user input, external API, deserialized payloads) into known types before use (FR-006)

**Independent Test**: Ask Claude to handle a parsed JSON/API response and verify it validates/narrows the shape before treating it as a typed value

### Implementation for User Story 4

- [ ] T009 [US4] Add FR-006 instruction bullet (validate/narrow boundary-crossing data before treating it as a typed internal value) to the "Type Safety" section in `/Users/taikiogihara/.claude/skills/coder/SKILL.md` (after T002)
- [ ] T010 [P] [US4] Create behavioral test scenario `tests/type-safety-coder/004-boundary-validation.md` per Contract 4 in `contracts/type-safety-behavior.md`, same format as T004

**Checkpoint**: All four user stories instructed and independently testable

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Wire up the test runner, keep repo-level references current, and validate end-to-end

- [ ] T011 [P] Create `tests/run-type-safety-coder.sh`, a bash runner modeled on `tests/run-live-documentation.sh` that iterates `tests/type-safety-coder/*.md`, evaluates each via `claude -p`, and reports PASS/FAIL with a non-zero exit on failure; `chmod +x` it
- [ ] T012 Update the `<!-- SPECKIT START --> … <!-- SPECKIT END -->` block in root `CLAUDE.md` to reference `specs/011-type-safety-coder/plan.md`, following the pattern in `specs/009-live-doc-enforcement/plan.md` (T009)
- [ ] T013 Re-read the full `/Users/taikiogihara/.claude/skills/coder/SKILL.md` after T002–T010 and confirm existing sections (TDD, SDD, Documentation Sync, Code quality and security, Language and stack conventions) are unchanged in substance and ordering
- [ ] T014 Run `bash tests/run-type-safety-coder.sh` per `quickstart.md` and confirm all four scenarios PASS

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 — BLOCKS all user stories (same file/section)
- **User Stories (Phase 3–6)**: Each depends on Phase 2 completion. The `SKILL.md` edit task within each story (T003/T005/T007/T009) must run **sequentially** relative to each other (same file, same section) in priority order P1→P2→P2→P3; each story's test-scenario task ([P]) can run in parallel with anything except its own `SKILL.md` edit task
- **Polish (Phase 7)**: Depends on all four user stories being complete

### Within Each User Story

- `SKILL.md` edit task before its paired test-scenario task is *not* required (scenario files don't depend on the edit to be authored — they encode expected behavior) — but running `tests/run-type-safety-coder.sh` (T014) requires all `SKILL.md` edits (T002, T003, T005, T007, T009) to be complete first

### Parallel Opportunities

- T004, T006, T008, T010 (test-scenario files) can all be authored in parallel with each other and with the `SKILL.md` edit tasks, since they are different files
- T003, T005, T007, T009 must NOT run in parallel with each other — all edit the same "Type Safety" section of the same file
- T011 (test runner) can be authored in parallel with any of the above — different file

---

## Parallel Example: User Story 1

```bash
# T003 (SKILL.md edit) and T004 (test scenario) touch different files —
# T004 can be drafted in parallel with T003:
Task: "Add FR-001/FR-002 instruction bullets to coder SKILL.md"
Task: "Create tests/type-safety-coder/001-typed-public-interface.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001)
2. Complete Phase 2: Foundational (T002) — CRITICAL, blocks all stories
3. Complete Phase 3: User Story 1 (T003, T004)
4. **STOP and VALIDATE**: manually spot-check per `quickstart.md` step 1

### Incremental Delivery

1. Setup + Foundational → scaffold ready
2. Add User Story 1 (P1) → validate → this alone already changes default annotation behavior
3. Add User Story 2 (P2) → validate → escape-hatch discipline added
4. Add User Story 3 (P2) → validate → type-checker verification added
5. Add User Story 4 (P3) → validate → boundary validation added
6. Polish: runner, CLAUDE.md reference, full-suite validation

## Notes

- All `SKILL.md` edit tasks (T002, T003, T005, T007, T009) share one file — do not parallelize them; commit after each to keep the diff reviewable.
- Test-scenario files (T004, T006, T008, T010) are independent of each other and of the `SKILL.md` edits — parallelize freely.
- Stop at any checkpoint to spot-check that story's behavior per `quickstart.md` before continuing.
- Avoid: adding type annotations to code outside this instruction change, inventing a new typing convention, or expanding scope into a standalone skill (see `research.md` Decision 1).
