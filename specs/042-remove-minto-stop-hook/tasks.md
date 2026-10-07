---

description: "Task list for removing the Minto Pyramid Stop hook"
---

# Tasks: Remove the Minto Pyramid Stop Hook

**Input**: Design documents from `/specs/042-remove-minto-stop-hook/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/minto-package.md, quickstart.md

**Tests**: Included. The plan requires red → green (research R7, plan D8; Beck, *Test-Driven Development: By Example*, <https://www.oreilly.com/library/view/test-driven-development/0321146530/>) and this repository's `CLAUDE.md` requires a failing automated check before an automatable contract changes.

**Organization**: Tasks are grouped by user story so each story can be implemented and checked on its own.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependency on an incomplete task)
- **[Story]**: The user story the task belongs to (US1, US2, US3)
- Paths are relative to the repository root. `PKG` below means `.claude/skills/minto-pyramid`.

## Sources cited by tasks

Same IDs as [research.md](research.md#sources):

- [S1] Claude Code Hooks reference: <https://code.claude.com/docs/en/hooks>
- [S2] Claude Code Plugin manifest reference: <https://code.claude.com/docs/en/plugins-reference>
- [S3] Claude Code memory docs: <https://code.claude.com/docs/en/memory>
- [S4] Semantic Versioning 2.0.0: <https://semver.org/spec/v2.0.0.html>
- [S7] ISO/IEC/IEEE 26514:2022: <https://www.iso.org/standard/77451.html>

S4 §9–§11 was fetched on 2026-10-07 and confirms T010's rationale (analysis A5). S7's wording was not fetched (**unverified**, research.md).

---

## Phase 1: Setup (Baseline)

**Purpose**: Record the pre-change state, so a later failure can be traced to this change rather than to an existing fault (quickstart V3).

- [X] T001 Record the baseline for the package in `.claude/skills/minto-pyramid/`: run `(cd .claude/skills/minto-pyramid && python3 -B -m unittest discover -s tests -v && claude plugin validate --strict .)`. Expect 5/5 tests to pass and `Validation passed` (research R7, observed 2026-10-07). If this run differs from that, stop and report it.
- [X] T002 [P] Record the repository baseline for `tests/run-*.sh`: run `for t in tests/run-*.sh; do bash "$t" >/dev/null 2>&1 && echo "PASS $t" || echo "FAIL $t"; done`, and note any suite that already fails before the change (FR-009).

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: None. The feature adds no shared infrastructure, and each story touches only files that already exist (plan, Structure Decision). User-story work can start as soon as Phase 1 is done.

---

## Phase 3: User Story 1 - Turns end without a Minto compliance round-trip (Priority: P1) 🎯 MVP

**Goal**: The Minto package declares 0 hooks, so a session that loads it runs no Minto `Stop` evaluation (FR-001, SC-001).

**Independent Test**: quickstart V1 (red), then V2 (green). Both must pass with no other story done. The installed-copy and live-session checks (V5, V6) are in the final phase, because they change `~/.claude/` and need the user's approval.

### Tests for User Story 1 ⚠️

> Write this test FIRST and confirm it FAILS before deleting the hook.

- [X] T003 [US1] In `.claude/skills/minto-pyramid/tests/test_package.py`, replace `test_stop_hook` (currently lines 25–29) with `test_declares_no_hooks`. The new test asserts two things: `(ROOT / 'hooks' / 'hooks.json')` does not exist, using the module's existing root-path constant; and the JSON loaded from `.claude-plugin/plugin.json` has no `'hooks'` key. Leave `test_manifest`, `test_skill`, `test_resources_exist`, and `test_eval_cases` unchanged (FR-004, contract C1.4). Why both assertions: a manifest `hooks` key merges with the default `hooks/hooks.json` [S2], so both locations must be empty.
- [X] T004 [US1] Red step (quickstart V1): run `(cd .claude/skills/minto-pyramid && python3 -B -m unittest discover -s tests -v)`. Expect exactly one failure, `test_declares_no_hooks`, and 4 passes. Any other result means T003 is wrong; fix it before going on.

### Implementation for User Story 1

- [X] T005 [US1] Delete `.claude/skills/minto-pyramid/hooks/hooks.json` and the then-empty `.claude/skills/minto-pyramid/hooks/` directory with `git rm -r .claude/skills/minto-pyramid/hooks` (plan D1, research R1). Do not replace it with an empty `{"hooks": {}}` file (R1, alternative rejected). Do not add a `hooks` key to `.claude/skills/minto-pyramid/.claude-plugin/plugin.json` (FR-001).
- [X] T006 [US1] Green step (quickstart V2, first two commands, plus the test/validator line): run `test ! -e .claude/skills/minto-pyramid/hooks && echo "no hooks dir"`, `jq -e 'has("hooks") | not' .claude/skills/minto-pyramid/.claude-plugin/plugin.json`, and `(cd .claude/skills/minto-pyramid && python3 -B -m unittest discover -s tests -v && claude plugin validate --strict .)`. Expect `no hooks dir`, `true`, 5/5 tests passing, and `Validation passed`. A missing `hooks/` directory is valid, because that path is only a default [S2] (data-model, Validation rules).

**Checkpoint**: The repository package declares 0 hooks and its own tests and validator pass. User Story 1 is complete in the repository. Activating it on the machine is T017–T018.

---

## Phase 4: User Story 2 - Package tests and docs match the package (Priority: P2)

**Goal**: The package README describes the package as it is now: a skill with a self-applied completion check and no hooks (FR-005, contracts C3.4–C3.5).

**Independent Test**: quickstart V4, first command, restricted to the package README: `grep -n -i "hook\|stop" .claude/skills/minto-pyramid/README.md`. No line may describe a `Stop` hook as current behavior; lines about its removal are fine. The package unit tests are US1's T006.

### Implementation for User Story 2

- [X] T007 [P] [US2] Edit `.claude/skills/minto-pyramid/README.md`, which is a different file from US1's, so this can run in parallel with T003–T006:
  - line 19: drop "plugin hooks are under `hooks/hooks.json`";
  - "Layout" (line 25): remove the `hooks/hooks.json` entry;
  - "Design" (line 35): remove the `hooks/hooks.json` bullet;
  - "Enforcement model" (line 40): replace the `Stop`-hook paragraph with the new model. The skill applies to every substantive task, its step 10 applies `rules/completion-check.md` before completion, and the package declares no hooks. This is advisory self-checking, because Claude treats instructions as context, not enforced configuration [S3] (C3.4). Keep the paragraph on user-requested format precedence (line 42) unchanged;
  - "Notes on portability" (line 46): drop the compliance-hook and model-call-cost sentences, and say that the plugin uses no hooks or executable scripts.
- [X] T008 [US2] In `.claude/skills/minto-pyramid/README.md`, add a short "Local modification" section. It says that this copy removes the upstream `Stop` prompt hook, and gives the rationale with evidence labels as research R4 records them (C3.5, FR-008):
  - (a) a prompt hook sends the hook input to a model at every turn's end [S1, <https://code.claude.com/docs/en/hooks>];
  - (b) a blocking `Stop` hook keeps the turn running [S1], and commit `753eb52` was needed to stop a re-output loop (observed);
  - (c) mark that these are the user's reasons as *inferred*, and mark the effect on output quality as *unverified*.
  
  Also say that a verbatim re-copy from upstream would restore the hook.
- [X] T020 [P] [US2] In `.claude/skills/minto-pyramid/references/anthropic-guidance.md`, rewrite line 24 only ("This plugin uses a `Stop` hook only for observable-output compliance. …"). The new sentence says that this plugin declares no hooks and relies on the skill's self-applied completion check (`rules/completion-check.md`), and keeps the point that it does not request hidden chain-of-thought. Leave lines 9 and 21–23 unchanged: they state Claude Code facts that S2 still confirms (`hooks/hooks.json` default; manifest `hooks` merges) [S2]. Different file from T007/T008, so it can run in parallel with them (spec FR-003 exception, plan D11, contract C2.2, analysis A1).
- [X] T009 [US2] Verify US2 (depends on T007, T008, T020):
  - run `grep -n -i "hook\|stop" .claude/skills/minto-pyramid/README.md .claude/skills/minto-pyramid/references/anthropic-guidance.md`, and confirm that every match describes the removal or the absence of hooks, or a general Claude Code fact, not this package's current hook behavior (SC-004);
  - read the "Local modification" section from T008 and confirm that each rationale statement carries a citation, an *observed* label, or an *inferred*/*unverified* label (SC-005, FR-008; analysis A6).

**Checkpoint**: The package README and package tests (T006) both describe a package with no hooks.

---

## Phase 5: User Story 3 - Repository docs record the local divergence (Priority: P3)

**Goal**: The repository documents stop calling `minto-pyramid` a verbatim upstream copy with a `Stop`-hook check, and the manifest version marks the local build (FR-006, contracts C2.1, C3.1–C3.3).

**Independent Test**: quickstart V4. Also read the `minto-pyramid` passages of `README.md` and `README.ja.md` side by side and confirm that they state facts C3.1–C3.3 identically.

### Implementation for User Story 3

- [X] T010 [P] [US3] In `.claude/skills/minto-pyramid/.claude-plugin/plugin.json`, change `"version": "0.3.0"` to `"version": "0.3.0+local.no-stop-hook"` and leave every other key unchanged (plan D6, contract C2.1). The field is not checked against semver [S2]. SemVer build metadata marks a local build without claiming a new release, and is ignored for precedence [S4 §10]. Then re-run `jq -r .version .claude/skills/minto-pyramid/.claude-plugin/plugin.json` and expect `0.3.0+local.no-stop-hook`.
- [X] T011 [P] [US3] Edit `README.md`:
  - In the managed-paths paragraph (lines 56–60, observed 2026-10-07; analysis A4), keep `maintaining-living-documentation` as before, including its `SessionStart` rule and `Stop`-hook gate (C3.3).
  - Describe `minto-pyramid` as Minto structure applied to every substantive task as advisory guidance, with no `Stop`-hook check (C3.1).
  - Replace "copied verbatim from their upstream packages" with wording that keeps the verbatim claim for `maintaining-living-documentation` only. For `minto-pyramid`, say that its local copy removes the upstream `Stop` hook, so a verbatim re-copy would restore it (C3.2).
  - In the tree (line 153), change the comment `(+ Stop-hook check)` to mark the copy as locally modified, with no Stop hook.
- [X] T012 [P] [US3] Edit `README.ja.md` lines 45–48 to state the same facts as T011 in Japanese:
  - drop "`Stop` フックの検査付き" for `minto-pyramid`;
  - keep the `maintaining-living-documentation` description, including "`Stop` フックのゲート付き";
  - limit "上流のパッケージのまま取り込んでいる" to `maintaining-living-documentation`, and note that the local copy of `minto-pyramid` has its `Stop` hook removed and that a verbatim re-copy would restore it.
  
  `README.ja.md` mentions `minto-pyramid` only at line 47 and has no tree line for it (observed 2026-10-07), so no tree edit is needed. Keep the facts in sync with T011 (repository `CLAUDE.md` README-sync rule).
- [X] T013 [P] [US3] In `docs/claude-config-design.md` line 87, change "上流のまま取り込んだ2つのプラグイン（`maintaining-living-documentation`、`minto-pyramid`）". Keep both plugins excluded from the target-skill list, and record that `minto-pyramid` is vendored with a local modification (its Stop hook removed) rather than verbatim (plan D7, research R6). Do not change any other sentence on that line.
- [X] T014 [P] [US3] In `tests/run-config-pyramid.sh`, edit only the comment at lines 132–134 (observed 2026-10-07; analysis A4) ("Vendored upstream plugins … are kept verbatim …"): say that `minto-pyramid` is vendored with its Stop hook removed. Change no command or assertion (research R6 scope note, FR-009).
- [X] T015 [US3] Verify US3 (depends on T011, T012, T013, T014):
  - run `grep -n -i "stop" README.md README.ja.md | grep -i minto` and `grep -n "上流のまま" docs/claude-config-design.md`;
  - confirm that no line presents a Minto `Stop` hook as current behavior, and that `minto-pyramid` is not called an unmodified upstream copy;
  - compare the README.md and README.ja.md passages for identical C3.1–C3.3 facts.

**Checkpoint**: All three user stories are complete in the repository.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Regression, documentation checks, and activation on the user's machine.

- [X] T016 Run quickstart V2 in full, then V3, from the repository root:
  - re-run all four V2 commands, including `jq -r .version …` and `claude plugin validate --strict .`, so the version set by T010 is validated on the final package state (C2.1, C2.3; analysis A2). Expect `0.3.0+local.no-stop-hook`, 5/5 tests, and `Validation passed`;
  - `git diff --stat main -- .claude/skills/minto-pyramid/{SKILL.md,rules,templates,references,evals} ':!.claude/skills/minto-pyramid/references/anthropic-guidance.md' .claude/skills/maintaining-living-documentation .claude/settings.json .claude/rules install.sh archive` must print nothing, and `git diff --numstat main -- .claude/skills/minto-pyramid/references/anthropic-guidance.md` must show exactly 1 line added and 1 removed (FR-003 with its exception, FR-007, C2.2);
  - re-run every `tests/run-*.sh` suite, and confirm that each suite that passed in T002 still passes (FR-009, SC-003).
- [X] T017 Run the living-documentation checks:
  - `python3 ~/.claude/skills/maintaining-living-documentation/scripts/check_links.py --changed`; fix any broken link and re-run.
  - Write the `Documentation impact` completion report, covering:
    - the documents changed by T007–T014 and T020;
    - that no CHANGELOG exists in this repository (observed: no `CHANGELOG*` at the root), so no entry is added;
    - a proposed (not created) ADR for the hook removal (research R8).
- [ ] T018 Activate on the machine (quickstart V5). This needs the user's explicit approval, because it replaces `~/.claude/` contents machine-wide. Recovery is re-running `install.sh` from the previous commit (data-model, Installed copy).
  - Run `./install.sh`.
  - Then run `test ! -e ~/.claude/skills/minto-pyramid/hooks && echo "installed copy has no hooks"`, and expect that line (FR-002, SC-001).
- [ ] T019 Manual live check (quickstart V6, SC-002), done by the user after T018:
  - start a new Claude Code session, because hooks are snapshotted at session start [S1];
  - in `/hooks`, confirm that no `minto-pyramid` `Stop` hook is listed;
  - complete 5 substantive turns with 0 Minto correction requests, and confirm that the `minto-pyramid` skill is still listed.
  
  A block from the `maintaining-living-documentation` Stop hook is out of scope.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies. T001 and T002 can run in parallel.
- **Foundational (Phase 2)**: Empty.
- **US1 (Phase 3)**: Depends on T001. Strict internal order: T003 → T004 → T005 → T006 (red before green).
- **US2 (Phase 4)**: Depends only on Phase 1. T007 → T008 edit the same file, so they run in sequence; T020 edits a different file and runs in parallel with them; T009 waits for T007, T008, and T020. It can run in parallel with US1.
- **US3 (Phase 5)**: Depends only on Phase 1. T010–T014 touch different files and run in parallel; T015 waits for T011–T014.
- **Polish (Phase 6)**:
  - T016 and T017 depend on all story phases.
  - T018 depends on T016 and on the user's approval.
  - T019 depends on T018.

### User Story Dependencies

- **US1 (P1)**: Independent. It is the MVP.
- **US2 (P2)**: Independent in its files. Its acceptance scenario 1 (tests pass with no Stop-hook requirement) is met by US1's T006.
- **US3 (P3)**: Independent in its files. T010 (version) does not affect US1's tests, because `test_manifest` only asserts that the version is non-empty (observed, `test_package.py` lines 20–23).

### Parallel Opportunities

- T001 ‖ T002
- After Phase 1: the US1 chain (T003–T006) ‖ US2 (T007, T020) ‖ US3 (T010, T011, T012, T013, T014)

---

## Parallel Example

```bash
# After Phase 1, launch in parallel:
Task: "T003 Replace test_stop_hook with test_declares_no_hooks in .claude/skills/minto-pyramid/tests/test_package.py"
Task: "T007 Rewrite hook passages in .claude/skills/minto-pyramid/README.md"
Task: "T020 Rewrite line 24 of .claude/skills/minto-pyramid/references/anthropic-guidance.md"
Task: "T010 Set version 0.3.0+local.no-stop-hook in .claude/skills/minto-pyramid/.claude-plugin/plugin.json"
Task: "T011 Update minto-pyramid description in README.md"
Task: "T012 Update minto-pyramid description in README.ja.md"
Task: "T013 Update line 87 in docs/claude-config-design.md"
Task: "T014 Update comment lines 132–134 in tests/run-config-pyramid.sh"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1 baseline (T001–T002).
2. US1 red → green (T003–T006).
3. **Stop and validate**: V1 and V2 pass. At this point the repository no longer ships the hook. Without US2 and US3, though, the READMEs describe a hook that does not exist, so the MVP alone is not a mergeable state under the repository's living-documentation rule.

### Incremental Delivery

1. US1 → US2 → US3 in one branch, so code and docs stay consistent in one PR.
2. Polish T016–T017 before committing.
3. T018–T019 after merge or on the branch, with the user's approval.

---

## Notes

- Unverified points carried from plan.md:
  - how Claude Code discovers a plugin under `~/.claude/skills/<name>/`, which T005 does not depend on;
  - whether output quality or eval pass rates change without the hook;
  - the exact wording of S7 (S4 was verified on 2026-10-07; analysis A5);
  - that the strict validator accepts the `+local` version string in practice, which T016 checks (analysis A2).
- No AWS service is involved, so the AWS MCP lookup has no target (research R9).
- Commit after each phase or logical group, only when the user asks.

## Analysis Remediation Log

Findings re-derived on 2026-10-07 (the original `/speckit-analyze` output was not persisted; see spec.md, Analysis Remediation Log). Changes made in this file:

| ID | Severity | Finding | Change here |
|----|----------|---------|-------------|
| A1 | HIGH | `references/anthropic-guidance.md` line 24 states the hook as current behavior and had no task | New T020; T009, T016, T017, dependencies, parallel example |
| A2 | MEDIUM | No task validated the manifest after T010 set the version | T016 re-runs V2 in full |
| A4 | LOW | Stale line numbers in T011 (57–61 → 56–60) and T014 (131–133 → 132–134) | T011, T014, parallel example |
| A5 | LOW | S4 marked unverified | Sources note and Notes |
| A6 | LOW | SC-005 (rationale labelled or cited) had no verification task | T009 second check |

New task IDs are appended (T020) rather than renumbered, so existing references to T001–T019 stay valid.

## Phase 7: Convergence

- [X] T021 Add an activation note to the "Local modification" section of `.claude/skills/minto-pyramid/README.md` stating that an existing user-level install keeps running the removed hook from `~/.claude/skills/minto-pyramid/hooks/` until `install.sh` is re-run, and that the change takes effect in a new session because hooks are snapshotted at session start [S1, <https://code.claude.com/docs/en/hooks>]; then re-run `grep -n -i "install.sh" .claude/skills/minto-pyramid/README.md` and confirm the note is present per spec Edge Case "Stale installed copy" (partial)
