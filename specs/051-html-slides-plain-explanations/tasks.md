---

description: "Task list for 051: HTML専用のDADSスライドと、初学者が追える説明"
---

# Tasks: HTML専用のDADSスライドと、初学者が追える説明

`SKILL` = `.claude/skills/digital-agency-slides`。

## Phase 1: Setup

- [X] T001 現行のスライドスキルのテスト(101件)が通ることを基準として記録する

## Phase 2: Foundational(失敗するテストを先に書く)

- [X] T002 `tests/run-digital-agency-slides-skill.sh` の契約を新しい仕様に書き換える(変換の痕跡なし、構成、DADSのマークアップ、検査の参照文書)
- [X] T003 `tests/assert_deck_units.py` を `lint` と `preview` だけの CLI に合わせて書き換える
- [X] T004 `tests/fixtures/slides/` に3つの fixture を作り、`tests/assert_lint.py` で所見のコードを検査する。`assert_classification.py` と `classification.html` を削除する
- [X] T005 `tests/run-config-pyramid.sh` に RULE-12 を加える
- [X] T006 書き換えたテストを現行の実装に対して実行し、失敗することを記録する

## Phase 3: User Story 2 - HTMLだけで完結しDADSに準拠する (P1)

- [X] T007 [US2] `SKILL/scripts/check_slides.js` を作り、`extract_slides.js` を削除する
- [X] T008 [US2] `SKILL/scripts/deck.py` を `lint`(`--json`)と `preview` に絞る。`requirements.txt` と `setup.sh` から変換の依存を除く
- [X] T009 [US2] `SKILL/scripts/fetch-dads-assets.sh` の既定コンポーネントをテンプレートが使うものに合わせる
- [X] T010 [US2] `SKILL/assets/slide.css` から変換の制約と見出しの再実装を除き、木のブロックを加える
- [X] T011 [US2] `SKILL/references/pptx-conversion.md` を削除し、`SKILL/references/deck-checks.md` を作る。`authoring-contract.md` と `asset-sourcing.md` を更新する

## Phase 4: User Story 1 - 前提 → 結論 → 論点の木 (P1) 🎯

- [X] T012 [US1] `SKILL/references/slide-design.md` の構成の節を木に基づく手順と枚数の上限に書き換える
- [X] T013 [US1] `SKILL/assets/deck-template.html` を本編7枚 + 付録1枚の構成で作り直す
- [X] T014 [US1] `SKILL/SKILL.md` を書き換える

## Phase 5: User Story 3 - 初学者が追える説明 (P2)

- [X] T015 [US3] `.claude/rules/pyramid-principle.md` に「前提と用語」の節を加える
- [X] T016 [US3] `claude-ai-system-prompt.md` に同じ義務を加え、文字数の記載を更新する

## Phase 6: Polish

- [X] T017 README.md と README.ja.md、ADR-0018、`docs/claude-config-design.md` を同期する
- [X] T018 全テストを実行し、`preview` の画像を目で確認する
