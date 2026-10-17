---

description: "Task list for slice S4: 処分規則と作成条件を手順に入れる"
---

# Tasks: 処分規則と作成条件を手順に入れる(スライス S4)

`SKILL` = `.claude/skills/maintaining-living-documentation`。`tests/test_scripts.py` を触るタスクは並行しない。スクリプト・スキーマ・README・eval は変更しない。

## Phase 1: Setup

- [ ] T001 ブランチが `048-disposition-rules` であることを確認し、既存 132 件が通ることを基準として記録する

## Phase 2: Foundational(失敗するテストを先に書く)

- [ ] T002 `SKILL/tests/test_scripts.py` の `SkillDefinitionTests` に S4a・S4b を追加する(処分の規則、作成の条件・上限・アンカー付きリンク・変更履歴の新設禁止)
- [ ] T003 `SKILL/tests/test_scripts.py` の `SkillDefinitionTests` に S4c・S4d を追加する(`Created:` 行の位置、`rule.md` の趣旨)
- [ ] T004 追加したテストを実行し、失敗することを確認して記録する。既存 132 件が通ったままであることも確認する

## Phase 3: User Story 1 - 関連文書の処分 (P1) 🎯 MVP

- [ ] T005 [US1] `SKILL/SKILL.md` の「For every change」に、関連文書の処分の規則を追加する
- [ ] T006 [US1] `SKILL/hooks/rule.md` に、処分と作成の条件を短く追加する
- [ ] T007 [US1] S4a・S4d が通ることを確認する

## Phase 4: User Story 2 - 作成の条件 (P2)

- [ ] T008 [US2] `SKILL/SKILL.md` の「For every change」に、作成の規則(条件、配置規則へのリンク、最大 3 ファイル、決定記録と変更履歴の禁止)を追加する
- [ ] T009 [US2] S4b が通ることと、`check_links.py` がアンカーを検証して通ることを確認する

## Phase 5: User Story 3 - `Created:` 行 (P3)

- [ ] T010 [US3] `SKILL/SKILL.md` の完了報告の書式に `Created:` 行を追加する
- [ ] T011 [US3] S4c と既存の定義検査(500 行未満、規則とスキルの一致)が通ることを確認する

## Phase 6: Polish

- [ ] T012 全テストを実行し、既存 132 件を含めてすべて通ることを確認する
- [ ] T013 [P] `check_links.py --root . --changed` を実行し、エラー 0 を確認する
- [ ] T014 [P] `git diff --stat -- SKILL/scripts SKILL/schemas SKILL/README.md SKILL/evals` が空であることを確認する
- [ ] T015 完了報告の項目を整理する(README の同期は S6、規則の効果の検証は S6 の eval として `Unresolved`)

## Dependencies

Phase 1 → 2 → 3 → 4 → 5 → 6。T005・T008・T010 は同じファイル(`SKILL.md`)を編集するため順に行う。T013・T014 は並行可能。
