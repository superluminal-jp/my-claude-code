---

description: "Task list for slice S3: 空の「不要」理由を弾く"
---

# Tasks: 空の「不要」理由を弾く(スライス S3)

**Input**: Design documents from `/specs/045-reject-empty-none-reason/`

**Prerequisites**: plan.md、spec.md、research.md、data-model.md、contracts/report-grammar.md、quickstart.md

**Tests**: 要求あり(テスト先行。失敗するテストを実装より先に書き、失敗を記録する)。

**Organization**: ユーザーストーリー別(US1: 理由のない「不要」を通さない、US2: 文書を変えていないなら変えない理由を言わせる)。テストは仕様の指示で先に書くため、Phase 2 にまとめる。

## 表記

- `SKILL` = `.claude/skills/maintaining-living-documentation`
- `tests/test_scripts.py` と `scripts/stop_gate.py` を触るタスクは**並行しない**。
- 禁止事項: `SKILL/scripts/common.py` を変更しない。変更が必要と分かったら**実装を止めて**証拠を報告する。

---

## Phase 1: Setup

- [X] T001 作業ブランチが `045-reject-empty-none-reason` であることを確認し、`python3 -B -m unittest discover -s SKILL/tests` で既存 90 件がすべて通ること、`git diff --stat -- SKILL/scripts/common.py` が空であることを基準として記録する

---

## Phase 2: Foundational(失敗するテストを先に書く)

**注意**: すべて `SKILL/tests/test_scripts.py` を編集するため順に行う。実装前に失敗を記録するまで次の Phase に進まない。

- [X] T002 `SKILL/tests/test_scripts.py` に `ReportQualityTests(unittest.TestCase)` を追加し(`import stop_gate` を使う)、R1 を書く: `stop_gate.is_boilerplate` が、空、空白のみ、`n/a`、`N/A`、`na`、`none`、`nil`、`no`、`nothing`、`no impact`、`No changes.`、`not applicable`、`なし`、`なし。`、`無し`、`該当なし`、`変更なし`、`影響なし`、`-`、`—`、`...`、`<reason>`、`<what is unchanged and why>`、全角の `ＮＯＮＥ` のすべてで `True` を返す(`subTest`)
- [X] T003 `SKILL/tests/test_scripts.py` の `ReportQualityTests` に R2・R3 を追加する: R2 `is_boilerplate` が `internal refactor`、`comment only`、`内部の変数名のみの変更で公開される挙動は不変`、`no behavior change: only renames a private helper` で `False`。R3 `stop_gate.none_declarations(message)` が、区切り `—` `–` `-` `:` `：` のそれぞれ、接頭辞(`- `、`* `、`> `、`**Documentation impact**:`)、大文字小文字違い、複数行(出現順)で理由を返し、区切りなしは `""`、文中(行頭でない)の言及は対象外
- [X] T004 `SKILL/tests/test_scripts.py` の `ReportQualityTests` に R4 を追加する: `stop_gate.report_lines(message)` が `(updated, no_change)` を返し、`Updated:` 行(接頭辞あり・なし、内容が空、テンプレート表記 `<file> — <what changed and why>` のまま)と、`No change needed: <area> — <reason>`(区切りは `—` `–` と空白に挟まれた `-`。パス中のハイフン `my-file` では分割しない)、区切りなしの行全体、を扱う
- [X] T005 `SKILL/tests/test_scripts.py` の `StopGateTests` に、実装系の変更だけがある状況(`app.py` を変更、文書は未変更)の補助 `send(message, **env)` を追加し、G1・G2・G3 を書く: G1 `Documentation impact: none —`(理由なし)で `block` かつ `reason` に直し方(`specific reason`)を含む。G2 `n/a` と `なし。` の理由で `block`。G3 具体的な理由(英語と日本語)で通る
- [X] T006 `SKILL/tests/test_scripts.py` の `StopGateTests` に G4・G5・G6・G7 を書く: G4 見出し `Documentation impact` のみ(実装系の変更のみ)で `block`。G5 同じ見出しのみでも文書が変更されていれば通る。G6 `Updated: app.py — …` で通る、`No change needed: x — <具体的な理由>` で通る、`No change needed: x — n/a` で `block`。G7 複数行の報告(`Updated` / `No change needed` / `Unresolved` / `Proposed decision record` / `Checks`)が具体的な内容で通る
- [X] T007 `SKILL/tests/test_scripts.py` の `StopGateTests` に G8〜G12 を書く: G8 文書が変更されていても無効な不要宣言は `block`、複数の不要宣言のうち 1 つでも無効なら `block`。G9 `LIVING_DOCS_GATE=warn` は `systemMessage` のみ、`off` は何も出さない。G10 `LIVING_DOCS_GATE_MAX_BLOCKS=1` で 2 回目は警告のみ、`stop_hook_active` の再入ではブロックしない。G11 S1 の未処分の兄弟 README の問題と同時に発生した場合、1 回のブロックの `reason` に両方を含む(`src/` を用意して `src/x.py` を変更)。G12 `last_assistant_message` が無いとこの検査は行われない
- [X] T008 追加したテストを実行し、期待どおりに**失敗する**ことを確認して記録する(R1〜R4 は関数が無いため `AttributeError`、G1・G2・G4・G6(定型句)・G8・G10・G11 は新しい検査が無いため)。通るテスト(G3・G5・G6 の有効な側・G7・G9・G12)は回帰の番人として数える。既存 90 件が通ったままであることも確認する

**Checkpoint**: 失敗の記録が無いまま次の Phase に進まない。

---

## Phase 3: User Story 1 - 理由のない「不要」を通さない (Priority: P1) 🎯 MVP

**Goal**: 理由が空・定型句の不要宣言を、常に無効な報告として問題にする。

**Independent Test**: R1〜R3 と G1・G2・G3・G8〜G12 が通り、既存のテストも通る。

- [X] T009 [US1] `SKILL/scripts/stop_gate.py` に、`import unicodedata` と、`BOILERPLATE_REASONS`(data-model.md の固定の一覧: `n/a`、`na`、`none`、`nil`、`no`、`nothing`、`no impact`、`no change`、`no changes`、`no change needed`、`not applicable`、`no documentation impact`、`なし`、`無し`、`該当なし`、`変更なし`、`影響なし`、`特になし`)、`normalize_reason(text)`(NFKC → 大文字小文字の畳み込み → `<…>` の除去 → 強調記号 `*`、`_`、`` ` `` の除去 → 両端の空白・句読点・記号(Unicode カテゴリ P*/S*/Z*)の除去)、`is_boilerplate(text)`(正規化後が空、英数字・かなを含まない、または一覧に一致)を追加する
- [X] T010 [US1] `SKILL/scripts/stop_gate.py` に `none_declarations(message) -> list[str]` を追加する: 行頭(空白、`>`、`-`、`*`、`•`、`_`、`#` の接頭辞を許す)の `Documentation impact`、任意のコロン、強調記号、`none` の語境界の後ろで、区切り(`—`、`–`、`-`、`:`、`：`)に続く部分を理由として返す。区切りが無ければ `""`。大文字小文字を問わない
- [X] T011 [US1] R1・R2・R3 を実行して通ることを確認する。通らなければ T009・T010 を直す(テストは変更しない。テスト自体の誤りと分かった場合のみ理由を記録して直す)
- [X] T012 [US1] `SKILL/scripts/stop_gate.py` に `report_quality_problems(message, needs_report, docs_changed) -> list[str]` を追加し(この時点では問題 A のみ: 無効な不要宣言が 1 つでもあれば `contracts/report-grammar.md` の文面で 1 件返す)、`evaluate()` の「見出しが無い」問題の後、`unaddressed_related` の前に呼び出す(`last_message is None` なら呼ばない。`docs_changed` は `categories` に `documentation` が含まれるか)
- [X] T013 [US1] G1・G2・G3・G8〜G12 と既存の `StopGateTests` のすべてを実行して通ることを確認し、`git diff --stat -- SKILL/scripts/common.py` が空であることを確認する(空でなければ停止して報告)

**Checkpoint**: US1 が単独で動作する。

---

## Phase 4: User Story 2 - 文書を変えていないなら変えない理由を言わせる (Priority: P2)

**Goal**: 実装系の変更があり文書が未変更なら、有効な根拠を必須にする。

**Independent Test**: R4 と G4〜G7 が通り、US1 のテストと既存のテストも通る。

- [X] T014 [US2] `SKILL/scripts/stop_gate.py` に `report_lines(message) -> tuple[list[str], list[str]]` を追加する: `Updated:` 行の内容(`<…>` を除いて英数字・かながあるもの)と、`No change needed:` 行の理由(最初の `—` / `–` / 空白に挟まれた `-` より後ろ。区切りが無ければ行全体)を、それぞれ返す。行頭の接頭辞は T010 と同じ
- [X] T015 [US2] `SKILL/scripts/stop_gate.py` の `report_quality_problems` に問題 B を追加する: `needs_report` が非空、見出し(`REPORT_MARKER`)があり、`docs_changed` が偽、不要宣言が 0 件で、内容のある `Updated:` 行も定型句でない理由の `No change needed:` 行も無いとき、`contracts/report-grammar.md` の文面で 1 件返す。有効な不要宣言があれば根拠として認め、無効な不要宣言があれば問題 A のみ(B は出さない)
- [X] T016 [US2] R4 と G4〜G7、続けて `StopGateTests` と `ReportQualityTests` の全件を実行して通ることを確認する

**Checkpoint**: US1 と US2 が独立に検証済み。

---

## Phase 5: Polish & Cross-Cutting

- [X] T017 全テスト `python3 -B -m unittest discover -s SKILL/tests -v` を実行し、既存 90 件を含めてすべて通ることを確認する(SC-003)。件数と結果を記録する
- [X] T018 [P] `python3 SKILL/scripts/check_links.py --root . --changed` を実行し、エラー 0 を確認する(失敗した場合は直して再実行する)
- [X] T019 [P] `quickstart.md` の手順 2(純粋関数の手動確認)を実行し、期待どおりの出力になることを確認する
- [X] T020 `git diff --stat -- SKILL/scripts/common.py` が空であることを最終確認する。空でなければ停止して報告する
- [X] T021 完了報告(`Documentation impact`)に含める項目を整理する: 更新した文書は本スライスの spec 一式のみ(`SKILL.md` の文言の同期は S4、README は S6 の範囲として `Unresolved` に記載)、検査と結果、既知の限界(意味の妥当性は検査できない)

---

## Dependencies & Execution Order

- Phase 1 → Phase 2 → Phase 3(US1)→ Phase 4(US2)→ Phase 5。
- Phase 2 のテスト追加(T002〜T007)は同じファイルを編集するため**順に**行う。T008 は T007 の後。
- US2(`report_lines` と問題 B)は US1 の `report_quality_problems` に依存するため、US1 の後に行う。
- `scripts/stop_gate.py` を触るタスク(T009、T010、T012、T014、T015)は並行しない。
- 並行可能: T018 と T019(どちらも読み取りのみ)。
- 停止条件: `common.py` の変更が必要と分かった時点(T013、T020)で停止して報告する。

## Implementation Strategy

1. Phase 1〜2 で基準と失敗するテストをそろえる。
2. MVP は US1(理由のない「不要」を通さない)。これだけで主要な穴が塞がる。
3. US2 で見出しのみの報告の穴を塞ぎ、Polish で仕上げる。各 Phase の終わりでテストを実行する。

## Notes

- 総タスク数: 21(Setup 1、Foundational 7、US1 5、US2 3、Polish 5)。
- テストの ID(R1〜R4、G1〜G12)は plan.md の表に対応する。
- 範囲外(`related.*` 設定、上限、作成規則、SKILL.md・README・eval)に手を出さない。

## Evidence(実装記録)

- **T001(基準)**: 既存 90 件が通る。`common.py` は未変更。
- **T008(失敗の記録)**: 追加した 19 件のテスト(ReportQualityTests 7 件、StopGateTests 12 件)のうち 15 件が実装前に失敗した(R1〜R4 の 7 件は関数が無いため、G1・G2・G4・G6・G8・G9・G10・G11 の 8 件は新しい検査が無いため)。残る 4 件(G3・G5・G7・G12)は、実装前から通る回帰の番人として意図したもの。合計 109 件、既存 90 件は通ったままだった。
- **T011〜T016**: 純粋関数と `report_quality_problems`、`evaluate()` への組み込みを実装し、初回の実行で 109 件すべてが通った。`common.py` は無変更。
- **T017**: 全 109 件が通った(約 29 秒)。
- **T018**: `check_links.py --changed` はエラー 0、警告 0。
- **T019**: `quickstart.md` の手順 2 は期待どおり(先頭 4 つが `True`、後ろ 2 つが `False`、不要宣言の理由が取り出せる)。
- **T020**: `git diff --stat -- scripts/common.py` が空(B3 に該当せず)。
- **既知の限界**: 具体的に見えて無意味な理由は検査できない。定型句の一覧は固定で、設定では拡張できない。
