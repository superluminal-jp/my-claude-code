# Contract: 候補レポート(C1 の拡張)と設定(C3)

## C1 の拡張

`find_related.py --json` の `candidates[].kind` に `mention`・`changelog`・`comment` が加わる(`sibling` は S1)。レコードのキーは変わらない。

| kind | proximity | 成立条件 | ゲート |
|---|---|---|---|
| `comment` | P0 | 変更された実装ファイル(分類が実装のみ)自身 | 強制しない(助言) |
| `sibling` | P1 | 同じディレクトリの未変更の文書 | 強制する |
| `mention` | P2 | パスまたは(最小長以上の)ファイル名を本文に含む未変更の文書 | 強制する |
| `changelog` | P3 | 変更履歴を持つプロジェクトで、利用者に見える変更があり、変更履歴が未変更 | 強制する |

`truncated`: `related.max_candidates` により省かれた異なる文書の数。

## C3 設定キー

`.living-documentation.json`:

```json
{ "related": { "max_candidates": 10, "min_name_length": 6 } }
```

`schemas/config.schema.json` が唯一の定義。不正な値は `invalid .living-documentation.json: related.<key> must be …` の形で拒否される。

## ゲートの問題の文面(形)

```text
Documents related to changed files were neither updated nor named in the final message: <path> (next to changed <src>); <path> (mentions changed <src>); <path> (change history; user-visible change <src>) (+N more not listed: raise related.max_candidates). Update each one, or name its path in your final message with the reason it needs no change.
```
