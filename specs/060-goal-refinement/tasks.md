---
description: "Task list for 060: 問題カード・要求グラフ・反証の記録を結び、実装へ進めるかを判定する"
---

# Tasks: 問題カード・要求グラフ・反証の記録を結び、実装へ進めるかを判定する

背景、用語、既定 D1〜D8、規則 C・R・G は同じディレクトリの `spec.md`、欄の詳細は `contracts/declarations.md` にある。作業は、ブランチ `feat/refinement-graph-checker`(コミット 0f5a148)から作ったワークツリー `my-claude-code-worktrees/goal-refinement`(ブランチ `feat/goal-refinement`)で行う。「スキル」は `.claude/skills/goal-refinement/`、「検査器」はその `scripts/check_graph.py` を指す。

## Phase 1: Setup

- [X] T001 変更前の状態を記録する(spec 059 の最終の件数を基準にする)。結果: spec 059 の最終のコミット 0f5a148 で、検査器のテスト49件と既存のローカルの検査がすべて通っていた(spec 059 の tasks.md T024 と PR #112 の CI)
- [X] T002 `git mv` で `tools/refinement-checker/` をスキルへ移す(`check_graph.py` → `scripts/`、`examples/`、`tests/`)。検査器の英語の README は `references/checker.md` へ移して T007 でスキルの文書に合わせ、日本語の README は削除する(スキルの参照文書は英語だけというリポジトリの慣例)。`tests/run-refinement-checker.sh` のパスを移した先へ変え、互換モードのテスト P1-11 をパッケージのテストから外す(まとめの検査の RC-04 が引き続き確かめる)。spec 059 の49件から P1-11 の1件を除いた48件が通ることを確かめる。結果: 48件が通った。まとめの検査の RC-01〜RC-04 も通った

## Phase 2: User Story 1 - 根拠のない問題を止める (P1)

- [X] T003 [US1] 問題カードの正例と負例(P2-01、P2-02、`refuted` で反対の根拠がない例、型の誤り)を `tests/fixtures/gate/` に作り、テストを書き、失敗を確かめる(Red)。結果: 新しい23件で24件の失敗(subTest を含む)。判定の入力の誤りのテストは、未実装の `--gate` が引数の誤り(終了コード 2)になるために通っていた
- [X] T004 [US1] 検査器に問題カードの読み込みと C-00〜C-03 を加える(Green)。結果: T006 とあわせて71件が通った(Python 3.14.3 と 3.9.6)

## Phase 3: User Story 2 - 3つを結び、未対応の異議で止める (P1)

- [X] T005 [US2] v2 の要求グラフ、反証の記録、判定の正例と負例(spec の User Story 2 のシナリオ1〜7)を作り、テストを書き、失敗を確かめる(Red)。結果: T003 に含めて書いた
- [X] T006 [US2] 検査器に v2 の要求グラフ、反証の記録(R-00〜R-03)、`--gate`(G-01〜G-04)を加える(Green)。結果: 71件が通った

## Phase 4: User Story 3 - スキルの手順と反証役の評価 (P2)

- [ ] T007 [US3] `SKILL.md`、`references/challenger.md`、`references/declarations.md` を書く。`tests/run-config-pyramid.sh` の `authored_skills`、RULE-03、SKILL-06 のパターンに `goal-refinement` を加え、検査が通ることを確かめる
- [ ] T008 [US3] 判定が `ready` になる例の1組を `examples/` に置き、まとめの検査で確かめる
- [ ] T009 [US3] 反証役の評価: P2-03〜P2-06 の入力を `tests/fixtures/challenger/` に置き、`references/challenger.md` の指示文で読み取り専用のサブエージェントを4件起動し、期待する種類の指摘が出たかを本ファイルに記録する

## Phase 5: Polish

- [ ] T010 README の英日(スキルの説明、構成、検証)を改め、`tests/run-readme-skill-index.sh` が通ることを確かめる
- [ ] T011 ローカルの検査をすべて実行し、件数を記録する
- [ ] T012 `/code-review` で差分をレビューし、確かめた指摘を直して記録する。仕様を会話を見ていないサブエージェントに読ませて直す
