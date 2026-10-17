# Data Model: 近接候補の発見を広げる(S2)

S1 の CandidateReport([044](../044-unaddressed-readme-detection/data-model.md))を拡張する。

## Candidate(拡張)

| 項目 | 内容 |
|---|---|
| `kind` | `sibling`(P1)、`mention`(P2)、`changelog`(P3)、`comment`(P0、助言) |
| `proximity` | `P0` / `P1` / `P2` / `P3` |
| `source` | 変更された文書でないファイル。`changelog` では利用者に見える変更の先頭の 1 件 |
| `path` | 候補の文書。`comment` では `source` と同じ |
| `reason` | 空でない説明。`mention` では一致した文字列を示す |

並び: 近接度 → パス → 元ファイルの昇順。`comment` は先頭。

## CandidateReport(拡張)

| 項目 | 内容 |
|---|---|
| `truncated` | 上限で省かれた異なる文書の数(S1 では常に 0) |

## RelatedSettings

| キー | 型 | 既定 | 検証 |
|---|---|---|---|
| `related.max_candidates` | 整数 | 10 | 1 以上、真偽値は不可 |
| `related.min_name_length` | 整数 | 6 | 1 以上、真偽値は不可 |

`related` はオブジェクトで、未知のキーは拒否される。
