---

description: "Task list for slice S6: 公開文書の同期と振る舞い eval"
---

# Tasks: 公開文書の同期と振る舞い eval(スライス S6)

`SKILL` = `.claude/skills/maintaining-living-documentation`。`tests/test_scripts.py` を触るタスクは並行しない。スクリプト・スキーマ・`SKILL.md`・`rule.md` は変更しない。eval は実行しない。

## Phase 1: Setup

- [ ] T001 ブランチが `049-sync-readme-evals` であることを確認し、既存 136 件が通ることを基準として記録する

## Phase 2: Foundational(失敗するテストを先に書く)

- [ ] T002 `SKILL/tests/test_scripts.py` に `EvalCaseTests` を追加する(6 ケースの構造、`fixture.sh` の実行結果、採点基準)
- [ ] T003 `SKILL/tests/test_scripts.py` に `ReadmeTests` を追加する(「Local modifications」が 1 つ、項目の語句、`find_related.py`・`related.*`・`Known limits` への言及)
- [ ] T004 追加したテストを実行し、失敗することを確認して記録する。既存 136 件が通ったままであることも確認する

## Phase 3: User Story 3 - eval の足場 (P3)

- [ ] T005 [US3] `SKILL/evals/updates-adjacent-doc/` を作成する(`case.yaml`、`prompt.md`、実行可能な `fixture.sh`、`graders/`)
- [ ] T006 [US3] `SKILL/evals/creates-doc-for-new-contract/` を作成する
- [ ] T007 [US3] `SKILL/evals/no-creation-for-internal-refactor/` を作成する
- [ ] T008 [US3] `EvalCaseTests` が通ることを確認する

## Phase 4: User Story 1 - README の同期 (P1) 🎯

- [ ] T009 [US1] `SKILL/README.md` の Layout、Scripts(表と注記)、Optional project configuration(`related`)を更新する
- [ ] T010 [US1] `SKILL/README.md` の Making it mandatory(表)と How the gate behaves を更新し、Known limits の小節を追加する
- [ ] T011 [US1] `SKILL/README.md` の Evals の節を 6 ケースと足場のみの旨で更新する

## Phase 5: User Story 2 - Local modifications の統合 (P2)

- [ ] T012 [US2] `SKILL/README.md` の 2 つの「Local modifications」を 1 つに統合し、以前の内容と新しい差分を実際の変更に基づいて列挙する
- [ ] T013 [US2] `ReadmeTests` が通ることを確認する

## Phase 6: Polish

- [ ] T014 全テストを実行し、既存 136 件を含めてすべて通ることを確認する
- [ ] T015 [P] `check_links.py --root . --changed` を実行し、エラー 0 を確認する
- [ ] T016 [P] `git diff --stat -- SKILL/scripts SKILL/schemas SKILL/SKILL.md SKILL/hooks` が空であることを確認する
- [ ] T017 完了報告の項目を整理する(eval は未実行であること、実行のための費用上限の承認が必要であること)

## Dependencies

Phase 1 → 2 → 3 → 4 → 5 → 6。T009〜T012 は同じファイル(README)を編集するため順に行う。T015・T016 は並行可能。
