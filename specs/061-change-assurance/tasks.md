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

## 中断時点の記録(2026-11-06、利用量の上限による)

T008 の `/code-review`(労力 medium、PR #114)は10件を指摘した。9件を受け入れ、回帰テストを先に書いた(このコミットの時点で12件が失敗する Red)。修正はまだしていない。

| # | 指摘 | 予定の対応 |
|---|---|---|
| 1 | 受け入れ条件のない空の要求グラフで `pass` になる | A-01 で、受け入れ条件が1つもなければ `blocked` |
| 2 | すべてを `not_applicable` にすると証拠なしで `pass` になる | A-03 で、各要求に `passed` の検査が1つ以上なければ `blocked` |
| 3 | `rejected` の承認が高リスク以外で無視される | リスクにかかわらず `fail` |
| 4 | 末尾が改行のコミットを受け入れる(`$` の挙動) | `fullmatch` にする |
| 5 | 承認者と実装担当の名前を、大文字小文字と空白を区別して比べる | 両端の空白を除き `casefold` して比べる |
| 6 | CDATA の中の `<!DOCTYPE` で正しいレポートを拒否する | 根の要素より前(プロローグ)だけを調べる |
| 7 | 合格とスキップの混在の理由が「スキップだけ」と誤る | 件数を正しく書く |
| 8 | ID の境界に `.` を含めない | 境界の文字に `.` を加える |
| 9 | `--format` をサブコマンドの後に置けない | サブコマンドにも `--format` を加える(既定は `SUPPRESS`) |
| 10 | goal-refinement の検査器との重複、文字の出力での違反の二重表示 | 重複は却下(spec 058 はパスでの参照を禁じる)。二重表示は、判定の文字の出力で理由だけを示すよう直す |

Phase 4 の作りかけの変更(`load_graph` が要求の ID を返す、判定が検査ごとの結果を返す)は、ワークツリー `my-claude-code-worktrees/review-card` から外し、パッチとして退避した。ブランチ `feat/review-card` には仕様 062 と失敗するテスト10件がコミット済みである。Phase 5 は未着手。
