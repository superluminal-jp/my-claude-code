---
description: "Task list for 061: 実行の証拠で、葉・親・システムの検証を別々に判定する"
---

# Tasks: 実行の証拠で、葉・親・システムの検証を別々に判定する

背景、用語、既定 D1〜D6、規則 A は同じディレクトリの `spec.md`、欄の詳細は `contracts/manifest.md` にある。作業は、ブランチ `feat/goal-refinement`(コミット d0736a2)から作ったワークツリー `my-claude-code-worktrees/change-assurance`(ブランチ `feat/change-assurance`)で行う。「スキル」は `.claude/skills/change-assurance/`、「検査器」はその `scripts/assure.py` を指す。

- [X] T001 [US1] [US2] 要求グラフと検証の記録のフィクスチャ(spec の User Story 1 のシナリオ1〜8、User Story 2 のシナリオ1〜4、M-00〜M-02 の負例)を `tests/fixtures/` に作り、テストを書き、失敗を確かめる(Red)。結果: 21件(T003 を含む)がすべて失敗した(subTest を含め失敗2件・エラー23件)
- [X] T002 [US1] [US2] 検査器の `check` と `gate` を実装する(Green)。結果: T004 とあわせて21件が通った(Python 3.14.3 と 3.9.6)
- [X] T003 [US3] JUnit XML のフィクスチャ(合格・失敗・スキップ・プロパティ・名前の中の ID・DOCTYPE)とテストを書き、失敗を確かめる(Red)。結果: T001 に含めて書いた
- [X] T004 [US3] `collect-junit` を実装する(Green)。結果: 通った
- [X] T005 [US3] `SKILL.md`、`references/manifest.md`、`references/reviewer.md`、例を書く。`tests/run-config-pyramid.sh` の自作スキルの一覧と名前のパターンに `change-assurance` を加え、親子の規則を含めて通ることを確かめる。結果: `run-config-pyramid` 57件が通った。このリポジトリで初めての実際の親スキルであり、宣言した子の名前による参照(spec 058)と、互換モードの S-10 も通った
- [X] T006 `tests/run-change-assurance-skill.sh` を書き、CI の必須ジョブに加える。`tests/run-refinement-checker.sh` の `NOT RUN` の4行を、`change-assurance` のテストで実装済みと示す行に改める(SC-002)。結果: `run-change-assurance-skill` 3件、`run-refinement-checker` 5件が通った。後者の `NOT RUN` の4行は消した
- [X] T007 README の英日を改め、ローカルの検査をすべて実行して件数を記録する。結果: `run-config-pyramid` 57件、`run-readme-skill-index` 33件、`run-removed-guardrails` 4件、`run-package-safety-bundle` 21件、`run-refinement-checker` 5件、`run-change-assurance-skill` 3件、`run-secure-logging-skill` 40件、`run-digital-agency-frontend-skill` 74件、`run-install` 成功、`pyramid-structure` の単体テストが通った
- [ ] T008 `/code-review` で差分をレビューし、確かめた指摘を直して記録する
