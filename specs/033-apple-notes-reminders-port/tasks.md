---

description: "Task list for feature implementation"
---

# Tasks: Apple Notes / Reminders 自動操作スキル

**Input**: Design documents from `/specs/033-apple-notes-reminders-port/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md（すべて存在）

**Tests**: 本リポジトリの `coder` スキルは TDD（失敗するテスト→実装→リファクタ）を必須とする。自動テスト可能なのは Apple Events/EventKit を呼ばない純粋ロジック（`note_write_guard.py` のハッシュゲート、`write_note.js` の Markdown→HTML変換・書式拒否・名前付き区画分割ロジック）に限られる（`plan.md` Technical Context 参照）。それ以外の実際の自動操作呼び出しは `quickstart.md` による実機検証で担保する。

**Organization**: `spec.md` のユーザーストーリー（P1〜P4）ごとにフェーズ分割する。

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 並行実行可能（別ファイル・依存なし）
- **[Story]**: 対応するユーザーストーリー（US1〜US4）
- ファイルパスは正確に記載する

## Path Conventions

単一プロジェクト構成（`plan.md` Structure Decision 参照）:

```text
.claude/skills/apple-notes/{SKILL.md, scripts/}
.claude/skills/apple-reminders/{SKILL.md, scripts/}
tests/
```

---

## Phase 1: Setup

**Purpose**: ディレクトリ構造と SKILL.md の骨格を用意する

- [X] T001 `.claude/skills/apple-notes/scripts/`, `.claude/skills/apple-reminders/scripts/`, `tests/` のディレクトリ構造を作成する
- [X] T002 [P] `.claude/skills/apple-notes/SKILL.md` の骨格を作成する（frontmatter、Notes の2制約セクション — フレームワーク不在／macOS専用、権限前提セクションの雛形、スクリプト一覧表の雛形）
- [X] T003 [P] `.claude/skills/apple-reminders/SKILL.md` の骨格を作成する（frontmatter、`docs/adr/0013-eventkit-for-reminders-automation.md` に基づく EventKit 選定の説明、ビルド手順＋2つの権限カテゴリのセクションの雛形、コマンド一覧表の雛形）

---

## Phase 2: Foundational（すべてのユーザーストーリーの前提）

**Purpose**: 両スキルの土台となる、どのストーリーからも参照される基盤

**⚠️ CRITICAL**: このフェーズ完了までユーザーストーリーの実装に着手しない

- [X] T004 [P] `.claude/skills/apple-reminders/scripts/Info.plist` を作成する（Reminders 権限ダイアログ用の usage description）
- [X] T005 [P] [TEST-FIRST] `tests/test_note_write_guard.py` を作成する — `contracts/note-write-guard.md` の `hash`/`decide` 契約に基づき、ハッシュの決定性・`decide` の proceed/refuse 判定・境界入力（空文字列、マルチバイト文字）を検証するテストを書く。この時点では `note_write_guard.py` が存在しないため失敗すること（Red）
- [X] T006 [P] `tests/run-note-write-guard.sh` を作成する（`python3 -m unittest discover -s tests -p "test_note_write_guard.py" -v` を実行するラッパー、`tests/run-mcp-startup.sh` 等の既存慣習に倣う）
- [X] T007 `.claude/skills/apple-notes/scripts/note_write_guard.py` を実装する（`hash`/`decide` サブコマンド、標準ライブラリのみ、`osascript` を呼ばない）— T005 のテストを通す（Green）。依存: T005
- [X] T008 `.claude/skills/apple-reminders/scripts/build.sh` を実装する（`swiftc` でビルドし、`Info.plist` を `__TEXT,__info_plist` へリンク、バイナリパスを標準出力へ、ビルド済みなら no-op）。依存: T004
- [X] T009 `.claude/skills/apple-reminders/scripts/main.swift` の骨格を実装する（`EKEventStore.requestFullAccessToReminders` による権限チェック、サブコマンド振り分け — `lists`/`ensure-list`/`list`/`get`/`create`/`update`/`complete` はいずれも「未実装」で非ゼロ終了するスタブ）。依存: T008

**Checkpoint**: 基盤完成 — ユーザーストーリーの実装に着手できる

---

## Phase 3: User Story 1 - 保存先を用意し、何かを書き留める (Priority: P1) 🎯 MVP

**Goal**: フォルダ／リストを冪等に用意し、ノート／リマインダーを1件作成できる

**Independent Test**: `quickstart.md` の「US1」セクション（`ensure_folder.js`/`ensure-list` を2回呼び、`created` が1回目 true・2回目 false になることと、作成したノート/リマインダーが読み戻せることを確認）

### Tests for User Story 1（TDD、純粋ロジックのみ）

- [X] T010 [P] [US1] [TEST-FIRST] `tests/test_note_body_conversion.js` を作成する — 安全な Markdown サブセット→HTML変換、および非対応書式（チェックリスト、引用ブロック、ハイライト、フォントファミリー、ダッシュ付きリスト）の明示的拒否を検証するテストを、`contracts/notes-write.md` モード1と `spec.md` エッジケースに基づき書く。変換ロジックがまだ存在しないため失敗すること（Red）
- [X] T011 [P] [US1] `tests/run-note-body-conversion.sh` を作成する（`node tests/test_note_body_conversion.js` を実行するラッパー。JXA は `require()`/`module.exports` を持たないため `osascript -l JavaScript` では内部関数を個別に呼べず、Node が必要 — `plan.md` Testing 参照。実行時のみの開発ツールであり、本番の呼び出し経路は `osascript -l JavaScript write_note.js ...` のまま変わらない）

### Implementation for User Story 1

- [X] T012 [US1] `.claude/skills/apple-notes/scripts/ensure_folder.js` を実装する（`contracts/notes-ensure-folder.md`: `--name`/`--parent-id`、完全一致0件で作成・1件で再利用・2件以上で失敗）
- [X] T013 [US1] `.claude/skills/apple-notes/scripts/write_note.js` に Markdown→HTML変換・書式拒否ロジックと作成モード（`--folder`/`--folder-id`, `--title`, `--text`/`--text-stdin`。`body` のみで `note` を構築し `name` は設定しない、タイトル重複除去規則）を実装する。`contracts/notes-write.md` モード1、`data-model.md` Note エンティティに基づく。T010 のテストを通す（Green）。依存: T010, T012
- [X] T014 [US1] `.claude/skills/apple-reminders/scripts/main.swift` に `lists` と `ensure-list` サブコマンドを実装する（`contracts/reminders-cli.md`。`lists` は US に個別の依存がない軽量な列挙のため、隣接する `ensure-list` と合わせて実装）。依存: T009
- [X] T015 [US1] `.claude/skills/apple-reminders/scripts/main.swift` に `create` サブコマンドを実装する（`--list`, `--name`, `--due`, `--body`。`contracts/reminders-cli.md`）。依存: T014
- [X] T016 [US1] `ensure_folder.js`、`write_note.js` 作成モード、Reminders `ensure-list`/`create` を `.claude/skills/apple-notes/SKILL.md` と `.claude/skills/apple-reminders/SKILL.md` に文書化する（使用例、FR-017 に基づく権限前提の記載）。依存: T013, T015

**Checkpoint**: US1 は単独で機能・検証可能（MVP）

---

## Phase 4: User Story 2 - 中身を読み戻す (Priority: P2)

**Goal**: フォルダ／リストの一覧取得、単一アイテムの取得ができる

**Independent Test**: `quickstart.md` の「US2」セクション（`--with-body` の有無で本文の有無が切り替わること、`--open-only` が完了済みを除外することを確認）

### Implementation for User Story 2

- [X] T017 [US2] `.claude/skills/apple-notes/scripts/list_notes.js` を実装する（フォルダ一覧、`--id` 単一取得、`--folders`、`--with-body`、`--plaintext`、`--field`。`contracts/notes-list.md`）。依存: T001
- [X] T018 [US2] `.claude/skills/apple-reminders/scripts/main.swift` に `list --open-only` と `get` サブコマンドを実装する（`contracts/reminders-cli.md`）。依存: T009
- [X] T019 [US2] `list_notes.js` と Reminders `list`/`get` を両 SKILL.md に文書化する（既定で本文を省略する挙動、`--field` のスクリプト連携用途）。依存: T017, T018

**Checkpoint**: US2 は単独で機能・検証可能

---

## Phase 5: User Story 3 - 既存内容を巻き添え被害なく更新する (Priority: P3)

**Goal**: ノートへの追記、名前付き区画のその場置換、リマインダーの更新・完了ができる

**Independent Test**: `quickstart.md` の「US3」セクション（追記が既存内容を保持すること、名前付き区画の置換が区画外に影響しないこと、未解決の識別子への更新が失敗すること）

### Tests for User Story 3（TDD、純粋ロジックのみ）

- [X] T020 [P] [US3] [TEST-FIRST] `tests/test_note_body_conversion.js` に名前付き区画の分割・置換ケース（0件で作成/追記、1件で置換、2件以上または区切り不正で拒否）を追加する。`data-model.md` Named Block の状態遷移に基づく。実装前のため失敗すること（Red）。実装過程で `findBlock` が JXA専用の `fail()`（`$` グローバル依存）を呼んでいたため Node 下で `ReferenceError` になる移植バグを検出・修正（`throw new Error(...)` に統一、`formatError` と同じ形へ）

### Implementation for User Story 3

- [X] T021 [US3] `.claude/skills/apple-notes/scripts/write_note.js` に追記モード（`--id --append`/`--append-stdin`/`--append-html`）を実装する。依存: T013。（T013 の一括移植時に既に実装済みであることを確認）
- [X] T022 [US3] `.claude/skills/apple-notes/scripts/write_note.js` に `--replace-block` 名前付き区画置換モードを実装する（`contracts/notes-write.md` モード3）。T020 のテストを通す（Green）。依存: T020, T021。（T013 の一括移植時に既に実装済みであることを確認。findBlock のバグ修正は T020 で実施済み）
- [X] T023 [US3] `.claude/skills/apple-reminders/scripts/main.swift` に `update` サブコマンドを実装する（識別子が未解決なら新規作成せず失敗。`contracts/reminders-cli.md`）。依存: T009
- [X] T024 [US3] `.claude/skills/apple-reminders/scripts/main.swift` に `complete`/`--undo` サブコマンドを実装する（`isCompleted` の切り替えのみ、`completionDate` は直接設定しない。`contracts/reminders-cli.md`、`data-model.md` 決定8）。依存: T023
- [X] T025 [US3] 追記・区画置換・`update`・`complete` を両 SKILL.md に文書化する。依存: T022, T024

**Checkpoint**: US3 は単独で機能・検証可能

---

## Phase 6: User Story 4 - ノートの全内容を安全に置き換える・削除する (Priority: P4)

**Goal**: 整合性チェック付きの全内容上書き・削除（ノートのみ）、リマインダー削除の明示的な非提供

**Independent Test**: `quickstart.md` の「US4」セクション（古いハッシュでの上書きが拒否され内容が変化しないこと、正しいハッシュでの上書きが成功すること、Reminders CLI に削除コマンドが存在しないこと）

### Implementation for User Story 4

- [X] T026 [US4] `.claude/skills/apple-notes/scripts/write_note.js` に `--overwrite-stdin` モードを実装する（`note_write_guard.py` の `decide` サブコマンドをサブプロセス呼び出しで連携。`contracts/notes-write.md` モード4）。依存: T007, T022。（T013 の一括移植時に既に実装済みであることを確認。`decide` の JSON/非ゼロ終了への対応は `guardDecide()` を修正済み）
- [X] T027 [US4] `.claude/skills/apple-notes/scripts/write_note.js` に `--delete` モードを、同じハッシュゲート連携で実装する（モード5）。依存: T026。（T013 の一括移植時に既に実装済みであることを確認）
- [X] T028 [US4] FR-015 の運用者責務（上書き・削除呼び出し前に、置き換え内容または削除対象を人間に提示し明示的承認を得ること）を `.claude/skills/apple-notes/SKILL.md` に明記する。依存: T027
- [X] T029 [US4] `.claude/skills/apple-reminders/scripts/main.swift` のサブコマンド振り分けに `delete` が存在せず、未知のサブコマンドとして拒否されることを確認し（FR-016 の構造的な非提供）、`.claude/skills/apple-reminders/SKILL.md` にリマインダー削除は手動操作へ案内する旨を明記する。依存: T009

**Checkpoint**: US4 は単独で機能・検証可能 — 4つのユーザーストーリーすべてが完成

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: 個別のユーザーストーリーに属さない、全体に関わる仕上げ

- [X] T030 [P] Apple 公式の Notes→Reminders 手動共有操作(macOS: `ファイル > 共有 > Reminders`、iOS:「コピーを送信」)を、一方向・元ノートへの参照が残らない・GUI専用・添付ファイルでの不具合報告という制約とともに、両 SKILL.md へ運用ガイダンスとして記載する(`research.md` 決定10)
- [X] T031 [P] `research.md` で再検証済みの Apple 公式ドキュメント URL(Notes 書式ガイド、Add Links ガイド、EventKit 権限ドキュメント、`calendarItemIdentifier`/`calendarItemExternalIdentifier`、`completionDate` の挙動)を出典として両 SKILL.md に記載する。`specs/033-*/` へのリンクは含めない(Intermediate-Artifact Isolation)。実装中、`spec.md`/`plan.md`/`contracts/`/`research.md` への裸の参照が SKILL.md 3箇所・スクリプトコメント7箇所に残っていたのを検出し、すべて地の文または削除に置き換えて是正
- [X] T032 [P] 両スキルのコード・SKILL.md のいずれにも `apple-scrum-files`、`project_registry.py`、`scrum_block.py`、`flow_metrics.py` への参照が存在しないことを grep で確認する(FR-019 の Scrum成果物除外の検証)。クリーン(0件)を確認
- [X] T033 `tests/run-note-write-guard.sh` と `tests/run-note-body-conversion.sh` を実行し、両方が成功することを確認する。14件・38件、計52件すべて成功
- [X] T034 `quickstart.md` を実機の Mac 上で最初から最後まで実行し(US1〜US4 のすべての受け入れシナリオ、同時編集による上書き拒否ケースを含む)、結果を記録する。両権限(Automation/Reminders)は既に許可済みで、実データに対して全シナリオ成功 — フォルダ/リストの冪等性、本文既定省略、追記の非破壊性、名前付き区画の作成/置換、リマインダーの更新/完了/取り消し、古いハッシュでの上書き拒否(内容不変)、正しいハッシュでの上書き/削除成功、削除済みノートが同一IDで解決可能(最近削除した項目への移動を裏付け)、Reminders CLI に delete が存在しないことを確認。副作用: Notes に「QuickstartTest」フォルダ、Reminders に「QuickstartTest」リストと1件のリマインダーが実データとして残存(フォルダ/リストの削除操作は本機能の対象外のため手動削除が必要 — ユーザーへ報告済み)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: 依存なし — 即座に開始可能
- **Foundational (Phase 2)**: Setup 完了に依存 — 全ユーザーストーリーをブロックする
- **User Stories (Phase 3–6)**: いずれも Foundational 完了に依存。US1〜US4 は互いに独立しており、並行または任意の順で進められる（ただし US1 が MVP のため優先度順を推奨）
- **Polish (Phase 7)**: 実施したいすべてのユーザーストーリーの完了に依存

### User Story Dependencies

- **US1 (P1)**: Foundational 完了後に開始可能。他ストーリーへの依存なし
- **US2 (P2)**: Foundational 完了後に開始可能。他ストーリーへの依存なし（US1 で作成したノート/リマインダーを読み戻す検証に使うのは自然だが、コード上の依存ではない）
- **US3 (P3)**: Foundational 完了後に開始可能。`write_note.js` への追記・区画置換モード追加は T013（US1）に依存するファイル依存はあるが、機能としては US1 の完了を待たずに実装できる
- **US4 (P4)**: Foundational（T007 の `note_write_guard.py`）と US3（T022、同じファイルへのモード追加）に依存

### Within Each User Story

- テスト（該当する場合）は実装前に書き、失敗を確認する
- 純粋ロジック（変換・検証・ハッシュゲート）を先に実装し、その後 Apple Events/EventKit 呼び出しモードを重ねる
- 各ストーリーの最後に SKILL.md 文書化タスクを置く（Drift Detection — 契約の変更と同じ変更で文書を更新する）

### Parallel Opportunities

- T002, T003（別ファイルの SKILL.md 骨格）
- T004, T005, T006（別ファイル、Foundational 内）
- T010, T011（別ファイル、US1 テスト）
- T017（Notes）と T018（Reminders）は別ファイルのため並行可能
- T030, T031, T032（Polish、いずれも別ファイルまたは独立した確認作業）

---

## Parallel Example: User Story 1

```bash
# US1 のテストを並行して用意する:
Task: "tests/test_note_body_conversion.js を作成し、Markdown→HTML変換と書式拒否を検証するテストを書く"
Task: "tests/run-note-body-conversion.sh を作成する"

# US1 の Notes 側と Reminders 側の実装は別ファイルのため並行できる:
Task: "ensure_folder.js を実装する"
Task: "main.swift に ensure-list サブコマンドを実装する"
```

---

## Implementation Strategy

### MVP First (User Story 1 のみ)

1. Phase 1: Setup を完了する
2. Phase 2: Foundational を完了する（すべてのストーリーをブロックするため必須）
3. Phase 3: User Story 1 を完了する
4. **停止して検証**: `quickstart.md` の US1 セクションで単独に確認する
5. 必要ならここでいったん区切ってレビューを受ける

### Incremental Delivery

1. Setup + Foundational → 基盤完成
2. US1 追加 → 単独検証 → MVP
3. US2 追加 → 単独検証
4. US3 追加 → 単独検証
5. US4 追加 → 単独検証 — 最もリスクが高いため最後
6. Polish → 出典記載・Scrum非依存の確認・quickstart 全体検証

---

## Notes

- [P] タスク = 別ファイル・依存なし
- [Story] ラベルはユーザーストーリーへのトレーサビリティのため付与する
- 各ユーザーストーリーは単独で完成・検証可能であること
- 実装前にテストが失敗することを確認する（該当タスクのみ）
- 論理的な単位ごとにコミットする
- 各チェックポイントで一度立ち止まり、そのストーリー単独の動作を検証する
- 避けるべきこと: 曖昧なタスク、同一ファイルへの競合、ストーリー間の独立性を壊す依存
