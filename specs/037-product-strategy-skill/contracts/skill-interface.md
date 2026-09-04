# 契約: `product-strategy` スキルインタフェース

**機能**: 037-product-strategy-skill | **日付**: 2026-09-04 | **計画**: [../plan.md](../plan.md)

本機能に外部 API は存在しない。ここでの「契約」は、(1) `SKILL.md` が満たすべき構造契約——`tests/run-config-pyramid.sh` が実際に検証するもの——と、(2) スキルが生成する戦略ブリーフファイルが満たすべき出力契約の2つである。

---

## 契約 A: `SKILL.md` フロントマター/構造契約

`product-strategy` を `tests/run-config-pyramid.sh` の `authored_skills` 配列に加える以上、以下すべてを満たさなければならない（research.md D2、data-model.md エンティティ「スキル」）。

| 契約ID | 要件 | 検証手段 | 対応する spec.md FR |
|---|---|---|---|
| SKILL-01 | `.claude/skills/product-strategy/SKILL.md` が存在する | `run_skill_contract()` のファイル存在チェック | FR-001 |
| SKILL-02 | フロントマターに `when_to_use:` フィールドを持たない | 正規表現 `^when_to_use:` の不在チェック | FR-002 |
| SKILL-03 | `description:` が除外境界を示す語（`Do not use`/`does not apply`/`exclude`/`not for`/`out of scope`/`対象外`/`使わない` のいずれか）を含む | 正規表現マッチ | FR-002、FR-005 |
| SKILL-04 | 本文が `.claude/CLAUDE.md`・`.claude/rules/`・`.claude/skills/`・`.agents/skills` などの設定パスに依存しない | 正規表現の不在チェック | FR-011（他ツール/他設定への依存を持たない） |
| SKILL-05 | 本文が `clarifier`・`scrum-master`・`minto-builder` 等の兄弟スキル名を埋め込まない | 全兄弟スキル名に対する正規表現の不在チェック | FR-017 |
| SKILL-06 | 本文が自分自身の配置パス（`.claude/skills/product-strategy`）をハードコードしない | 正規表現の不在チェック | FR-018 |
| ROUTE-09（新規） | `description:` が本スキル固有のトリガー・境界語（例: 「戦略/strategy」と「before/prerequisite/開発着手前」、および `clarifier`/`scrum-master`/`minto-builder` との違いを示す語）を含む | `run_routing_fixtures()` への新規アサーション（FR-005 の実装先） | FR-005 |

**書式の指針**（規範ではなく実装上の目安）:

```yaml
---
name: product-strategy
description: >-
  Formulate product/business strategy — vision, target users, value
  proposition, success metrics, MoSCoW-prioritized scope — before
  development work begins, for both greenfield and existing projects.
  Use when ... Do not use when the request is single-feature scope/
  acceptance-criteria clarification (that's `clarifier`), Scrum/
  facilitation (`scrum-master`), or open-ended document co-creation
  with no development destination (`minto-builder`).
---
```

---

## 契約 B: 戦略ブリーフ出力ファイル

スキルが対象プロジェクトに生成するファイルが満たすべき構造契約（data-model.md エンティティ「戦略ブリーフ」を実ファイルの書式に落としたもの）。

**先頭のステータスマーカー**（必須、機械可読）:

```markdown
# プロダクト戦略ブリーフ: <対象の名称>

**ステータス**: 完成 | ドラフト（未完成）
**生成日**: <YYYY-MM-DD>
```

- `完成` の場合: 本文は「ビジョン/課題」「ターゲットユーザー」「提供価値」「成功指標」「スコープと優先順位」「制約」の6セクションを漏れなく含まなければならない（data-model.md V7）。
- `ドラフト（未完成）` の場合: 上記6セクションに加え、`## 未回答のセクション` という見出しの下に、まだ引き出せていないセクション名を列挙しなければならない（V8）。

**上書き確認ダイアログの契約**（FR-011a）:

書き込み先に既にファイルが存在する場合、スキルは書き込みの前に必ず以下のいずれかをユーザーに確認しなければならない——確認なしに上書き・別名保存のどちらか一方を無条件に選んではならない:

1. 既存ファイルを上書きする
2. 新しいバージョンとして別ファイルに保存する（例: `strategy-<YYYY-MM-DD>.md`）

**既存文脈との関係の明示**（FR-009、既存プロジェクトかつ既存文脈がある場合）:

```markdown
## 既存の戦略との関係

本ブリーフは <既存ファイルへの相対リンク> の内容を **拡張する / 狭める / 置き換える**。
```

このセクションを省略してよいのは、対象プロジェクトに既存の文書化された文脈が一切存在しない場合（新規プロジェクト、または未文書化の既存プロジェクト）のみである。
