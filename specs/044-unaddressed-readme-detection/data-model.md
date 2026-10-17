# Data Model: 未処分の兄弟 README の検出(S1)

永続データは無い。以下は `find_related.py` が返す辞書(契約 C1)と、ゲートが使う判定の入出力。

## ChangedSet(変更集合)

| 項目 | 内容 |
|---|---|
| 由来 | `common.changed_files(root, base)` の結果から、除外設定の対象を除いたもの |
| 要素 | `Change(path, status, old_path)`(`path` はルート相対の POSIX パス。名前変更では新しいパス) |
| 出力上の表現 | `changed`: パスの昇順の配列(重複なし) |

## Candidate(候補)— C1

| 項目 | 型 | 内容 | 検証 |
|---|---|---|---|
| `source` | 文字列 | 候補の元になった、変更された文書でないファイルのパス | 変更集合に含まれる、`classify` に `documentation` を含まない |
| `path` | 文字列 | 候補の文書のパス | `list_files` に含まれ、R1 の文書判定を満たし、変更集合に含まれない、`source` と異なる |
| `kind` | 文字列 | 本スライスでは `"sibling"` のみ | 固定 |
| `proximity` | 文字列 | 本スライスでは `"P1"` のみ | 固定 |
| `reason` | 文字列 | 人間が読める理由(例: `同じディレクトリ src/ の文書。src/x.py が変更されたが未変更`) | 空でない |

並び順: `(path, source)` の昇順(再現性のため)。

## CandidateReport(出力全体)— C1

```json
{
  "changed": ["src/x.py"],
  "candidates": [
    {"source": "src/x.py", "path": "src/README.md", "kind": "sibling", "proximity": "P1", "reason": "..."}
  ],
  "truncated": 0
}
```

`truncated` は本スライスでは常に 0(上限は S2)。

## Disposition(処分)— C2 の最小形

| 状態 | 条件 | ゲートの扱い |
|---|---|---|
| 処分済み(変更) | 候補のパスが変更集合に含まれる | 問題にしない(そもそも候補に出ない) |
| 処分済み(言及) | 候補のパスが最終メッセージに部分文字列として現れる | 問題にしない |
| 未処分 | 上記のどちらでもない | 問題として報告する |
| 判定不能 | 最終メッセージが取得できない | 問題を報告しない |

## 状態遷移

なし。ゲートの回数管理(同じ作業状態に対する最大ブロック数、`last_ok`)は既存の仕組みを変更せずに使う。
