# Tasks: Codex CLI Guardrail Implementation (AGENTS.md + Native Hooks)

**Input**: Design documents from `/specs/013-cross-agent-guardrail-implementation/`
**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/guardrail-script-io.md](./contracts/guardrail-script-io.md), [quickstart.md](./quickstart.md)

**Tests**: Included. `.claude/hooks/*.sh` currently has no test suite (spec Assumptions), and this repository's own `coder` skill mandates TDD for source-code changes — the three shared scripts (US3–US5) are source code with a defined contract (`contracts/guardrail-script-io.md`), so their tests are written first, expected to fail, then made to pass.

**Organization**: Tasks are grouped by user story (US1–US6, matching `spec.md`'s priorities P1/P1/P2/P2/P3/P2) so each can be implemented, tested, and delivered independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependency on an incomplete task)
- **[Story]**: Which user story this task belongs to (US1–US6)

## Path Conventions

Single project, repository root. See `plan.md`'s Project Structure for the full tree; paths below are relative to the repository root.

---

## Phase 1: Setup

**Purpose**: Create the new directories and permission entries every later phase writes into.

- [X] T001 Create `scripts/guardrails/` directory at the repository root
- [X] T002 Create `.codex/hooks/` directory at the repository root
- [X] T003 [P] Add `Bash(scripts/guardrails/*.sh)` and `Bash(.codex/hooks/*.sh)` to `.claude/settings.json`'s `permissions.allow`, matching the existing `Bash(scripts/check-mcp-consistency.sh)` entry style

---

## Phase 2: Foundational

**Purpose**: Cross-story blocking prerequisites.

No additional foundational work exists for this feature beyond Phase 1 — each user story below extracts a *different* existing hook or authors independent content, so none of US1–US5 depends on another's implementation. (US6 depends on US1's content, not its infrastructure — see Dependencies below.) Proceed directly to Phase 3.

---

## Phase 3: User Story 1 - Shared baseline guidance via AGENTS.md (Priority: P1) 🎯 MVP

**Goal**: A root-level `AGENTS.md` exists with all 12 prose-appropriate decision-record items, ready for `install.sh` to deploy globally.

**Independent Test**: `cat AGENTS.md`, confirm all 12 items present and correctly worded per `spec.md`'s Acceptance Scenarios 1–3 (see `quickstart.md` User Story 1). No other story's implementation is required.

### Implementation for User Story 1

- [X] T004 [US1] Draft `AGENTS.md` entries for Q1, Q2, Q4, Q5 (the `unify_full` items plus Q4/Q5) in `AGENTS.md`, per `data-model.md`'s AGENTS.md Entry entity and FR-001/002/003
- [X] T005 [US1] Draft `AGENTS.md` entries for Q7, Q9, Q10 in `AGENTS.md`, each stating plainly that Codex CLI enforces the item via hook (FR-002)
- [X] T006 [US1] Draft `AGENTS.md` entries for Q8, Q11, Q12, Q13, Q14 in `AGENTS.md`, phrased as notes/requests with no enforcement guarantee (FR-002) and no Claude Code-specific mechanism names for Q13/Q14 (FR-005)
- [X] T007 [US1] Add `AGENTS.md`'s file header/intro and confirm total size is under 32 KiB (`wc -c AGENTS.md`, FR-011a) — trim wording if over budget (4382 bytes, well under budget)
- [X] T008 [US1] Extend `install.sh` with a new step that copies `AGENTS.md` to `~/.codex/AGENTS.md` (`sync_path`-style, per R4), surfacing existing content first if `~/.codex/AGENTS.md` already has unrelated content (FR-011/025)

**Checkpoint**: User Story 1 is fully functional — `AGENTS.md` exists and, once `install.sh` is run, is globally deployed.

---

## Phase 4: User Story 2 - Native skill discovery for Codex CLI via .agents/skills (Priority: P1)

**Goal**: This repository's 9 custom skills are discoverable to Codex CLI as real `SKILL.md` files, both in this repository's working tree and (once installed) globally.

**Independent Test**: `ls -la .agents/skills/` shows the 9 symlinks resolving correctly; a Codex CLI session triggers a skill using its real content. Independent of User Story 1.

### Implementation for User Story 2

- [X] T009 [P] [US2] Create relative symlinks `.agents/skills/<name>` → `../../.claude/skills/<name>` for all 9 custom skills (`adr`, `advisor`, `clarifier`, `coder`, `domain-model`, `minto-builder`, `minto-reviewer`, `minto-rewriter`, `ubiquitous-language`), commit them to git
- [X] T010 [US2] Verify each of the 9 symlinks resolves (`readlink`) and its `SKILL.md` is byte-identical to `.claude/skills/<name>/SKILL.md` (`diff`), confirming FR-014's zero-drift property
- [X] T011 [US2] Extend `install.sh` with a new step, after its existing `sync_path("skills")` call, that symlinks `~/.agents/skills/<name>` → `~/.claude/skills/<name>` for each of the 9 custom names (FR-026, per R5 — pointing at the installed copy, not the repository working tree)

**Checkpoint**: User Stories 1 AND 2 both work independently.

---

## Phase 5: User Story 3 - Real destructive-command blocking for Codex CLI (Priority: P2)

**Goal**: Codex CLI sessions get the same force-push/`rm -rf`/credential-access/etc. blocking Claude Code sessions already get, via a shared script both tools call.

**Independent Test**: `bash tests/run-destructive-command-guard.sh` passes against both the shared script and the Codex CLI adapter; a live Codex CLI session denies a hard-blocked command. Independent of every other story.

### Tests for User Story 3 ⚠️

> Write these first; confirm they fail (the target script doesn't exist yet).

- [X] T012 [P] [US3] Write `tests/run-destructive-command-guard.sh` and fixtures under `tests/destructive-command-guard/`, covering every category in `contracts/guardrail-script-io.md`'s `destructive-command.sh` section (force push, `git reset --hard`, `git clean -f`, `rm -rf` root/home/cwd, other `rm -rf`, `mkfs`/`dd`/fork-bomb, `curl\|bash`, non-HTTPS, credential read/write, global installs, `sudo`) — run against `scripts/guardrails/destructive-command.sh` (not yet created) and confirm the suite fails for that reason

### Implementation for User Story 3

- [X] T013 [US3] Implement `scripts/guardrails/destructive-command.sh` per `contracts/guardrail-script-io.md`, extracting `.claude/hooks/pre-bash.sh`'s matching logic verbatim (FR-006) — run T012 until it passes against this script directly
- [X] T014 [US3] Refactor `.claude/hooks/pre-bash.sh` into a thin wrapper that calls `scripts/guardrails/destructive-command.sh` and translates its decision to Claude Code's existing `PreToolUse` exit-code/JSON contract (FR-009) — re-run T012's Claude Code-side assertions to confirm zero regression (SC-003)
- [X] T015 [US3] Implement `.codex/hooks/destructive-command-adapter.sh`, wrapping `scripts/guardrails/destructive-command.sh` for Codex CLI's `PreToolUse` (matcher `Bash`) contract per R1, including the `ask`→`deny` fallback (FR-007/008) — extend T012 to assert against this adapter (SC-002)
- [ ] T016 [US3] **BLOCKED**: Re-verify `research.md` R1's claim (Codex CLI `PreToolUse` scope and response shape) against a live Codex CLI session (FR-010) — the `codex` binary is not runnable in the implementing environment (native binary missing under the npm wrapper); adjust T015 once verified on a machine with a working Codex CLI install
- [X] T017 [US3] Extend `install.sh` with a new step that deploys `.codex/hooks/destructive-command-adapter.sh` to `~/.codex/hooks/` and registers it in `~/.codex/config.toml`'s `[hooks]` table, idempotently (FR-027)

**Checkpoint**: User Stories 1, 2, and 3 all work independently.

---

## Phase 6: User Story 4 - Real pre-edit blocking for Codex CLI (Priority: P2)

**Goal**: Codex CLI sessions get the same `.git/`-edit and main/master-branch-edit blocking Claude Code sessions already get.

**Independent Test**: `bash tests/run-pre-edit-guard.sh` passes against both the shared script and the Codex CLI adapter; a live Codex CLI session denies an edit under `.git/` and an edit on `main`. Independent of every other story.

### Tests for User Story 4 ⚠️

- [X] T018 [P] [US4] Write `tests/run-pre-edit-guard.sh` and fixtures under `tests/pre-edit-guard/`, covering `contracts/guardrail-script-io.md`'s `pre-edit-block.sh` section (`.git/` path → deny, `main`/`master` branch → deny, everything else → allow, missing `project_dir` → branch check skipped) — run against `scripts/guardrails/pre-edit-block.sh` (not yet created) and confirm the suite fails for that reason

### Implementation for User Story 4

- [X] T019 [US4] Implement `scripts/guardrails/pre-edit-block.sh` per `contracts/guardrail-script-io.md`, extracting `.claude/hooks/pre-edit.sh`'s `.git/`/branch-block logic verbatim (FR-016) — run T018 until it passes directly
- [X] T020 [US4] Refactor `.claude/hooks/pre-edit.sh` into a thin wrapper calling `scripts/guardrails/pre-edit-block.sh` (FR-018) — re-run T018's Claude Code-side assertions to confirm zero regression (SC-009); the CI/settings/production-path *warnings* (Q1) stay in the wrapper unchanged, since they are not part of this script's contract
- [X] T021 [US4] Implement `.codex/hooks/pre-edit-adapter.sh` for Codex CLI's `PreToolUse` (matcher `apply_patch\|Edit\|Write`) contract per R1 (FR-017) — extend T018 to assert against this adapter (SC-007)
- [ ] T022 [US4] **BLOCKED**: Re-verify [learn.chatgpt.com/docs/hooks](https://learn.chatgpt.com/docs/hooks)'s claim that `PreToolUse` covers `apply_patch`/`Edit`/`Write` against a live Codex CLI session (FR-022, first half) — same environment limitation as T016; adjust T021 once verified
- [X] T023 [US4] Extend `install.sh` with a new step that deploys and registers `.codex/hooks/pre-edit-adapter.sh` in `~/.codex/config.toml`'s `[hooks]` table, idempotently (FR-027) — satisfied by T017's generic adapter-registration loop, which picks up any `.codex/hooks/*.sh` present

**Checkpoint**: User Stories 1–4 all work independently.

---

## Phase 7: User Story 5 - Real post-edit auto-format for Codex CLI (Priority: P3)

**Goal**: Codex CLI sessions get the same `shfmt`/`shellcheck`/`yamllint`/JSON-syntax formatting-on-edit Claude Code sessions already get.

**Independent Test**: `bash tests/run-post-edit-format-guard.sh` passes; a live Codex CLI session editing a `.sh` file triggers `shfmt`/`shellcheck`. Independent of every other story.

### Tests for User Story 5 ⚠️

- [X] T024 [P] [US5] Write `tests/run-post-edit-format-guard.sh` and fixtures under `tests/post-edit-format-guard/`, covering `contracts/guardrail-script-io.md`'s `post-edit-format.sh` section (`.sh` → `shfmt -w -i 2` + `shellcheck`; `.yaml`/`.yml` → `yamllint`; `.json` → `jq empty`; `*/CLAUDE.md` → `@import` resolution check; missing tools silently skipped) — run against `scripts/guardrails/post-edit-format.sh` (not yet created) and confirm the suite fails for that reason

### Implementation for User Story 5

- [X] T025 [US5] Implement `scripts/guardrails/post-edit-format.sh` per `contracts/guardrail-script-io.md`, extracting `.claude/hooks/post-edit-format.sh`'s per-extension logic verbatim (FR-019) — run T024 until it passes directly
- [X] T026 [US5] Refactor `.claude/hooks/post-edit-format.sh` into a thin wrapper calling `scripts/guardrails/post-edit-format.sh` (FR-021) — re-run T024's Claude Code-side assertions to confirm zero regression (SC-009)
- [X] T027 [US5] Implement `.codex/hooks/post-edit-adapter.sh` for Codex CLI's `PostToolUse` (matcher `apply_patch\|Edit\|Write`) contract per R1 (FR-020) — extend T024 to assert against this adapter (SC-008)
- [ ] T028 [US5] **BLOCKED**: Re-verify the hooks doc's `PostToolUse` coverage claim against a live Codex CLI session (FR-022, second half) — same environment limitation as T016/T022; adjust T027 once verified
- [X] T029 [US5] Extend `install.sh` with a new step that deploys and registers `.codex/hooks/post-edit-adapter.sh` in `~/.codex/config.toml`'s `[hooks]` table, idempotently (FR-027) — satisfied by T017's generic adapter-registration loop

**Checkpoint**: User Stories 1–5 all work independently.

---

## Phase 8: User Story 6 - Deduplicate the MCP catalog via a `@path` import (Priority: P2)

**Goal**: `.claude/rules/mcp.md` imports `AGENTS.md`'s Q4 entry instead of duplicating it.

**Independent Test**: `.claude/rules/mcp.md` contains a `@path` import, not a standalone catalog; a Claude Code session still sees the full catalog in context. **Depends on User Story 1** (needs `AGENTS.md`'s Q4 entry, T004, to exist first) — not independent of every story, unlike US2–US5.

### Implementation for User Story 6

- [ ] T030 [US6] **BLOCKED**: Verify Claude Code's `@path` import syntax can target the installed global `AGENTS.md` (`~/.codex/AGENTS.md`) from `.claude/rules/mcp.md`'s installed location (`~/.claude/rules/mcp.md`), against a live Claude Code session (FR-024, resolves R7) — imports resolve at session start, and spawning a fresh session to test a newly-added import wasn't possible mid-conversation in the implementing session
- [X] T031 [US6] FR-024's fallback applied (T030 unverified): `.claude/rules/mcp.md` keeps its standalone content, with a comment documenting why the `@path` import wasn't adopted and what to do once T030 is verified

**Checkpoint**: All 6 user stories are independently functional.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Verify the whole feature together and keep documentation in sync (this repository's own Live Documentation rule).

- [X] T032 [P] Run `scripts/check-mcp-consistency.sh` after T031 to confirm `.claude/rules/mcp.md`'s restructuring didn't break MCP name/version consistency checks (passed: "6 servers consistent")
- [X] T033 Update `README.md` to document the new Codex CLI-side artifacts (`AGENTS.md`, `.agents/skills/`, `.codex/hooks/`) and `install.sh`'s extended behavior — required by this repository's own Live Documentation drift check, since `install.sh`'s public behavior changed in the same feature (`README.ja.md` still needs a matching update — not done in this pass, flagged as follow-up)
- [X] T034 [P] Update `.claude/hooks/README.md` to note that `pre-bash.sh`/`pre-edit.sh`/`post-edit-format.sh` are now thin wrappers around `scripts/guardrails/*.sh`, cross-referencing `contracts/guardrail-script-io.md` for the shared contract
- [X] T035 Run the full `quickstart.md` validation checklist end-to-end for everything not requiring a live Codex CLI/Claude Code session: all three new test suites pass (23+10+3=36/36), `AGENTS.md` is 4382 bytes (under the 32 KiB budget), all 9 skill symlinks resolve and are content-identical, `check-mcp-consistency.sh` passes. `install.sh`'s idempotency (SC-011) was verified in isolation (dry-run of its TOML-merge logic against a temp file, twice) but **not** by actually running `install.sh` against the real `~/.claude`/`~/.codex` — that would modify the maintainer's live global config without explicit permission
- [X] T036 [P] Confirmed `bash -n` syntax validity for every new/modified `.sh` file (all pass). `shellcheck`/`shfmt` are not installed in the implementing environment, so full lint/format compliance is **unverified** — run `shellcheck` and `shfmt -d` on a machine that has them before merging

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately.
- **Foundational (Phase 2)**: Empty for this feature — proceed straight to user stories after Setup.
- **User Stories (Phase 3–8)**: All depend on Setup (T001–T003) only, **except User Story 6 (Phase 8)**, which additionally depends on User Story 1's `AGENTS.md` Q4 entry (T004) being written.
- **Polish (Phase 9)**: Depends on all six user stories being complete (T032 specifically needs US6/T031 done).

### User Story Dependencies

- **US1 (P1)**: No dependencies beyond Setup.
- **US2 (P1)**: No dependencies beyond Setup. Independent of US1.
- **US3 (P2)**: No dependencies beyond Setup. Independent of US1/US2.
- **US4 (P2)**: No dependencies beyond Setup. Independent of US1–US3.
- **US5 (P3)**: No dependencies beyond Setup. Independent of US1–US4.
- **US6 (P2)**: Depends on **US1's T004** (the `AGENTS.md` Q4 entry) specifically — not on US1's `install.sh` step (T008) or any other story.

### Shared-file caveat: `install.sh`

Five tasks each add a new step to `install.sh`: T008 (US1), T011 (US2), T017 (US3), T023 (US4), T029 (US5). These are the **last** task in their respective stories, so within one story there's no conflict — but if multiple stories are implemented in parallel (e.g. by different developers or agents), all five edit the same file and will conflict. Either serialize these five specifically (any order — each appends an independent, self-contained step) or resolve the merge conflict manually; the rest of each story (T004–T007, T009–T010, T012–T016, T018–T022, T024–T028) has no such conflict and is safely parallelizable.

### Parallel Opportunities

- T003 (Setup) can run parallel to T001/T002.
- Once Setup completes, US1, US2, US3, US4, and US5 can all start in parallel (US6 waits on US1's T004 only).
- T012, T018, T024 (the three "write failing tests first" tasks, one per story) can run in parallel with each other and with US1/US2's tasks — different files, no shared dependency.
- T009 (US2's 9 symlinks) can run in parallel with any US1/US3/US4/US5 task.
- T032, T034, T036 (Polish) can run in parallel with each other, after their prerequisites.

---

## Parallel Example: Setup + first wave

```bash
# After T001/T002 create the two directories:
Task: "Add scripts/guardrails/*.sh and .codex/hooks/*.sh to .claude/settings.json permissions.allow"   # T003

# Once Setup is done, these can all start together:
Task: "Draft AGENTS.md entries for Q1, Q2, Q4, Q5"                                                      # T004 (US1)
Task: "Create relative symlinks .agents/skills/<name> for all 9 custom skills"                          # T009 (US2)
Task: "Write tests/run-destructive-command-guard.sh + fixtures"                                         # T012 (US3)
Task: "Write tests/run-pre-edit-guard.sh + fixtures"                                                    # T018 (US4)
Task: "Write tests/run-post-edit-format-guard.sh + fixtures"                                            # T024 (US5)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Phase 2: Foundational is empty — skip.
3. Complete Phase 3: User Story 1 (T004–T008).
4. **STOP and VALIDATE**: run `quickstart.md`'s User Story 1 section. `AGENTS.md` exists and deploys via `install.sh`.
5. This alone already satisfies the original request's core ask ("make `.claude`'s skills and rules referenceable by Codex") at the documentation level, before any enforcement work.

### Incremental Delivery

1. Setup → Phase 3 (US1, P1) → validate → this is the MVP.
2. Add Phase 4 (US2, P1) → validate → Codex CLI now gets real skill triggering, not just prose.
3. Add Phase 5 (US3, P2) → validate → real destructive-command protection lands (the highest-security-value item).
4. Add Phase 6 (US4, P2) → validate → real pre-edit protection lands.
5. Add Phase 8 (US6, P2) → validate → `mcp.md` duplication eliminated (needs US1's T004 already done, which it is by this point).
6. Add Phase 7 (US5, P3) → validate → post-edit auto-format lands (lowest-priority, quality-of-life only).
7. Phase 9: Polish, then a final full `quickstart.md` pass.

### Parallel Team Strategy

With multiple developers: one team completes Setup together, then split — one person per user story (US1–US5 in parallel immediately; whoever finishes US1's T004 first unblocks US6). Coordinate the five `install.sh`-editing tasks (see Shared-file caveat above) so they don't land as simultaneous conflicting edits.

---

## Notes

- [P] tasks touch different files and have no dependency on an incomplete task in the same phase.
- [Story] labels trace every task back to `spec.md`'s user stories for independent verification.
- US3/US4/US5 follow an identical five-task shape (test → shared script → refactor existing hook → adapter → live re-verify → install.sh registration) because they extract from three structurally similar existing hooks — this repetition is intentional, not accidental duplication.
- Commit after each task or logical group, per this repository's own git-workflow conventions (one logical change per commit).
- `install.sh`'s five extension points (T008/T011/T017/T023/T029) are each self-contained; skipping a story simply means skipping its step, with no renumbering required elsewhere in the script.
