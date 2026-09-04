# 契約: `problem-definition` スキルインタフェース

**機能**: 038-problem-definition-skill | **日付**: 2026-09-05 | **計画**: [../plan.md](../plan.md)

本機能に外部 API は存在しない。ここでの「契約」は、(1) `SKILL.md` が満たすべき構造契約——`tests/run-config-pyramid.sh` が実際に検証するもの——と、(2) スキルが生成する問題文ファイルが満たすべき出力契約の2つである。

---

## 契約 A: `SKILL.md` フロントマター/構造契約

`problem-definition` を `tests/run-config-pyramid.sh` の `authored_skills` 配列に加える以上、以下すべてを満たさなければならない（`037`実装で確立済みの契約。research.md D1）。

| 契約ID | 要件 | 対応する spec.md FR |
|---|---|---|
| SKILL-01 | `.claude/skills/problem-definition/SKILL.md` が存在する | FR-001 |
| SKILL-02 | フロントマターに `when_to_use:` フィールドを持たない | FR-002 |
| SKILL-03 | `description:` が除外境界を示す語（`Do not use`/`does not apply`/`exclude`/`not for`/`out of scope`/`対象外`/`使わない` のいずれか）を含む | FR-002 |
| SKILL-04 | 本文が `.claude/CLAUDE.md`・`.claude/rules/`・`.claude/skills/`・`.agents/skills` などの設定パスに依存しない | FR-015（他ツール/他設定への依存を持たない） |
| SKILL-05 | 本文が `product-strategy`・`clarifier`・`adr` 等の兄弟スキル名を埋め込まない | FR-016 |
| SKILL-06 | 本文が自分自身の配置パス（`.claude/skills/problem-definition`）をハードコードしない | FR-017 |
| ROUTE-10（新規） | `description:` が本スキル固有のトリガー・境界語（例: 「問題/problem」と「対象外/out of scope/not for」）を含む | FR-002（`run_routing_fixtures()` への実装先。research.md D2） |

---

## 契約 B: 問題文出力ファイル

**先頭のステータスマーカー**（必須、機械可読）:

```markdown
# 問題文: <対象の名称>

**ステータス**: 完成 | ドラフト（未完成）
**生成日**: <YYYY-MM-DD>
```

- `完成` の場合: 本文は「現状」「あるべき姿」「ギャップ」「重要性」の4要素を漏れなく含まなければならない（data-model.md V8）。
- `ドラフト（未完成）` の場合: 上記4要素に加え、`## 未回答の要素` という見出しの下に、まだ引き出せていない要素名を列挙しなければならない（V9）。

**上書き確認ダイアログの契約**（FR-015a）: 書き込み先に既にファイルが存在する場合、スキルは書き込みの前に必ず以下のいずれかをユーザーに確認しなければならない:

1. 既存ファイルを上書きする
2. 新しいバージョンとして別ファイルに保存する（例: `problem-<YYYY-MM-DD>.md`）

**混入した非問題入力の記録**（FR-010、FR-011、data-model.md「混入した非問題入力」エンティティ）:

```markdown
## 識別された解決策（問題文には含めない）

<ユーザーが提示した解決策の内容>。これが解消しようとしているギャップ: <対応する現状/あるべき姿の対比>
```

```markdown
## 識別された未検証の原因（問題文には含めない）

<ユーザーが提示した原因仮説>。検証されていない前提として記録する。原因分析は本スキルが担わない、完全に別の後続の関心事である。
```

**対立するあるべき姿の記録**（FR-012）:

```markdown
## あるべき姿に関する見解の対立

- <関係者Aの見解>
- <関係者Bの見解>

どちらを基準とするかは未確定——[未解決の論点の記録形式に従って記載]。
```
