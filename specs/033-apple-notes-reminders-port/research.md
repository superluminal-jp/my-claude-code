# Phase 0 調査結果: Apple Notes / Reminders 自動操作スキル

Technical Context に `NEEDS CLARIFICATION` は残っていない — スコープ・自動操作技術・ドキュメント再検証方針は仕様策定前のセッション内で既に確定済みである。本ドキュメントは、その決定の根拠と、移植対象の挙動を現行 Apple 公式ドキュメントに対して独立に再検証した結果を記録する。

## 決定1: Notes の自動操作は JXA（AppleScript/Apple Events）一択

- **Decision**: `osascript -l JavaScript` 経由の JXA を Notes 自動操作の唯一の手段とする。
- **Rationale**: Notes.app には EventKit のような公式フレームワークが存在しない。Apple 自身のスクリプト対応アプリ一覧でも Calendar/Reminders は EventKit を持つ一方、Notes は Apple Events（AppleScript／JXA）以外の経路を持たない。他の手段（Shortcuts、Automator）はいずれも Apple Events の上に構築されているか、GUI 操作の言い換えに過ぎない。
- **Alternatives considered**: private ReminderKit 相当のフレームワークや SQLite ストア直接アクセス — OS アップデートで壊れるプライベート実装のため却下（移植元スキルの既定方針を踏襲）。
- **Source**: [Scriptable Applications – Apple Developer](https://developer.apple.com/library/archive/documentation/AppleScript/Conceptual/AppleScriptX/Concepts/scriptable_apps.html)（本セッションで再取得・再確認済み）。

## 決定2: Notes の `note`/`folder` プロパティ一覧は Script Editor の実機検査に基づく

- **Decision**: `id`, `name`, `body`, `creation date`, `modification date`, `container`（および `folder`: `name`, `id`, `container`）というプロパティ一覧は、引用可能な Apple ドキュメント URL ではなく、操作者自身のマシン上で Script Editor の辞書ビューアを用いて検査した結果として扱う。
- **Rationale**: 本セッションで再検証を試みたが、Apple は現在この辞書のブラウズ可能なリファレンスページを公開していない。
- **Source citation policy**: 出荷する SKILL.md は、このプロパティ一覧の出典を「Script Editor でのライブ辞書検査」と明記し、外部 URL を装った引用はしない（`spec.md` 前提条件に反映済み）。

## 決定3: Notes の書式サポートは「アプリが対応する書式」と「Apple Events 経由で確実に再現できる書式」を区別する

- **Decision**: Title/Heading/Subheading/Body、Bold/Italic/Underline/Strikethrough、色/サイズ、段落揃え、Highlight は Apple の Notes フォーマットガイドで確認済み。Bulleted/Numbered/Dashed/Checklist リストは別ページ（リストガイド）の対象であり、本セッションでは書式ページ単体からは未確認。Block Quote、Highlight、フォントファミリー変更、Dashed List、Checklist は、Apple Events の HTML 本文境界を通じて確実に再現できないという移植元スキルの独自の実機検証結果（三者三様の使い捨てノートによる直接実験）に基づき、引き続き未対応として拒否する。
- **Rationale**: 「アプリの UI が対応している」ことと「自動操作のHTML境界で確実に再現できる」ことは別の主張であり、両者を混同して引用してはならない。
- **Source**: [Format notes on Mac – Apple Support](https://support.apple.com/guide/notes/format-notes-apd1955d3b21/mac)（アプリ側の対応書式について再確認済み。リスト書式は別ページのため未取得 — 実装時に該当ページを別途確認する）。

## 決定4: Notes「最近削除した項目」の保持期間は数値を断定しない

- **Decision**: 削除済みノートは OS レベルの「最近削除した項目」で一定期間復元可能だが、その正確な日数（30日 vs 40日）は Apple 自身の情報源間でも一致しないため、出荷ドキュメントでは具体的な日数を保証として書かない。
- **Rationale**: 本セッションでの再検証時、複数の Apple 系情報源が矛盾する日数を報告しており、単一の権威あるライブページを直接確認できなかった。

## 決定5: Reminders の自動操作はコンパイル済み Swift/EventKit CLI（ビルド不要な AppleScript 案は却下）

- **Decision**: `swiftc` でビルドする単一ファイルの EventKit CLI（`remind-cli` 相当）を Reminders 自動操作の手段とする。ユーザーとの事前合意により、ビルド不要な AppleScript 版という選択肢は明示的に却下した。
- **Rationale**: EventKit は型付きオブジェクトを返し、AppleScript では取得できないフィールド（繰り返しルール、サーバー側の安定識別子、優先度）を公開する。`EKEventStore.requestFullAccessToReminders(completion:)` と、macOS 14 で導入されたフルアクセス/書き込み専用の権限区分は、本セッションで現行ドキュメントに対し再確認済み。
- **Alternatives considered**: AppleScript 版 Reminders CLI — ビルド不要という利点はあるが、型付きフィールドと安定識別子（`calendarItemExternalIdentifier`）を失う。ユーザーはビルド手順の負担よりもこれらのフィールドを優先すると明示的に判断した。
- **Source**: [`requestFullAccessToReminders(completion:)` – Apple Developer Documentation](https://developer.apple.com/documentation/eventkit/ekeventstore/requestfullaccesstoreminders(completion:))

## 決定6: `Info.plist` を `__TEXT,__info_plist` にリンクするビルド手順は必須

- **Decision**: `build.sh` は `Info.plist` をバイナリの `__TEXT,__info_plist` セクションへリンクするリンカフラグを含める。このフラグを欠いたビルドは、TCC が権限ダイアログの説明文を読み取れず、「アクセスが許可されていない」というユーザーが解消不可能な状態を生む。
- **Rationale**: 移植元スキルが明記する既知の落とし穴であり、独立の再検証は行っていない（Apple の公開ドキュメントに直接の記載はなく、実機でのビルド経験に基づく実務知識）。実装時に手順として明記し、手動ビルドを推奨しない。

## 決定7: `calendarItemIdentifier` と `calendarItemExternalIdentifier` の安定性差は再確認済み・ニュアンスに注意

- **Decision**: クロスアプリ用途や外部参照には `calendarItemExternalIdentifier`（サーバー提供、より安定）を用い、`calendarItemIdentifier`（ローカル、アカウント間移動で不安定）は用いない、という区別を維持する。
- **Rationale**: 公式 API ドキュメントの文言自体は簡潔（「カレンダーアイテムの一意識別子」「カレンダーサーバーが提供する外部識別子」）であり、「アカウント移動で永続しない」「繰り返しアイテムで一意性が保証されない」という詳細な注意書きは、公式ドキュメントの警告文というよりコミュニティ・フォーラムの報告に基づく。この区別自体は現行の API 定義と矛盾しない。
- **Source**: [`calendarItemIdentifier`](https://developer.apple.com/documentation/eventkit/ekcalendaritem/calendaritemidentifier), [`calendarItemExternalIdentifier`](https://developer.apple.com/documentation/eventkit/ekcalendaritem/calendaritemexternalidentifier)

## 決定8: `completionDate` は `isCompleted` 切り替えに応じてフレームワークが自動設定する

- **Decision**: `complete`/`--undo` 操作は `isCompleted` の切り替えのみを行い、`completionDate` を直接設定しない。
- **Rationale**: 本セッションで再確認済み — `isCompleted` を true にすると `completionDate` が現在時刻に設定され、false に戻すと `nil` に戻るという双方向の同期がドキュメント化されている。
- **Source**: EventKit 公式ドキュメント（`EKReminder.completionDate` / `isCompleted` の関係、本セッションで再確認）。

## 決定9: EventKit の公開 API にリマインダーリストのグループ／セクション型は存在しない

- **Decision**: リストのグルーピング機能は提供しない。
- **Rationale**: 現行ドキュメントでも `EKReminder` にセクション/グループを表す公開型は存在しないことを再確認した（Reminders.app 自体は iOS 17 以降セクションに対応しているにもかかわらず）。プライベート API・SQLite ストア直接アクセスは、他の未到達領域（タグ、サブタスク）と同じ理由で採用しない。

## 決定10: ノート・リマインダー間の自動リンク機構は実装しない（Apple 公式の手動共有操作を案内）

- **Decision**: 双方向に解決可能な独自のクロスアプリ識別子リンク規約は実装しない。代わりに、Apple 公式の手動共有操作（macOS: `ファイル > 共有 > Reminders`、iOS: 「コピーを送信」）を SKILL.md の運用ガイダンスとして案内する。
- **Rationale**: ユーザーとの合意により、公式な双方向リンク機構が存在しないことが確認された時点で、独自機構よりも公式操作への案内を優先する方針を採用した（詳細は `spec.md` 前提条件を参照）。
- **Findings**:
  - Notes の「リンクを追加」機能は Safari・Podcasts・他のノートのみを対象とし、Reminders は含まれない（[Add links in Notes on Mac – Apple Support](https://support.apple.com/guide/notes/add-links-apde615d29c2/mac)、本セッションで再取得・再確認）。
  - `EKReminder.url`（`EKCalendarItem` 継承）は、Reminders アプリの画面上でリンクが表示されている場合でも、EventKit 経由で読み取ると一貫して `nil` になることが長年報告されている（[EKReminder URL property is nil – Apple Developer Forums](https://developer.apple.com/forums/thread/128140)）。
  - 一方、`ファイル > 共有 > Reminders`（macOS）／「コピーを送信」（iOS）という、ノート内容を新規リマインダーへ複製する公式な手動操作が存在する（[Add a reminder from another app – Apple Support](https://support.apple.com/guide/reminders/add-a-reminder-from-another-app-remn1f735fdc/mac)）。ただしこれは一方向（ノート→リマインダー）のコピーであり、複製後のリマインダーに元のノートへの参照は残らず、GUI操作専用でスクリプト/APIからは呼び出せず、添付ファイルを含むノートでは正しく動作しない場合があると報告されている。
- **Alternatives considered**: 独自の識別子マーカー規約（移植元スキルの設計、本文中に `[[reminder:<id>]]` 等を埋め込み、スクリプトで解決）— 技術的には実装可能だが、ネイティブな機能ではなく保守コストを伴う独自規約であるため、明確な必要性が示されない限り採用しない。
