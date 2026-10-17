# Implementation Plan: 処分規則と作成条件を手順に入れる(スライス S4)

**Branch**: `048-disposition-rules` | **Date**: 2026-10-17 | **Spec**: [spec.md](spec.md)

## Summary

`SKILL.md` の「For every change」に処分と作成の規則を 2 項目(合計数行)で加え、完了報告の書式に `Created:` 行を加え、`hooks/rule.md` に短い箇条書きを 1 つ加える。文書のみで、スクリプトは変更しない。`SkillDefinitionTests` に、必須の語句・アンカー・書式を確認するテストを先に追加する。

## Technical Context

**Language/Version**: Markdown(テストは Python 3.9 以上の標準ライブラリ)

**Testing**: `unittest`(`SkillDefinitionTests`)と `check_links.py --changed`

**Constraints**: `SKILL.md` は 500 行未満(現状 95 行)。配置規則へのリンクのアンカーは `references/practices.md#layers-placement-and-proximity`(`check_links.py` が検証)。スクリプト・スキーマ・README・eval は無変更。既存 132 件を維持

## Constitution Check

`.specify/memory/constitution.md` は未記入のテンプレートで、適用される制約はない。CLAUDE.md とグローバル規則を実質のゲートとする。

| ゲート | 判定 |
|---|---|
| 最小で一貫した変更 | 合格: `SKILL.md`・`rule.md`・テストのみ |
| 失敗するチェックを先に用意 | 合格: テストを先に追加し、失敗を記録する |
| 既存の規則との整合 | 合格(予定): 既存の決定記録の規則(ユーザーが依頼したときのみ作成)を再掲するのみで、変更しない |

## 設計の要点

1. **SKILL.md「For every change」に追加する項目(英語、簡潔)**:
   - 関連文書の処分: 「Dispose of every related document that `find_related.py` lists: update it, or name its path in the final message with the reason it needs no change.」
   - 作成の規則: 「Create a document only when the change adds a new public contract (command, option, setting, API, module) and no related document covers it. Follow the placement in [references/practices.md](references/practices.md#layers-placement-and-proximity). Create at most three new files per change and propose the rest in the report. Never create a decision record unless the user asks, and never start a change history the project does not keep.」(`at most three new files` を含める)
2. **完了報告の書式**: `- Updated:` の次に `- Created: <file> — <what it documents and why no existing document fit>` を加える。「Omit empty lines.」は変更しない。
3. **hooks/rule.md**: 既存の箇条書きの後に 1 つ: 「Update each document related to a changed file (`find_related.py`), or name its path in the final message with the reason it needs no change. Create a document only for a new public contract with no covering document, and follow the skill's placement rules.」
4. **テスト(`SkillDefinitionTests`)**:
   - S4a 「For every change」に処分の規則(`name its path in the final message`)がある
   - S4b 作成の規則: `new public contract`、`at most three new files`、アンカー付きリンク `references/practices.md#layers-placement-and-proximity`、`never start a change history`
   - S4c 完了報告の書式に `- Created:` 行があり、`- Updated:` の後、`- No change needed:` の前にある
   - S4d `rule.md` に `find_related.py` と `new public contract` がある
   - 既存の定義検査と、`test_scripts_named_in_the_skill_exist`(S1)が通る

## テスト先行

S4a〜S4d を先に追加し、失敗を記録する。その後 `SKILL.md`、`rule.md` の順に変更して通す。

## リスクと分岐

- **A4**: 規則が LLM の振る舞いを改善するかは、このスライスでは検証できない。S6 の eval(費用の承認後)で検証し、偽なら再仕様(S4)またはユーザーへの相談(分岐 B4)。
- **語数の増加**: `SKILL.md` は規則の追加により行数が増えるが、500 行未満の検査がある。

## Complexity Tracking

違反なし。
