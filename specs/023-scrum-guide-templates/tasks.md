---

description: "Task list template for feature implementation"
---

# Tasks: Scrum Guide 作成物・イベント テンプレート

**Input**: Design documents from `/specs/023-scrum-guide-templates/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: spec.mdはテストを明示的に要求していない（コンテンツのみのfeature）。テストタスクは含めない。代わりに`quickstart.md`のgrep/findベースの検証をPolishフェーズで実行する。

**Organization**: タスクはspec.mdのユーザーストーリー（P1/P2/P3）ごとにグループ化されている。

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 並列実行可能（異なるファイル、依存なし）
- **[Story]**: どのユーザーストーリーに属するか（US1/US2/US3）

## Path Conventions

すべて既存の`.claude/skills/scrum-master/`スキルパッケージへのin-place追加。`src/`/`tests/`のアプリケーション構造は適用されない。

---

## Phase 1: Setup

**Purpose**: テンプレートを配置する新規ディレクトリを用意する

- [X] T001 `.claude/skills/scrum-master/references/templates/` ディレクトリを作成する

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 全ユーザーストーリーに共通するブロッキング前提作業

Phase 1のディレクトリ作成以外に共有のブロッキング作業はない。US1〜US3はそれぞれ独立したファイルを新規作成・編集するのみで、相互依存はない。**このフェーズにタスクはなく、Phase 1完了後ただちにPhase 3へ進む。**

**Checkpoint**: ディレクトリが存在すればユーザーストーリー実装を開始できる

---

## Phase 3: User Story 1 - 作成物（Product Backlog／Sprint Backlog／Increment）のテンプレート (Priority: P1) 🎯 MVP

**Goal**: 3つの作成物テンプレートを、Scrum Guideが定める属性・対応コミットメントの記入欄付きで提供する

**Independent Test**: `references/templates/` 配下の3ファイルを開き、data-model.mdが定める記入欄（属性・コミットメント）と`[SG20, p.X]`引用が揃っていることを確認する

### Implementation for User Story 1

- [X] T002 [P] [US1] `.claude/skills/scrum-master/references/templates/product-backlog.md` を作成する：Product Backlog itemsの属性（description／order／estimate／value）の記入欄、Product Goal（コミットメント）の記入欄、`[SG20, p.10-11]`の出典を含める（spec.md FR-002, data-model.md）。**実装時の訂正**：当初`sources.md`への相対リンクを含めていたが、ユーザー指示（「テンプレートは単体で完結するように。相対リンクなどは排除。公式URLの直リンクは許容」）によりScrum Guide公式サイトへの直リンクに差し替えた（全7テンプレート共通、FR-010改訂）。
- [X] T003 [P] [US1] `.claude/skills/scrum-master/references/templates/sprint-backlog.md` を作成する：Sprint Goal（コミットメント）欄、選択したProduct Backlog items一覧欄、Incrementを届ける計画欄、`[SG20, p.9-11]`の出典を含める（spec.md FR-003, data-model.md）
- [X] T004 [P] [US1] `.claude/skills/scrum-master/references/templates/increment.md` を作成する：Definition of Done（コミットメント）欄、Incrementの説明欄、DoDを満たした時点でIncrementが生まれるという定義の記載、`[SG20, p.11-12]`の出典を含める（spec.md FR-004, data-model.md）

**Checkpoint**: 作成物3テンプレートが独立して開いて使える状態。`quickstart.md` SC-001（3/7分）・SC-005がこの3ファイルについて検証可能。

---

## Phase 4: User Story 2 - Scrumイベントのテンプレート (Priority: P2)

**Goal**: 4つのイベントテンプレートを、目的・タイムボックス・Scrum Guideが定める検討内容の記入欄付きで提供する

**Independent Test**: `references/templates/` 配下の4ファイルを開き、各イベントの目的・タイムボックス・検討項目が記載されていることを確認する

### Implementation for User Story 2

- [X] T005 [P] [US2] `.claude/skills/scrum-master/references/templates/sprint-planning.md` を作成する：Why／What／Howの3つの問いの記入欄、タイムボックス（1か月Sprintで最大8時間、短いSprintでは比例して短縮する旨の注記）、`[SG20, p.8]`の出典を含める（spec.md FR-005）
- [X] T006 [P] [US2] `.claude/skills/scrum-master/references/templates/daily-scrum.md` を作成する：目的（Sprint Goalへの進捗検査とSprint Backlogの適応）、タイムボックス（15分、毎日同じ時間・場所）、`[SG20, p.9]`の出典を含める（spec.md FR-006）
- [X] T007 [P] [US2] `.claude/skills/scrum-master/references/templates/sprint-review.md` を作成する：目的（成果の提示とProduct Goalへの進捗確認、作業セッションでありステータス報告ではない旨）、タイムボックス（1か月Sprintで最大4時間）、`[SG20, p.9-10, p.12]`の出典を含める（spec.md FR-007）
- [X] T008 [P] [US2] `.claude/skills/scrum-master/references/templates/sprint-retrospective.md` を作成する：検査対象（個人・相互作用・プロセス・ツール・Definition of Done）、目的（品質と効果を高める改善計画の作成）、タイムボックス（1か月Sprintで最大3時間）、`[SG20, p.10]`の出典を含める（spec.md FR-008）

**Checkpoint**: 7テンプレートすべてが揃う。`quickstart.md` SC-001（7/7）・SC-005が全ファイルで検証可能。

---

## Phase 5: User Story 3 - SKILL.mdからテンプレートへの導線 (Priority: P3)

**Goal**: `SKILL.md`の「参照ファイル」表から新規テンプレート群を発見できるようにする

**Independent Test**: `SKILL.md`を開き、「参照ファイル」表または「成果物を作る」節にテンプレートディレクトリへのリンクがあることを確認する

### Implementation for User Story 3

- [X] T009 [US3] `.claude/skills/scrum-master/SKILL.md` の「参照ファイル」表に、`references/templates/` への導線となる行を1行追加する（spec.md FR-011。既存の`when_to_use`・原則・ワークフロー本文は変更しない）

**Checkpoint**: SKILL.mdからテンプレートへ1回の参照で到達できる。`quickstart.md` SC-004が検証可能。

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: リポジトリ横断の整合性確認とLive Documentation対応

- [X] T010 [P] `README.md` のscrum-masterスキルのファイルツリー説明（283-285行目付近）を更新し、`references/templates/`（7ファイル）の存在を反映する（research.md Decision 2）
- [X] T011 `quickstart.md` のSC-001〜SC-005検証コマンドとデッドリンク確認コマンドを実行し、全て期待値どおりであることを確認する
- [X] T012 `bash tests/run-skill-routing.sh` を実行し、`tests/skill-routing/007-scrum-facilitation.md` を含む全件が変更後も通ることを確認する
- [X] T013 リポジトリ横断の整合性チェックを実行する：`./scripts/check-mcp-consistency.sh`、`bash tests/run-codex-references.sh`、`bash tests/run-codex-drift.sh`
- [X] T014 `git status`/`git diff`で変更内容を確認し、コミット前に`post-edit-format.sh`によるフォーマッタ差分がないか点検する

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: 依存なし。ただちに開始できる
- **Foundational (Phase 2)**: タスクなし。Phase 1完了後、直接Phase 3へ
- **User Stories (Phase 3–5)**: すべてPhase 1完了後に開始可能。US1/US2は完全に独立（異なるファイル）。US3（SKILL.md編集）はUS1・US2の成果物パスを参照するテキストを書くため、実務上はUS1・US2完了後に行うのが自然だが、技術的な依存はない
- **Polish (Phase 6)**: 全ユーザーストーリー完了後

### User Story Dependencies

- **User Story 1 (P1)**: Foundational完了後すぐ開始可能。他ストーリーへの依存なし
- **User Story 2 (P2)**: Foundational完了後すぐ開始可能。US1と並行実施可（別ファイル）
- **User Story 3 (P3)**: 技術的にはFoundational完了後すぐ開始可能。ただしUS1・US2が作るファイル名を`SKILL.md`の表に記載するため、実施順としてはUS1・US2の後が望ましい

### Parallel Opportunities

- T002・T003・T004（US1の3ファイル）は並列実行可能
- T005・T006・T007・T008（US2の4ファイル）は並列実行可能
- US1とUS2は全体としても並列実行可能（別ディレクトリ内の別ファイル）
- T009（US3）はT002〜T008の完了を待ってから実施するのが実務上安全（表に載せるファイル名の存在を前提とするため）

---

## Parallel Example: User Story 1 + User Story 2

```bash
# US1の3テンプレートを並行して作成:
Task: "product-backlog.md を作成"
Task: "sprint-backlog.md を作成"
Task: "increment.md を作成"

# US2の4テンプレートを並行して作成:
Task: "sprint-planning.md を作成"
Task: "daily-scrum.md を作成"
Task: "sprint-review.md を作成"
Task: "sprint-retrospective.md を作成"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1: Setup完了
2. Phase 2: タスクなし（スキップ）
3. Phase 3: User Story 1完了（作成物3テンプレート）
4. **STOP and VALIDATE**: 3ファイルを独立して確認
5. ここまでで、最も価値の高い作成物テンプレートが利用可能になる

### Incremental Delivery

1. Setup → 基盤完了
2. US1追加 → 独立検証 → 作成物テンプレート利用可能（MVP）
3. US2追加 → 独立検証 → イベントテンプレートも利用可能
4. US3追加 → 独立検証 → SKILL.mdから発見可能に
5. Polish → README更新、全検証コマンド実行、リグレッション確認

---

## Notes

- [P]タスク＝異なるファイル、依存なし
- [Story]ラベルはspec.mdのユーザーストーリーへのトレーサビリティを示す
- 各ユーザーストーリーは独立して完了・検証可能
- 論理的なまとまりごとにコミットする
- 各チェックポイントで独立検証してから次に進む
