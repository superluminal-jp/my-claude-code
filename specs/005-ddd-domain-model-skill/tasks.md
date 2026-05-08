# Tasks: DDD ドメインモデル管理スキル

**Input**: Design documents from `specs/005-ddd-domain-model-skill/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/skill-interface.md, quickstart.md

**Tests**: 手動（会話での動作確認）— 自動テストなし（Markdown スキル）

**Organization**: Tasks are grouped by user story to enable independent review and testing of each story's slice.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1 〜 US4)

## Path Conventions

成果物パス（リポジトリルート基準）:

```
.claude/skills/domain-model/
├── SKILL.md
├── index-template.md
└── context-template.md
.claude/CLAUDE.md       ← スキル登録更新
```

---

## Phase 1: Setup

**Purpose**: ディレクトリ作成

- [x] T001 Create `.claude/skills/domain-model/` directory

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 全 US が参照するファイルテンプレートを先に完成させる

**⚠️ CRITICAL**: US1〜US4 の実装は本フェーズ完了後に開始する

- [x] T002 [P] Write `.claude/skills/domain-model/context-template.md` — `docs/models/<context-kebab>.md` の初期テンプレート。data-model.md §3 の全テーブル（集約・エンティティ・VO・ドメインイベント・不変条件）の見出し行のみを含む空テーブルと、Mermaid classDiagram プレースホルダーを記述する
- [x] T003 [P] Write `.claude/skills/domain-model/index-template.md` — `docs/models/index.md` の初期テンプレート。data-model.md §2 のヘッダー・BC 一覧テーブル・空の Mermaid graph LR セクション（research.md Decision 4 の形式）を記述する

**Checkpoint**: テンプレート 2 ファイルが作成されており、Bootstrap・Update の両フローで参照できる状態

---

## Phase 3: User Story 1 — 会話からドメイン語彙を受動収集する (Priority: P1) 🎯 MVP

**Goal**: スキルが DDD 語彙パターンを会話から検出し、候補キューに積んで、適切なタイミングでバッチ提示する

**Independent Test**: 「注文は複数の明細を持つ」「注文IDで識別される」「在庫がゼロの場合は注文できない」を含む会話を想定して SKILL.md の Passive Collection セクションを読み、各発言が正しい trigger_type でキューに追加されるかをレビューで確認できる

### Implementation for User Story 1

- [x] T004 [US1] Create `.claude/skills/domain-model/SKILL.md` — ファイル冒頭（Pre-check セクション）を書く。フロー選択ロジック（`docs/models/` 内に対象コンテキストファイルが存在しない → Bootstrap flow、存在する → Maintenance/Update flow）と、セッション内候補キューのスキーマ（data-model.md §1 の 5 フィールド）を記述する
- [x] T005 [US1] Append Passive Collection section to `.claude/skills/domain-model/SKILL.md` — research.md Decision 2 の 5 パターン（aggregate/entity/value-object/domain-event/invariant）の検出ルールと偽陽性対策、キュー積みルール（会話中断なし）、提示条件（キュー≥1 かつ直前ターンで新規候補なし）を記述する

**Checkpoint**: SKILL.md の Pre-check + Passive Collection セクションを読むだけで、キュー積みと提示タイミングが完全に理解できる状態

---

## Phase 4: User Story 2 — 明示コマンドでモデルファイルを生成・更新する (Priority: P2)

**Goal**: ユーザーの明示指示でモデルファイルを新規生成または差分更新し、確認後にファイルに書き込む

**Independent Test**: 「注文コンテキストのドメインモデルを作成して」という呼び出しで Bootstrap フローが起動し、4 段階のヒアリング→差分提示→確認→書き込み の流れが SKILL.md から読み取れることをレビューで確認できる

### Implementation for User Story 2

- [x] T006 [US2] Append Bootstrap Flow section to `.claude/skills/domain-model/SKILL.md` — research.md Decision 3 の 4 ステップ（集約発見→エンティティ/VO 分類→ドメインイベント列挙→不変条件確認）のヒアリングフロー、context-template.md を元にした差分生成、「書き込み前に差分提示・明示確認」ルールを記述する
- [x] T007 [US2] Append Maintenance/Update Flow section to `.claude/skills/domain-model/SKILL.md` — 既存ファイルの読み込み、変更内容の差分提示、確認後書き込み、「変更なしの場合は上書きしない」ルール、Mermaid 図とテーブルの乖離検出と再生成提案を記述する
- [x] T008 [US2] Append Mermaid classDiagram generation rules to `.claude/skills/domain-model/SKILL.md` — research.md Decision 1 の規約（ステレオタイプ・コンポジション・関連の記法）を記述する。コード例を含める

**Checkpoint**: SKILL.md の Bootstrap + Maintenance フローと Mermaid 規約を読むだけで、モデルファイルの生成・更新・図の再生成が一貫して実行できる状態

---

## Phase 5: User Story 3 — ユビキタス言語との連携ブートストラップ (Priority: P3)

**Goal**: `docs/ubiquitous-language.md` が存在するとき、UL エントリをモデル候補として読み込み提案する。ドメインイベント命名は UL を正とする

**Independent Test**: `docs/ubiquitous-language.md` がある前提で SKILL.md の UL Integration セクションを読み、UL エントリが候補提案に含まれ、ドメインイベントが UL から参照されること（上書き不可）がレビューで確認できる

### Implementation for User Story 3

- [x] T009 [US3] Append UL Integration section to `.claude/skills/domain-model/SKILL.md` — Pre-check 拡張として「`docs/ubiquitous-language.md` 存在確認 → 存在すればエントリを候補キューに追加（trigger_type は元の DDD パターンから判定）」を記述する。ドメインイベントセクションでは「イベント名は UL に登録済みの表記を使用し、このスキルは UL に書き込まない」を明記する。UL 非存在時は独立ブートストラップモードで動作することを記述する

**Checkpoint**: SKILL.md の UL Integration セクションを読むだけで、UL との連携ルールと UL 非存在時の fallback が明確に理解できる状態

---

## Phase 6: User Story 4 — インデックスで全コンテキストを一元管理する (Priority: P4)

**Goal**: `docs/models/index.md` を常に全コンテキストファイルと同期し、コンテキスト間関係を記述できる

**Independent Test**: コンテキストファイルの作成・更新・削除のそれぞれで SKILL.md の Index Sync セクションを読み、index.md が自動同期される手順が記述されていることをレビューで確認できる

### Implementation for User Story 4

- [x] T010 [US4] Append Index Sync section to `.claude/skills/domain-model/SKILL.md` — コンテキストファイルの作成・更新・削除の各タイミングで `docs/models/index.md` を同期するルール（index-template.md のフォーマットに従う、BC 一覧テーブルの更新、Mermaid コンテキスト間関係図のオプション記述）を記述する
- [x] T011 [US4] Append Cross-context Conflict section to `.claude/skills/domain-model/SKILL.md` — コンテキスト間で同一概念が衝突した場合の「分離か改名かをユーザーに提示する」フロー（contracts/skill-interface.md のエラー条件を参照）を記述する。サイレントマージ禁止を不変条件として明記する

**Checkpoint**: SKILL.md の Index Sync + Conflict セクションを読むだけで、index.md の同期と概念衝突解決の手順が明確に理解できる状態

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: 不変条件の明示、スキル登録、最終検証

- [x] T012 Append Invariants section to `.claude/skills/domain-model/SKILL.md` — spec.md の 6 不変条件（Diff before write / Explicit confirmation / No silent cross-context merge / Single-file per BC / Index always reflects files / Diagram from tables）を SKILL.md の末尾に記述する
- [x] T013 Register domain-model skill in `.claude/CLAUDE.md` — skills セクションの `ubiquitous-language` エントリの直後に research.md Decision 5 のトリガー文言を追記する（1 行追加）
- [x] T014 [P] Validate SKILL.md against spec.md invariants — SKILL.md 全体を読み、FR-001〜FR-012 の各要件が少なくとも 1 つのセクションに対応していることを確認し、抜けがあれば補足する
- [x] T015 [P] Run quickstart.md validation — quickstart.md の 3 パターン（受動収集 / 明示コマンド / UL 連携）を SKILL.md と照合し、各ステップが SKILL.md の記述で実行可能であることを確認する

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: 依存なし — 即開始可
- **Foundational (Phase 2)**: Phase 1 完了後 — **全 US をブロック**
- **US1 (Phase 3)**: Phase 2 完了後 — 他 US に依存しない
- **US2 (Phase 4)**: Phase 2 完了後 — US1 に依存しない（SKILL.md は 1 ファイルだが各セクションは独立）
- **US3 (Phase 5)**: Phase 2 完了後 — US2 完了後に実施推奨（Bootstrap Flow が前提知識）
- **US4 (Phase 6)**: Phase 2 完了後 — US2 完了後に実施推奨（モデルファイル生成が前提）
- **Polish (Phase 7)**: US1〜US4 完了後

### User Story Dependencies

- **US1 (P1)**: Phase 2 完了後に開始可 — 他 US に依存しない
- **US2 (P2)**: Phase 2 完了後に開始可 — US1 と並行可
- **US3 (P3)**: US2 完了後を推奨（Bootstrap フローの理解が必要）
- **US4 (P4)**: US2 完了後を推奨（モデルファイル管理の理解が必要）

### Within Each User Story

- SKILL.md の各セクションは append 形式（前のセクションを前提として追記）
- T004 → T005（Pre-check 後に Passive Collection）
- T006 → T007 → T008（Bootstrap → Maintenance → Mermaid rules の順）
- T010 → T011（Index Sync → Cross-context Conflict の順）
- T014, T015 は並行実行可

### Parallel Opportunities

- T002, T003（テンプレート 2 ファイル）は並行作成可
- T014, T015 は並行実行可
- US1 と US2 は並行着手可（別の SKILL.md セクション）

---

## Parallel Example: Phase 2 (Templates)

```
# テンプレート 2 ファイルは並行作成可:
Task T002: Write .claude/skills/domain-model/context-template.md
Task T003: Write .claude/skills/domain-model/index-template.md
```

---

## Implementation Strategy

### MVP First (User Story 1 のみ)

1. Phase 1: Setup
2. Phase 2: Foundational（テンプレート作成）
3. Phase 3: US1（受動収集フロー）
4. **STOP and VALIDATE**: 受動収集セクションを会話でテスト
5. 問題なければ US2 へ

### Incremental Delivery

1. Setup + Foundational → テンプレート完成
2. US1 → 受動収集が機能するスキル（MVP）
3. US2 → モデルファイル生成が機能する完全なスキル
4. US3 → UL 連携を追加
5. US4 → インデックス管理を追加
6. Polish → 登録・検証

---

## Notes

- SKILL.md は 1 ファイルへの append 形式で構築。各タスク後に SKILL.md 全体が valid な Markdown であること
- [P] タスクは異なるファイルを対象とするか、完全に独立した検証作業であることが条件
- 各チェックポイントで SKILL.md を精読してレビューし、問題があれば当該フェーズのタスクに戻る
- テスト = 手動レビュー（会話内での動作確認）。自動テストは対象外
