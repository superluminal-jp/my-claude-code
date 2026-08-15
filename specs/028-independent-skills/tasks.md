# Tasks: Skill Bodies Independent of Sibling Skills

**Input**: Design documents from `/specs/028-independent-skills/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Delegation**: Scope is small (8 files) and every replacement's exact text is already drafted in research.md — executed directly in the main conversation, no subagent delegation needed.

## Phase 1: Setup / Phase 2: Foundational

Not applicable — no shared infrastructure; each edit is independent text replacement in an existing file.

## Phase 3: User Story 1 - digital-agency-frontend works without naming coder or clarifier (Priority: P1) 🎯 MVP

- [X] T001 [US1] Edit `.claude/skills/digital-agency-frontend/SKILL.md`: replace "## Compose the workflow" section per research.md R1 (rename heading, drop `coder`/`clarifier` naming, inline the substantive requirement)
- [X] T002 [US1] Edit `.claude/skills/digital-agency-frontend/SKILL.md`: rename "### 4. Implement through `coder`" heading and add the type-safety bullet, per research.md R1
- [X] T003 [US1] Edit `.claude/skills/digital-agency-frontend/SKILL.md`: fix "### 6. Close out with traceability" bullet (drop "required by `coder` and") and add the documentation-sync bullet, per research.md R1
- [X] T004 [US1] Edit `specs/015-digital-agency-frontend/spec.md`: rewrite FR-004 and its Assumptions line per research.md R7
- [X] T005 [US1] Edit `tests/run-digital-agency-frontend-skill.sh`: rewrite DADS-06 and DADS-07 assertions per research.md R8, checked against the actual T001–T003 text
- [X] T006 [US1] Run `bash tests/run-digital-agency-frontend-skill.sh`; confirm all checks pass including unmodified SYNC-SKILL-05A
- [X] T007 [US1] Run quickstart.md steps 1–4 (grep for removed instructions, grep for inlined behavior, confirm router files untouched, confirm FR-004 supersession text present)

## Phase 4: User Story 2 - coder and adr describe their own scope without naming each other (Priority: P2)

- [X] T008 [P] [US2] Edit `.claude/skills/coder/SKILL.md`: remove the `adr`-loading line per research.md R2
- [X] T009 [P] [US2] Edit `.claude/skills/adr/SKILL.md`: reword purpose statement per research.md R3

## Phase 5: User Story 3 - the minto triad each describe only their own function (Priority: P3)

- [X] T010 [P] [US3] Edit `.claude/skills/minto-builder/SKILL.md`: remove the two routing sentences per research.md R4
- [X] T011 [P] [US3] Edit `.claude/skills/minto-reviewer/SKILL.md`: remove the two routing sentences per research.md R5
- [X] T012 [P] [US3] Edit `.claude/skills/minto-rewriter/SKILL.md`: remove the two routing sentences per research.md R6

## Phase 6: Polish & Cross-Cutting

- [X] T013 Run quickstart.md step 1 across all six SKILL.md files (confirms T001–T003, T008–T012 together)
- [X] T014 Run the full remaining `tests/run-*.sh` suite (quickstart.md step 6); confirm zero failures
- [X] T015 Confirm `docs/adr/` has no new file (quickstart.md step 7) — no ADR needed per research.md R11

## Dependencies

- T001 → T002, T003 (same file, same section rename referenced by T002's heading edit — do in order within the file, but all three can be one pass)
- T001–T003 → T005 (DADS-07's assertion text must match what T001–T003 actually wrote)
- T004 independent of T001–T003 but must land in the same change (data-model.md: FR-004 drift if separated)
- T006, T007 depend on T001–T005 complete
- T008–T012 are fully independent of US1 and of each other — parallelizable
- T013–T015 depend on all prior tasks complete

## Parallel execution example

```
# After T001–T007 (US1) land, T008–T012 can run in parallel (different files, no shared state):
T008, T009, T010, T011, T012
```

## Implementation strategy

MVP = User Story 1 alone (T001–T007): resolves the specific conflict named in the request (spec 015 FR-004, DADS-06/07) and the largest cross-reference (4 instructions in one file). User Stories 2 and 3 are lower-risk, untested-by-suite cleanups that can land in the same change or be deferred without leaving US1 incomplete.

## Notes

Commit only when asked.
