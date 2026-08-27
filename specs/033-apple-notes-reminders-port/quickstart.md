# クイックスタート検証ガイド: Apple Notes / Reminders 自動操作スキル

このガイドは、実装後に本機能が仕様どおり動作することを実機の Mac 上で確認するための手順である。Apple Events / EventKit を用いる操作は自動テストできないため（`plan.md` Technical Context の Testing 参照）、ここに書かれた手順が実質的な受け入れテストになる。各手順は `spec.md` の該当ユーザーストーリー／受け入れシナリオに対応させてある。

## 前提条件

1. macOS 14 以降。
2. Xcode Command Line Tools: `xcode-select --install`
3. Notes.app と Reminders.app にサンプルデータがなくてよい（このガイドが作成する）。
4. 初回実行時に表示される権限ダイアログを許可する:
   - Automation（Notes 用）: ダイアログが出ない場合は システム設定 → プライバシーとセキュリティ → Automation → (ターミナルアプリ) → Notes
   - Reminders（フルアクセス）: システム設定 → プライバシーとセキュリティ → リマインダー

非対話的（ヘッドレス）環境ではこのガイドを実行できない（`spec.md` 前提条件）。

## セットアップ

```bash
S_NOTES="$HOME/.claude/skills/apple-notes/scripts"   # または本リポジトリのプロジェクトスコープパス
S_REM="$HOME/.claude/skills/apple-reminders/scripts"

CLI="$(bash "$S_REM/build.sh")"   # 初回はビルドが走る。以後は no-op
echo "Reminders CLI: $CLI"
```

## US1: 保存先を用意し、何かを書き留める

```bash
# フォルダ／リストの存在保証 — 冪等性の確認（受け入れシナリオ1,2,3）
osascript -l JavaScript "$S_NOTES/ensure_folder.js" --name "QuickstartTest"
osascript -l JavaScript "$S_NOTES/ensure_folder.js" --name "QuickstartTest"   # 2回目: created:false になること
"$CLI" ensure-list --name "QuickstartTest"
"$CLI" ensure-list --name "QuickstartTest"                                    # 2回目: created:false になること

# 書き込み（受け入れシナリオ4）
osascript -l JavaScript "$S_NOTES/write_note.js" --folder "QuickstartTest" \
  --title "Hello" --text "This is a test note."
"$CLI" create --list "QuickstartTest" --name "Hello reminder" --due "$(date -v+1d +%F)"
```

**期待結果**: 2回目の ensure 呼び出しはいずれも `created: false` を返し、フォルダ／リストは重複しない（SC-001）。作成したノート・リマインダーは Notes.app / Reminders.app の GUI 上でも確認できる。

## US2: 中身を読み戻す

```bash
osascript -l JavaScript "$S_NOTES/list_notes.js" "QuickstartTest"              # body は既定で省略
osascript -l JavaScript "$S_NOTES/list_notes.js" "QuickstartTest" --with-body  # body を含める
"$CLI" list "QuickstartTest" --open-only
```

**期待結果**: 1回目の一覧に `body` フィールドが含まれない／2回目には含まれる（SC-005）。`--open-only` は未完了のみを返す。

## US3: 既存内容を巻き添え被害なく更新する

```bash
NOTE_ID="<US1で作成したノートのid>"

echo "Appended line." | osascript -l JavaScript "$S_NOTES/write_note.js" --id "$NOTE_ID" --append-stdin
osascript -l JavaScript "$S_NOTES/list_notes.js" --id "$NOTE_ID" --plaintext --field plaintext
# → 元の "This is a test note." が残り、末尾に "Appended line." が追加されていること

echo "status: in progress" | osascript -l JavaScript "$S_NOTES/write_note.js" --id "$NOTE_ID" --replace-block "status" --replace-stdin
# 2回目に別の内容で再実行 → 区画のみ置換されること。手動で同名区画を2つ作ってから実行 → 拒否されること
```

**期待結果**: 追記は既存内容を壊さない。名前付き区画の置換は対象区画のみを変更する。

## US4: ノートの全内容を安全に置き換える・削除する

```bash
CURRENT=$(osascript -l JavaScript "$S_NOTES/list_notes.js" --id "$NOTE_ID" --plaintext --field plaintext)
HASH=$(printf '%s' "$CURRENT" | python3 "$S_NOTES/note_write_guard.py" hash)

# 意図的に不一致を作る: 別経路（Notes.app のGUI）でノートを編集してから、古いHASHのまま上書きを試みる
echo "replacement content" | osascript -l JavaScript "$S_NOTES/write_note.js" --id "$NOTE_ID" --overwrite-stdin --expect-hash "$HASH"
# → 拒否され、内容が変化していないことを確認する（SC-003）

# 正しい手順: 直前に読み直してからハッシュを計算し、置き換え内容を人間に提示・承認を得たうえで実行する
CURRENT=$(osascript -l JavaScript "$S_NOTES/list_notes.js" --id "$NOTE_ID" --plaintext --field plaintext)
HASH=$(printf '%s' "$CURRENT" | python3 "$S_NOTES/note_write_guard.py" hash)
echo "replacement content" | osascript -l JavaScript "$S_NOTES/write_note.js" --id "$NOTE_ID" --overwrite-stdin --expect-hash "$HASH"
# → 成功することを確認する
```

**期待結果**: 古いハッシュでの上書きは常に拒否され内容は変化しない（SC-003）。正しいハッシュでの上書きは成功する。削除も同じハッシュゲートで確認する（`--delete`）。リマインダーの削除は `"$CLI"` に存在しないことを確認する。

## 後片付け

```bash
# ノート・フォルダ・リマインダー・リストは Notes.app / Reminders.app の GUI から手動で削除する
# （本機能はリマインダーの削除操作を提供しない — FR-016）
```
