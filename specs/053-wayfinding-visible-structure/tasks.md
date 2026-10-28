---

description: "Task list for 053: 現在地の分かるスライドと、見て分かる文章構造"
---

# Tasks: 現在地の分かるスライドと、見て分かる文章構造

## Phase 1: 失敗するテストを先に書く

- [X] T001 fixture `tests/fixtures/slides/tracker.html` と LINT-13・14 を加える
- [X] T002 契約テスト DSN-19・20、CHK-06、CSS-11、TPL-15〜17、TOOL-19 と、RULE-16・17 を加える
- [X] T003 実行して12件が失敗することを確認する

## Phase 2: User Story 1 - 現在地 (P1)

- [X] T004 `check_slides.js` に `tracker` と `tracker-missing` を加え、密度の検査から現在地の表示を除く
- [X] T005 `slide.css` に `sld-tracker` を加える
- [X] T006 テンプレートの本編6枚に現在地の表示を置き、フッターを「n / 7」「付録 1」にする。プレビューを目で確認する

## Phase 3: User Story 2 - 階層の見た目 (P1)

- [X] T007 `slide-design.md` に「Making the structure visible」を加え、`authoring-contract.md`、`deck-checks.md`、`SKILL.md` を更新する

## Phase 4: User Story 3 - 回答と文章 (P2)

- [X] T008 `pyramid-principle.md` に見出しの番号付けと太字の主張、リストと表の使い分けを加える
- [X] T009 `claude-ai-system-prompt.md` に同じ内容を加え、7,000 字以下に収める

## Phase 5: Polish

- [X] T010 README.md と README.ja.md を同期する
- [X] T011 全テストとリンク検査を実行する
