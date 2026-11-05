# Quickstart: 検査器が動くことを確かめる

前提は Python 3.9 以上と Bash である。ネットワークは使わない。すべてリポジトリの根から実行する。

## 1. 受け入れテストと例をまとめて確かめる

```sh
bash tests/run-refinement-checker.sh
```

期待する結果: すべての行が `PASS` で、最後の行が `Results: N passed, 0 failed`、終了コードが 0。

## 2. 例の宣言ファイルを検査する

```sh
python3 tools/refinement-checker/check_graph.py tools/refinement-checker/examples/requirements-graph.example.json
python3 tools/refinement-checker/check_graph.py --format json tools/refinement-checker/examples/skills-graph.example.json
```

期待する結果: どちらも終了コード 0。1つ目は `Result: passed (requirements; ...)` の1行、2つ目は `"status": "passed"` の JSON。出力の詳細は [contracts/cli.md](contracts/cli.md) にある。

## 3. 現在のスキルを互換モードで検査する

```sh
python3 tools/refinement-checker/check_graph.py --skills-dir .claude/skills
```

期待する結果: 終了コード 0(現在、親スキルはない)。

## 4. 違反を観測する

```sh
python3 tools/refinement-checker/check_graph.py tools/refinement-checker/tests/fixtures/requirements/p1-03-cycle.json; echo "exit=$?"
```

期待する結果: `S-03` の行に循環の経路 `A -> B -> C -> A` が出て、`exit=1`。

## 5. 既存の検査が変わらないことを確かめる

```sh
bash tests/run-config-pyramid.sh
```

期待する結果: 変更前と同じ 57 件がすべて通る(spec SC-002)。
