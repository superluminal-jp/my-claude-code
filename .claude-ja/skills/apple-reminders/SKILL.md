---
name: apple-reminders
description: macOS 上の Apple Reminders を、同梱の EventKit CLI を通じて読み書きする——Reminders リストを確保または JSON として一覧表示し、リマインダーを作成・更新・完了させ、識別子で 1 件を解決する。Reminders.app からリマインダーやタスクのデータが必要なとき、安定したリストを用意する必要があるとき、または項目を追加・完了させる必要があるときに使用する。
when_to_use: macOS 上で Apple Reminders または Reminders.app に触れるあらゆるリクエスト——「<list> には何が入っている？」「リマインダーを追加して」「完了にして」「まだ残っているリマインダーは？」。また、Reminders に対して EventKit・AppleScript・JXA のいずれかを書く前にも読み込み、プロパティの一覧・ビルド手順・権限モデルを先に把握しておくこと。
---

# Apple Reminders

Reminders.app を、このスキルに含まれる単一の Swift ファイルからビルドされた小さな EventKit CLI を通じて操作する。

## なぜここでは EventKit を使い、Notes では JXA を使うのか

Reminders には EventKit がある——Apple の公式フレームワークであり、`osascript` の出力から後で解析し直す必要がある Apple Event レコードではなく、型付けされ、クエリ可能なオブジェクトとしてリマインダーを返す経路である。Notes には同等のフレームワークが存在しないため、姉妹スキルである `apple-notes` は代わりに JXA を使用する。これは意図的な決定である。EventKit が AppleScript の経路より選ばれたのは、再解析が必要なテキストではなく、型付けされたオブジェクトを返すのがこの方式だけだからだ。

EventKit を使う代償はビルドステップと、異なる権限カテゴリが必要になることである。どちらも以下で扱うが、いずれも省略できない。

## 最初の呼び出しの前に

### 1. ツールをビルドする

```bash
bash "${CLAUDE_SKILL_DIR}/scripts/build.sh"   # prints the binary path; no-op if current
```

Xcode Command Line Tools（`xcode-select --install`）が必要。1 つのファイルに対する 1 回の `swiftc` 呼び出しのみで、パッケージマニフェストもロックファイルも存在しない。

**リンカフラグなしで手動ビルドしてはならない。** `build.sh` は `Info.plist` をバイナリの `__TEXT,__info_plist` セクションにリンクしており、これは構造上不可欠である。TCC は実行中のバイナリから使用目的の説明文を読み取るため、そのセクションを持たない素の Mach-O では権限ダイアログの出しようがない。このフラグを付けずにビルドすると「access not granted」で失敗し、ユーザーが許可を与える手段が一切なくなる——これはユーザーによる拒否とまったく同じに見えるビルド上の欠陥である。

### 2. Reminders へのアクセスを許可する

EventKit の権限は **Reminders** プライバシーカテゴリであり——`apple-notes` スキルが必要とする Automation とは*異なる*。両者は別個の許可であり、別個に拒否されうる。

初回実行時にダイアログが表示される。表示されない場合や拒否された場合は、*システム設定 → プライバシーとセキュリティ → リマインダー* で許可を与える。macOS 14 ではこれがフルアクセスと書き込み専用アクセスに分割された。このツールは読み取りを行うため、フルアクセスを要求する。

ビルドも許可付与も非対話的には実行できない。ヘッドレス実行の場合は、リトライするのではなくその旨を伝えること。`Bash` 呼び出し自体も Claude Code 内で確認を求める——ここでは意図的に何も事前承認されていない。

## プロパティの一覧

各リマインダーが持つのは: `id`, `externalId`, `name`, `body`, `completed`,
`completionDate`, `creationDate`, `modificationDate`, `dueDate`, `priority`,
`list`。

**2 つの識別子があり、互換ではない:**

- `id`（`calendarItemIdentifier`）——ローカルなものであり、項目がアカウント間を移動した際に維持される保証はない。
- `externalId`（`calendarItemExternalIdentifier`）——サーバー側から提供され、より安定しているが、繰り返しの項目については一意性が保証されない。

現在のセッションを超えて保持する参照には `externalId` を優先すること。

`completionDate` を手動で設定してはならない——`completed` が反転した際（どちら向きでも）に EventKit が自動的に設定する。

## コマンド

| コマンド | 動作 |
|---|---|
| `lists` | すべてのリマインダーリストを名前で列挙 |
| `ensure-list --name <name>` | 指定した名前と完全一致するリストを作成、または既存のものを再利用 |
| `list <name> [--open-only]` | 1 つのリストを JSON として取得 |
| `get <identifier>` | いずれかの識別子で 1 件のリマインダーを取得 |
| `create --list … --name …` | 1 件作成 |
| `update <identifier> …` | 1 件更新（新規作成はしない） |
| `complete <identifier> [--undo]` | 1 件を完了、または再オープン |

```bash
CLI="$(bash "${CLAUDE_SKILL_DIR}/scripts/build.sh")"

"$CLI" lists
"$CLI" ensure-list --name "Some List"
"$CLI" create --list "Some List" --name "Ship the login form" --due 2026-08-08
"$CLI" list "Some List" --open-only
"$CLI" get "<identifier>"
"$CLI" update "<identifier>" --name "Ship the login form (v2)"
"$CLI" complete "<identifier>"
"$CLI" complete "<identifier>" --undo
```

`update` は作成にフォールバックすることは決してない——解決できない識別子を渡した場合、黙って重複項目を新規作成するのではなく、呼び出し自体が失敗する。

`ensure-list` は前後の空白を除去し、空でない名前を要求する。リマインダー対応カレンダー全体を対象に、大文字小文字を区別する完全一致で照合する。一致が 1 件あればそれを再利用し（`created: false`）、一致がなければ設定済みのデフォルトリマインダーリストと同じソースに 1 つのリストを新規作成し（`created: true`）、一致が複数ある場合は書き込み前に失敗する。デフォルトのリマインダーリスト／ソースが設定されていない場合、このコマンドはアカウントを推測せずに停止する。

**削除コマンドは存在せず**、`update` が作成にフォールバックすることもない。どちらも助言的なものではなく構造上の制約である。リマインダーを削除すると、その唯一の記録が失われ、Notes の OS レベルの「最近削除した項目」フォルダのような、この CLI が頼れる復旧手段は存在しない。呼び出し元がリマインダーの削除を求めてきた場合は断り、Reminders.app での手動操作を案内すること。

## メモとリマインダーの紐付け

どちらのアプリも、GUI に表示される「リンクされた項目」のチップに対応する公開 API を提供していない。Apple は公式な一方向のワークフローを*用意している*——macOS では `File > Share > Reminders`（iOS では「コピーを送信」）により、メモの内容を新しいリマインダーに変換できる。ただし実際には制約がある。Notes → Reminders の一方向にしか動作しない、新しいリマインダーは元のメモへの参照を保持しない、スクリプトや API による経路がない手動の GUI 操作のみである、そして添付ファイル付きのメモでは正しく動作しないことがある。独自のリンク規約を考案するのではなく、ユーザーにはこの方法を案内すること。

## 結果の報告

実行記録ではなく、答えを返すこと。コマンドが失敗した場合は、3 つの前提条件——ビルド、Reminders の許可、Claude Code の Bash 権限——のうちどれが原因である可能性が高いかを述べること。

## 出典

引用した URL は、このスキルの構築時（2026-08-27）に、以前の出典から未検証のまま引き継ぐのではなく、現行の Apple ドキュメントに照らして個別に再検証したものである。

- `EKEventStore.requestFullAccessToReminders` と macOS 14 におけるフル／書き込み専用アクセスの分割 — [Apple Developer Documentation](https://developer.apple.com/documentation/eventkit/ekeventstore/requestfullaccesstoreminders(completion:))
- `calendarItemIdentifier` — [Apple Developer Documentation](https://developer.apple.com/documentation/eventkit/ekcalendaritem/calendaritemidentifier)
- `calendarItemExternalIdentifier` — [Apple Developer Documentation](https://developer.apple.com/documentation/eventkit/ekcalendaritem/calendaritemexternalidentifier)
- GUI にリンクが表示されている場合でも、EventKit 経由では `EKReminder.url` が nil として報告される — [Apple Developer Forums thread 128140](https://developer.apple.com/forums/thread/128140)
- 共有シートを使って別のアプリからリマインダーを追加する — [Add a reminder from another app – Apple Support](https://support.apple.com/guide/reminders/add-a-reminder-from-another-app-remn1f735fdc/mac)
- EventKit の公開 API にはリマインダーリストのグループ／セクション型が存在しないことを、Apple のエンジニアが確認 — [Apple Developer Forums thread 683611](https://developer.apple.com/forums/thread/683611)
