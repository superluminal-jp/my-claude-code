# Tasks: Clarify Skill Pre-Trigger on Speckit Specify

**Input**: Design documents from `specs/008-clarify-pretrigger-specify/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓

**Note**: This feature is a single YAML configuration change. No source code, no automated tests.
Verification is manual (run `/speckit-specify` and observe hook output).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm prerequisites before making the change

- [x] T001 Verify `.claude/skills/clarifier/SKILL.md` exists and `name: clarifier` is declared in frontmatter
- [x] T002 [P] Verify `.specify/extensions.yml` is valid YAML and `hooks.before_specify` list is present

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Understand current before_specify hook order before inserting the new entry

**⚠️ CRITICAL**: Must complete T001 and T002 before modifying extensions.yml

- [x] T003 Read current `before_specify` list in `.specify/extensions.yml` and note the existing entries (ubiquitous-language, speckit.git.feature) and their positions

**Checkpoint**: Extension list confirmed — ready to insert clarifier hook as first entry

---

## Phase 3: User Story 1 — Clarify Runs Before Spec Generation (Priority: P1) 🎯 MVP

**Goal**: When `/speckit-specify` is invoked, the speckit-specify playbook presents the clarifier as an optional pre-hook prompt before spec generation begins.

**Independent Test**: Run `/speckit-specify "test feature"` and confirm the output contains:
```
**Optional Pre-Hook**: clarifier
Command: `/clarifier`
```
Then run `/clarifier`, answer the questions, and verify the generated spec.md reflects the answers.

### Implementation for User Story 1

- [x] T004 [US1] Add clarifier hook entry as the **first** item in `hooks.before_specify` in `.specify/extensions.yml`:
  ```yaml
  - extension: clarifier
    command: clarifier
    enabled: true
    optional: true
    prompt: Run clarifier before specifying to sharpen requirements?
    description: Elicit intent, scope, constraints, and acceptance criteria before generating the spec
    condition: null
  ```
- [x] T005 [US1] Confirm hook list order in `.specify/extensions.yml` is: clarifier → ubiquitous-language → speckit.git.feature
- [x] T006 [US1] Manual verification: run `/speckit-specify "test feature description"` and confirm clarifier hook is presented in the pre-execution output

**Checkpoint**: User Story 1 complete — clarifier hook triggers on `/speckit-specify`

---

## Phase 4: User Story 2 — Enable/Disable via extensions.yml (Priority: P2)

**Goal**: Users can set `enabled: false` in the clarifier hook entry to suppress it project-wide without removing the entry.

**Independent Test**: Set `enabled: false` on the clarifier entry, run `/speckit-specify "test"`, and confirm clarifier hook does NOT appear in the pre-execution output. Restore to `enabled: true` after verification.

### Implementation for User Story 2

- [x] T007 [US2] Manual verification: temporarily set `enabled: false` on the clarifier hook entry in `.specify/extensions.yml`
- [x] T008 [US2] Run `/speckit-specify "test feature"` and confirm clarifier hook is absent from output
- [x] T009 [US2] Restore `enabled: true` on the clarifier hook entry

**Checkpoint**: Enable/disable control verified

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Regression check — existing hooks must be unaffected

- [x] T010 [P] Manual regression: run `/speckit-specify "test"` and confirm ubiquitous-language hook still appears as Optional Pre-Hook
- [x] T011 [P] Manual regression: confirm speckit.git.feature hook still appears as Automatic Pre-Hook (mandatory) and executes
- [x] T012 Run quickstart.md validation: follow the steps in `specs/008-clarify-pretrigger-specify/quickstart.md` end-to-end and confirm no discrepancies

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately (T001, T002 in parallel)
- **Foundational (Phase 2)**: Depends on T001 + T002 completion
- **User Story 1 (Phase 3)**: Depends on T003 completion — the single YAML change
- **User Story 2 (Phase 4)**: Depends on T004 (the hook entry must exist to test disable)
- **Polish (Phase 5)**: Depends on US1 and US2 completion

### User Story Dependencies

- **US1 (P1)**: Can start immediately after Phase 2 — no dependencies on US2
- **US2 (P2)**: Depends on US1 completion (hook entry must be present to test enable/disable)

### Within Each Phase

- T001 and T002 can run in parallel (different files)
- T007–T009 must run sequentially (set disabled → verify → restore)
- T010 and T011 can run in parallel

---

## Parallel Example: Phase 1

```
Launch T001 and T002 in parallel:
  Task: "Verify .claude/skills/clarifier/SKILL.md exists"
  Task: "Verify .specify/extensions.yml is valid YAML"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Verify prerequisites (T001, T002)
2. Complete Phase 2: Read current hook list (T003)
3. Complete Phase 3: Add YAML entry and verify (T004–T006)
4. **STOP and VALIDATE**: `/speckit-specify` shows clarifier hook
5. Ship: the feature is done

### Incremental Delivery

1. Setup + Foundational → confirmed prerequisites
2. US1 → clarifier hook active (MVP — spec quality improves immediately)
3. US2 → enable/disable confirmed (operational control)
4. Polish → regressions cleared

---

## Notes

- [P] tasks can run in parallel (different files / independent verification steps)
- No automated tests — all verification is manual interactive testing in Claude Code
- The entire implementation is T004 (one YAML entry); all other tasks are verification
- Estimated effort: ~15 minutes end-to-end (config change + manual verification)
