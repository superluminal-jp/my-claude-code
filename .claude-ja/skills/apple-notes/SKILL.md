---
name: apple-notes
description: 同梱のJXA（osascript -l JavaScript）スクリプトを通じてmacOSのApple Notesを読み書きする — フォルダを確保する（任意で別フォルダのサブフォルダとして）、フォルダをJSONとして一覧表示する、idで1件のノートを取得する、ノートを作成する、既存ノートに追記する、名前付きブロックを1つその場で置き換える、SHA-256ハッシュゲートの下で条件付きでノートを上書き・削除する。Notes.appから内容を取り出す必要があるとき、安定したフォルダを用意する必要があるとき、あるいは文章をそこに記録する必要があるときに使う。
when_to_use: Apple NotesやmacOSのNotes.appに触れるあらゆる依頼 — 「私の<フォルダ>ノートには何が書いてある」「これをNotesに書いておいて」「今日の決定を追記して」「<トピック>のノートを探して」。Notesに対してAppleScriptやJXAを書く前にも、HTMLの本文モデルとmacOS専用という制約を先に把握するために読み込むこと。
---

# Apple Notes

このスキルに含まれるスクリプトを通じて、コマンドラインからNotes.appを操作する。

このスキルがプロジェクトスコープ・ユーザースコープのどちらにインストールされていても動くよう、スクリプトは絶対パスで実行する。

```bash
osascript -l JavaScript "${CLAUDE_SKILL_DIR}/scripts/list_notes.js" "Some Folder"
```

## 最初に述べておくべき2つの制約

**Notesにはフレームワークが存在しない。** EventKitに相当するものも、Contacts風のAPIも存在しない。Apple Events — AppleScript、あるいは同じディクショナリ上のJXA — が唯一サポートされているプログラム的経路である。

**macOS専用である。** ノートをプログラムから書き込むiOS側の経路は存在せず、完全に非対話的（ヘッドレス）な実行経路も存在しない — 詳細は後述の「最初の呼び出しの前に」を参照。もしワークフローがiPhoneから、あるいはCI上で動く必要があるなら、ノート側のその部分は実現できない。存在しない経路を前提に設計するのではなく、そう明言すること。

## 最初の呼び出しの前に

失敗の仕方が異なる、3つの独立した要件がある。いずれも非対話的には満たせない — ヘッドレス実行では、リトライするのではなくその旨を明言すること。

1. **オートメーション（TCC）。** 最初の `osascript` 呼び出しは、ターミナルアプリにNotesの制御を許可するかを尋ねるダイアログを表示する。これを承認するか、あらかじめ *システム設定 → プライバシーとセキュリティ → オートメーション → (ターミナルアプリ) → Notes* で許可しておく。エラー `-1743`、`-10004`、`-10827` はこれが拒否されたことを意味する。
2. **Claude Codeのパーミッション。** `Bash(osascript …)` の呼び出し自体がプロンプトを出す。ここではあえて何も事前承認されていない — これらのスクリプトはユーザー自身のノートを変更するためである。
3. **アクティブなGUI（Aqua）ログインセッション。** `osascript`/JXAは、ユーザーがMacのグラフィカルセッションにログインしているときにのみNotes.appを起動・制御できる — SSH経由や、そのセッションに紐づいていないLaunchAgent/LaunchDaemonから、あるいはログイン画面からは制御できない。エラー `-600`（「Application isn't running」）はTCCの拒否ではなくこれを意味する。すなわちNotesを起動して権限を尋ねることすらできなかったということである。ここにある各スクリプトは、他の処理を行う前にNotesを起動し、それが実行中であると報告するまで最大5秒待つため、単純なコールドスタート（Notesがまだ開かれていなかっただけ）は自動的に解消する — それでも呼び出し元に `-600` が届く場合は、GUIセッション自体が利用できないことを意味し、同じ呼び出しをリトライしても解決せず、別のマシンの環境であれば解決する類のものである。

各スクリプト自身のエラー出力は、これら3つのうちどれに該当するかを既に名指ししている — `-600`、`-1743`、`-10004`、`-10827` は、素の数値のまま残されるのではなく、上記の文章に変換される。

## プロパティの表面

`id`、`name`、`body`、`creation date`、`modification date`、`container`（そして `folder`：`name`、`id`、`container`）。このプロパティ一覧は、このマシン上でScript Editorのライブなスクリプティングディクショナリを調べた結果であり — Appleは現時点でこれについて閲覧可能なリファレンスページを公開していない（後述の「出典」を参照）。

`id` は安定したハンドルであり、`x-coredata://<store>/ICNote/p<N>` の形式である。不透明な値として扱うこと。

**`body` はテキストではなくHTMLである。** これに派生する事項は次の通り。

- リスト出力は、要求されない限り（`--with-body`）本文を省略する。
- `--plaintext` は読み取り用にマークアップを取り除く。これを本文に書き戻してはならない — 構造上、不可逆（lossy）である。
- 作成とボディ全体の上書きは、安全なMarkdownサブセット（後述）を受け付け、Notes互換のHTMLに変換する。
- Notesは表示されるタイトルを、別途設定された `name` プロパティからではなく、**本文の1行目**から導出する。`write_note.js` は作成時に1つの `<h1>` で始まる本文のみを供給し、`body` と一緒に `name` を設定することは決してない。そうするとNotesが重複したタイトル行を挿入してしまうためである。

クエリ言語は存在しない。フォルダを絞り込むということは、それを取得した上で呼び出し元側でフィルタすることを意味する。

## スクリプト

| スクリプト | 機能 |
|---|---|
| `scripts/ensure_folder.js` | 名前が一致する1つのフォルダを作成または再利用する。`--parent-id` を指定すれば、別のフォルダの直接の子として作成する |
| `scripts/list_notes.js` | 1つのフォルダ（またはid、あるいは `--folders`）をJSONとして返す |
| `scripts/write_note.js` | ノートを作成する、idを指定して既存ノートに追記する、名前付きブロックを置き換える、あるいは — ハッシュゲートの下で — 上書きまたは削除する |
| `scripts/note_write_guard.py` | `--overwrite-stdin`/`--delete` のチェックに使うSHA-256ハッシュゲートを計算する |

```bash
S="${CLAUDE_SKILL_DIR}/scripts"

# 送信先を確保する（何度リトライしても安全 — 完全一致する名前で照合し、
# 一致が複数あれば、どれか1つを選ぶのではなく失敗する）
osascript -l JavaScript "$S/ensure_folder.js" --name "Some Folder"

# 別のフォルダの中にサブフォルダを確保する
osascript -l JavaScript "$S/ensure_folder.js" --name "Sub Folder" --parent-id "<folder id>"

# 読み取り — 要求しない限り本文は省略される
osascript -l JavaScript "$S/list_notes.js" --folders
osascript -l JavaScript "$S/list_notes.js" "Some Folder"
osascript -l JavaScript "$S/list_notes.js" "Some Folder" --with-body
osascript -l JavaScript "$S/list_notes.js" --id "<id>" --plaintext

# 作成 — --text の1行目がNotes.appに表示されるタイトルになる
osascript -l JavaScript "$S/write_note.js" --folder "Some Folder" \
  --title "Sprint 7 Goal" --text "Cut checkout drop-off on mobile."

# 同名のフォルダが別々の場所に存在しうる場合（例えば、それぞれ独自の
# "Sprint 1" サブフォルダを持つ2つのプロジェクトなど）は --folder-id を優先する —
# --folder はアカウント全体を完全一致名で検索し、一致が複数あれば拒否する。
osascript -l JavaScript "$S/write_note.js" --folder-id "<folder id>" \
  --title "Sprint 1 Goal" --text "..."

# 追記（既存の内容は決して変更されない）
echo "Follow-up: check with design" \
  | osascript -l JavaScript "$S/write_note.js" --id "<id>" --append-stdin

# 名前付きの囲まれた領域をその場で置き換える — 最初の書き込みで作成され、
# それ以降の書き込みでは（重複せず）置き換えられる
echo "status: in progress" \
  | osascript -l JavaScript "$S/write_note.js" --id "<id>" --replace-block "status" --replace-stdin
```

### 名前付きブロックをその場で編集する

`--replace-block <name>`（`--id` に加えて、`--replace <text>` / `--replace-stdin` / `--replace-html <html>` のいずれかと併用）は、ノートの生のHTML本文の中から `--- <name> ---` … `---` で囲まれた領域を見つけ、その範囲だけを — それ以外の部分は一切変更せず — 置き換える。ブロックがまだ存在しない場合は（`ensure_folder.js` が既に取っているのと同じ「確保する」姿勢で）作成（追記）される。ちょうど1回存在する場合は置き換えられる。名前が複数箇所に一致する場合、あるいは囲みが閉じられていない場合は、推測するのではなく呼び出しを拒否する。これは機械が所有する構造化コンテンツをノート内で扱うために使うものであり — 人間の自由形式の文章を編集するためのものではない。それには追記（append）を使う。

`ensure_folder.js` は前後の空白をトリムし、空でない名前を要求する。一致が1件なら再利用され（`created: false`）、一致がなければ1件のフォルダが作成され（`created: true`）、一致が複数あれば書き込む前に失敗する。

`write_note.js` の作成モードは、`body` と一緒に `name` を設定することは決してない — 理由は前述の「プロパティの表面」を参照。安全なMarkdownサブセットの完全な文法（見出し、インラインスタイル、リスト、配置、コードブロック）と、Apple Eventsが再現できない形式についての明示的な拒否リスト（Block Quote、Highlight、Font family、Dashed List、Checklist）は、そのスクリプト内の `markdownToNotesHtml`/`validateNotesMarkdown` に実装されている — 文法を拡張する前にそれを読むこと。そこで受け入れられている各形式は、アプリ自体が対応しているかどうかではなく、公開されているApple EventsのHTML境界が実際に何を保持するかを基準に検証されているためである。

### 条件付きの上書きと削除

`--overwrite-stdin`（本文全体を置き換える）と `--delete`（ノートを削除する）はどちらも `--expect-hash <sha256>` を要求する — これは、直前に行った `--plaintext` の読み取りから計算した、ノートのプレーンテキスト本文のSHA-256ハッシュ値（16進数）である。

```bash
S="${CLAUDE_SKILL_DIR}/scripts"

CURRENT=$(osascript -l JavaScript "$S/list_notes.js" --id "<id>" --plaintext --field plaintext)
HASH=$(printf '%s' "$CURRENT" | python3 "$S/note_write_guard.py" hash)

# 本文全体の置き換え
echo "corrected content" | osascript -l JavaScript "$S/write_note.js" --id "<id>" \
  --overwrite-stdin --expect-hash "$HASH"

# 削除
osascript -l JavaScript "$S/write_note.js" --id "<id>" --delete --expect-hash "$HASH"
```

どちらの呼び出しの前にも、`write_note.js` はノートの*現在の*プレーンテキスト本文のハッシュを再計算し、それを `--expect-hash` と比較する。一致しない場合 — 呼び出し元が最後に読み取ってからノートが変更された場合 — 呼び出しは拒否される。**書き込みは一切行われず**、コマンドは非ゼロで終了する。これは権限チェックではなく楽観的並行性制御であり、数秒前にノートを読み取り、正しく意図的にそれを上書きしようとしている呼び出し元は問題なく通過する。これが防ぐのは、読み取りと書き込みの間にノートが横から変更されたことに気づかず、それを黙って上書きしてしまうことである。

**これは本物の、取り返しがつかないと感じられる能力である。** 追記や `--replace-block` とは異なり、誤った `--overwrite-stdin` や `--delete` の呼び出しは人間の書いた文章を破壊しうる。ハッシュゲートは、ノートを正しく読み取った上でそれでも誤った呼び出しを行う呼び出し元から保護するものではないし、そうすることもできない — Apple Eventが実際に何を送っているかをフックが検査することはできないからである。**どちらのフラグを呼び出す前にも、毎回、置き換える内容を — `--delete` の場合は削除対象のノートを — ユーザーに提示し、明示的な承認を得ること。** これはこのスクリプトが強制できる規約ではなく、操作する側の責任である。

削除されたノートは、UI経由の削除と同じ、Notes.appの「最近削除した項目」フォルダに移動し、完全に削除されるまでの一定期間はそこから復元可能なままである。Apple自身の情報源は正確な保持期間について一致しておらず（報告によれば30日から40日の幅がある）、特定の日数を確定した事実として述べないこと。

## ノートとリマインダーの紐付け

どちらのアプリも、GUIに表示される「リンクされた項目」チップのための公開APIを公開していない。またNotes自体の「リンクを追加」機能は、対象としてSafari、Podcasts、他のノートのみを文書化しており — Reminders はその中に含まれていない。ただしAppleは、代わりに公式の一方向のワークフローを提供している — macOSでは、ノート（またはノート内のテキスト）を選択して `File > Share > Reminders`（iOSでは「コピーを送信」）を使うことで、その内容を新しいリマインダーに変換できる。これには実際の制限がある。Notes → Reminders の方向にしか動かないこと、新しく作られたリマインダーは元のノートへの参照を一切保持しないこと、スクリプト／APIの経路がない手動のGUI操作のみであること、添付ファイルのあるノートでは正しく動かないことがあることである。独自のリンク付け規約を考案するのではなく、ユーザーをこちらへ案内すること。

## 結果の報告

トランスクリプトではなく答えを返すこと。フォルダ丸ごとのHTML本文は結果ではない。呼び出し元が尋ねた2行こそが結果である。スクリプトが失敗した場合は、そのエラーテキストをそのまま伝えること — 失敗が上記3つの要件のうち既知のApple Eventエラーコードに一致する場合、エラーテキストは既にありそうな原因を名指ししている。

## 出典

引用されているURLは、いずれも以前の出典から未確認のまま引き継いだものではなく、このスキルの構築時（2026-08-27）に現行のApple公式ドキュメントに照らして独自に再検証されたものである。

- Notesに対してAppleScript/Apple Events以外の公式フレームワークが存在しないこと — [Scriptable Applications – Apple Developer](https://developer.apple.com/library/archive/documentation/AppleScript/Conceptual/AppleScriptX/Concepts/scriptable_apps.html)
- オートメーションはmacOSの独立したプライバシーカテゴリであること — [Allow apps to control other apps on Mac – Apple Support](https://support.apple.com/guide/mac-help/mchl07817563/mac)
- Notesのテキストスタイル、フォント／色／サイズ、ハイライト、配置 — [Format notes on Mac](https://support.apple.com/guide/notes/format-notes-apd1955d3b21/mac)
- 「リンクを追加」で文書化されている対象（Safari、Podcasts、他のノート — Remindersはなし） — [Add links in Notes on Mac](https://support.apple.com/guide/notes/add-links-apde615d29c2/mac)
- 上記で使用した `note`/`folder` のプロパティの表面は、公開されているAppleのリファレンスページではなく、このマシン上のScript Editorのライブなスクリプティングディクショナリビューアーによるものである — [View an app's scripting dictionary in Script Editor](https://support.apple.com/guide/script-editor/view-an-apps-scripting-dictionary-scpedt1126/mac)

以下の2件は、「-600」のトラブルシューティング項目と、`list_notes.js`/`write_note.js` における `.whose()`/`.byId()` の回避が追加された際に、別のMacから両方の症状が報告されたことを受けて、2026-08-28にWeb検索で独自に検証されたものである。

- `-600` は「Application isn't running」を意味し、`osascript` が対象アプリを起動することすらできない場合（アクティブなGUIセッションがない、ハードンドランタイムによってオートメーションがブロックされているなど）にスローされる — [Error Number: -600 Application isn't running – MacScripter](https://www.macscripter.net/t/error-number-600-application-isn-t-running/70925)
- Notes.app自身のAppleScript/JXAディクショナリは、JXA一般の `.whose()`/`.byId()` サポートとは独立に、広く「不安定」であると報告されている（「中途半端なスクリプティングサポート……奇妙な挙動やエラーについての膨大な数の疑問」） — [Notes – JavaScript for Automation (JXA)](https://bru6.de/jxa/automating-applications/notes/)
