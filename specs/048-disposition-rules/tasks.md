---

description: "Task list for slice S4: 処分規則と作成条件を手順に入れる"
---

# Tasks: 処分規則と作成条件を手順に入れる(スライス S4)

`SKILL` = `.claude/skills/maintaining-living-documentation`。`tests/test_scripts.py` を触るタスクは並行しない。スクリプト・スキーマ・README・eval は変更しない。

## Phase 1: Setup

- [X] T001 ブランチが `048-disposition-rules` であることを確認し、既存 132 件が通ることを基準として記録する

## Phase 2: Foundational(失敗するテストを先に書く)

- [X] T002 `SKILL/tests/test_scripts.py` の `SkillDefinitionTests` に S4a・S4b を追加する(処分の規則、作成の条件・上限・アンカー付きリンク・変更履歴の新設禁止)
- [X] T003 `SKILL/tests/test_scripts.py` の `SkillDefinitionTests` に S4c・S4d を追加する(`Created:` 行の位置、`rule.md` の趣旨)
- [X] T004 追加したテストを実行し、失敗することを確認して記録する。既存 132 件が通ったままであることも確認する

## Phase 3: User Story 1 - 関連文書の処分 (P1) 🎯 MVP

- [X] T005 [US1] `SKILL/SKILL.md` の「For every change」に、関連文書の処分の規則を追加する
- [X] T006 [US1] `SKILL/hooks/rule.md` に、処分と作成の条件を短く追加する
- [X] T007 [US1] S4a・S4d が通ることを確認する

## Phase 4: User Story 2 - 作成の条件 (P2)

- [X] T008 [US2] `SKILL/SKILL.md` の「For every change」に、作成の規則(条件、配置規則へのリンク、最大 3 ファイル、決定記録と変更履歴の禁止)を追加する
- [X] T009 [US2] S4b が通ることと、`check_links.py` がアンカーを検証して通ることを確認する

## Phase 5: User Story 3 - `Created:` 行 (P3)

- [X] T010 [US3] `SKILL/SKILL.md` の完了報告の書式に `Created:` 行を追加する
- [X] T011 [US3] S4c と既存の定義検査(500 行未満、規則とスキルの一致)が通ることを確認する

## Phase 6: Polish

- [X] T012 全テストを実行し、既存 132 件を含めてすべて通ることを確認する
- [X] T013 [P] `check_links.py --root . --changed` を実行し、エラー 0 を確認する
- [X] T014 [P] `git diff --stat -- SKILL/scripts SKILL/schemas SKILL/README.md SKILL/evals` が空であることを確認する
- [X] T015 完了報告の項目を整理する(README の同期は S6、規則の効果の検証は S6 の eval として `Unresolved`)

## Dependencies

Phase 1 → 2 → 3 → 4 → 5 → 6。T005・T008・T010 は同じファイル(`SKILL.md`)を編集するため順に行う。T013・T014 は並行可能。

## Evidence(実装記録)

- **T001**: 既存 132 件が通る。
- **T004(失敗の記録)**: 追加した 4 件(S4a〜S4d、S4b は 4 つの語句を `subTest`)が実装前に失敗した(7 件の失敗)。合計 136 件、既存 132 件は通ったまま。
- **T005〜T011**: `SKILL.md` の「For every change」に処分と作成の規則を 2 項目追加し、完了報告に `Created:` 行を `Updated:` の次に追加した。`hooks/rule.md` に処分と作成の条件を既存の箇条書きの末尾に追加した。
- **T012**: 全 136 件が通った(約 35 秒)。`SKILL.md` は 98 行(500 行未満)。
- **T013**: `check_links.py --changed` はエラー 0(配置規則へのアンカーを含む)。
- **T014**: スクリプト・スキーマの差分は無い(README・eval は S6)。
- **未検証**: 仮定 A4(規則が LLM の振る舞いを改善する)は、S6 の eval をユーザーが費用上限を承認した後に実行して検証する。
