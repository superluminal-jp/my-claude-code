# Contract: `refinement-checker` のコマンド、入力、出力、終了コード

この契約は、利用者と CI が依存する外から見える振る舞いを固定する。規則の意味は [spec.md](../spec.md) の FR-003、要素の詳細は [data-model.md](../data-model.md) にある。

## 1. 起動の仕方は2つあり、どちらか一方だけを指定する

```text
python3 tools/refinement-checker/check_graph.py [--format text|json] FILE
python3 tools/refinement-checker/check_graph.py [--format text|json] --skills-dir DIR
```

| 引数 | 意味 |
|---|---|
| `FILE` | 宣言ファイル(JSON)のパス |
| `--skills-dir DIR` | 互換モード。`DIR` の直下の各サブディレクトリの `SKILL.md` を読む |
| `--format text` | 既定。違反を1行に1つ、最後に結果の1行を標準出力に書く |
| `--format json` | 下の §3 の JSON を標準出力に1つ書く |

`FILE` と `--skills-dir` の両方、またはどちらも指定しないときは、引数の誤りとして終了コード 2 を返す。

## 2. 宣言ファイルの形

```json
{
  "schema_version": 1,
  "requirements": [
    {
      "id": "REQ-ROOT",
      "statement": "非認可利用者が保護対象データを取得できない",
      "decomposition": "AND",
      "children": ["REQ-READ", "REQ-EXPORT"],
      "assumptions": ["対象の読み取り経路とエクスポート経路が把握されている"],
      "acceptance": [
        {"id": "TEST-PARENT-001", "description": "全ての取得経路を横断する統合認可試験", "level": "L2"}
      ],
      "counterexamples": ["読み取りとエクスポートは拒否されるが別経路から取得できる"]
    }
  ]
}
```

```json
{
  "schema_version": 1,
  "skills": [
    {"id": "goal-refinement", "children": ["refinement-checker"], "permission": "read_only", "role": "worker"}
  ]
}
```

- 最上位は `schema_version`(整数 1)と、`requirements` か `skills` のちょうど一方(配列)だけを持つ。
- OR のノードは `"selection": {"<子の ID>": "<その子を選ぶ条件>", ...}` を持つ。
- 欄の一覧と、欄がないときの規則は [data-model.md](../data-model.md) にある。

## 3. JSON の出力

```json
{
  "output_version": 1,
  "input_file": "tools/refinement-checker/examples/requirements-graph.example.json",
  "graph": "requirements",
  "status": "passed",
  "rules_checked": ["S-00", "S-01", "S-02", "S-03", "S-04", "S-05", "S-06", "S-07", "S-08", "S-11"],
  "violations": [],
  "error": null
}
```

| 欄 | 値 |
|---|---|
| `output_version` | 出力の形式の版。整数 1 |
| `input_file` | 起動時に渡したファイルまたはディレクトリのパス |
| `graph` | `requirements`、`skills`、`skills-dir`(互換モード)。入力を解釈できなかったときは `null` |
| `status` | `passed`(違反なし)、`failed`(違反あり)、`error`(入力を解釈できない) |
| `rules_checked` | 判定した規則 ID の一覧。`requirements` は S-00〜S-08 と S-11、`skills` は S-00〜S-03・S-08・S-09、`skills-dir` は S-02・S-03・S-08・S-10。`error` のときは空 |
| `violations` | `{"rule_id", "node_id", "message"}` の配列。`node_id` はノードに結び付かない違反で `null`。規則 ID、ノードの宣言の順、理由の順に並ぶ |
| `error` | `error` のときの理由の文字列。それ以外は `null` |

`status: passed` は構造の規則に合うことだけを意味し、セキュリティへの適合や、子が親を満たす十分性を意味しない。

## 4. 終了コード

| コード | 条件 |
|---|---|
| 0 | 違反がない |
| 1 | 規則 S-00〜S-11 のどれかに違反がある |
| 2 | 入力を解釈できない: 引数の誤り、読めないファイルやディレクトリ、5 MiB を超える入力、UTF-8 でない入力、JSON の構文の誤り、同じキーの重複、JSON の読み込みが扱えない深い入れ子、最上位がオブジェクトでない、`schema_version` が整数 1 でない、`requirements` と `skills` のちょうど一方を配列として持たない、最上位に定義していない欄がある。検査器自身の異常(終了コード 1 と区別するため)も 2 とする |

## 5. 人が読む形式の出力

```text
S-02 REQ-ROOT: child "REQ-MISSING" is not defined
Result: failed (requirements; 1 violation; checked S-00 S-01 S-02 S-03 S-04 S-05 S-06 S-07 S-08 S-11; structural rules only)
```

違反がなければ結果の1行だけを書く。ID と理由の中の制御文字は `\n` や `\x1b` のようにエスケープする(spec FR-013)。終了コード 2 のときは `error: <理由>` を標準エラー出力に書く。
