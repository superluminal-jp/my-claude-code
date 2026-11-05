---
description: "Task list for 062: 判定の結果と証拠を、1画面のレビューカードに表示する"
---

# Tasks: 判定の結果と証拠を、1画面のレビューカードに表示する

背景と既定 D1〜D5 は同じディレクトリの `spec.md` にある。作業は、ブランチ `feat/change-assurance` から作ったワークツリー `my-claude-code-worktrees/review-card`(ブランチ `feat/review-card`)で行った。「検査器」は `.claude/skills/change-assurance/scripts/assure.py` を指す。

- [X] T001 [US1] [US2] spec の User Story 1・2 のシナリオを `tests/test_card.py` に書き、失敗を確かめる(Red)。結果: 10件が失敗した(コミット 9d4d34b)
- [X] T002 PR #114 の `/code-review` の指摘の修正(コミット 9a1768e)を取り込む。作りかけの変更は、修正と重なる部分を除いて加え直した
- [X] T003 [US1] [US2] `card` を実装する(Green)。結果: 44件(Phase 3 の34件とカードの10件)が Python 3.14.3 と 3.9.6 で通った
- [X] T004 `SKILL.md` の手順7、`references/manifest.md` のカードの節、例の問題カード、まとめの検査の CA-04、README の英日を加える
- [ ] T005 ローカルの検査をすべて実行し、`/code-review` で差分をレビューして記録する
