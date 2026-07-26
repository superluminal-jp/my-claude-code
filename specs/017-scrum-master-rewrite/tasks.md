---

description: "Task list for restructuring scrum-master into a citation-grounded pure Scrum Master playbook"
---

# Tasks: Restructure `scrum-master` into a citation-grounded pure Scrum Master playbook

**Input**: Design documents from `/specs/017-scrum-master-rewrite/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [contracts/citation-contract.md](contracts/citation-contract.md), [quickstart.md](quickstart.md)

**Tests**: Not requested for this feature — it is a content/documentation rewrite, not software with automated test coverage. [quickstart.md](quickstart.md) is the manual verification procedure, run in the Polish phase.

**Organization**: Tasks are grouped by user story (spec.md's US1/US2/US3) so each can be validated independently. Every task that edits a file must first **read that page/section of the relevant primary-source PDF via the Read tool** before writing a quotation — never quote from memory (research.md R1).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1/US2/US3)
- All file paths are relative to the repository root

## Path Conventions

Single skill directory, no `src/`/`tests/` split: `.claude/skills/scrum-master/SKILL.md` and `.claude/skills/scrum-master/references/*.md`.

---

## Phase 1: Setup

**Purpose**: Confirm the primary-source corpus this whole feature depends on is present and readable before any file is edited.

- [X] T001 Verify `/Users/taikiogihara/Downloads/scrum_official_docs/` contains `Scrum-Guide-2020.pdf`, `Scrum-Guide-2020-Japanese.pdf`, `Nexus-Guide-2021.pdf`, `Nexus-Guide-2021-Japanese.pdf`, `Kanban-Guide-2021.pdf`, `Kanban-Guide-2021-Japanese.pdf`, `Evidence-Based-Management-Guide-2024.pdf`, `Evidence-Based-Management-Guide-2024-Japanese.pdf`, `scrum-at-scale-guide-v2_1.pdf`, `scrum-at-scale-guide-v1_02-japanese.pdf`, `アジャイルソフトウェア開発宣言.md`, and the `Scrum_Guide_Expansion_Pack/` directory; open each guide's first 2 pages to confirm it is text-readable (not a scanned image) before relying on it for quotations

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The Scrum Guide's language-pagination offset must be documented once, centrally, before any file cites Scrum Guide page numbers — otherwise every downstream citation task re-derives (and risks re-guessing) the same fact.

**⚠️ CRITICAL**: T002 must complete before any US1 task that cites `[SG20, p.X]` against the Japanese edition.

- [X] T002 In `.claude/skills/scrum-master/references/sources.md`'s `[SG20]` entry, add one line documenting that page numbers follow the English edition and that `Scrum-Guide-2020-Japanese.pdf` is offset by +1 page from "スクラムの定義" onward (research.md R2's verified table), so a reader opening the Japanese PDF isn't misled by an apparently-wrong page number

**Checkpoint**: Foundation ready — per-file citation work (US1) can now proceed.

---

## Phase 3: User Story 1 - Every normative claim is directly traceable to its source (Priority: P1) 🎯 MVP

**Goal**: Every sentence in `SKILL.md` and `references/*.md` stating a Scrum Guide rule or a complementary-source claim carries a verified short direct quotation plus its citation, sourced by reading the actual primary-source PDF/file — not memory.

**Independent Test**: Sample sentences per `quickstart.md` steps 1–2; each carries a citation tag and a quotation that appears verbatim on the cited page of the corresponding PDF.

### Implementation for User Story 1

- [X] T003 [US1] In `.claude/skills/scrum-master/references/scrum-framework.md`, read `Scrum-Guide-2020.pdf` pages 3–13 (English) via the Read tool, and add a short verified direct quotation next to each existing `[SG20, p.X]` citation (Scrum定義, 経験主義の三本柱, Scrum Values, Scrum Teamのアカウンタビリティ, イベント表の各目的とタイムボックス, 作成物とコミットメント表, 2020年版での変更点). This file becomes the canonical, fully-quoted source other files link to for event timeboxes and framework facts (data-model.md's Canonical location table).
- [X] T004 [P] [US1] In `.claude/skills/scrum-master/references/scrum-master-role.md`, read `Scrum-Guide-2020.pdf` p.6 (English) via the Read tool, add a short verified direct quotation to the "中核的なアカウンタビリティ" `[SG20, p.6]` claims. Label the "コーチングスタンス" table and "この役割ではないもの" list explicitly as the skill's own operating stance/community practice (not an `[SG20]` claim) per contract C4, while keeping the PM-boundary statement's citation scoped to only the accountability fact `[SG20]` actually states.
- [X] T005 [US1] In `.claude/skills/scrum-master/references/event-playbooks.md`, add short verified direct quotations to each event's 目的 statement (Sprint Planning, Daily Scrum, Sprint Review, Sprint Retrospective, Product Backlog Refinement, 障害除去), reusing the exact wording already verified in T003 for `scrum-framework.md` rather than re-deriving it independently (depends on T003).
- [X] T006 [US1] In `.claude/skills/scrum-master/SKILL.md`, add short verified direct quotations to the `[SG20]`-tagged claims in "アカウンタビリティの境界" table and "標準ワークフロー" section, reusing wording already verified in T003/T004 (depends on T003, T004). Leave "必ず守る原則"'s skill-stance bullets (e.g., "人ではなくシステム...を診断する") unattributed to `[SG20]` — they are the skill's own methodology per contract C4.
- [X] T007 [P] [US1] In `.claude/skills/scrum-master/references/measurement-and-diagnostics.md`, read `Kanban-Guide-2021.pdf`/`-Japanese.pdf`, `Evidence-Based-Management-Guide-2024.pdf`/`-Japanese.pdf`, checking each pair for the same kind of EN/JA pagination offset found in research.md R2 before citing; add short verified quotations to the `[KGS21]`, `[EBM24]`, `[DORA26]`, `[SG20]`, `[EDM99]` claims, keeping DORA's software-delivery-only scope note and EBM's outcome framing attached at their point of use (contract C2).
- [X] T008 [P] [US1] In `.claude/skills/scrum-master/references/facilitation-and-coaching.md`, add short verified quotations to the `[SG20, pp.6–7]` claim (using T004's verified wording) and the `[EDM99]` psychological-safety definition; add a citation for the `[ICA]` reference to the coaching-stance concept (paraphrase-level, since no local primary copy of Adkins 2010 exists per research.md R3).
- [X] T009 [P] [US1] In `.claude/skills/scrum-master/references/anti-patterns-and-coaching.md`, add source tags with short quotation/precise paraphrase (per research.md R3, no local primary file exists for `[SAP]`/`[AAP]`/`[ZBS]` — use `sources.md`'s existing accurate description as the paraphrase basis, cited to the blog URLs already in `sources.md`) for each anti-pattern claim currently missing a per-item tag.
- [X] T010 [P] [US1] In `.claude/skills/scrum-master/references/scaling-frameworks.md`, read `Nexus-Guide-2021.pdf`/`-Japanese.pdf` to add a short verified quotation to the `[NXG]` claim; keep `[LESS]`/`[SAFE]` at paraphrase level (no local primary text supplied for either). If proportionate (FR-015, research.md R5), read `scrum-at-scale-guide-v2_1.pdf` and add one parallel-brevity paragraph for Scrum@Scale, explicitly naming which guide version is quoted.
- [X] T011 [P] [US1] In `.claude/skills/scrum-master/references/solo-practice.md`, add a short verified quotation to the `[SG20, pp.3–4]` empiricism claim, reusing wording already verified in T003.

**Checkpoint**: Every file now carries verified quotations for its existing citations. US1 is independently complete and testable via `quickstart.md` steps 1–2.

---

## Phase 4: User Story 2 - Extraneous, unsourced, or duplicated text is removed (Priority: P2)

**Goal**: No sentence states a fact without a citation or an explicit stance/technique label, and each of the three identified duplication clusters (data-model.md) exists in exactly one canonical file.

**Independent Test**: Diff against pre-rewrite versions per `quickstart.md` steps 3–4; no unlabeled factual claim remains; each cluster's full detail exists only in its canonical file.

### Implementation for User Story 2

- [X] T012 [US2] Trim `.claude/skills/scrum-master/SKILL.md`'s "アカウンタビリティの境界" table to a one-line pointer to `references/scrum-master-role.md` (depends on T004, T006 — the canonical file must already carry the full, quoted accountability content).
- [X] T013 [US2] Trim `.claude/skills/scrum-master/references/event-playbooks.md`'s "共通設計" section so it no longer restates the numeric timeboxes (8h/4h/3h/15min), replacing them with a link to `references/scrum-framework.md`'s events table; keep the section's own 6-point per-event design checklist, which is not duplicated elsewhere (depends on T003, T005).
- [X] T014 [US2] Consolidate the support-mode/stance taxonomy into `references/scrum-master-role.md`'s "コーチングスタンス" table as the single canonical enumeration (merge in the "システム介入／組織への働きかけ" mode currently only in `SKILL.md`, labeled as skill-stance per contract C4); trim `SKILL.md`'s "支援モードを選ぶ" table to a compact situation→mode decision aid that links out instead of restating expected outcomes; trim `references/facilitation-and-coaching.md`'s "スタンス" section to keep only its distinct content (the facilitator/content-authority distinction) and link to `scrum-master-role.md` for the full taxonomy (depends on T004, T006, T008).
- [X] T015 [US2] Read every declarative sentence across `.claude/skills/scrum-master/SKILL.md` and all `references/*.md` files (per contract C3 / quickstart.md step 3); for any sentence making a factual or normative claim with neither a citation (from Phase 3) nor an explicit stance/contextual-technique label, either remove it, rewrite it as a labeled stance, or attach the citation it is missing (depends on T003–T014 being complete so the citation baseline is stable).

**Checkpoint**: US1 and US2 both hold — every claim is either cited or labeled, and each duplication cluster lives in one place.

---

## Phase 5: User Story 3 - The structure makes the evidence hierarchy and file boundaries legible (Priority: P3)

**Goal**: Each `references/*.md` file's headings make its sections' evidence tier (規範/公式補完/研究・実務知見/文脈依存の技法) identifiable without opening `sources.md`, and every internal link still resolves after all edits.

**Independent Test**: Open each reference file in isolation per `quickstart.md` steps 6–7; tier is identifiable from heading/structure alone; zero broken links.

### Implementation for User Story 3

- [X] T016 [P] [US3] In `.claude/skills/scrum-master/references/measurement-and-diagnostics.md`, adjust the "推奨指標" table/headings so the tier distinction between generically-applicable flow metrics and DORA's narrower (software-delivery-only) scope is visible at the table itself, not only inferable from the surrounding prose.
- [X] T017 [P] [US3] Review the heading structure and tables of contents of `.claude/skills/scrum-master/references/scrum-framework.md`, `scrum-master-role.md`, `event-playbooks.md`, `facilitation-and-coaching.md`, `anti-patterns-and-coaching.md`, `scaling-frameworks.md`, and `solo-practice.md` against contract C6; add a minimal heading/label wherever a section blends evidence tiers without one (most sections already group by tier correctly per research.md R6 — only fix genuine gaps, don't restructure sections that already pass).
- [X] T018 [US3] Verify every internal Markdown link between `SKILL.md` and `references/*.md`, and among the reference files, resolves to an existing file and heading (contract C8 / quickstart.md step 6), after all edits from Phases 3–5 (depends on T003–T017).

**Checkpoint**: All three user stories complete — citations verified, duplication consolidated, structure legible, links intact.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Confirm the rewrite meets every success criterion in `spec.md` and touched nothing out of scope.

- [X] T019 Run `quickstart.md` steps 1–8 in full (citation sampling, duplication check, word-count delta, link integrity, evidence-tier legibility, frontmatter/routing diff) and record results.
- [X] T020 Run `bash tests/run-skill-routing.sh` and `bash tests/run-codex-sync.sh`; confirm both pass exactly as before the rewrite (FR-012, quickstart.md step 9).
- [X] T021 Confirm via `git diff` that `SKILL.md`'s YAML frontmatter (lines 1–5), `.claude/rules/skill-routing.md`, any installer/distribution mechanism, and `scripts/flow_metrics.py` (including its declared permission) show zero changes (contract C7).

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately.
- **Foundational (Phase 2)**: Depends on Setup. Blocks any US1 task citing `[SG20]` against the Japanese edition.
- **User Story 1 (Phase 3)**: Depends on Foundational. T003/T004 (the two canonical files) should complete before T005/T006 (which reuse their verified wording); T007–T011 are independent of T003–T006 and of each other.
- **User Story 2 (Phase 4)**: Depends on the specific US1 tasks named in each task's own dependency note (T004+T006 → T012; T003+T005 → T013; T004+T006+T008 → T014); T015 depends on all of Phase 3–4 being otherwise done.
- **User Story 3 (Phase 5)**: Can start once the files it touches are stable; T018 (link verification) must be last since it depends on every prior edit.
- **Polish (Phase 6)**: Depends on all of Phases 3–5.

### Parallel Opportunities

- Phase 3: T007, T008, T009, T010, T011 can all run in parallel with each other and with the T003→T004→{T005,T006} chain, since they touch different files with no shared dependency.
- Phase 5: T016 and T017 can run in parallel (different files' headings); T018 must run after both.

---

## Parallel Example: User Story 1

```bash
# After T003 and T004 complete, launch the independent file tasks together:
Task: "Add quotations to event-playbooks.md's event purposes (T005, depends on T003)"
Task: "Add quotations to SKILL.md's accountability table and workflow (T006, depends on T003, T004)"
Task: "Add quotations to measurement-and-diagnostics.md (T007, independent)"
Task: "Add quotations to facilitation-and-coaching.md (T008, independent)"
Task: "Add citations to anti-patterns-and-coaching.md (T009, independent)"
Task: "Add citations to scaling-frameworks.md (T010, independent)"
Task: "Add quotation to solo-practice.md (T011, independent)"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 (Setup) and Phase 2 (Foundational).
2. Complete Phase 3 (US1) — every claim is now traceable to a verified quotation. This alone satisfies the request's core ask ("直接引用をつけるように強化") and is independently checkable via `quickstart.md` steps 1–2.
3. **STOP and VALIDATE**: sample citations against the primary PDFs before proceeding to the trimming work in Phase 4, since Phase 4 assumes Phase 3's canonical-file content is correct.

### Incremental Delivery

1. Setup + Foundational → corpus confirmed, pagination note in place.
2. US1 → every claim cited and quoted → independently valuable and reviewable.
3. US2 → duplication removed, no unlabeled claims → "pure" per the request.
4. US3 → structure/legibility polish.
5. Polish → full `quickstart.md` run + regression suites confirm nothing broke.

---

## Notes

- [P] tasks touch different files with no unmet dependency.
- Every quotation-adding task MUST open the actual primary-source file (PDF or `.md`) via the Read tool before writing a quote — this is the feature's core integrity guarantee (research.md R1), not an optional nicety.
- Commit after each phase checkpoint, not after every single task, to keep the history reviewable (per this repo's one-logical-change-per-commit convention) — ask before committing, per this session's git policy.
- Avoid re-deriving the same primary-source page twice: T005/T006/T011 explicitly reuse wording already verified in T003/T004 rather than re-opening the PDF redundantly.
