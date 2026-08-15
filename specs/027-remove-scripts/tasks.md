# Tasks: Remove scripts/ Entirely

**Input**: Design documents from `/specs/027-remove-scripts/`

**Delegation**: Direct execution — exact content already drafted in research.md.

## Phase 3: User Story 1 - No dangling references (Priority: P1) 🎯 MVP

- [X] T001 [US1] Delete `scripts/` entirely (guardrails/ 4 files + check-mcp-consistency.sh)
- [X] T002 [US1] Delete the 4 guardrail test suites (`tests/run-{destructive-command,pre-edit,post-edit-format,prompt-secret}-guard.sh`)
- [X] T003 [US1] Edit `install.sh`: replace conditional guardrails sync with unconditional cleanup (research.md R2)
- [X] T004 [US1] Edit `README.md`: 5 locations (research.md R1)
- [X] T005 [US1] Edit `README.ja.md`: 3 locations (research.md R1)
- [X] T006 [US1] Edit `.claude/rules/permissions.md`: 1 location
- [X] T007 [US1] Edit `.claude/rules/mcp.md`: 1 location
- [X] T008 [US1] Run grep validation (quickstart.md step 2)

## Phase 4: User Story 2 - Decision recorded as its own ADR (Priority: P2)

- [X] T009 [US2] Run every remaining `tests/run-*.sh` suite and confirm all pass
  - User-approved exception: 5 suites passed; the 3 suites that require an
    authenticated Claude CLI were treated as skipped after returning
    `Not logged in`.
- [X] T010 [US2] Draft `docs/adr/0007-remove-scripts.md` via the `adr` skill; confirm ADR-0005/0006 unchanged

## Notes

Commit only when asked.
