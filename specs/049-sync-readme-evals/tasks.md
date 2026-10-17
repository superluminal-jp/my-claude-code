---

description: "Task list for slice S6: 公開文書の同期と振る舞い eval"
---

# Tasks: 公開文書の同期と振る舞い eval(スライス S6)

`SKILL` = `.claude/skills/maintaining-living-documentation`。`tests/test_scripts.py` を触るタスクは並行しない。スクリプト・スキーマ・`SKILL.md`・`rule.md` は変更しない。eval は実行しない。

## Phase 1: Setup

- [X] T001 ブランチが `049-sync-readme-evals` であることを確認し、既存 136 件が通ることを基準として記録する

## Phase 2: Foundational(失敗するテストを先に書く)

- [X] T002 `SKILL/tests/test_scripts.py` に `EvalCaseTests` を追加する(6 ケースの構造、`fixture.sh` の実行結果、採点基準)
- [X] T003 `SKILL/tests/test_scripts.py` に `ReadmeTests` を追加する(「Local modifications」が 1 つ、項目の語句、`find_related.py`・`related.*`・`Known limits` への言及)
- [X] T004 追加したテストを実行し、失敗することを確認して記録する。既存 136 件が通ったままであることも確認する

## Phase 3: User Story 3 - eval の足場 (P3)

- [X] T005 [US3] `SKILL/evals/updates-adjacent-doc/` を作成する(`case.yaml`、`prompt.md`、実行可能な `fixture.sh`、`graders/`)
- [X] T006 [US3] `SKILL/evals/creates-doc-for-new-contract/` を作成する
- [X] T007 [US3] `SKILL/evals/no-creation-for-internal-refactor/` を作成する
- [X] T008 [US3] `EvalCaseTests` が通ることを確認する

## Phase 4: User Story 1 - README の同期 (P1) 🎯

- [X] T009 [US1] `SKILL/README.md` の Layout、Scripts(表と注記)、Optional project configuration(`related`)を更新する
- [X] T010 [US1] `SKILL/README.md` の Making it mandatory(表)と How the gate behaves を更新し、Known limits の小節を追加する
- [X] T011 [US1] `SKILL/README.md` の Evals の節を 6 ケースと足場のみの旨で更新する

## Phase 5: User Story 2 - Local modifications の統合 (P2)

- [X] T012 [US2] `SKILL/README.md` の 2 つの「Local modifications」を 1 つに統合し、以前の内容と新しい差分を実際の変更に基づいて列挙する
- [X] T013 [US2] `ReadmeTests` が通ることを確認する

## Phase 6: Polish

- [X] T014 全テストを実行し、既存 136 件を含めてすべて通ることを確認する
- [X] T015 [P] `check_links.py --root . --changed` を実行し、エラー 0 を確認する
- [X] T016 [P] `git diff --stat -- SKILL/scripts SKILL/schemas SKILL/SKILL.md SKILL/hooks` が空であることを確認する
- [X] T017 完了報告の項目を整理する(eval は未実行であること、実行のための費用上限の承認が必要であること)

## Dependencies

Phase 1 → 2 → 3 → 4 → 5 → 6。T009〜T012 は同じファイル(README)を編集するため順に行う。T015・T016 は並行可能。

## Evidence(実装記録)

- **T001**: 既存 136 件が通る。
- **T004(失敗の記録)**: 追加した `EvalCaseTests` 2 件と `ReadmeTests` 2 件が実装前に失敗した(新しい 3 ケースが無い、README に項目が無い)。合計 140 件、既存 136 件は通ったまま。
- **T005〜T008**: eval の 3 ケース(`updates-adjacent-doc`、`creates-doc-for-new-contract`、`no-creation-for-internal-refactor`)を既存と同じ形式で作成した。構造の検査と、各 `fixture.sh` が初期コミット付きの清潔な Git リポジトリを作ることが通った。
- **T009〜T013**: README のレイアウト、スクリプトの表、設定、ゲートの挙動、Known limits、Evals、Local modifications(1 つに統合)を更新した。
- **T014**: 全 140 件が通った(約 44 秒)。
- **T015**: `check_links.py --changed` はエラー 0、警告 0。
- **T016**: スクリプト、スキーマ、`SKILL.md`、`hooks/` の差分は無い。
- **未実行**: eval は実行していない。採点基準が実際のモデル出力に合うかは未検証で、README にもその旨を記載した。実行にはユーザーの費用上限の承認が必要。
