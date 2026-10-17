---

description: "Task list for slice S1: 未処分の兄弟 README の検出"
---

# Tasks: 未処分の兄弟 README の検出(スライス S1)

**Input**: Design documents from `/specs/044-unaddressed-readme-detection/`

**Prerequisites**: plan.md、spec.md、research.md、data-model.md、contracts/、quickstart.md

**Tests**: 要求あり(テスト先行。失敗するテストを実装より先に書き、失敗を記録する)。

**Organization**: タスクはユーザーストーリー別だが、依存により実装の順序は US2(候補の列挙)→ US1(ゲート)→ US3(手順書)とする。US1 が US2 の関数に依存するため。

## 表記

- `SKILL` = `.claude/skills/maintaining-living-documentation`
- `[P]` = 他の未完了タスクと別ファイルで、依存がなく並行できる。`tests/test_scripts.py` と `scripts/stop_gate.py` を触るタスクは**並行しない**。
- 禁止事項: `SKILL/scripts/common.py` を変更しない。変更が必要と分かったら**実装を止めて**証拠(必要な関数と理由)を報告する(分岐 B3)。

---

## Phase 1: Setup(基準の確認)

- [ ] T001 作業ブランチが `044-unaddressed-readme-detection` であることを `git branch --show-current` で確認し、`python3 -B -m unittest discover -s SKILL/tests` を実行して既存 67 件がすべて通ること(基準)を記録する
- [ ] T002 `SKILL/scripts/common.py` が未変更であることの基準として `git diff --stat -- SKILL/scripts/common.py` が空であることを確認する

---

## Phase 2: Foundational(失敗するテストを先に書く)

**注意**: 実装前に、この Phase のテストをすべて書き、失敗を記録する。すべて `SKILL/tests/test_scripts.py` を編集するため、順に行う。

- [ ] T003 `SKILL/tests/test_scripts.py` に `FindRelatedTests(TempDirTestCase)` を追加し、`setUp` で Git リポジトリ(`init_repo`)に `src/x.py`、`src/README.md`、`src/design.md`、`app.py` を作ってコミットする。`find_related.py` を `run_script("find_related.py", "--root", ..., "--json")` で呼ぶヘルパーを用意する
- [ ] T004 `SKILL/tests/test_scripts.py` の `FindRelatedTests` に F1・F2・F3 を追加する: F1 `src/x.py` の変更で `src/README.md` と `src/design.md` が `kind="sibling"`、`proximity="P1"`、空でない `reason`、`source="src/x.py"` で出力され、トップレベルのキーが `changed`・`candidates`・`truncated`(0)である。F2 変更済みの文書は候補にならない。F3 `.living-documentation.json` の `exclude_globs` の対象と `.gitignore` の対象は候補にならない
- [ ] T005 `SKILL/tests/test_scripts.py` の `FindRelatedTests` に F4・F5・F6・F7 を追加する: F4 文書だけの変更では `candidates` が空。F5 ルート直下の `app.py` の変更でルート直下の `README.md` が候補になる。F6 1 つの文書が複数の変更ファイルの候補になる場合、元ファイルごとに別レコードで、`(path, source)` の昇順、2 回実行して出力が同一。F7 コミット済みの変更が `--base` で対象になる
- [ ] T006 `SKILL/tests/test_scripts.py` の `FindRelatedTests` に F8・F9・F10 を追加する: F8 Git でないディレクトリは終了コード 2 で、標準エラーに Git が必要なことを示し、実行前後でファイルの内容が一致する。F9 コードファイルの削除・名前変更でも同じディレクトリの文書が候補になり、削除された文書は候補にならない。F10 `--json` なしのテキスト出力が終了コード 0 で、候補のパスを含む
- [ ] T007 `SKILL/tests/test_scripts.py` の `StopGateTests` にヘルパー `add_src_tree()`(`src/x.py` と `src/README.md` を書いてコミット)を追加し、G1・G2・G3・G4 を追加する: G1 未処分の `src/README.md` で `decision == "block"` かつ `reason` に `src/README.md` を含む。G2 README の更新で通る。G3 未変更でも最終メッセージにパス `src/README.md` があれば通る。G4 `Documentation impact: none — …` の報告があっても、パスの言及が無ければ `block` する
- [ ] T008 `SKILL/tests/test_scripts.py` の `StopGateTests` に G5・G6・G7・G8・G9 を追加する: G5 `LIVING_DOCS_GATE=warn` は `systemMessage` のみ、`off` は何も出さない。G6 `stop_hook_active` の再入ではブロックしない。G7 `LIVING_DOCS_GATE_MAX_BLOCKS=1` で 2 回目以降は警告のみ。G8 `last_assistant_message` が無いと候補の問題は報告されない。G9 セッション開始前から存在する変更では動作しない
- [ ] T009 `SKILL/tests/test_scripts.py` の `SkillDefinitionTests` に D1・D2 を追加する: D1 `SKILL.md` が `find_related.py` のコマンドと、処分の最小限の約束(候補を更新する、または最終メッセージでパスと理由を述べる)を含む。D2 既存の定義検査(500 行未満、規則とスキルの一致)が通る
- [ ] T010 追加したテストを実行し、期待どおりに**失敗する**ことを確認して記録する(F1〜F10 は `find_related.py` が無いため、G1〜G4・G7 はゲートが候補を見ないため、D1 は SKILL.md に記載が無いため)。既存 67 件は通ったままであることも確認する

**Checkpoint**: 失敗の記録が無いまま次の Phase に進まない。

---

## Phase 3: User Story 2 - 候補を機械可読な形で確認する (Priority: P2)

**Goal**: 変更に対する P1 候補を、C1 の形で読み取り専用に列挙する。US1 の前提のため先に実装する。

**Independent Test**: T004〜T006 の F1〜F10 が通る。

- [ ] T011 [US2] `SKILL/scripts/find_related.py` を新規作成し、純粋関数 `find_candidates(root, config, changes) -> dict` を実装する。元ファイル: 除外対象でなく `classify` に `documentation` を含まないもの。候補: `common.list_files(root, config)` のうち元ファイルと同じディレクトリ(再帰しない)にあり、拡張子が文書の拡張子(`.md`、`.mdx`、`.markdown`、`.rst`、`.adoc`、`.asciidoc`)で、`is_changelog` と `decision` 分類に該当せず、変更集合にも含まれないもの。戻り値は `changed`(昇順)、`candidates`(`source`、`path`、`kind="sibling"`、`proximity="P1"`、空でない `reason`、`(path, source)` の昇順)、`truncated=0`。`common.py` は変更しない
- [ ] T012 [US2] `SKILL/scripts/find_related.py` に CLI(`--root`、`--base`、`--json`)を実装する。`audit.py` と同じ作法(`sys.dont_write_bytecode = True`、`ConfigError`/`GitError` は標準エラーに原因と「Git が必要」という代替手段を出して終了コード 2)。人間向け出力は `contracts/find-related-cli.md` の形(候補なしは `no related documents found.`)
- [ ] T013 [US2] F1〜F10 を実行してすべて通ることを確認する。通らない場合は T011・T012 を直す(テストは変更しない。テスト自体の誤りと分かった場合のみ、理由を記録して直す)
- [ ] T014 [US2] `git diff --stat -- SKILL/scripts/common.py` が空であることを確認する。空でない、または `common.py` の変更が必要と分かった場合は**ここで停止**し、分岐 B3 として証拠をユーザーに報告する

**Checkpoint**: US2 が単独で動作し、`common.py` は無変更。

---

## Phase 4: User Story 1 - 隣の README を更新し忘れたまま終わらせない (Priority: P1)

**Goal**: ゲートが、未処分の P1 候補を問題として報告する。

**Independent Test**: G1〜G9 が通り、既存の `StopGateTests` も通る。

- [ ] T015 [US1] `SKILL/scripts/stop_gate.py` に関数 `unaddressed_related(root, config, changes, last_message) -> list[str]` を追加する。`find_related.find_candidates` を(evaluate と同様にローカル import で)呼び、候補の `path` が変更集合にも `last_message` にも(ルート相対 POSIX パスの部分文字列として)現れないものを集める。`path` で重複を除き、元の変更ファイルを併記し、`path` の昇順、10 件を超える場合は `(+N more)` を付ける。文面は `contracts/gate-problem.md` の形。`last_message is None` なら空のリストを返す
- [ ] T016 [US1] `SKILL/scripts/stop_gate.py` の `evaluate()` に T015 の呼び出しを、完了報告の検査の後に追加し、結果を `problems` に加える。`on_stop` のブロック回数、強制の度合い、再入の処理は変更しない
- [ ] T017 [US1] G1〜G9 と既存の `StopGateTests`(すべて)を実行して通ることを確認する。既存のテストが落ちた場合は、既存の期待を変えずに T015・T016 を直す
- [ ] T018 [US1] `git diff --stat -- SKILL/scripts/common.py` が空であることを再確認する(空でなければ B3 として停止して報告)

**Checkpoint**: US1 が単独で動作し、US2 と合わせて端から端までの経路が成立する。

---

## Phase 5: User Story 3 - 手順書に新しい確認手順が載っている (Priority: P3)

**Goal**: SKILL.md の手順にコマンドと処分の最小限の約束を載せる。

**Independent Test**: D1・D2 が通る。

- [ ] T019 [US3] `SKILL/SKILL.md` の「Workflow」手順 3(Assess impact)に、`python3 "${CLAUDE_SKILL_DIR}/scripts/find_related.py" --root "${CLAUDE_PROJECT_DIR}"` を 1 行(`audit.py` のコマンドの直後)で追加し、処分の最小限の約束を 1〜2 文で追記する: 変更されたファイルの隣の文書(候補)は、更新するか、最終メッセージでそのパスを挙げて変更不要の理由を述べる。ゲートが未処分の候補を検出することも 1 文で示す。報告の書式(`Documentation impact` の各行)は変更しない
- [ ] T020 [US3] D1・D2 と `SkillDefinitionTests` の全件を実行して通ることを確認する。`wc -l SKILL/SKILL.md` が 500 未満であることも確認する

**Checkpoint**: 3 つのストーリーがすべて独立に検証済み。

---

## Phase 6: Polish & Cross-Cutting

- [ ] T021 全テスト `python3 -B -m unittest discover -s SKILL/tests -v` を実行し、既存 67 件を含めてすべて通ることを確認する(SC-004)。件数と結果を記録する
- [ ] T022 [P] `python3 SKILL/scripts/check_links.py --root . --changed` を実行し、エラー 0 を確認する。失敗した場合は直して再実行する
- [ ] T023 [P] `quickstart.md` の手順 2 を一時ディレクトリで実行し、期待どおり(`changed` が `["src/x.py"]`、候補が `src/README.md`)になることを確認する。作業ツリー(このリポジトリ)が書き換わっていないことも確認する
- [ ] T024 実測の予備観察として、`python3 SKILL/scripts/find_related.py --root . --base main --json` を実行し、このブランチの変更に対する候補の件数と内容を記録する(仮定 A1 の予備データ。S2 で本格的に評価する)
- [ ] T025 スキルの完了報告(`Documentation impact`)に含める項目を整理する: 更新した文書は `SKILL.md` のみ、スキル README は S6 の範囲(`Unresolved` に記載)、検査と結果

---

## Dependencies & Execution Order

- Phase 1 → Phase 2 → Phase 3(US2) → Phase 4(US1) → Phase 5(US3) → Phase 6。
- Phase 2 のテスト追加(T003〜T009)は同じファイルを編集するため**順に**行う。T010 は T003〜T009 の後。
- US1(Phase 4)は US2(Phase 3)の `find_candidates` に依存する。そのため優先度(P1 → P2)の順ではなく、US2 → US1 の順で実装する。
- `scripts/stop_gate.py` を触るタスク(T015、T016)は並行しない。
- 並行可能: T022 と T023(どちらも読み取りのみで別の出力)。
- 停止条件: `common.py` の変更が必要と分かった時点(T014、T018)で B3 として停止・報告。

## Implementation Strategy

1. Phase 1〜2 で基準と失敗するテストをそろえる。
2. MVP は US2 + US1(Phase 3〜4)。この時点で「未処分の README が止まる」経路が成立する。
3. US3(手順書)と Polish で仕上げる。各 Phase の終わりでテストを実行し、問題があればその Phase 内で直す。

## Notes

- 総タスク数: 25(Setup 2、Foundational 8、US2 4、US1 4、US3 2、Polish 5)。
- テストの ID(F1〜F10、G1〜G9、D1〜D2)は plan.md の表に対応する。
- 範囲外(P0・P2・変更履歴の候補、`related.*` の設定キー、上限、空の理由の拒否、作成規則、README・eval)に手を出さない。
