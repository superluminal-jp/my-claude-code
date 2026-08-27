# コントラクト: Reminders CLI（EventKit ベース、`build.sh` でビルド）

対応要求: FR-002, FR-003, FR-005〜FR-007, FR-010, FR-011, FR-016, FR-018。ビルド: `bash build.sh`（バイナリパスを標準出力に返す。ビルド済みなら no-op）。

## `lists`

```bash
"$CLI" lists
```

全リマインダーリストを名前とともに返す。

## `ensure-list --name <name>`

対応要求: FR-002, FR-003。`notes-ensure-folder.md` と同じ存在保証規則（完全一致、0件で作成、1件で再利用、2件以上で失敗）を、Reminders カレンダーに対して適用する。既定のリマインダー送信先アカウントが未設定の場合は推測せず停止する。

出力: `{"id": "<list-id>", "name": "<name>", "source": "<source-name>", "created": true}`

## `list <name> [--open-only]`

対応要求: FR-006。指定リストのリマインダーを JSON 配列で返す。`--open-only` は完了済みを除外する。

## `get <identifier>`

対応要求: FR-007。`id`（`calendarItemIdentifier`）・`externalId`（`calendarItemExternalIdentifier`）のいずれでも解決する。単一リマインダーの全フィールドを返す。

## `create --list <name> --name <name> [--due <date>] [--body <text>]`

対応要求: FR-005。指定リストにリマインダーを作成する。`--list` は完全一致名。

## `update <identifier> [--name ...] [--due ...] [--body ...]`

対応要求: FR-010。指定した識別子が既存のいずれのリマインダーにも一致しない場合、新規作成せず失敗する。

## `complete <identifier> [--undo]`

対応要求: FR-011。`isCompleted` を切り替える。`completionDate` は呼び出し側から直接設定しない — EventKit が自動的に設定/クリアする（`data-model.md` 参照）。

## 削除

**提供しない**（FR-016）。削除要求を受けた呼び出し元は、Reminders アプリ内での手動削除を案内する。この CLI に `delete` サブコマンドを追加してはならない。

## 識別子の使い分け（FR-018）

| 用途 | 使う識別子 |
|---|---|
| 同一セッション内の `get`/`update`/`complete` 呼び出し | `id` で十分（どちらでも解決可能） |
| セッションをまたいで保存・再利用する参照、外部への提示 | `externalId` を優先する（`id` はアカウント/カレンダー移動で永続しない場合がある） |

## 前提条件（FR-017 と連動）

1. `build.sh` が未実行、または `Info.plist` リンクを欠くビルドが行われていた場合、原因を名指しして報告する（「コマンドラインツールが未ビルド」）。
2. Reminders プライバシー権限（フルアクセス）が未許可の場合、その旨と許可場所（システム設定 → プライバシーとセキュリティ → リマインダー）を報告する。
3. ハーネス自体のツール呼び出し許可が拒否された場合はその旨を報告する。

いずれも非対話的には解決できない（ヘッドレス実行では再試行せず報告する）。
