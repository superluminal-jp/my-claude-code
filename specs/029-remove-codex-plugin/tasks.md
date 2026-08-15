# Tasks: Remove the codex-plugin-cc Claude Code Plugin

**Input**: Design documents from `/specs/029-remove-codex-plugin/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md (N/A — no entities), quickstart.md

**Tests**: This feature is a pure deletion verified by the existing deterministic installer suite (`tests/run-install.sh`) plus repository-wide `grep` checks in quickstart.md — no new unit/contract tests are warranted (no new behavior is introduced). Per the `coder` skill's red→green discipline, each story's verification command is run *before* its edit (expected to still show the old behavior/reference) and *after* (expected clean), rather than adding a synthetic failing test for a deletion.

**Organization**: Tasks are grouped by user story (US1, US2, US3 from spec.md), in priority order.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)

## Path Conventions

Single-project tooling repo. All paths are repository-root-relative: `install.sh`, `tests/run-install.sh`.

---

## Phase 1: Setup

Not applicable — no project initialization, dependency install, or scaffolding is required. Both target files already exist.

---

## Phase 2: Foundational

Not applicable — no shared infrastructure blocks the user stories below. US1/US2 edit `install.sh` sequentially (same file); US3 edits `tests/run-install.sh` independently.

---

## Phase 3: User Story 1 - Running the installer no longer installs codex-plugin-cc (Priority: P1) 🎯 MVP

**Goal**: `install.sh` no longer registers the `codex-plugin-cc` marketplace or installs `codex@openai-codex`.

**Independent Test**: Run `install.sh` against an isolated home with stubbed `claude`/`uvx`; the stub's command log contains no `plugin marketplace add`, `plugin marketplace update`, or `plugin install` call for `codex-plugin-cc` / `openai-codex` / `codex@openai-codex`.

- [ ] T001 [US1] Confirm current state: run `grep -n "codex-plugin-cc\|openai-codex\|codex@openai-codex" install.sh` and verify the section-4 block (lines ~123-131) is present (pre-change baseline).
- [ ] T002 [US1] Delete section 4 from `install.sh` (the `# 4. Install codex-plugin-cc ...` comment and both `if` blocks, lines 123-131, plus the blank line separating them from the closing `echo`), per research.md R1 — leave the `upsert_user_mcp microsoft-learn` block and the closing `echo "Done. ..."` line adjacent with a single blank line between them.
- [ ] T003 [US1] Verify: run `grep -n "codex-plugin-cc\|openai-codex\|codex@openai-codex" install.sh` and confirm no output.

**Checkpoint**: `install.sh` contains no codex-plugin-cc install logic. Story 1 is independently complete and testable via `bash tests/run-install.sh` (still using the not-yet-updated stub from US3 at this point — it will still pass, since the stub's extra branches are merely unused, not exercised).

---

## Phase 4: User Story 2 - The installer's section comments read cleanly (Priority: P2)

**Goal**: `install.sh`'s remaining numbered step comments are contiguous and each accurately describes the code beneath it.

**Independent Test**: Read `install.sh` top to bottom; run `grep -nE '^# [0-9]' install.sh` and confirm the sequence `0.`, `1.`, `2.`, `3.` with no gap and no reference to a deleted step.

- [ ] T004 [US2] Verify (no edit expected): run `grep -nE '^# [0-9]' install.sh` after T002 and confirm the sequence is `0.` (preflight), `1.` (sync managed paths), `2.` (chmod), `3.` (MCP upsert) — contiguous, per research.md R2 (step 4 was the last step, so its deletion leaves no gap).
- [ ] T005 [US2] Read the full file (`install.sh`) end to end and confirm no remaining comment references the deleted codex-plugin-cc step or otherwise describes code that no longer exists, per research.md R3.

**Checkpoint**: `install.sh`'s comments read as a complete, gap-free, accurate sequence. Story 2 is independently verifiable by inspection plus the grep in T004 — no code change beyond T002 was required (research.md R2/R3 confirmed the deletion alone satisfies this story).

---

## Phase 5: User Story 3 - The installer test suite has no dead stubs (Priority: P1)

**Goal**: `tests/run-install.sh`'s `claude` stub no longer special-cases `plugin marketplace list` / `plugin list`.

**Independent Test**: Run `tests/run-install.sh`; it passes, and `grep -n "plugin marketplace list\|plugin list" tests/run-install.sh` returns no output.

- [ ] T006 [US3] Confirm current state: run `grep -n "plugin marketplace list\|plugin list" tests/run-install.sh` and verify the two stub branches (lines ~45-49) are present (pre-change baseline).
- [ ] T007 [US3] Edit the `claude` stub heredoc in `tests/run-install.sh` (lines 40-50) to remove the `if [ "${1:-}" = "plugin" ] && [ "${2:-}" = "marketplace" ] && [ "${3:-}" = "list" ]; then ... elif ... fi` block, leaving only the `printf '%s\n' "$*" >>"$CLAUDE_LOG"` line inside the stub, per research.md R4.
- [ ] T008 [US3] Verify: run `grep -n "plugin marketplace list\|plugin list" tests/run-install.sh` and confirm no output.
- [ ] T009 [US3] Run `bash tests/run-install.sh` and confirm it passes end to end (exercises T002's `install.sh` change together with T007's stub cleanup).

**Checkpoint**: `tests/run-install.sh` has no dead stub branches and passes. All three user stories are complete.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Full-repository verification per spec.md Success Criteria.

- [ ] T010 Run `bash -n install.sh tests/run-install.sh` (syntax check) and, if available, `shfmt -d -i 2 install.sh tests/run-install.sh` and `shellcheck install.sh tests/run-install.sh`.
- [ ] T011 Run the full quickstart.md validation sequence (all 7 steps) and confirm every expected outcome holds, in `specs/029-remove-codex-plugin/quickstart.md`.
- [ ] T012 [P] Run the full remaining behavior-suite set: `for t in tests/run-*.sh; do bash "$t" || echo "FAILED: $t"; done` and confirm every suite passes (SC-003).
- [ ] T013 [P] Run `git status --porcelain docs/adr/` and confirm no output (SC-005 — no ADR was added or modified, per spec.md Assumptions).

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup / Foundational**: N/A — work starts immediately at Phase 3.
- **User Story 1 (Phase 3)**: No dependencies. Must complete before Phase 4's verification (T004/T005 read the post-T002 file).
- **User Story 2 (Phase 4)**: Depends on T002 (US1) having already been applied — it verifies the *result* of that edit rather than making an independent code change.
- **User Story 3 (Phase 5)**: Independent of US1/US2 at the edit level (different file), but T009's end-to-end run exercises both `install.sh` (T002) and the stub (T007) together, so US1 should land first for a meaningful T009 run.
- **Polish (Phase 6)**: Depends on US1, US2, and US3 all being complete.

### User Story Dependencies

- **US1 (P1)**: No dependency on other stories. This is the MVP — the actual removal.
- **US2 (P2)**: Logically sequenced after US1 (verifies US1's side effect); no separate code change of its own.
- **US3 (P1)**: Independent edit (different file); best validated after US1 lands.

### Parallel Opportunities

- T012 and T013 (Phase 6) can run in parallel — different commands, no shared state.
- US3 (T006-T008, on `tests/run-install.sh`) can be edited in parallel with US1 (T001-T003, on `install.sh`) by different contributors, since they touch different files; only the final integration check (T009) requires both to be done.

---

## Parallel Example: Phase 6

```bash
# Launch independent verification checks together:
Task: "Run full behavior-suite set (tests/run-*.sh)"
Task: "Confirm docs/adr/ has no uncommitted changes"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. T001-T003: delete the plugin-install section from `install.sh`.
2. **STOP and VALIDATE**: `bash tests/run-install.sh` still passes (US3's stub cleanup is not required for US1 alone to be correct — the unused stub branches are harmless dead code until US3 removes them).
3. This alone satisfies the maintainer's core ask: the installer no longer installs the deprecated plugin.

### Incremental Delivery

1. US1 (T001-T003) → installer no longer installs the plugin → deploy/demo (MVP).
2. US2 (T004-T005) → confirm comment cleanliness (verification-only, no additional edit needed).
3. US3 (T006-T009) → test suite has no dead stubs → full installer contract re-verified end to end.
4. Polish (T010-T013) → lint, full quickstart, full suite, ADR-untouched check.

---

## Notes

- This feature is small enough that most tasks are single-line edits or verification greps; task granularity favors traceability to spec.md's acceptance scenarios over splitting for its own sake.
- Commit after Phase 5 (all three stories complete) rather than per-task, consistent with `rules/git-workflow.md`'s "one logical change per commit" — the codex-plugin-cc removal is one logical change spanning both files.
- No `data-model.md` entities or `contracts/` exist for this feature (see plan.md, research.md R6/R7) — no tasks map from either.
