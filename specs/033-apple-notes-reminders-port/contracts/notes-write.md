# コントラクト: `write_note.js`（作成・追記・区画置換・ハッシュゲート付き上書き/削除）

対応要求: FR-004, FR-008, FR-009, FR-012〜FR-016。呼び出し形は用途ごとに異なる。以下は各モードの契約。

## モード1: 作成 (`--folder <name>` または `--folder-id <id>`)

```bash
osascript -l JavaScript write_note.js --folder "<name>" --title "<title>" --text "<markdown>"
# または: echo "<markdown>" | write_note.js --folder-id "<id>" --title "<title>" --text-stdin
```

- `--folder <name>` は完全一致名でアカウント全体を検索し、複数一致で拒否する。`--folder-id <id>` は曖昧さがないため優先すべき（同名フォルダが複数プロジェクトに存在しうる場合）。
- 入力は FR-012, FR-013 に従い、書き込み前に全体を検証・変換する。対応していない書式（表: `data-model.md` は参照しないが、`spec.md` エッジケースに列挙 — チェックリスト、引用ブロック、ハイライト、フォントファミリー、ダッシュ付きリスト）が含まれる場合、どの書式が非対応かを名指しして、何も書き込まずに失敗する。
- 成功時、`body` の1行目からタイトルが導出される（`name` プロパティは設定しない — `data-model.md` 参照）。

**出力**: 作成されたノートの `id` を含む JSON。

## モード2: 追記 (`--id <id> --append` / `--append-stdin` / `--append-html`)

```bash
echo "<text>" | write_note.js --id "<id>" --append-stdin
```

既存の `body` の末尾に、変換済みコンテンツを追加する。既存内容は一切変更しない（FR-008）。

## モード3: 名前付き区画の置換 (`--id <id> --replace-block <name>`)

```bash
echo "<text>" | write_note.js --id "<id>" --replace-block "<name>" --replace-stdin
```

`data-model.md` の Named Block 状態遷移に従う: 0件なら作成（追記）、1件なら置換、2件以上または区切り不正なら拒否。区画外の内容は変更しない（FR-009）。

## モード4: ハッシュゲート付き上書き (`--id <id> --overwrite-stdin --expect-hash <sha256>`)

```bash
CURRENT=$(list_notes.js --id "<id>" --plaintext --field plaintext)
HASH=$(printf '%s' "$CURRENT" | note_write_guard.py hash)
echo "<new content>" | write_note.js --id "<id>" --overwrite-stdin --expect-hash "$HASH"
```

- 実行前に `note_write_guard.py`（`contracts/note-write-guard.md` 参照）で現在のプレーンテキスト本文のハッシュを再計算し、`--expect-hash` と比較する。
- 不一致 → **何も変更せず**、非ゼロ終了コードで失敗し、「読み取り後にノートが変化した」ことを示すメッセージを返す（FR-014）。
- 一致 → 本文全体を新しい内容で置き換える（FR-004 の変換規則を適用）。
- **呼び出し前提条件（FR-015、スクリプトは強制できない）**: 置き換え内容そのものを人間に提示し、明示的な承認を得てから呼び出すこと。SKILL.md はこれを運用者責務として明記する。

## モード5: ハッシュゲート付き削除 (`--id <id> --delete --expect-hash <sha256>`)

上書きと同じハッシュゲート規則。一致すればノートを削除する（OS の「最近削除した項目」へ移動、即時完全削除ではない）。不一致なら何もしない（FR-014）。呼び出し前提条件はモード4と同じ（FR-015）。

## リマインダー側との非対称性

Reminders には対応する削除モードは存在しない（FR-016）。これは Notes 側の「最近削除した項目」に相当する復元機構が Reminders になく、削除の取り消しをシステムが保証できないためであり、実装上の手抜きではなく意図的な非対称性である（`spec.md` 前提条件）。
