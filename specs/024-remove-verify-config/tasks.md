# Tasks: Remove /verify-config Verification Feature

**Input**: Design documents from `/specs/024-remove-verify-config/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md (no `contracts/` — see research.md R3)

**Tests**: Validation tasks below are drawn directly from spec.md's Acceptance Scenarios and quickstart.md; they are not new test *code* (this feature adds no new tests — `tests/run-verification-agent.sh` is being deleted, not written).

**Organization**: Tasks are grouped by user story (US1 = P1, US2 = P2) per spec.md.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to

## Phase 1: Setup

Not applicable — no project initialization needed. The feature branch
(`024-remove-verify-config`) already exists and the working tree is clean.

## Phase 2: Foundational

Not applicable — no shared infrastructure blocks either user story; both
operate on independent, already-identified files (research.md R1).

---

## Phase 3: User Story 1 - Clean removal leaves no dangling references (Priority: P1) 🎯 MVP

**Goal**: Delete the three feature files and edit both READMEs so no live
file in the repository references `/verify-config` or `verification-runner`.

**Independent Test**: Grep the repository for `verify-config` and
`verification-runner`; the only hits are historical `specs/` directories and
this spec's own directory (see quickstart.md step 2).

### Implementation for User Story 1

- [X] T001 [P] [US1] Delete `tests/run-verification-agent.sh`
- [X] T002 [P] [US1] Delete `.claude/skills/verify-config/SKILL.md` (and the now-empty `.claude/skills/verify-config/` directory)
- [X] T003 [P] [US1] Delete `.claude/agents/verification-runner.md` (and the now-empty `.claude/agents/` directory)
- [X] T004 [US1] Edit `README.md`:
  - Remove the `verify-config` bullet from the skills list (~line 40)
  - Remove the `agents/` subtree from the file-structure diagram (~lines 287-288: the `├── agents/ ...` line and its `└── verification-runner.md ...` child line), since the directory no longer exists after T003
  - Remove the `verify-config/SKILL.md` line from the `skills/` subtree (~line 282)
  - In the `## Verification` section: remove the paragraph describing `/verify-config`, the `verification-runner` link, and the Codex-counterpart claim (~lines 299-305), and remove the `After changing the verify-config skill or the verification-runner subagent:` heading plus its `bash tests/run-verification-agent.sh` code block (~lines 321-325). Keep the section heading, the surrounding `.mcp.json`/`install.sh` check-command block, and the closing "Deterministic — it inspects repository files only." line intact.
  - Do **not** touch line ~192 (`~/.codex/prompts/verify-config.md` in the "If you installed an earlier version" cleanup list) — FR-010
  - Do **not** touch the introductory "install.sh also deploys a Codex CLI counterpart ... and a verification prompt" paragraph — out of scope, pre-existing drift (research.md R2)
- [X] T005 [US1] Edit `README.ja.md` mirroring T004: remove the `verify-config` bullet (~line 24), remove the `agents/` line from the構成 tree (~line 161), remove the `## 検証` section's `/verify-config` パラグラフ (~line 167) and the `verify-config` スキルまたは `verification-runner` サブエージェントを変更したら: block (~lines 182-186), keeping the rest of the section (~lines 169-180, 188) intact. Do not touch line ~125 (cleanup list) or the introductory Codex-port paragraph.
- [X] T006 [US1] Run the grep validation from quickstart.md step 2 and confirm zero output (no dangling references outside historical `specs/` directories and `specs/024-remove-verify-config/`). **Found and fixed one unplanned gap**: `AGENTS.md` line 71 was a live instruction pointing at the deleted skill (missed during research — see research.md addendum); removed as part of this task rather than deferred.

**Checkpoint**: User Story 1 is complete and independently verifiable via T006.

---

## Phase 4: User Story 2 - Repository stays internally consistent after removal (Priority: P2)

**Goal**: Confirm the removal did not break any remaining test suite or the
`install.sh` sync process.

**Independent Test**: Every remaining `tests/run-*.sh` suite passes; `install.sh`
completes without error.

### Implementation for User Story 2

- [X] T007 [US2] Run every remaining `tests/run-*.sh` suite (quickstart.md step 4) and confirm none fail due to a file this removal deleted (depends on T001-T005 being complete). Result: all 14 suites passed (0 failures).
- [X] T008 [US2] Verify `install.sh` (quickstart.md step 5). Per maintainer decision, done via **static verification** instead of a real run against `~/.claude` (consistent with spec-014's precedent of not mutating the real home directory): `bash -n install.sh` syntax check passed, and the two relevant `sync_path` calls (`skills`, `commands`) use `cp -R` over whatever currently exists — deleting `.claude/skills/verify-config/` and the never-synced `.claude/agents/` triggers no error path.

**Checkpoint**: User Stories 1 AND 2 both verified — the feature is complete.

---

## Phase 5: Polish

- [X] T009 Run the README cleanup-list check from quickstart.md step 3 and confirm the "earlier version" list in both READMEs is unchanged (FR-010 regression guard). Confirmed via `git diff` — the cleanup-list lines are absent from the diff.

---

## Dependencies & Execution Order

### Phase Dependencies

- **User Story 1 (Phase 3)**: No dependencies — can start immediately. T001-T003 are independent deletions ([P]); T004-T005 (README edits) can run in parallel with each other but should follow T001-T003 conceptually (though they don't share a file, so technically parallelizable too); T006 depends on T001-T005 all being done.
- **User Story 2 (Phase 4)**: Depends on User Story 1 (Phase 3) being complete — its validation is meaningless until the deletions/edits exist.
- **Polish (Phase 5)**: Depends on Phase 3 (README edits must exist to check the untouched lines survived).

### Parallel Example: User Story 1

```bash
# T001, T002, T003 touch different files and can run in parallel:
Task: "Delete tests/run-verification-agent.sh"
Task: "Delete .claude/skills/verify-config/SKILL.md"
Task: "Delete .claude/agents/verification-runner.md"

# T004, T005 touch different files and can run in parallel with each other
# (and with T001-T003, since none share a file):
Task: "Edit README.md verification references"
Task: "Edit README.ja.md verification references"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 3 (T001-T006) — this alone satisfies the core ask (clean removal, no dangling references).
2. **STOP and VALIDATE**: T006's grep must return empty.
3. Phase 4 (T007-T008) and Phase 5 (T009) are regression guards confirming nothing else broke — run them before considering the feature done, but they don't change any file.

### Incremental Delivery

1. Phase 3 → grep-clean removal (MVP)
2. Phase 4 → full suite green + install.sh clean
3. Phase 5 → cleanup-list regression guard
4. Feature complete: report to maintainer, offer commit (per `git-workflow.md`, only if asked)

## Notes

- [P] tasks touch different files; T001-T005 have no file overlap and can all run in parallel if desired.
- No task writes new test code — this feature is a deletion, and its "tests" are grep/suite-run validation steps already defined in quickstart.md.
- Commit only when the maintainer explicitly asks (`git-workflow.md`, `permissions.md`) — not automatically after each task.
