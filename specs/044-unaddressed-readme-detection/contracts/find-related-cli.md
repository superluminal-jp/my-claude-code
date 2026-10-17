# Contract: `find_related.py`(コマンドラインの契約)

## 呼び出し

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/find_related.py" --root "${CLAUDE_PROJECT_DIR}" [--base <ref>] [--json]
```

| 引数 | 内容 |
|---|---|
| `--root` | プロジェクトのルート(既定: カレントディレクトリ)。リポジトリのサブディレクトリでもよい。その場合、ルート以下の変更だけを対象にする |
| `--base` | 比較の基点。指定すると `merge-base(BASE, HEAD)` からの変更(コミット済みと未コミットの両方)を対象にする |
| `--json` | C1 の JSON を標準出力に出す。未指定なら人間向けの要約 |

## 終了コード

| コード | 意味 |
|---|---|
| 0 | 成功(候補が 0 件でも 0) |
| 2 | 使い方、設定、Git のエラー。標準エラーに原因と代替手段(Git が必要なこと)を出す |

## 保証

- プロジェクトのファイルを書き換えない。ネットワークに接続しない。読み取り専用の Git のみを実行する
- 同じ作業ツリーに対して、出力は常に同じ内容と順序になる
- 出力の形は [data-model.md](../data-model.md) の CandidateReport

## 人間向け出力(参考)

```text
changed files: 1
related documents (P1):
  src/README.md  <- src/x.py
```

候補が無い場合は `no related documents found.` を出す。
