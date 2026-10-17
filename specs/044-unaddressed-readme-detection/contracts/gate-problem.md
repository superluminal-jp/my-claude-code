# Contract: Stop ゲートの「未処分の候補」の報告

## 発火条件

次をすべて満たすとき、ゲートの問題の一覧に 1 件加える(既存の問題と同じ経路で報告される)。

1. ゲートが評価を行う作業状態である(既存の条件: 作業ツリーに、セッション開始時・ターン開始時・前回の合格時と異なる変更がある)
2. 最終メッセージが取得できている(`last_assistant_message` が空でない)
3. 候補のうち、パスが変更集合にも最終メッセージにも現れないものが 1 件以上ある

## 文面(形)

```text
Related documents next to changed files were neither updated nor mentioned: <path> (changed: <source>[, <source>…])[; …]. Update each one, or name its path in your final message with the reason it needs no change.
```

- 候補は `path` の昇順、同じ `path` は 1 件にまとめて元の変更ファイルを併記する
- 10 件を超える場合は、先頭 10 件と `(+N more)` を示す(既存のリンク切れの報告と同じ形式)

## 強制の度合い・回数

既存の `on_stop` に従う。本スライスでは変更しない。

| 度合い | 動作 |
|---|---|
| `block`(既定) | 同じ作業状態に対し最大 2 回(`LIVING_DOCS_GATE_MAX_BLOCKS`)ブロックし、以降は警告のみ。再入(`stop_hook_active`)ではブロックしない |
| `warn` | 警告のみ |
| `off` | 何もしない |

## 非目標

- 完了報告の語(`Documentation impact`)の検査は既存のまま。報告があっても、候補が未処分なら問題になる
- 空の `none —` の理由の拒否は S3
