# Tasks: Remove the permissions Block Entirely

**Input**: Design documents from `/specs/026-remove-permissions-config/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Delegation**: Scope is small (9 files) and every replacement's exact text is already drafted in research.md — executed directly in the main conversation, no subagent delegation needed this time.

## Phase 1: Setup / Phase 2: Foundational

Not applicable.

## Phase 3: User Story 1 - No dangling references (Priority: P1) 🎯 MVP

- [X] T001 [US1] Edit `.claude/settings.json`: remove `permissions` key
- [X] T002 [US1] Edit `.claude/settings.local.json`: remove `permissions` key
- [X] T003 [US1] Edit `.claude/rules/permissions.md`: fix Credential Safety closing line; remove "## `.claude/settings.json` permissions" section
- [X] T004 [US1] Edit `.claude/rules/git-workflow.md` line 3
- [X] T005 [US1] Edit `README.md`: 3 locations
- [X] T006 [US1] Edit `README.ja.md`: 3 locations
- [X] T007 [US1] Edit `AGENTS.md`: 1 location
- [X] T008 [US1] Ran grep validation — clean (only past-tense descriptions, RULE-09 pending removal in T009, and ADR-0005 correctly left untouched)

## Phase 4: User Story 2 - Decision recorded as its own ADR (Priority: P2)

- [X] T009 [US2] Edit `tests/run-codex-references.sh`: removed RULE-09 block entirely
- [X] T010 [US2] Ran every remaining `tests/run-*.sh` suite — all 12 pass
- [X] T011 [US2] Drafted `docs/adr/0006-remove-permissions-config.md` via the `adr` skill (status `Proposed`); confirmed ADR-0005 byte-for-byte unchanged (`git diff --stat` empty)

## Notes

Commit only when asked.
