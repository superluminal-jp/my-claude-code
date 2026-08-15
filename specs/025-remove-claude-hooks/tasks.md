# Tasks: Remove .claude/hooks/ Entirely

**Input**: Design documents from `/specs/025-remove-claude-hooks/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md (no `contracts/`)

**Tests**: Validation tasks are grep/suite-run steps from quickstart.md, not new test code.

**Organization**: Tasks grouped by user story (US1 = P1, US2 = P2).

**Delegation**: Per the maintainer's explicit "use subagents" instruction, T004/T005 (README bulk edits) and T008-T011 (guardrail test edits) are executed via subagent delegation during `/speckit-implement` — their replacement content is fully predetermined in research.md R1/R2, so the subagents execute, not decide (`subagent-delegation.md`: "never delegate understanding"). Everything touching settings.json, install.sh, AGENTS.md, and verification runs directly in the main conversation, since those are either small/precise or load-bearing for judging whether the rest succeeded.

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup / Phase 2: Foundational

Not applicable — feature branch already created, no shared infrastructure blocks either story.

---

## Phase 3: User Story 1 - Hooks are gone with no dangling references (Priority: P1) 🎯 MVP

**Goal**: Delete `.claude/hooks/`, remove its wiring, and correct every document that described it as live.

**Independent Test**: quickstart.md steps 1-4.

### Implementation for User Story 1

- [X] T001 [US1] Delete `.claude/hooks/` (all 7 files: `pre-bash.sh`, `pre-edit.sh`, `post-edit-format.sh`, `user-prompt-submit.sh`, `speckit-expand-update.sh`, `statusline.sh`, `README.md`)
- [X] T002 [US1] Edit `.claude/settings.json`: remove the `hooks` key and the top-level `statusLine` key (research.md R1)
- [X] T003 [US1] Edit `install.sh`: remove line 95 (`chmod +x "$TARGET_DIR"/hooks/*.sh`); keep `sync_path "hooks"` (line 58) unchanged — it is the uninstall path per spec-024 precedent; reword the comments at lines 3, 55, and 80-83 so they no longer describe `.claude/hooks/*.sh` as an existing thing being deployed (research.md R1)
- [X] T004 [P] [US1] **Delegated to subagent**: Edit `README.md` per research.md R1/R2 — 9 locations including the comparison table rewrite
- [X] T005 [P] [US1] **Delegated to subagent** (same call as T004): Edit `README.ja.md` — mirrored edits in Japanese
- [X] T006 [US1] Edit `AGENTS.md`: lines 61, 66, 90, and the section framing sentence
- [X] T007 [US1] Ran the grep validation from quickstart.md step 3. **Found and fixed one unplanned gap**: `.claude/rules/permissions.md` had two live references to the deleted `.claude/hooks/README.md` that the original spec incorrectly assumed didn't exist (FR-012 amended — see spec.md Edge Cases). Fixed directly, then re-validated clean.

**Checkpoint**: User Story 1 complete and independently verifiable via T007.

---

## Phase 4: User Story 2 - Remaining tests still test something real (Priority: P2)

**Goal**: Guardrail test suites test only what still exists.

**Independent Test**: quickstart.md step 5.

### Implementation for User Story 2

- [X] T008 [P] [US2] **Delegated to subagent** (batched with T009-T011 in one call): Edit `tests/run-destructive-command-guard.sh` — removed `CLAUDE_HOOK` var and 2 assertions, `SHARED` assertions untouched. Verified passing (18/18).
- [X] T009 [P] [US2] Edit `tests/run-pre-edit-guard.sh` — removed `CLAUDE_HOOK` var and 3 assertions. Verified passing (4/4).
- [X] T010 [P] [US2] Edit `tests/run-post-edit-format-guard.sh` — removed `CLAUDE_HOOK` var and 1 assertion. Verified passing (2/2).
- [X] T011 [P] [US2] Edit `tests/run-prompt-secret-guard.sh` — removed `CLAUDE_HOOK` var and 3 assertions. Verified passing (9/9).
- [X] T012 [US2] Delete `tests/run-speckit-update.sh` entirely
- [X] T013 [US2] Ran every remaining `tests/run-*.sh` suite. **Found and fixed one unplanned gap**: `tests/run-codex-references.sh` RULE-09 (from spec-021, NFR-002) asserted `.claude/settings.json` still had four hook events — not caught by the original impact survey since it checks `settings.json`'s `hooks` key structure, not a `.claude/hooks/` file path. Fixed to assert only `permissions.deny` (FR-015 added — see spec.md). Full suite re-run: all 12 remaining suites pass.

**Checkpoint**: Both user stories verified — feature complete pending polish.

---

## Phase 5: Polish

- [X] T014 Confirmed `install.sh` syntax OK and no dangling `chmod ... hooks` line
- [X] T015 Drafted `docs/adr/0005-remove-claude-hooks.md` via the `adr` skill (FR-014/SC-005), status `Proposed` pending maintainer acceptance

---

## Dependencies & Execution Order

- **User Story 1 (Phase 3)**: T001-T003 can run in any order relative to each other but should precede T007 (verification needs the deletions/edits done). T004/T005 (subagent-delegated) are independent of T001-T003 (different files) and of each other — dispatch in parallel.
- **User Story 2 (Phase 4)**: Independent of User Story 1's file set (different files) except that T013's suite run is only meaningful after both stories' edits land — run T013 last.
- **Polish (Phase 5)**: T014 depends on T003. T015 (ADR) depends on nothing else being incomplete — write it once the removal itself is verified (T007, T013) so the ADR's "Consequences" section can state verified facts, not predictions.

### Parallel Example

```bash
# T004, T005 (subagent-delegated), and T008-T011 (test edits) touch disjoint
# file sets and can all be dispatched together:
Task: "Edit README.md per research.md R1/R2"
Task: "Edit README.ja.md per research.md R1/R2"
Task: "Edit the four guardrail test suites per research.md R1 (drop CLAUDE_HOOK assertions only)"
```

## Implementation Strategy

1. T001-T003, T006 directly (small, precise, or judgment-heavy — settings.json/install.sh/AGENTS.md).
2. Dispatch T004, T005 (README pair) and T008-T011 (test-file batch) to subagents in parallel — their exact replacement content is already decided in research.md, so this is execution, not decision-making.
3. T007 verifies User Story 1; T012-T013 finish and verify User Story 2.
4. T014 polish check, then T015 (ADR) as the final close-out step.

## Notes

- Commit only when the maintainer explicitly asks.
- No task writes new test code; edits remove dead assertions or delete files whose subject is gone.
