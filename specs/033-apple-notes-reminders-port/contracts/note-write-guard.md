# コントラクト: `note_write_guard.py`（ハッシュゲート計算・照合）

対応要求: FR-014。純粋ロジックのみ（`osascript` を一切呼び出さない）— macOS 以外でも、Automation 権限がなくても実行・テスト可能。

## サブコマンド

### `hash`

```bash
printf '%s' "<plaintext-body>" | note_write_guard.py hash
```

標準入力のプレーンテキストの SHA-256 16進ダイジェストを標準出力に返す。

### `decide`

```bash
printf '%s' "<current-plaintext-body>" | note_write_guard.py decide --expect-hash "<sha256>"
```

標準入力から現在のプレーンテキスト本文を受け取り、そのハッシュと `--expect-hash` を比較する。

| 判定 | 終了コード | 標準出力 |
|---|---|---|
| 一致 | 0 | `{"decision": "proceed"}` |
| 不一致 | 非0 | `{"decision": "refuse", "reason": "note changed since last read"}` |

呼び出し元（`write_note.js`）は `decide` の判定に厳密に従い、`refuse` の場合は一切の書き込み・削除操作を発行してはならない。

## 単体テスト方針

`tests/test_note_write_guard.py`（`tests/run-note-write-guard.sh` 経由、`python3 -m unittest discover`）でカバーする:

- 同一入力に対する `hash` の決定性（同じ入力は常に同じハッシュを返す）。
- 異なる入力に対する `hash` の非衝突性（現実的なテストケース範囲で）。
- `decide` が一致時に `proceed`、不一致時に `refuse` を返すこと。
- 空文字列・空白のみ・マルチバイト文字を含む入力での境界動作。
