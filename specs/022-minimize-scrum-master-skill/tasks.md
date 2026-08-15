---
description: "Task list for minimizing the scrum-master skill to official Scrum Guide content"
---

# Tasks: Minimize scrum-master Skill to Official Scrum Guide Content

**Input**: Design documents from `/specs/022-minimize-scrum-master-skill/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md (no `contracts/` — plan.md explains why)

**Tests**: Not requested in the spec. This feature has no automated test suite of its own; verification is via the grep/find commands in `quickstart.md` and the repository's existing suites, both wired into the Polish phase below.

**Organization**: Tasks are grouped by user story (US1/US2/US3, matching spec.md's P1/P2/P3), plus a Polish phase for the cross-cutting cleanup outside the skill directory that research.md's Decision 3 requires.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- All file paths are relative to the repository root

## Phase 1: Setup

No setup tasks — this feature edits existing files in place; there is no project, dependency, or environment to initialize.

## Phase 2: Foundational

No blocking foundational phase. Ordering between stories is a direct content dependency, not shared infrastructure, and is captured per-task below and in **Dependencies & Execution Order**: US2's T011 depends on US1's T007, and all of US3 depends on US1 and US2 being complete (spec.md states this explicitly for both).

---

## Phase 3: User Story 1 - Strip references to a single normative source (Priority: P1) 🎯 MVP

**Goal**: Every citation anywhere in the skill traces to `[SG20]` only; the four reference files and the one script sourced entirely from supplementary material are gone.

**Independent Test**: Search every file under `.claude/skills/scrum-master/` for a citation tag other than `[SG20]`; confirm zero matches. Confirm `references/sources.md` lists only the Scrum Guide entry, and that the four deleted reference files plus the script no longer exist.

### Implementation for User Story 1

- [X] T001 [P] [US1] Delete `.claude/skills/scrum-master/references/scaling-frameworks.md` (FR-002)
- [X] T002 [P] [US1] Delete `.claude/skills/scrum-master/references/measurement-and-diagnostics.md` (FR-003)
- [X] T003 [P] [US1] Delete `.claude/skills/scrum-master/references/anti-patterns-and-coaching.md` (FR-004)
- [X] T004 [P] [US1] Delete `.claude/skills/scrum-master/references/facilitation-and-coaching.md` (FR-005)
- [X] T005 [P] [US1] Delete `.claude/skills/scrum-master/scripts/flow_metrics.py` and `.claude/skills/scrum-master/scripts/__pycache__/` (FR-006)
- [X] T006 [P] [US1] Trim `.claude/skills/scrum-master/references/sources.md` to a single `[SG20]` bibliographic entry (both PDF paths, the Japanese-edition page-numbering note already present) plus one citation rule; remove the four-tier evidence-strength framing and the other 13 source entries (`[NXG]`, `[AM01]`, `[EBM24]`, `[KGS21]`, `[DORA26]`, `[EDM99]`, `[ART]`, `[ICA]`, `[SAP]`, `[ZBS]`, `[AAP]`, `[LESS]`, `[SAFE]`, `[SC@S]`) (FR-001; research.md Decision 2)
- [X] T007 [P] [US1] Remove the "コーチングスタンス" section (and its `[ICA]` citation) from `.claude/skills/scrum-master/references/scrum-master-role.md`; keep 中核的アカウンタビリティ, Scrum Teamへの奉仕, Product Ownerへの奉仕, 組織への奉仕, この役割ではないもの, 誰がScrum Masterになれるか intact (FR-007)
- [X] T008 [US1] Verify: `grep -rEn '\[(NXG|AM01|EBM24|KGS21|DORA26|EDM99|ART|ICA|SAP|ZBS|AAP|LESS|SAFE|SC@S)\b' .claude/skills/scrum-master/` returns no matches from the files touched by T001–T007, and that T001–T005's targets no longer exist (depends on T001–T007)

**Checkpoint**: At this point, the skill's reference material cites only the Scrum Guide. `SKILL.md` and `scrum-framework.md` still contain some links/quotes that will only be resolved by US2/US3 — that is expected at this checkpoint.

---

## Phase 4: User Story 2 - Limit event guidance to the Guide's stated purpose and timebox (Priority: P2)

**Goal**: `references/event-playbooks.md` (the file carrying every non-Guide facilitation technique, retro format, and improvement-experiment template) is gone; the small number of directly Scrum-Guide-quoted statements it held that aren't duplicated elsewhere survive in `scrum-framework.md` / `scrum-master-role.md`.

**Independent Test**: Ask the skill "How do I run a Sprint Retrospective?" — confirm the answer states only the Guide's purpose and 3-hour timebox, with no staged facilitation structure or named retro format. Confirm `event-playbooks.md` no longer exists.

**Depends on**: User Story 1 (T007) — T011 below confirms content that US1's trim of `scrum-master-role.md` must not have removed.

### Implementation for User Story 2

- [X] T009 [US2] In `.claude/skills/scrum-master/references/scrum-framework.md`, append the Sprint Review Guide quotes "スプリントレビューはワーキングセッションであり…プレゼンテーションだけに限定しないようにする" [SG20, p.9] and "…価値をリリースするための関門と見なすべきではない" [SG20, p.12] to the Sprint Review event description (research.md Decision 1)
- [X] T010 [US2] In `.claude/skills/scrum-master/references/scrum-framework.md`, add a short Product Backlog Refinement subsection quoting its Guide definition "プロダクトバックログアイテムがより小さく詳細になるように、分割および定義をする活動である" [SG20, p.10] and noting it is not a formal timeboxed Scrum event (research.md Decision 1) — depends on T009 (same file)
- [X] T011 [US2] Confirm the impediment-removal duty quote "スクラムチームの進捗を妨げる障害物を排除するように働きかける" [SG20, p.6] is still present in `.claude/skills/scrum-master/references/scrum-master-role.md`'s "Scrum Teamへの奉仕" list after US1's T007 trim; add it back only if T007 removed it (research.md Decision 1) — depends on T007
- [X] T012 [US2] Delete `.claude/skills/scrum-master/references/event-playbooks.md` (FR-008; research.md Decision 1) — depends on T009, T010, T011

**Checkpoint**: Every Scrum event's guidance remaining in the skill is limited to purpose, participants, and timebox as the Guide states it. `SKILL.md` still links to `event-playbooks.md` at this checkpoint — resolved in US3.

---

## Phase 5: User Story 3 - Keep the skill's own routing free of dead links and scope overreach (Priority: P3)

**Goal**: `SKILL.md` only ever points at files/practices that survived US1 and US2, and explicitly declines out-of-scope questions instead of answering from memory of deleted material.

**Independent Test**: Read `SKILL.md` after the change; confirm every relative markdown link resolves to an existing file, and no section instructs the skill to compute flow metrics, recommend a scaling framework, or select a coaching stance.

**Depends on**: User Story 1 and User Story 2 (both fully complete) — spec.md states this phase "only makes sense once US1 and US2 are complete."

### Implementation for User Story 3

- [X] T013 [US3] In `.claude/skills/scrum-master/SKILL.md`, rewrite the「参照ファイル」table to drop rows for `scaling-frameworks.md`, `measurement-and-diagnostics.md`, `anti-patterns-and-coaching.md`, `facilitation-and-coaching.md`, and `event-playbooks.md`, keeping only rows for files that still exist (FR-009, FR-010)
- [X] T014 [US3] In `.claude/skills/scrum-master/SKILL.md`, rewrite the description and「必ず守る原則」so the skill is described as scoped to the official Scrum Guide (2020) only, without implying coverage of scaling, flow-metrics computation, anti-pattern taxonomies, or facilitation-technique coaching (FR-010). Implemented with one deviation: `when_to_use` was trimmed of its two phrases naming now-out-of-scope topics ("velocity, burndown/burnup" and "or scaling framework (Nexus/LeSS/SAFe)"), reconciling FR-010's requirement to rescope `when_to_use` trigger text with spec.md's Assumption that routing is unaffected — every phrase the routing regression test depends on is untouched — same file as T013, sequential
- [X] T015 [US3] In `.claude/skills/scrum-master/SKILL.md`, remove the「支援モードを選ぶ」section (coaching-stance routing, now that `scrum-master-role.md`'s stance section is gone) and the「アンチパターンを検知する」section (which pointed at the deleted `anti-patterns-and-coaching.md`); add explicit out-of-scope guidance per FR-011 for when a user asks about a removed topic (scaling framework choice, flow-metric computation, coaching-stance selection, retro-format selection) — same file as T013/T014, sequential
- [X] T016 [US3] In `.claude/skills/scrum-master/SKILL.md`, remove the「スクリプト：フロー指標の計算」subsection and any other `flow_metrics.py` invocation instructions (FR-006, FR-009) — same file as T013–T015, sequential
- [X] T017 [US3] In `.claude/skills/scrum-master/SKILL.md`, review the「標準ワークフロー」and「出力品質の確認」sections for remaining references to deleted files or practices and update them to point only at surviving files (`scrum-framework.md`, `scrum-master-role.md`, `sources.md`) (FR-009) — same file as T013–T016, sequential
- [X] T018 [US3] Verify: run the SC-005 dead-link check from `quickstart.md` against `.claude/skills/scrum-master/` and confirm zero "DEAD LINK" lines (depends on T013–T017)

**Checkpoint**: All user stories are now complete — the skill directory itself satisfies spec.md's FR-001–FR-012 and SC-001, SC-002, SC-003, SC-005. Only the outside-the-skill cleanup (Polish phase) remains.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Repository-root files that reference artifacts deleted in US1 (research.md Decision 3) — required by this repository's Live Documentation and least-privilege rules, not new scope.

- [ ] T019 [P] Update `README.md`: remove "flow metrics" from the scrum-master skill's one-line capability summary (~L39); update the file-tree diagram to drop the `scripts/flow_metrics.py` row (~L283–286); correct "8 on-demand reference documents" to the actual post-deletion count; remove the "After changing... `flow_metrics.py`... run `tests/run-flow-metrics.sh`" instruction block (~L321–327) (research.md Decision 3) — depends on T001–T012 for an accurate final file count
- [ ] T020 [P] Remove the two `Bash(python3 .../flow_metrics.py *)` entries from `.claude/settings.json`'s `permissions.allow`; confirm the file remains valid JSON (research.md Decision 3) — depends on T005
- [ ] T021 [P] Delete `tests/run-flow-metrics.sh` (research.md Decision 3) — depends on T005
- [ ] T022 [P] Delete `tests/test_flow_metrics.py` and `tests/__pycache__/test_flow_metrics.cpython-314.pyc` (research.md Decision 3) — depends on T005
- [ ] T023 Run the full `quickstart.md` validation (SC-001 through SC-005 grep/find commands) and confirm every check passes (depends on T001–T022)
- [ ] T024 Run the repo-wide consistency checks from `quickstart.md`: `./scripts/check-mcp-consistency.sh`, `bash tests/run-codex-sync.sh`, `bash tests/run-codex-references.sh`, `bash tests/run-codex-drift.sh`, and confirm `tests/skill-routing/007-scrum-facilitation.md` still passes unchanged via this repo's skill-routing regression harness (depends on T001–T022)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup / Foundational**: None — skipped (see Phase 1/2 notes above).
- **User Story 1 (Phase 3)**: No dependencies. Can start immediately.
- **User Story 2 (Phase 4)**: T011 depends on US1's T007; T009/T010/T012 have no US1 dependency but T012 depends on T009–T011 within US2.
- **User Story 3 (Phase 5)**: Depends on User Story 1 AND User Story 2 being fully complete (explicit in spec.md).
- **Polish (Phase 6)**: T019 depends on US1+US2 (needs final file count); T020–T022 depend only on T005 (US1); T023–T024 depend on everything.

### Within Each User Story

- US1: T001–T007 are independent file operations, all parallelizable; T008 verifies afterward.
- US2: T009 → T010 (same file, sequential); T011 depends on US1's T007; T012 depends on T009–T011.
- US3: T013–T017 all edit `SKILL.md` — same-file, sequential, in the listed order; T018 verifies afterward.

### Parallel Opportunities

- All of T001–T007 (US1) can run in parallel — five deletions and two independent-file trims.
- T019–T022 (Polish) can run in parallel with each other once their individual dependencies (T005, or T001–T012 for T019) are met.
- US2 and US3 cannot run in parallel with each other (US3 depends on US2's completion), and neither can start its story-defining work before US1's T007 (US2) or before both US1+US2 (US3) — this feature does not offer a multi-developer parallel-story opportunity beyond the intra-US1 parallelism above.

---

## Parallel Example: User Story 1

```bash
# Launch all five independent US1 file operations together:
Task: "Delete .claude/skills/scrum-master/references/scaling-frameworks.md"
Task: "Delete .claude/skills/scrum-master/references/measurement-and-diagnostics.md"
Task: "Delete .claude/skills/scrum-master/references/anti-patterns-and-coaching.md"
Task: "Delete .claude/skills/scrum-master/references/facilitation-and-coaching.md"
Task: "Delete .claude/skills/scrum-master/scripts/flow_metrics.py and its __pycache__"
Task: "Trim .claude/skills/scrum-master/references/sources.md to a single [SG20] entry"
Task: "Remove the コーチングスタンス section from .claude/skills/scrum-master/references/scrum-master-role.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 3: User Story 1 (T001–T008).
2. **STOP and VALIDATE**: run T008's grep check. At this point every citation the skill carries traces to `[SG20]`, which is the core of the user's request, even though `SKILL.md` still references some now-deleted files until US3 lands.
3. Commit as a reviewable increment if desired.

### Incremental Delivery

1. User Story 1 → verify → commit (MVP: single-source citations).
2. User Story 2 → verify → commit (event guidance limited to purpose+timebox).
3. User Story 3 → verify → commit (SKILL.md internally consistent, zero dead links).
4. Polish (Phase 6) → verify → commit (README/settings.json/tests kept truthful).

Given the strict sequential content dependencies (US2 needs US1's T007, US3 needs both US1 and US2), this feature is best delivered as a single sequential pass rather than a parallel-team effort — see **Parallel Opportunities** above.

## Notes

- [P] tasks = different files, no dependencies.
- [Story] label maps task to specific user story for traceability.
- No test tasks were generated — not requested in spec.md; verification is via `quickstart.md`'s grep/find commands (T008, T018, T023) and this repo's existing suites (T024).
- Commit after each checkpoint (end of US1, US2, US3, Polish) rather than after every individual task, since most tasks within a story are small file-content edits.
