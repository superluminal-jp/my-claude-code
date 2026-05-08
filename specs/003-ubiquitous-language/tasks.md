# Tasks: Ubiquitous Language Skill Simplification

**Input**: Design documents from `specs/003-ubiquitous-language/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓, quickstart.md ✓

**Organization**: Tasks grouped by user story for independent implementation and verification.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no shared dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- No test tasks — validation is manual via `quickstart.md` tests 1–5

---

## Phase 1: Setup

**Purpose**: Audit existing files before any rewriting begins.

- [X] T001 Read `.claude/skills/ubiquitous-language/SKILL.md` and list: (a) speckit references to remove, (b) subcommands to eliminate, (c) storage paths to change from `.specify/ubiquitous-language/` to `docs/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Templates must be ready before SKILL.md references them.

**⚠️ CRITICAL**: No user story work can begin until T002–T003 are complete.

- [X] T002 [P] Rewrite `.claude/skills/ubiquitous-language/ubiquitous-language-template.md` — file header (Project, Last Updated, Total Entries), `## Watchlist` section with Add/Remove lines, `## Bounded Context: <name>` section heading (not abbreviated "BC"), 7-field UL table (用語/定義/文脈/状態・ルール/例/反例/実装名) per data-model.md §1; target path `docs/ubiquitous-language.md`
- [X] T003 [P] Rewrite `.claude/skills/ubiquitous-language/context-map-template.md` — file header (Project, Last Updated), empty relationship table (用語/Context A/Context B/関係種別/備考) and relation-type legend per data-model.md §2; target path `docs/context-map.md`; remove all `.specify/` path references

**Checkpoint**: Templates ready — SKILL.md authoring can begin.

---

## Phase 3: User Story 1 — 初回実行・UL ファイルの自動作成 (Priority: P1) 🎯 MVP

**Goal**: `/ubiquitous-language` detects absent `docs/ubiquitous-language.md`, runs business-event elicitation, and creates both `docs/ubiquitous-language.md` and `docs/context-map.md` after user confirmation.

**Independent Test**: In a project with no `docs/ubiquitous-language.md`, type `/ubiquitous-language`. Verify: (a) skill announces file absence, (b) asks for business events, (c) produces 7-field UL draft, (d) shows diff, (e) creates both files only after confirmation (quickstart.md Test 1).

- [X] T004 [US1] Create `.claude/skills/ubiquitous-language/SKILL.md` — write: skill title and one-line description; Pre-check section that reads `docs/ubiquitous-language.md` presence and routes to Bootstrap or Maintenance; Bootstrap flow: announce absence, open with 「業務で実際に起きる出来事を 5〜10 個挙げてください」, extract roles/concepts/states/exceptions per event (FR-007), draft 7-field entries with `[NEEDS DOMAIN INPUT]` for missing fields (FR-008, FR-009), show diff of proposed `docs/ubiquitous-language.md` and empty `docs/context-map.md`, create `docs/` if absent (FR-003), write both files only on explicit user confirmation (FR-004, FR-003b)
- [X] T005 [P] [US1] Add Invariants section to `.claude/skills/ubiquitous-language/SKILL.md` (append after Bootstrap section): diff-before-write rule, explicit-confirmation rule, no-silent-Bounded-Context-unification rule, no-speckit-references rule (FR-016)

**Checkpoint**: US1 independently testable — run quickstart.md Test 1 before proceeding.

---

## Phase 4: User Story 2 — 既存 UL のメンテナンスと用語追加 (Priority: P1)

**Goal**: `/ubiquitous-language` on an existing file surfaces queued candidates, checks watchlist hits, handles Bounded Context conflicts, and supports watchlist management — all with diff-before-write.

**Independent Test**: With `docs/ubiquitous-language.md` present, type `/ubiquitous-language` after a conversation containing domain terms. Verify: (a) batch proposal of detected candidates, (b) accept/skip/custom choice works, (c) file updated after confirmation, (d) watchlist hit shows replacement candidates (quickstart.md Tests 2–3).

- [X] T006 [US2] Add Maintenance flow section to `.claude/skills/ubiquitous-language/SKILL.md` — display queued session candidates as batch proposal (FR-010); for each candidate: add / skip / custom definition options; scan recent conversation for watchlist terms (default 10: データ/情報/処理/管理/ステータス/フラグ/有効/完了/対象/ユーザー) and propose UL-grounded replacements (FR-012); detect same-term Bounded Context conflict and present split-or-rename choice, update `docs/context-map.md` (FR-011); re-surface `[NEEDS DOMAIN INPUT]` entries; offer interactive watchlist add/remove, persist to `## Watchlist` section of `docs/ubiquitous-language.md`; show cumulative diff of all proposed changes, write on confirmation (FR-004)

**Checkpoint**: US2 independently testable — run quickstart.md Tests 2–3 before proceeding.

---

## Phase 5: User Story 3 — 会話中の自動検出（パッシブ収集） (Priority: P2)

**Goal**: Claude passively detects business event expressions in conversation, queues candidates, and surfaces them at natural pauses. When no file exists and domain vocabulary is detected, bootstrap is proposed.

**Independent Test**: Send 「注文が確定されると在庫引当が走ります」 (no command). Then send a neutral follow-up with no domain vocabulary. Verify batch proposal appears after the second message. Also verify: with no file, detection triggers bootstrap proposal (quickstart.md Test 3).

- [X] T007 [US3] Add Passive Collection section to `.claude/skills/ubiquitous-language/SKILL.md` — rules for detecting business event expressions (past/passive verb+noun, role names, state names) without interrupting the current response (FR-013); queue candidate with source_text and trigger_type; surface batch proposal when queue ≥ 1 AND preceding turn had zero new candidates (FR-014); when `docs/ubiquitous-language.md` absent and vocab detected, propose bootstrap flow (FR-015); do not initiate collection when no domain vocabulary is detectable
- [X] T008 [P] [US3] Update ubiquitous-language routing rule in `.claude/CLAUDE.md` — replace existing file-presence-based line with content-based trigger line per `contracts/extensions-yml-additions.md`: activate when conversation contains business event expressions or domain vocabulary candidates; note passive queuing and natural-pause surfacing behavior (FR-017)
- [X] T012 [P] [US3] Update `.specify/extensions.yml` — in every `before_*` hook array that contains a `ubiquitous-language` entry, change `command: ubiquitous-language.collect` to `command: ubiquitous-language`; applies to `before_specify`, `before_clarify`, `before_plan`, `before_tasks`, `before_analyze`; all other hook fields unchanged (per `contracts/extensions-yml-additions.md`)

**Checkpoint**: US3 independently testable — run quickstart.md Test 3 before proceeding.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Completeness check and full validation sweep.

- [X] T009 [P] Search `.claude/skills/ubiquitous-language/SKILL.md` for any occurrence of "speckit", "spec-kit", "/speckit", or "extensions.yml"; remove all found references (FR-016, SC-003)
- [X] T010 [P] Search `.claude/CLAUDE.md` ubiquitous-language routing line for "speckit" or ".specify/"; confirm only content-based trigger language remains (SC-003)
- [X] T011 Run quickstart.md validation Tests 1–5 in order; verify each expected behavior matches SKILL.md instructions and CLAUDE.md rule

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 — **BLOCKS all user story phases**
- **US1 (Phase 3)**: Depends on Phase 2 — T004 creates SKILL.md; T005 appends to it (can start once T004 is in progress)
- **US2 (Phase 4)**: Depends on T004 complete (SKILL.md exists); T006 appends Maintenance section
- **US3 (Phase 5)**: Depends on T006 complete (SKILL.md has Maintenance); T007 appends Passive Collection; T008 and T012 are independent (different files — CLAUDE.md and extensions.yml respectively)
- **Polish (Phase 6)**: Depends on T004–T008 all complete

### Within Each Phase

- T002 and T003 are fully independent — run in parallel
- T004 creates SKILL.md; T005/T006/T007 append to it — sequential order matters
- T008 (CLAUDE.md) is independent of all SKILL.md edits — run in parallel with any phase
- T009 and T010 are independent checks — run in parallel

---

## Parallel Execution Examples

### Phase 2 (Foundational)

```
Parallel: T002 (UL template) + T003 (context-map template)
After both: T004 (begin SKILL.md)
```

### Phase 3–5 (SKILL.md construction)

```
Sequential in SKILL.md: T004 → T005 → T006 → T007
Parallel at any time: T008 (CLAUDE.md, different file)
Parallel at any time: T012 (extensions.yml, different file)
Parallel at any time: T009 + T010 (read-only checks, safe once SKILL.md exists)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1: T001 (audit)
2. Phase 2: T002 + T003 in parallel (templates)
3. Phase 3: T004 → T005 (SKILL.md bootstrap + invariants)
4. **STOP and VALIDATE**: quickstart.md Test 1
5. Proceed to US2 only after Test 1 passes

### Incremental Delivery

1. Phases 1–2 → Templates ready
2. Phase 3 → Bootstrap functional (MVP — creates files on first run)
3. Phase 4 → Maintenance functional (ongoing UL updates)
4. Phase 5 → Passive collection active (conversation-driven detection)
5. Phase 6 → All validation tests pass; no speckit references remain

---

## Notes

- [P] tasks modify different files — safe to run concurrently
- SKILL.md is a single file; T004 → T005 → T006 → T007 must be sequential to preserve section order
- Every write-capable section (Bootstrap, Maintenance) must include the diff-before-write + explicit-confirmation invariant — verify during T009 review
- T008 targets `.claude/CLAUDE.md` only; make the minimal 1-line replacement described in `contracts/extensions-yml-additions.md`
- T011 is manual prompt-based validation; each quickstart.md test includes input, expected behavior, and pass/fail criterion
