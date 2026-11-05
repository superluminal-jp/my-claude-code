---
description: "Task list for 063: 介入時間の削減と品質の維持を、事前に固定した基準で判定する"
---

# Tasks: 介入時間の削減と品質の維持を、事前に固定した基準で判定する

背景と既定 D1〜D6 は同じディレクトリの `spec.md` にある。作業は、ブランチ `feat/review-card` から作ったワークツリー `my-claude-code-worktrees/pilot-metrics`(ブランチ `feat/pilot-metrics`)で行った。

- [X] T001 [US1] [US2] spec の User Story 1・2 のシナリオを `tests/test_pilot.py` に合成のデータで書き、失敗を確かめる(Red)。結果: 10件が失敗した(コミット e0f787b)
- [X] T002 [US1] [US2] `scripts/pilot.py` を実装する(Green)。結果: 54件(当時の change-assurance の全テスト)が Python 3.14.3 と 3.9.6 で通った
- [X] T003 PR #115 のレビューの修正を取り込む。結果: 62件が通った
- [X] T004 `references/pilot.md`(事前登録、記録、判定の手順)、`SKILL.md` の節、README の英日を書く
- [ ] T005 ローカルの検査をすべて実行し、`/code-review` で差分をレビューして記録する

実験そのもの(実案件の選定、割り当て、人の作業時間の計測)と、その結果は、本仕様に含まない。
