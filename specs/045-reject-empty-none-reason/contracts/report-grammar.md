# Contract: 完了報告の文法(C2 の理由の部分)

Stop ゲートが最終メッセージに対して認識する行の形。生産者は完了報告を書く側(スキルの手順)、消費者は `stop_gate.py`。

## 認識する行

| 行 | 形 | 備考 |
|---|---|---|
| 見出し | `Documentation impact` | 大文字小文字を問わない。見出しのみでも報告の存在としては認める |
| 不要宣言 | `Documentation impact: none — <理由>` | 区切りは `—` `–` `-` `:` `：`。理由が無効なら報告は無効 |
| 更新 | `Updated: <file> — <what changed and why>` | 内容があれば有効 |
| 変更不要 | `No change needed: <area> — <reason>` | 理由が有効なら根拠になる |
| その他 | `Unresolved:` / `Proposed decision record:` / `Checks:` | 根拠にはならない(従来どおり) |

行頭には空白、`>`、`-`、`*`、`•`、`_`、`#` が付いてもよい。

## 理由の有効性

[data-model.md](../data-model.md) の Reason を参照。定型句(`n/a`、`none`、`nothing`、`no impact`、`なし`、`該当なし` など)、空、記号のみ、未記入のテンプレート(`<reason>`)は無効。具体的な説明は長さを問わず有効。

## ゲートの判定

1. 無効な不要宣言が 1 つでもあれば、問題 A(文書の変更の有無を問わない)。
2. 完了報告が必要な変更があり、見出しがあり、文書の変更が無く、不要宣言が 0 件のとき、有効な `Updated:` 行または有効な `No change needed:` 行が無ければ、問題 B。
3. 有効な不要宣言があれば、(2) の根拠として認める。

## 問題の文面(形)

- A: `The final message says 'Documentation impact: none' without a specific reason. State why the change needs no documentation update: 'Documentation impact: none — <what stays unchanged and why>'.`
- B: `Changed files include <分類> artifacts and no documentation file changed, but the report has no 'Updated: <file> — <what changed>' line, no 'No change needed: <area> — <specific reason>' line, and no 'Documentation impact: none — <reason>' line. Add one.`

## 強制の度合い・回数

既存の `on_stop` に従う(変更しない)。`block` は同じ作業状態に最大 2 回、再入ではブロックしない。`warn` は警告のみ、`off` は何もしない。
