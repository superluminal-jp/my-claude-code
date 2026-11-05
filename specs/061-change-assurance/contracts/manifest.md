# Contract: 検証の記録、保証の判定、JUnit XML の取り込み

規則の意味は [spec.md](../spec.md) の FR-002 にある。出力の共通の欄(`output_version`、`input_file`、`status`、`rules_checked`、`violations`、`error`)と終了コード 2 の意味は、spec 059 の [contracts/cli.md](../../059-refinement-graph-checker/contracts/cli.md) と同じである。

## 1. コマンド

```text
python3 <skill-dir>/scripts/assure.py [--format text|json] check MANIFEST
python3 <skill-dir>/scripts/assure.py [--format text|json] gate GRAPH MANIFEST
python3 <skill-dir>/scripts/assure.py collect-junit REPORT --graph GRAPH --commit SHA --ref REF
```

`collect-junit` は、検証の記録の `checks` に入れる項目の配列を JSON で標準出力に書く。`GRAPH` は spec 060 の v2 の要求グラフである。

## 2. 検証の記録

```json
{
  "schema_version": 1,
  "verification_manifest": {
    "change_id": "CHG-001",
    "problem_id": "PRB-001",
    "reviewed_commit": "0f5a148c2d7a9e1b3f6a8c0d2e4f6a8b0c2d4e6f",
    "implementer": "claude (session 2026-11-06)",
    "risk": {"class": "high", "rationale": "認可の変更"},
    "approvals": [{"by": "owner-a", "decision": "approved", "scope": "認可の変更と残存リスク"}],
    "checks": [
      {"check_id": "TEST-REQ-READ", "status": "passed",
       "evidence": {"kind": "ci_job", "ref": "https://github.com/org/repo/actions/runs/1/job/2", "commit": "0f5a148c2d7a9e1b3f6a8c0d2e4f6a8b0c2d4e6f"}},
      {"check_id": "TEST-REQ-ROOT", "status": "not_applicable", "reason": "..."}
    ],
    "test_changes": [{"path": "tests/test_orders.py::test_legacy", "change": "deleted", "approved_by": "owner-a"}],
    "infra_changes": [{"kind": "permission_expansion", "ref": "cdk diff の該当行"}]
  }
}
```

| 欄 | 型と値 | 必須 |
|---|---|---|
| `change_id`、`problem_id`、`implementer` | 空でない文字列 | はい |
| `reviewed_commit` | 7〜40 桁の16進数の文字列 | はい |
| `risk` | `{class, rationale}`。`class` は `low`・`medium`・`high`・`unclassified` | はい(欠けると A-04 で `blocked`) |
| `approvals` | `{by, decision, scope}` の配列。`decision` は `approved`・`rejected` | いいえ |
| `checks` | `{check_id, status, evidence?, reason?}` の配列。`status` は `passed`・`failed`・`not_run`・`blocked`・`not_applicable` | はい |
| `evidence` | `{kind, ref, commit}`。`kind` は `ci_job`・`local_run`・`scanner`・`human_review`・`ai_review` | `passed` では必須 |
| `test_changes` | `{path, change, approved_by?}` の配列。`change` は `deleted`・`skipped`・`weakened` | いいえ |
| `infra_changes` | `{kind, ref}` の配列。`kind` は `permission_expansion`・`public_exposure`・`resource_deletion`・`resource_replacement` | いいえ |

| 規則 | 合格の条件 |
|---|---|
| M-00 | 必須の欄があり、値の型と列挙の値が正しく、定義していない欄がない(`risk` の欠けは A-04 で扱う) |
| M-01 | `check_id` が空でなく一意である |
| M-02 | `passed` の検査は `evidence` を持ち、`not_applicable` の検査は空でない `reason` を持つ |

検証の記録に M の違反があれば、判定は `blocked` である(理由は M-xx の違反がある、とする)。

## 3. 判定の結果

```json
{"graph": "assurance", "decision": "blocked",
 "levels": {"L1": {"passed": 2}, "L2": {"not_run": 1}, "L3": {}},
 "reasons": [{"rule_id": "A-01", "message": "acceptance \"TEST-REQ-ROOT\" has no check (treated as not_run)"}],
 "rules_checked": ["A-01", "A-02", "A-03", "A-04", "A-05", "A-06", "A-07"]}
```

`status` は `pass` なら `passed`、それ以外は `failed` である。`levels` は、要求グラフの受け入れ条件の水準ごとに、判定に使った状態(A-02 で退けた `passed` と、M-00 で証拠を拒んだ `passed` は `blocked` に数える)の件数を示す。

## 4. JUnit XML の取り込み

| 規則 | 内容 |
|---|---|
| J-01 | 文書型宣言(`<!DOCTYPE`。実体はその中で宣言する)を持つ XML、壊れた XML は、入力を解釈できない(終了コード 2)。宣言は XML の構文解析器で見つけるため、コメント、処理命令、CDATA の中の同じ文字列は宣言とみなさず、それらの後ろの宣言も見落とさない |
| J-02 | テストケースは、プロパティ `acceptance_id` の値か、名前(`classname` と `name`)の中の語として現れる受け入れ条件の ID に対応する。1つの ID に対応するテストケースが、すべて合格なら `passed`、1つでも `failure` か `error` なら `failed`、ほかは `not_run` とする。どのテストケースにも対応しない ID も `not_run` として出力する |

出力の各項目の `evidence` は `{"kind": "ci_job", "ref": REF, "commit": SHA}` とし、`local_run` を指定するときは `--kind local_run` を加える。
