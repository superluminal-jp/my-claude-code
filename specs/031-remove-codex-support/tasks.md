# Tasks: Remove Codex CLI Support and All Codex References

**Input**: Design documents from `/specs/031-remove-codex-support/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md (N/A — no entities), quickstart.md

**Tests**: This feature is a documentation/tooling removal verified by the existing deterministic test suites (`tests/run-subagent-delegation.sh`, `tests/run-digital-agency-frontend-skill.sh`, `tests/run-mcp-startup.sh`) plus repository-wide `grep` checks in quickstart.md — no new unit/contract tests are warranted (no new behavior is introduced). Per the `coder` skill's red→green discipline, each story's verification command is run *before* its edit (expected to still show Codex references) and *after* (expected clean), rather than adding a synthetic failing test for a deletion.

**Organization**: Tasks are grouped by user story (US1-US4 from spec.md), in priority order. Tasks within a phase that touch different files and have no dependency on each other are marked `[P]` and are intended to be dispatched to parallel subagents during implementation.

## Format: `[ID] [P?] [Story] Description`

## Path Conventions

Single-project tooling/documentation repo. All paths are repository-root-relative.

---

## Phase 1: Setup

Not applicable — no project initialization, dependency install, or scaffolding is required. All target files already exist except the new ADR.

---

## Phase 2: Foundational

Not applicable — no shared infrastructure blocks the user stories below. Every story below edits a disjoint set of files (only README.md/README.ja.md are shared between US1 and US2's AGENTS.md-reference cleanup, but each touches a different, non-overlapping line range — see research.md R2/R3).

---

## Phase 3: User Story 1 - The repository no longer ships any Codex-facing guidance (Priority: P1) 🎯 MVP

**Goal**: `AGENTS.md` no longer exists, and no other file dangles a reference to it.

**Independent Test**: `test -f AGENTS.md` fails; `grep -rn "AGENTS\.md" --exclude-dir=.git --exclude-dir=specs --exclude-dir=docs .` returns no output.

- [ ] T001 [US1] Confirm baseline: run `grep -rl "AGENTS.md" --exclude-dir=.git --exclude-dir=specs .` and record every referencing file (expected: `README.md`, `README.ja.md`, `tests/run-subagent-delegation.sh`, `tests/run-digital-agency-frontend-skill.sh`), per research.md R1.
- [ ] T002 [US1] Delete `AGENTS.md` from the repository root.
- [ ] T003 [US1] Verify: run `test -f AGENTS.md && echo FAIL || echo OK` and confirm `OK`.

**Checkpoint**: `AGENTS.md` is gone. The four referencing files are updated in US2/US3 below (this story's independent test for *dangling* references only passes once those land too — US1 alone only guarantees the file itself is deleted).

---

## Phase 4: User Story 2 - The documentation makes no Codex claims (Priority: P1)

**Goal**: `README.md`, `README.ja.md`, and `install.sh` contain no Codex mention and no dangling reference to the deleted `AGENTS.md` or the deleted test suites.

**Independent Test**: `grep -ni codex README.md README.ja.md install.sh` returns no output.

- [ ] T004 [P] [US2] Confirm baseline: run `grep -ni codex README.md` and record the full line list (expected: matches research.md R2's ten-location table).
- [ ] T005 [US2] Edit `README.md` per research.md R2 — apply all ten edits: rewrite the lines-13-17 sentence to end after "preserving unrelated user files."; delete the `AGENTS.md` bullet (lines 44-46); delete the entire `## Codex CLI support` section (lines 48-192) leaving exactly one blank line before `## Install as user configuration`; rewrite the lines-208-211 sentence to end after "upserts MCP servers."; delete the "Nothing under `~/.codex`..." bullet (lines 222-225); delete the `AGENTS.md` file-tree row (line 241); delete the two `run-codex-*.sh` lines from the Verification block (lines 277-278); delete the `# specify init --here --force --integration codex` example line (line 369); reword the `.agents/skills/` example sentence to drop the `codex` case (line 381). Depends on T004 for the confirmed anchor set.
- [ ] T006 [US2] Verify: run `grep -ni codex README.md` and confirm no output.
- [ ] T007 [P] [US2] Confirm baseline: run `grep -ni codex README.ja.md` and record the full line list (expected: matches research.md R3's eight-location table).
- [ ] T008 [US2] Edit `README.ja.md` per research.md R3 — apply all eight edits, mirroring T005 in Japanese: delete the standalone Codex paragraph (line 9); delete the "Codex 側には何も展開しません" sentence (line 40, keep the rest of the paragraph); delete the entire `## Codex CLI サポート` section (lines 59-146) leaving one blank line before `## 代替: \`CLAUDE.md\` から import`; delete the `AGENTS.md` file-tree row (line 163); delete the two `run-codex-*.sh` lines from the Verification block (lines 180-181); delete the `# specify init --here --force --integration codex` example line (line 243); reword the `--integration` example sentence to drop the `codex` case, keeping `cursor-agent` (lines 254-255). Depends on T007 for the confirmed anchor set.
- [ ] T009 [US2] Verify: run `grep -ni codex README.ja.md` and confirm no output.
- [ ] T010 [P] [US2] Edit `install.sh` per research.md R4 — delete lines 6-8 (the Codex/AGENTS.md/ADR-0004 disclaimer), leaving the header as: shebang, sync/MCP/plugins description (3 lines), blank, `# Requires: claude CLI, uvx. Optional: GOOGLE_DEV_KNOWLEDGE_API_KEY.`, then the existing Usage lines unchanged.
- [ ] T011 [P] [US2] Verify: run `grep -ni codex install.sh` and confirm no output; run `bash -n install.sh` to confirm the file is still syntactically valid.

**Checkpoint**: `README.md`, `README.ja.md`, and `install.sh` are fully Codex-free and self-consistent (no dangling section links, no gap in the file-structure trees).

---

## Phase 5: User Story 3 - The test suite has no dead or dangling Codex checks (Priority: P1)

**Goal**: The two Codex-only suites are deleted; the two surviving suites that had a Codex-specific check no longer do; `tests/run-mcp-startup.sh`'s comment no longer names Codex.

**Independent Test**: `tests/run-codex-references.sh` and `tests/run-codex-drift.sh` do not exist; `grep -rli codex tests/` returns no output; `tests/run-subagent-delegation.sh`, `tests/run-digital-agency-frontend-skill.sh`, and `tests/run-mcp-startup.sh` run with no new failure versus research.md R12's baseline.

- [ ] T012 [P] [US3] Confirm baseline (pre-change): run `bash tests/run-codex-drift.sh` and `bash tests/run-codex-references.sh`, record pass counts (expected: 6 passed / 9 passed, matching research.md R12).
- [ ] T013 [P] [US3] Delete `tests/run-codex-references.sh` entirely, per research.md R5.
- [ ] T014 [P] [US3] Delete `tests/run-codex-drift.sh` entirely, per research.md R5.
- [ ] T015 [US3] Verify: `test -f tests/run-codex-references.sh && echo FAIL || echo OK` and `test -f tests/run-codex-drift.sh && echo FAIL || echo OK` both print `OK`.
- [ ] T016 [P] [US3] Confirm baseline (pre-change): run `bash tests/run-subagent-delegation.sh`, confirm it fails only on the pre-existing `.claude/rules/subagent-delegation.md`-missing checks and currently also passes `"root AGENTS.md addresses delegation for Codex"`, per research.md R12/R6.
- [ ] T017 [US3] Edit `tests/run-subagent-delegation.sh` per research.md R6 — delete the `AGENTS_MD="$REPO_ROOT/AGENTS.md"` variable declaration (line 19) and the entire R5 block (lines 131-141: the `--- R5: cross-agent parity ---` header, its four-line comment, the `check "root AGENTS.md addresses delegation for Codex"` line, and the trailing blank line). Depends on T016.
- [ ] T018 [US3] Verify: run `grep -ni "codex\|AGENTS_MD\|AGENTS\.md" tests/run-subagent-delegation.sh` and confirm no output; run `bash tests/run-subagent-delegation.sh` and confirm the only failing checks are the pre-existing ones identified in T016 (no check mentioning Codex/AGENTS.md appears in the output at all, pass or fail).
- [ ] T019 [P] [US3] Confirm baseline (pre-change): run `bash tests/run-digital-agency-frontend-skill.sh`, confirm 47 passed including `"SYNC-SKILL-06: Codex routing lists the skill"`, per research.md R12/R7.
- [ ] T020 [US3] Edit `tests/run-digital-agency-frontend-skill.sh` per research.md R7 — delete the `SYNC-SKILL-06` `check_contains` line inside `run_sync_contract()`, and extend the function's leading comment so it states `06` has now also been retired (moved from "kept" to "retired" in the existing "01…04, 06, 07 and 10" list). Depends on T019.
- [ ] T021 [US3] Verify: run `grep -ni "codex\|AGENTS\.md" tests/run-digital-agency-frontend-skill.sh` and confirm no output; run `bash tests/run-digital-agency-frontend-skill.sh` and confirm 46 passed, 0 failed (one fewer than baseline, with no failures).
- [ ] T022 [P] [US3] Edit `tests/run-mcp-startup.sh` per research.md R8 — reword the comment at lines 4-6 to replace "catches packages that Codex would report as a failed MCP handshake." with "is exactly what a client would see as a failed MCP handshake."
- [ ] T023 [P] [US3] Verify: run `grep -ni codex tests/run-mcp-startup.sh` and confirm no output; run `bash tests/run-mcp-startup.sh` and confirm the same pass count as research.md R12's baseline (3/3 packages).

**Checkpoint**: `tests/` directory has zero Codex references anywhere (`grep -rli codex tests/` returns nothing), and every suite this feature touches behaves exactly as predicted by the baseline in research.md R12.

---

## Phase 6: User Story 4 - The decision is recorded, not silently made (Priority: P2)

**Goal**: A new Accepted ADR supersedes ADR-0004; ADR-0002 and ADR-0004's bodies are otherwise untouched.

**Independent Test**: `docs/adr/0010-remove-codex-cli-support.md` exists with `status: Accepted`; `git diff main -- docs/adr/0002-*.md` is empty; `git diff main -- docs/adr/0004-*.md` shows only its `status:` line changed.

- [ ] T024 [US4] Confirm baseline: run `head -5 docs/adr/0002-deploy-codex-configuration-at-user-scope.md docs/adr/0004-adopt-official-codex-import.md` and record their current `status:` lines (expected: `Superseded by 0004` and `Proposed`, per research.md R9).
- [ ] T025 [US4] Change `docs/adr/0004-adopt-official-codex-import.md`'s frontmatter `status:` line only, from `Proposed` to `Superseded by 0010`. No other line in the file changes.
- [ ] T026 [US4] Verify: run `git diff main -- docs/adr/0004-adopt-official-codex-import.md` and confirm exactly one changed line (the `status:` line); run `git diff main -- docs/adr/0002-deploy-codex-configuration-at-user-scope.md` and confirm no output.
- [ ] T027 [US4] Author `docs/adr/0010-remove-codex-cli-support.md` in MADR format (matching the structure of ADR-0001/0004-0009: frontmatter `status: Accepted`, date 2026-08-16, deciders; `# 0010. Remove Codex CLI support`; Context and problem statement — summarizing ADR-0004's Proposed-but-implemented history, ADR-0002's existing Superseded status, and this feature's scope per spec.md; Decision drivers; Considered options; Decision outcome — drop Codex documentation/guidance entirely rather than continue documenting the user-driven `/import` path; Consequences; Confirmation — cite the quickstart.md validation sequence and the edited/deleted test suites; More information — "Supersedes ADR-0004", link to `specs/031-remove-codex-support/`).
- [ ] T028 [US4] Verify: run `head -5 docs/adr/0010-remove-codex-cli-support.md` and confirm `status: Accepted`; confirm the file names ADR-0004 as superseded.

**Checkpoint**: The ADR chain is complete and accurate (0002 → superseded by 0004 → superseded by 0010, Accepted).

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: `.gitignore` cleanup and full-repository verification per spec.md Success Criteria.

- [ ] T029 [P] Edit `.gitignore` per research.md R10 — reword the comment at lines 76-78 to drop the word "Codex" while keeping both citations and both ignore lines (`.codex/`, `.agents/`) unchanged: "# These directories may be written locally by external CLI tooling this\n# repository does not generate, deploy, or manage — see\n# specs/021-codex-official-import/ and docs/adr/0004-*."
- [ ] T030 [P] Verify: run `grep -ni codex .gitignore` and confirm exactly two hits, both bare `.codex/`/`.agents/` lines with no "Codex" word in surrounding prose (SC-001's documented exception).
- [ ] T031 Run the full quickstart.md validation sequence (all 8 steps) and confirm every expected outcome holds, in `specs/031-remove-codex-support/quickstart.md`.
- [ ] T032 [P] Run `grep -rli codex --exclude-dir=.git --exclude-dir=specs .` and confirm the result set matches exactly: `docs/adr/0002-*.md`, `docs/adr/0004-*.md`, `docs/adr/0010-*.md`, `.specify/integrations/codex.manifest.json`, `.specify/extensions/.registry`, `.gitignore` (SC-001).
- [ ] T033 [P] Run `git status --porcelain specs/` and `git status --porcelain .specify/integrations/ .specify/extensions/.registry` and confirm both return no output (SC-005).
- [ ] T034 [P] Run the full remaining behavior-suite set: `for t in tests/run-*.sh; do bash "$t" >/tmp/t.log 2>&1; echo "$t: exit $?"; done` and confirm every suite's exit code matches research.md R12's predicted post-change state (SC-003).

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup / Foundational**: N/A — work starts immediately at Phase 3.
- **User Story 1 (Phase 3)**: No dependencies. T002 (the deletion) should land before US2/US3's verification steps that assert `AGENTS.md` is gone, but US2/US3's own *edits* (T005, T008, T017, T020) do not read `AGENTS.md`'s content — they only remove references to it — so they have no hard ordering dependency on T002 completing first.
- **User Story 2 (Phase 4)**: Independent of US1's file deletion (only removes references). T005/T008/T010 can run in parallel with each other and with US1/US3, since each touches a different file.
- **User Story 3 (Phase 5)**: Independent of US1/US2 at the file level. T013/T014 (deletions) and T017/T020/T022 (edits) touch five different files and can all run in parallel; T017 and T020 both reference `AGENTS.md` in their *baseline* confirmation (T016/T019) but that only requires reading the file's presence, not its content, so no ordering dependency on US1's T002 is required — though running T002 first makes the "file no longer exists" framing in each edited comment literally true at verification time.
- **User Story 4 (Phase 6)**: Fully independent of US1-US3 (only touches `docs/adr/`).
- **Polish (Phase 7)**: Depends on all of US1-US4 being complete (T031/T032/T034 verify the combined end state).

### User Story Dependencies

- **US1 (P1)**: No dependency on other stories.
- **US2 (P1)**: No dependency on other stories (removes references to a file whose deletion is tracked separately in US1).
- **US3 (P1)**: No dependency on other stories.
- **US4 (P2)**: No dependency on other stories.

### Parallel Opportunities

- **Across stories**: US1, US2, US3, and US4 touch entirely disjoint file sets (`AGENTS.md`; `README.md`/`README.ja.md`/`install.sh`; `tests/*`; `docs/adr/*`) and can be dispatched to four parallel subagents simultaneously — this is the primary parallelization opportunity in this feature.
- **Within US2**: T005 (README.md), T008 (README.ja.md), and T010 (install.sh) are three different files — parallelizable.
- **Within US3**: T013, T014 (deletions) and T017, T020, T022 (edits) span five different files — parallelizable; each edit's own baseline-confirm task (T016/T019) should precede it within the same file's line, but different files' pairs are independent of each other.
- **Within Phase 7**: T029 (`.gitignore`) is independent of T031-T034 (verification), which themselves can run in parallel with each other since they're read-only checks against the same completed state.

---

## Parallel Example: Phase 4 + 5 + 6 dispatched together

```bash
# Four subagents, one per user story, each given its own research.md sections and file list:
Task: "US2 — edit README.md, README.ja.md, install.sh per research.md R2-R4"
Task: "US3 — delete/edit the five test files per research.md R5-R8"
Task: "US4 — write the new ADR and re-status ADR-0004 per research.md R9"
# US1 (T001-T003) is small enough to do directly rather than dispatch.
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. T001-T003: delete `AGENTS.md`.
2. **STOP and VALIDATE**: `test -f AGENTS.md` fails. Note that `grep -rn AGENTS.md` will still show four dangling references until US2/US3 land — this alone is not yet a clean state, but it is the single irreducible action the whole feature exists to perform.

### Incremental Delivery

1. US1 (T001-T003) → `AGENTS.md` deleted → dangling refs remain (expected, tracked below).
2. US2 (T004-T011) → README/install.sh fully Codex-free, no dangling `AGENTS.md`/test-suite references → deploy/demo.
3. US3 (T012-T023) → test suite fully Codex-free, no dangling `AGENTS.md` references, two dead suites gone.
4. US4 (T024-T028) → decision recorded via ADR-0010.
5. Polish (T029-T034) → `.gitignore` reworded, full quickstart run, full regression baseline compared, untouched trees confirmed.

### Suggested Parallel Dispatch

Given the file-level independence documented above, the most effective split for subagent dispatch is: one agent for US1 (trivial, do inline), one agent each for US2, US3, and US4 (each self-contained given its research.md sections), then a single pass for Phase 7 polish once all four report back.

## Notes

- Task granularity favors traceability to spec.md's acceptance scenarios and research.md's per-file decisions over splitting for its own sake — most tasks are single-file edits with an explicit before/after grep as their own verification.
- Commit after all of Phase 3-6 are complete (not per-task), consistent with `rules/git-workflow.md`'s "one logical change per commit" — removing Codex support is one logical change spanning many files, matching spec 029's precedent. Phase 7's `.gitignore` edit is small enough to fold into the same commit.
- research.md R12's baseline table is the authoritative "what should still fail and why" reference for every verification task in this file — consult it rather than re-deriving pass/fail expectations from scratch.
