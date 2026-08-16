# Tasks: Remove subagent-delegation Rule

**Input**: Design documents from `/specs/030-remove-subagent-delegation-rule/`

**Delegation**: Direct execution — three files, no new abstractions.

## Phase 3: User Story 1 - Always-loaded context shrinks with no dangling references (Priority: P1) 🎯 MVP

- [X] T001 [US1] Delete `.claude/rules/subagent-delegation.md` entirely
- [X] T002 [US1] Edit `.claude/CLAUDE.md`: remove the `@.claude/rules/subagent-delegation.md` include line and the cross-reference sentence in the "Execution: parallelize whenever valid" section, keeping the rest of the section self-contained
- [X] T003 [US1] Edit `README.md`: remove the `subagent-delegation.md` line from the repository file-tree listing (line 247)
- [X] T004 [US1] Run quickstart.md steps 1-5 (file absence, grep for dangling references, CLAUDE.md/README.md coherence check, historical specs untouched) and confirm all pass

## Dependencies

T001 → T002 → T003 → T004 (sequential; T002/T003 are independent edits but touch different files so may run in either order — T004 depends on both).

## Implementation Strategy

Single user story, single MVP: delete the file, strip its two references,
verify. No tests beyond the quickstart grep/read checks — there is no code
to unit-test in an instruction-file removal.
