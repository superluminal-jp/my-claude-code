# コントラクト: `ensure_folder.js`（Notes フォルダの存在保証）

対応要求: FR-001, FR-003。呼び出し形: `osascript -l JavaScript ensure_folder.js --name <name> [--parent-id <id>]`

## 入力

| 引数 | 必須 | 説明 |
|---|---|---|
| `--name <name>` | 必須 | フォルダ名。前後の空白は除去する。除去後に空文字列であれば拒否する。 |
| `--parent-id <id>` | 任意 | 指定時、この親フォルダの直下の子フォルダに限定してマッチングする。未指定時は既定アカウント直下を対象とする。 |

## 出力（JSON, stdout）

```json
{ "id": "<folder-id>", "name": "<folder-name>", "created": true, "account": "<account-name>" }
```

`--parent-id` 指定時は `"account"` の代わりに `"parent": "<parent-folder-id>"` を返す。

## 挙動

1. `--name` を完全一致・大文字小文字区別ありで照合する（`--parent-id` 指定時はその親の直下の子フォルダのみが対象）。
2. 一致 0件 → 新規作成し `created: true` を返す。
3. 一致 1件 → 何も作成せず再利用し `created: false` を返す。
4. 一致 2件以上 → 何も作成せず、非ゼロ終了コードで失敗する。

## エラー

| 状況 | 挙動 |
|---|---|
| `--name` が空/空白のみ | 何も作成せず失敗 |
| 複数一致 | 何も作成せず失敗（曖昧さを解消しない） |
| Automation 権限未許可 | osascript レベルのエラー（`-1743`/`-10004`/`-10827` 相当）。呼び出し元（SKILL.md 運用者向けガイダンス）が FR-017 に基づき「Automation 権限が必要」と案内する。 |
