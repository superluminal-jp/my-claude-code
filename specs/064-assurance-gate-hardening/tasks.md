---
description: "Task list for 064: 工程を飛ばしても、保証の判定が合格を出さないようにする"
---

# Tasks: 工程を飛ばしても、保証の判定が合格を出さないようにする

背景と決めた事項 D1〜D7 は同じディレクトリの `spec.md` にある。作業は、`origin/main`(コミット 07caea0)から作ったブランチ `feat/assurance-gate-hardening` で行った。

- [X] T001 会話で示した失敗注入の8件を、`origin/main` の検査器で再現する。結果: 8件とも `pass`(終了コード 0)だった。`goal-refinement` の検査器は、構造の4件のうち3件を違反とし、`L1` だけの親は合格させた
- [X] T002 [US1] [US2] [US3] User Story 1〜3 のシナリオをテストに書き、失敗を確かめる(Red)。結果: `goal-refinement` の75件のうち2件、`change-assurance` の110件のうち37件(失敗12、エラー25。エラーは `--review` が未定義の引数だったため)が失敗した。`tests/assert_assurance_parity.py` は16のグラフのうち7つで食い違った(`p1-06-parent-without-acceptance.json` の空の受け入れ条件を含む)
- [X] T003 [US1] `check_graph.py` に S-12 を加える(Green)。既存のテスト `test_children_of_the_wrong_type_are_reported_once` は、子のない親から作った L1 の条件のために S-12 にも当たったので、S-00 だけを確かめる意図を保つよう、子のある親から作るようにした
- [X] T004 [US1] [US2] [US3] `assure.py` に A-09、A-08 の変更、A-10、`--review` を実装する(Green)。既存のテストのうち、`medium` か `high` の変更で別の規則を確かめるものには、答えられた保証レビューの記録を渡した(SC-003)。レビューカードのテストの反証の記録は、`resolution` の代わりに定義にない欄 `reason` を書いていたので、`resolution` に直した
- [X] T005 `SKILL.md`(保証レビューを判定の前に移す)、`references/manifest.md`、`references/reviewer.md`、`goal-refinement` の `references/checker.md`、README の英日を書く。例 `examples/assurance-review.example.json` を加える
- [X] T006 検査をすべて実行する。結果: `goal-refinement` の75件と `change-assurance` の110件が Python 3.11、3.12、3.13 で通る。`tests/run-*.sh` はすべて終了コード 0。会話の失敗注入の8件は、すべて `blocked` になった。Python 3.9 では実行していない(この環境にない)
