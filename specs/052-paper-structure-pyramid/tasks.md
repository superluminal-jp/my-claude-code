---

description: "Task list for 052: 論文の構成とミント・ピラミッドの統合"
---

# Tasks: 論文の構成とミント・ピラミッドの統合

## Phase 1: 失敗するテストを先に書く

- [X] T001 `tests/run-config-pyramid.sh` に RULE-14(部の順序)と RULE-15(段落の先頭文)を加える
- [X] T002 `tests/run-digital-agency-slides-skill.sh` に DSN-17、DSN-18、TPL-13、TPL-14 を加える
- [X] T003 実行して6件が失敗することを確認する

## Phase 2: User Story 1 - 回答と文章 (P1)

- [X] T004 `.claude/rules/pyramid-principle.md` に「Parts」の節と出典を加える

## Phase 3: User Story 2 - スライド (P1)

- [X] T005 `slide-design.md` に部とスライドの対応表を加え、前提と依頼の役割を更新する
- [X] T006 テンプレートの前提スライドに方法の行、依頼スライドに限界の行を加え、プレビューを目で確認する
- [X] T007 `SKILL.md` の手順と `authoring-contract.md` の確認項目を更新する

## Phase 4: User Story 3 - Claude.ai (P2)

- [X] T008 `claude-ai-system-prompt.md` に部の順序を加え、7,000 字以下に収め、文字数の記載を更新する

## Phase 5: Polish

- [X] T009 README.md と README.ja.md を同期する
- [X] T010 全テストとリンク検査を実行する
