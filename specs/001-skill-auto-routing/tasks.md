# Tasks: Automatic Skill Routing

**Input**: Design documents from `specs/001-skill-auto-routing/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Organization**: タスクはユーザーストーリー単位でグループ化。各フェーズが独立してテスト可能。  
**Tests**: FR-007 に基づき `tests/skill-routing/` にプロンプトシナリオを先行作成（TDD 的アプローチ）。

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 並列実行可（異なるファイル、依存なし）
- **[Story]**: 対応するユーザーストーリー（US1/US2/US3）

---

## Phase 1: Setup

**Purpose**: テスト環境の初期化

- [ ] T001 Create `tests/skill-routing/` directory structure (`mkdir -p tests/skill-routing`)

---

## Phase 2: Foundational — プロンプトテストシナリオ作成

**Purpose**: 変更前にテストシナリオを作成し、現行ルールへの適合を baseline として記録する（TDD: Red フェーズ）

**⚠️ CRITICAL**: US1〜US3 の実装前にシナリオを作成すること。変更後に全シナリオが Pass することで受け入れ基準を満たす。

- [ ] T002 [P] Create code request test scenario in `tests/skill-routing/001-code-implement.md` (入力: "バグを修正して", 期待: `coder`, category: code)
- [ ] T003 [P] Create document request test scenario in `tests/skill-routing/002-document-create.md` (入力: "READMEを書いて", 期待: `editor`, category: document)
- [ ] T004 [P] Create mixed request test scenario in `tests/skill-routing/003-mixed-code-and-doc.md` (入力: "実装してREADMEも更新して", 期待: `coder` → `editor`, category: mixed)
- [ ] T005 [P] Create ambiguous request test scenario in `tests/skill-routing/004-ambiguous-request.md` (入力: "なんとかして", 期待: `clarifier`, category: ambiguous)

**Checkpoint**: テストシナリオ 4 件作成完了。US1〜US3 の実装に進む。

---

## Phase 3: User Story 1 — Code Request Auto-Routes to Coder (Priority: P1) 🎯 MVP

**Goal**: コード関連リクエストで `coder` スキルが自動ロードされる

**Independent Test**: `tests/skill-routing/001-code-implement.md` のシナリオを実行し、`coder` スキルがロードされることを確認

### Test Verification for User Story 1

- [ ] T006 [US1] Run `tests/skill-routing/001-code-implement.md` against current rules and document current behavior (baseline)

### Implementation for User Story 1

- [ ] T007 [US1] Edit `.claude/CLAUDE.md` — Skills セクションの見出しを "Skills (on-demand)" から "Skills (mandatory routing)" に変更し、`coder` のトリガー行を「コードの実装・修正・リファクタリング・テスト・デバッグを含むリクエスト → load \`coder\`」1 行に書き換える
- [ ] T008 [US1] Verify `tests/skill-routing/001-code-implement.md` passes after T007 (coder が自動ロードされることを目視確認)

**Checkpoint**: コードリクエストで `coder` が自動ロードされることを確認。US1 完了。

---

## Phase 4: User Story 2 — Document Request Auto-Routes to Editor (Priority: P2)

**Goal**: ドキュメント関連リクエストで `editor` スキルが自動ロードされる

**Independent Test**: `tests/skill-routing/002-document-create.md` および `003-mixed-code-and-doc.md` のシナリオを実行し、`editor` スキルがロードされることを確認

### Test Verification for User Story 2

- [ ] T009 [US2] Run `tests/skill-routing/002-document-create.md` and `003-mixed-code-and-doc.md` against current state and document baseline behavior

### Implementation for User Story 2

- [ ] T010 [US2] Edit `.claude/CLAUDE.md` — `editor` のトリガー行を「ドキュメント・スライド・チャート・翻訳・文章編集を含むリクエスト → load \`editor\`」1 行に書き換える
- [ ] T011 [US2] Verify `tests/skill-routing/002-document-create.md` passes (editor が自動ロードされることを目視確認)
- [ ] T012 [US2] Verify `tests/skill-routing/003-mixed-code-and-doc.md` passes (coder → editor の順にロードされることを目視確認)

**Checkpoint**: ドキュメント・混在リクエストで正しいスキルが自動ロードされることを確認。US2 完了。

---

## Phase 5: User Story 3 — Minimal Rules Description (Priority: P3)

**Goal**: `CLAUDE.md` と `rules/skill-routing.md` のスキルルーティング記述がトリガー条件のみ（各スキル 1 行）に収まる

**Independent Test**: 削減後のルールで全 4 シナリオが引き続き Pass することを確認

### Implementation for User Story 3

- [ ] T013 [P] [US3] Edit `.claude/CLAUDE.md` — `clarifier` のトリガー行を「任意の曖昧さ（intent/scope/acceptance/constraint gap を含む）→ load \`clarifier\`」1 行に書き換え、"For spec-kit projects..." 注記を削除する
- [ ] T014 [P] [US3] Edit `.claude/rules/skill-routing.md` — "Mandatory gate" セクションおよび "Scope discipline" セクションを削除し、"Routing" セクションの 3 行のみ残す
- [ ] T015 [US3] Verify all 4 scenarios in `tests/skill-routing/` pass after T013 and T014 (全シナリオ目視確認)
- [ ] T016 [US3] Verify SC-004: `.claude/CLAUDE.md` の各スキル記述が 1 行トリガーのみに収まっていることを確認

**Checkpoint**: 全ユーザーストーリー実装完了。全シナリオ Pass を確認。

---

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T017 [P] Update spec status from "Draft" to "Complete" in `specs/001-skill-auto-routing/spec.md`
- [ ] T018 [P] Update `specs/001-skill-auto-routing/checklists/requirements.md` — 最終検証結果を記録
- [ ] T019 Run `specs/001-skill-auto-routing/quickstart.md` end-to-end validation (全変更の整合性確認)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: 依存なし — 即時開始可
- **Foundational (Phase 2)**: Phase 1 完了後 — US1〜US3 の前提
- **US1 (Phase 3)**: Phase 2 完了後 — MVP 起点
- **US2 (Phase 4)**: Phase 2 完了後、US1 とほぼ並列可（同ファイルへの追記）
- **US3 (Phase 5)**: US1 + US2 完了後（削減前に正確なルーティングを確認）
- **Polish (Phase 6)**: Phase 5 完了後

### User Story Dependencies

- **US1 (P1)**: Phase 2 完了後に開始可。他ストーリーへの依存なし
- **US2 (P2)**: Phase 2 完了後に開始可。US1 の実装が CLAUDE.md にあるため、US1 の T007 完了後に着手が望ましい（同ファイル競合を避けるため）
- **US3 (P3)**: US1 + US2 完了後（削減対象のルールが正確に機能していることを確認してから削減）

### Parallel Opportunities

- T002〜T005（テストシナリオ作成）は完全並列実行可
- T013 と T014（US3 内）は別ファイルのため並列実行可
- T017 と T018（Polish）は並列実行可

---

## Parallel Example: Foundational Phase

```
# T002〜T005 を同時実行:
Task: "Create tests/skill-routing/001-code-implement.md"
Task: "Create tests/skill-routing/002-document-create.md"
Task: "Create tests/skill-routing/003-mixed-code-and-doc.md"
Task: "Create tests/skill-routing/004-ambiguous-request.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1: Setup — `tests/skill-routing/` 作成
2. Phase 2: Foundational — テストシナリオ 4 件作成
3. Phase 3: US1 — `coder` の mandatory ルーティング
4. **STOP and VALIDATE**: `001-code-implement.md` が Pass することを確認
5. US1 だけで「コードリクエストに coder が自動適用される」という価値を提供

### Incremental Delivery

1. Setup + Foundational → テスト基盤完成
2. US1 → `coder` 自動ルーティング（MVP）
3. US2 → `editor` 自動ルーティング
4. US3 → ルール削減（記述量最小化）
5. 各ステップで全テストシナリオが Pass することを確認

---

## Notes

- [P] タスクは別ファイルへの操作で依存なし
- [Story] ラベルはユーザーストーリーとのトレーサビリティを確保
- テストシナリオは手動実行（プロンプト入力 → 目視確認）
- US3 は US1+US2 の確認後に実施（削減前に正確性を担保）
- `rules/skill-routing.md` の Mandatory gate 削除は `CLAUDE.md` の Response Preflight で機能が代替される前提
