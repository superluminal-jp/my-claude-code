---

description: "Task list for slice S5: 層・配置・近接性の実践を文書化する"
---

# Tasks: 層・配置・近接性の実践を文書化する(スライス S5)

**Input**: `/specs/046-layers-placement-proximity/`(plan.md、spec.md、quickstart.md)

**Tests**: 要求あり(テスト先行)。

`SKILL` = `.claude/skills/maintaining-living-documentation`。`tests/test_scripts.py` を触るタスクは並行しない。`common.py` とスクリプトは変更しない。

## Phase 1: Setup

- [ ] T001 ブランチが `046-layers-placement-proximity` であることを確認し、既存 109 件が通ることを基準として記録する

## Phase 2: Foundational(失敗するテストを先に書く)

- [ ] T002 `SKILL/tests/test_scripts.py` に `PracticesDocumentTests` を追加し、P1(節の存在、9 層の表、各行 5 列、Basis が `Sourced` または `Design decision` で始まる)を書く
- [ ] T003 `SKILL/tests/test_scripts.py` の `PracticesDocumentTests` に P2(引用された書誌キーがすべて `bibliography.bib` にある、新しい 4 キー `GoogleSWE2020`・`PEP8`・`LinuxKernelStyle`・`Diataxis` がすべて引用されている)と P3(P0〜P4 と README の設計判断のラベル、`No source reviewed presents a single hierarchy` の文)を書く
- [ ] T004 追加したテストを実行し、失敗することを確認して記録する。既存 109 件が通ったままであることも確認する

## Phase 3: User Story 1 - 規則を参照できる (P1) 🎯 MVP

- [ ] T005 [US1] `SKILL/references/bibliography.bib` に `GoogleSWE2020`、`PEP8`、`LinuxKernelStyle`、`Diataxis` を追加する(plan.md の確認済みの情報のみ。未確認の項目は書かない)
- [ ] T006 [US1] `SKILL/references/practices.md` の「Decision records」の後、「Evidence and uncertainty」の前に、節 `## Layers, placement, and proximity` の導入と層の表(9 層)を追加する
- [ ] T007 [US1] P1・P2 のうち表と書誌に関する検査が通ることを確認する

## Phase 4: User Story 2 - コメントの書き分けと置き場所 (P2)

- [ ] T008 [US2] 節に「Code comments: two audiences」(API コメントと実装コメント。出典の差異と、このスキルの読み方を設計判断として明記)を追加する
- [ ] T009 [US2] 節に「Placement patterns」(対象の隣、トピック別の独立した文書群、所有者のない共有 wiki を避ける、正本と重複の廃止、リンクのみのランディングページ、1 文書 1 目的、参照文書の単一情報源)を、出典の参照付きで追加する。鮮度の日付は観察された実践としてのみ書く

## Phase 5: User Story 3 - 近接性が設計判断であることの明示 (P3)

- [ ] T010 [US3] 節に「Proximity (design decision)」を追加する: P0〜P4 の定義、ディレクトリ単位の README(P1)の扱い、「No source reviewed presents a single hierarchy from the project README down to code comments」の文と、C4・arc42・Diátaxis がそれぞれ別の軸であることの説明
- [ ] T011 [US3] P1〜P3 のすべてが通ることを確認する

## Phase 6: Polish

- [ ] T012 全テスト(既存 109 件 + 新規)を実行し、すべて通ることを確認する
- [ ] T013 [P] `check_links.py --root . --changed` を実行し、エラー 0 を確認する
- [ ] T014 [P] `git diff --stat -- SKILL/scripts SKILL/SKILL.md SKILL/README.md` が空であることを確認する(範囲外の変更が無いこと)
- [ ] T015 完了報告に含める項目を整理する(更新した文書、`SKILL.md` の同期は S4、README は S6 として `Unresolved`、検査と結果)

## Dependencies

Phase 1 → 2 → 3 → 4 → 5 → 6。T005 と T006 は異なるファイルだが、T006 が T005 のキーを引用するため順に行う。
