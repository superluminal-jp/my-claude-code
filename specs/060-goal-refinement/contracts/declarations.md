# Contract: 問題カード、v2 の要求グラフ、反証の記録、判定

規則の意味は [spec.md](../spec.md) の FR-002〜FR-004 にある。spec 059 の [contracts/cli.md](../../059-refinement-graph-checker/contracts/cli.md) の出力の欄と終了コードは、そのまま引き継ぐ。

## 1. 問題カード

```json
{
  "schema_version": 1,
  "problem_card": {
    "id": "PRB-001",
    "ideal": "利用者は、閲覧を許可されたデータにしかアクセスできない",
    "current": "隔離したテスト環境で、利用者 B が利用者 A の注文を取得できた",
    "evidence": [{"source": "pytest tests/test_orders.py::test_other_user (2026-11-06)", "observation": "200 が返った"}],
    "counter_evidence": [],
    "gap": "注文の取得 API で、オブジェクト単位の認可の要件が満たされていない",
    "significance": "他人の個人情報が漏れる",
    "hypotheses": ["API が所有者を検証していない"],
    "proposed_solutions": ["ID を UUID に変える"],
    "out_of_scope": ["管理者向け API"],
    "status": "verified",
    "status_rationale": ""
  }
}
```

| 欄 | 型 | 必須 |
|---|---|---|
| `id`、`ideal`、`current`、`gap`、`significance` | 空でない文字列 | はい |
| `status` | `verified`・`unverified`・`refuted` | はい |
| `evidence`、`counter_evidence` | `{source, observation}` の配列(どちらも空でない文字列) | `evidence` だけ必須(空の配列は可) |
| `hypotheses`、`proposed_solutions`、`out_of_scope` | 文字列の配列 | いいえ |
| `status_rationale` | 文字列 | いいえ |

欄がない・型が誤る・定義していない欄は C-00、`status` の値の誤りは C-03 である。

## 2. v2 の要求グラフ

spec 059 の要求グラフに、最上位の `"problem_id": "PRB-001"` を加え、`"schema_version": 2` とする。`problem_id` がない・空・文字列でないときは、入力を解釈できない(終了コード 2)。v1 は変わらない。v2 は `requirements` だけに使え、`skills` は v1 のままである。

## 3. 反証の記録

```json
{
  "schema_version": 1,
  "challenge_report": {
    "problem_id": "PRB-001",
    "reviewer": "read-only subagent (Explore), 2026-11-06",
    "context_given": ["problem card", "requirements graph"],
    "findings": [
      {"id": "CH-01", "kind": "counterexample", "target": "REQ-ROOT", "severity": "high",
       "statement": "読み取りとエクスポートを拒否しても、一覧 API から取得できる",
       "disposition": "accepted", "resolution": "REQ-LIST と統合試験 TEST-PARENT-002 を加えた"}
    ]
  }
}
```

| 欄 | 値 |
|---|---|
| `kind` | `false_positive`(問題が実在しない疑い)、`alternative_cause`(別の原因)、`solution_as_problem`(手段を問題としている)、`mixed_statement`(事実・仮説・解決策の混在)、`counterexample`(子がすべて真でも親が偽になる例)、`missing_child`(子の欠け)、`or_overlap`(OR の枝の重なりや覆い残し)、`missing_evidence`(根拠の欠け)、`other` |
| `severity` | `high`、`medium`、`low` |
| `disposition` | `open`(未対応)、`accepted`(受け入れて直した)、`rejected`(理由を付けて退けた) |
| `resolution` | `accepted` と `rejected` では空でない文字列 |

必須の欄(`problem_id`、`reviewer`、`context_given`、`findings`、各指摘の `id`・`kind`・`target`・`severity`・`statement`・`disposition`)の欠けと型の誤りは R-00、値の誤りと ID の重複は R-01 である。

## 4. 判定

```text
python3 <skill>/scripts/check_graph.py [--format text|json] --gate CARD GRAPH [REPORT]
```

`--gate` は `FILE` と `--skills-dir` のどちらとも同時に指定できない。JSON の結果は、spec 059 の欄に次を加える。

```json
{
  "graph": "gate",
  "decision": "blocked",
  "challenge": "recorded",
  "reasons": [{"rule_id": "G-04", "message": "finding \"CH-01\" is still open"}],
  "rules_checked": ["G-01", "G-02", "G-03", "G-04"]
}
```

`violations` には、3つの入力それぞれの規則の違反(S-xx、C-xx、R-xx)を、入力ごとに並べる。`status` は `decision` が `ready` なら `passed`、`blocked` なら `failed` である。終了コードは `ready` で 0、`blocked` で 1、どれか1つでも入力を解釈できなければ 2 である。
