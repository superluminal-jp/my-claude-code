# Tasks: Ubiquitous Language Auto-Builder

**Input**: Design documents from `specs/003-ubiquitous-language/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓, quickstart.md ✓

**Organization**: Tasks grouped by user story to enable independent implementation and verification of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no shared dependencies)
- **[Story]**: Which user story this task belongs to (US1–US4)
- Tests are **manual scenario files** (prompt-based verification); no automated test framework is used

---

## Phase 1: Setup

**Purpose**: Create directory scaffolding before any file writing begins.

- [X] T001 Create directories `.claude/skills/ubiquitous-language/` and `tests/ubiquitous-language/` per plan.md project structure

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Templates and skill skeleton — required by all user story phases. No external tooling dependency.

**⚠️ CRITICAL**: No user story implementation can begin until this phase is complete.

- [X] T002 Create `.claude/skills/ubiquitous-language/ubiquitous-language-template.md` — BC file header (Bounded Context, Project, Last Updated, Entry Count, Status) and 7-field UL table (用語/定義/文脈/状態・ルール/例/反例/実装名) with `[NEEDS DOMAIN INPUT]` marker convention, per data-model.md §1 [stored in skill dir per user instruction]
- [X] T003 [P] Create `.claude/skills/ubiquitous-language/context-map-template.md` — context map table with 用語/BC-A/BC-B/関係種別/備考 columns and four relation-type enum values (same-name-different-meaning, synonym, identical, refines), per data-model.md §2 [stored in skill dir per user instruction]
- [X] T004 Author Pre-check section of `.claude/skills/ubiquitous-language/SKILL.md` — context-state detection (UL store present/absent, artifact-under-review flag, conversational flag) without encoding caller identity; shared in-session queue structure (candidate_term, source_text, trigger_type, detected_at); Batch Proposal and Drift Report output formats defined inline (self-contained — no runtime dependency on contracts/ artifacts); Error/Edge Conditions table including UL-store-not-found and same-turn deduplication guard

**Checkpoint**: Templates and skill skeleton ready — user story sections can now be appended in parallel to SKILL.md.

---

## Phase 3: User Story 1 — 新規プロジェクトでのユビキタス言語ブートストラップ (Priority: P1) 🎯 MVP

**Goal**: Detect UL absence and run business-event-driven elicitation to produce per-BC UL files with all 7 fields.

**Independent Test**: Provide a 1–2 paragraph domain description with no existing `.specify/ubiquitous-language/` directory; system must produce (a) business-event candidate list, (b) BC candidates, (c) per-BC UL table with 7 fields. Domain reviewer confirms ≥ 80% of terms match actual business vocabulary (SC-001, SC-007).

- [X] T005 [US1] Implement Bootstrap mode section in `.claude/skills/ubiquitous-language/SKILL.md` — UL-absence detection (FR-001), business-event-first elicitation opening question (FR-004), role/concept/state/exception extraction per event (FR-005), developer-derived tagging when no domain expert is present (FR-006), 7-field entry creation with mandatory 例 and 反例 (FR-007, FR-008), state-transition capture in 状態・ルール field using arrow notation (FR-009), size-budget check with BC-split/consolidation proposal when > 30 entries (FR-019), incomplete-entry `[NEEDS DOMAIN INPUT]` marking and re-surface at next lifecycle event (FR-025)
- [X] T023 [US1] Implement single-row-entry enforcement in Bootstrap and Collect modes of `.claude/skills/ubiquitous-language/SKILL.md` — reject multi-paragraph definitions; prompt user to restructure input into the 7-field form before any row is appended (FR-020)
- [X] T024 [US1] Implement within-BC duplicate-term check in Bootstrap and Collect modes of `.claude/skills/ubiquitous-language/SKILL.md` — before writing any new entry, scan the target BC file for an existing row matching the same 用語; if found, prompt to update the existing entry rather than append a duplicate (FR-021)
- [X] T025 [US1] Implement auto-population of `更新イベント` field in Bootstrap and Collect modes of `.claude/skills/ubiquitous-language/SKILL.md` — when creating or updating any UL entry, record the current lifecycle event name (or "conversational" when no lifecycle event is active) in the `更新イベント` field; this field is set by the skill, never editable directly by users (FR-027)
- [X] T006 [P] [US1] Create `tests/ubiquitous-language/001-bootstrap-new-project.md` — manual scenario covering all four US1 acceptance scenarios: (1) UL-absence detection triggers elicitation, (2) 7-field file generation, (3) same-term multi-BC detection during bootstrap, (4) size-budget exceeded proposal
- [X] T007 [P] [US1] Create `tests/ubiquitous-language/007-state-transition-elicitation.md` — manual scenario covering FR-009: stateful term identified, system prompts for normal and exception transitions, transitions recorded in 状態・ルール field using arrow notation
- [X] T008 [P] [US1] Create `tests/ubiquitous-language/008-size-budget-enforcement.md` — manual scenario covering FR-019: 30-entry budget exceeded, system proposes BC split or term consolidation before allowing new entry write

**Checkpoint**: US1 independently functional — bootstrap elicitation and initial BC file generation verified.

---

## Phase 4: User Story 2 — 通常会話・ライフサイクル自動発火と曖昧語検知 (Priority: P2)

**Goal**: Passive vocabulary collection in general conversation, lifecycle-triggered UL sweep, vague-term detection, and implementation-name drift detection without interrupting user flow.

**Independent Test**: Without any `/speckit-*` command, send a business-description chat message; system queues new candidates and surfaces a batch proposal at the next natural pause. Vague-term "ユーザー" in a spec artifact triggers a quoted replacement proposal before artifact is finalized. Implementation name `Order.process()` in plan.md while UL records `Order.confirm()` triggers a drift warning with 3-option resolution (SC-003, SC-008).

- [X] T009 [US2] Implement Collect mode section in `.claude/skills/ubiquitous-language/SKILL.md` — passive monitoring for business events, roles, states, rules in user messages without interrupting current response (FR-030), queue accumulation, batch proposal trigger at natural conversation pause or next lifecycle event (FR-031), no-activation guard when UL store is not discoverable (FR-032), per-invocation skip/defer handling with re-surface guarantee (FR-003)
- [X] T026 [US2] Implement clarification-trigger pattern detection in Collect mode of `.claude/skills/ubiquitous-language/SKILL.md` — when the conversation contains clarification-question patterns (e.g., "つまり何を指していますか？", "それはどういう意味ですか？"), immediately propose adding or refining the relevant UL entry rather than queuing for batch proposal (FR-026)
- [X] T010 [US2] Implement vague-term watchlist subsection in Validate mode of `.claude/skills/ubiquitous-language/SKILL.md` — default 10-term Japanese watchlist (データ/情報/処理/管理/ステータス/フラグ/有効/完了/対象/ユーザー, FR-010), in-artifact detection with quoted location and UL-grounded replacement proposal (FR-011), project-specific extension and override support via `.specify/ubiquitous-language/watchlist.md` (FR-012)
- [X] T011 [US2] Implement drift detection subsection in Validate mode of `.claude/skills/ubiquitous-language/SKILL.md` — compare AI-generated artifact identifiers against UL 実装名 field (FR-016), case/separator normalization (no false positives on casing), semantic divergence flagging, 3-option resolution (align artifact / update UL / split term, FR-017), no-silent-rewrite guarantee with diff-before-write (FR-018)
- [X] T013 [US2] Update `.claude/CLAUDE.md` Skills routing section — add one line for `ubiquitous-language` conversational-mode rule: active when `.specify/ubiquitous-language/` exists; passively collects domain vocabulary and surfaces candidates at natural conversation pauses, per contracts/extensions-yml-additions.md
- [X] T014 [P] [US2] Create `tests/ubiquitous-language/002-vague-term-detection.md` — manual scenario covering FR-010 and FR-011: vague term "ユーザー" in spec artifact is detected, quoted with line reference, and replacement candidates (契約管理者/利用者/請求担当者) are proposed before artifact acceptance
- [X] T015 [P] [US2] Create `tests/ubiquitous-language/003-conversational-collection.md` — manual scenario covering FR-030 and FR-031: no speckit command used; business events in chat are queued; batch proposal appears at next natural pause; confirmed terms update the UL file
- [X] T016 [P] [US2] Create `tests/ubiquitous-language/005-drift-detection.md` — manual scenario covering FR-016 and FR-017: `Order.process()` in plan.md vs. `Order.confirm()` in UL triggers drift warning and 3-option resolution dialog

**Checkpoint**: US2 independently functional — passive collection, vague-term detection, drift detection, and extensions.yml hooks all verified.

---

## Phase 5: User Story 3 — 境界づけられた文脈ごとの分割と意味衝突の解決 (Priority: P2)

**Goal**: Detect same-term / different-meaning conflicts across BCs, split into per-BC entries, and record cross-BC relationships in context-map.md.

**Independent Test**: Input conflicting definitions of "顧客" for 営業 / 請求 / サポート; system creates three separate BC UL files each with a "顧客" entry and distinct 実装名 (SalesAccount / BillingParty / SupportContact); context-map.md records all three as same-name-different-meaning (SC-005).

- [X] T017 [US3] Implement BC conflict resolution subsection in Validate mode of `.claude/skills/ubiquitous-language/SKILL.md` — multi-BC file support with one file per BC (FR-013), conflict detection when same term receives differing definitions, 3-option dialog (BC-specific split / BC merge / rename one term, FR-014), no silent global unification, context-map.md update recording cross-BC relation type (FR-015), bilingual entry support with 用語 in domain language and 実装名 in English (FR-028, FR-029)
- [X] T018 [P] [US3] Create `tests/ubiquitous-language/004-bc-split-conflict.md` — manual scenario covering FR-014 and FR-015: same-term conflict presented, 3-choice dialog shown, BC-split selection results in separate BC entries and context-map.md entry with same-name-different-meaning relation

**Checkpoint**: US3 independently functional — BC conflict detection, per-BC file generation, and context-map.md recording verified.

---

## Phase 6: User Story 4 — コンテキスト長圧縮のための語彙運用 (Priority: P3)

**Goal**: Use stabilized UL as a compression dictionary — Ontology Header injection, paraphrase → UL-term substitution, Delta Notation for UL updates.

**Independent Test**: With ≥ 20 terms in UL, input a long spec containing paraphrases of registered definitions; system detects paraphrases, proposes UL-term substitution, shows diff preserving meaning; average artifact length for recurring concepts reduces ≥ 20% (SC-009).

- [X] T019 [US4] Implement Context compression section in `.claude/skills/ubiquitous-language/SKILL.md` — Ontology Header generation (summary table: 用語 + 1行定義 per BC, injected at session or lifecycle event start, FR-022), paraphrase-to-UL-term detection and substitution proposal with diff (FR-023), linkability guarantee — every UL term in an artifact resolves to its BC entry without ambiguity (FR-024), Delta Notation for UL updates ([+]/[~]/[-] prefix), Frequency-Based Depth (high-frequency terms in Ontology Header as short form), State-Machine Compression (transitions as 1-line arrow notation linking to UL file)
- [X] T020 [P] [US4] Create `tests/ubiquitous-language/006-context-compression.md` — manual scenario covering FR-022 and FR-023: Ontology Header appears at session start, paraphrase detected in spec input, substitution proposed with diff, meaning equivalence confirmed by user

**Checkpoint**: US4 independently functional — Ontology Header, paraphrase detection, and Delta Notation verified.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Completeness verification and quickstart validation across all artifacts.

- [X] T021 [P] Verify SKILL.md completeness: all five sections present (Pre-check, Bootstrap, Collect, Validate, Context compression); all FR-001–FR-032 traceable to at least one section; all SC-001–SC-011 addressable; slash-command subcommands (bootstrap / show / add / check) defined in SKILL.md; diff-before-write and explicit-confirmation invariant present in Bootstrap, Collect, and Validate write-capable sections (FR-018); SC-010 timing target documented in test scenarios; SKILL.md contains no speckit-specific references in its own logic (caller-agnostic invariant)
- [X] T022 [P] Run quickstart.md verification steps 1–6: confirm each step maps to a generated artifact (SKILL.md, two templates, extensions.yml entries, CLAUDE.md line, 8 test scenario files) and that all 6 quickstart confirmation checks (Confirmations 1–6) have corresponding playbook instructions in SKILL.md

---

## Optional: speckit Integration

**Purpose**: Wire the skill into speckit's lifecycle hook system so it fires automatically before each speckit command. Skip entirely if not using speckit — the skill is fully functional without this.

- [X] T012 [P] Update `.specify/extensions.yml` — append ubiquitous-language.collect optional hook entry (enabled: true, optional: true) to `before_specify`, `before_clarify`, `before_plan`, `before_tasks`, `before_analyze` arrays after existing hooks, per contracts/extensions-yml-additions.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 (directories must exist) — **BLOCKS all user story phases**
- **User Story Phases (3–6)**: All depend on Phase 2 completion
  - SKILL.md sections for US1–US4 must be appended in order (Pre-check → Bootstrap → Collect → Validate → Context compression) since each mode builds on the Pre-check shared structure
  - US3 (Validate: BC conflict) can be written in parallel with US2 Collect mode since they target different SKILL.md subsections; T013 (CLAUDE.md) is the only US2 file edit independent of SKILL.md
- **Polish (Phase 7)**: Depends on all six preceding phases complete

### User Story Dependencies

- **US1 (P1)**: Starts after Foundational — no dependency on US2/US3/US4
- **US2 (P2)**: Starts after Foundational; T009–T011 append to SKILL.md after T005 (Bootstrap) is complete to preserve section order; T013 (CLAUDE.md) can run in parallel with T009–T011
- **US3 (P2)**: T017 appends to SKILL.md Validate mode; can proceed concurrently with US2 Collect mode tasks once Pre-check (T004) is done
- **US4 (P3)**: Must follow US1–US3 (Context compression references stable UL from all prior modes)

### Within Each Phase

- Templates (T002, T003) are independent — run in parallel
- Test scenarios within a phase are all independent — run in parallel
- SKILL.md edits (T004, T005, T023–T025, T009, T026, T010, T011, T017, T019) must be sequential to maintain section order within the file
- CLAUDE.md (T013) edits are independent of SKILL.md edits
- T012 (extensions.yml) is independent of all core phases — execute only if using speckit

---

## Parallel Execution Examples

### Phase 2 (Foundational)

```
Parallel: T002 (UL template) + T003 (context-map template)
Sequential after both: T004 (SKILL.md Pre-check section)
```

### Phase 3 (US1)

```
Sequential: T005 → T023 → T024 → T025 (Bootstrap mode + enforcement sections in SKILL.md)
Parallel after T005: T006 + T007 + T008 (test scenario files, independent of SKILL.md edits)
```

### Phase 4 (US2)

```
Sequential: T009 → T026 → T010 → T011 (SKILL.md Collect + Validate subsections, order matters for file coherence)
Parallel with T009–T011: T013 (CLAUDE.md)
Parallel: T014 + T015 + T016 (test scenarios, independent files)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001)
2. Complete Phase 2: Foundational (T002, T003, T004)
3. Complete Phase 3: US1 Bootstrap (T005–T008)
4. **STOP and VALIDATE**: Run `tests/ubiquitous-language/001-bootstrap-new-project.md` — confirm 7-field BC file is produced from a domain description
5. Proceed to US2/US3 once US1 is confirmed working

### Incremental Delivery

1. Phase 1 + 2 → Skill skeleton and templates ready
2. Phase 3 (US1) → Bootstrap elicitation functional (MVP — highest value)
3. Phase 4 (US2) → Passive collection, vague-term detection, drift detection, and lifecycle hooks active
4. Phase 5 (US3) → Multi-BC conflict resolution active
5. Phase 6 (US4) → Context compression active (opportunistic optimization)
6. Phase 7 → Cross-cutting validation complete

---

## Notes

- [P] tasks modify different files or independent sections — safe to run concurrently
- SKILL.md is a single file; sequential section-by-section authoring avoids merge conflicts
- SKILL.md must not reference speckit by name in its own logic — the skill is caller-agnostic; speckit integration is handled entirely by T012 (optional) and T013 (CLAUDE.md routing)
- All UL writes in the playbook must include a diff-before-write step and explicit user confirmation (FR-018) — verify this invariant is present in every write-capable section (Bootstrap, Collect, Validate)
- Test scenarios are manual prompt-based (no test runner); each file should include the input to provide, the expected system behavior, and the pass/fail criterion
- Slash-command subcommands (bootstrap / show / add / check) defined in skill-interface.md Mode B must be implemented in SKILL.md Mode B section during T004 or T005
