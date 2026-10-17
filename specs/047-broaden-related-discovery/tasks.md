---

description: "Task list for slice S2: 近接候補の発見を広げる"
---

# Tasks: 近接候補の発見を広げる(スライス S2)

**Input**: `/specs/047-broaden-related-discovery/`(plan.md、spec.md、research.md、data-model.md、contracts/、quickstart.md)

**Tests**: 要求あり(テスト先行)。`SKILL` = `.claude/skills/maintaining-living-documentation`。`tests/test_scripts.py`、`scripts/find_related.py`、`scripts/stop_gate.py`、`scripts/common.py` を触るタスクは並行しない。`common.py` は FR-009 の加算的拡張のみ。それ以外が必要なら停止して報告する。

## Phase 1: Setup

- [X] T001 ブランチが `047-broaden-related-discovery` であることを確認し、既存 112 件が通ること、`common.py` の差分が空であることを基準として記録する

## Phase 2: Foundational(失敗するテストを先に書く)

- [X] T002 `SKILL/tests/test_scripts.py` の `FindRelatedTests.pairs` を `kind != "comment"` のみ取り出すよう更新する(P0 の追加に伴う補助の更新。この時点で既存 112 件が通ることを確認する)
- [X] T003 `SKILL/tests/test_scripts.py` の `FindRelatedTests` に M1〜M4 を追加する(パス全体の言及が `mention`・P2・理由付き、最小長以上のファイル名の言及、短い名前はパス全体のみ、`reinstall.sh`・`install.shx` は不成立、同じディレクトリで名前も挙げる文書は `sibling` 1 件のみ)
- [X] T004 `SKILL/tests/test_scripts.py` の `FindRelatedTests` に M5〜M7 を追加する(変更済み・除外設定・決定記録・変更履歴は対象外、削除されたファイルの言及、不正な文字コードと 1 MiB 超の文書の読み飛ばし)
- [X] T005 `SKILL/tests/test_scripts.py` の `FindRelatedTests` に H1・H2・K1 を追加する(変更履歴の候補 P3: 出る/変更済みなら出ない/変更履歴なし・テストのみ・文書のみでは出ない/文書ごとに 1 件で理由に件数、`comment` P0: 実装ファイルで出て設定・テスト・文書のみでは出ない)
- [X] T006 `SKILL/tests/test_scripts.py` の `FindRelatedTests` に X1・X2 を追加する(`max_candidates` で近接度が高い順に残り `truncated` が省かれた文書数、P0 は数えない、`min_name_length` の変更で成立が変わる。設定は `.living-documentation.json` で与える)
- [X] T007 `SKILL/tests/test_scripts.py` の `ConfigTests` に C1 を追加する(`related` の正しい設定の受理、文字列・0・真偽値・`"6"`・未知のキー・オブジェクトでない値の拒否と、メッセージにキー名を含むこと。既存の C2 は既存テストのまま)
- [X] T008 `SKILL/tests/test_scripts.py` の `StopGateTests` に G1〜G4 を追加する(名前参照の未処分でブロック・更新または言及で通る、P0 のみでは問題にならない、変更履歴の未処分でブロック、省略件数が文面に出る)
- [X] T009 追加したテストを実行し、期待どおりに失敗することを確認して記録する。既存 112 件が通ったままであることも確認する

**Checkpoint**: 失敗の記録が無いまま次の Phase に進まない。

## Phase 3: User Story 3 の前提 - 設定の検証(B3)

- [X] T010 `SKILL/schemas/config.schema.json` に `related`(オブジェクト、`additionalProperties: false`、`max_candidates` 整数 `minimum: 1` 既定 10、`min_name_length` 整数 `minimum: 1` 既定 6、説明つき)を追加する
- [X] T011 `SKILL/scripts/common.py` の `_check_type` に `integer`(真偽値を除く、`minimum` を尊重)と `object` を追加し、`load_config` が `object` 型のキーの入れ子(未知のキー、各値の型・下限)を検証して `related.<key> must be …` の形で報告するようにする。既存の関数のシグネチャと既存のキーの挙動は変えない
- [X] T012 C1 と既存の `ConfigTests` が通ることを確認する。`git diff -- SKILL/scripts/common.py` が加算的であること(削除行が無い、または既存の挙動を変える行が無い)を確認する

## Phase 4: User Story 1 - 名前参照 (P1) 🎯 MVP

- [X] T013 [US1] `SKILL/scripts/find_related.py` に名前参照(P2)を実装する: 設定の `related` を読み(既定 10・6)、文書を 1 回だけ読み(1 MiB 超・読み取り失敗は除外)、元ファイルごとにパス全体とファイル名(最小長以上)を `(?<![\w.-])TOKEN(?![\w-])` で照合する。同じ組が P1 の場合は P1 のみ。変更済み・除外・決定記録・変更履歴は対象外
- [X] T014 [US1] M1〜M7 を実行して通ることを確認する

## Phase 5: User Story 2 - 変更履歴 (P2)

- [X] T015 [US2] `SKILL/scripts/find_related.py` に変更履歴の候補(P3)を実装する: `list_files` から `is_changelog` のファイルを選び、変更集合に変更履歴がなく、利用者に見える変更(分類に実装・仕様・設定・インフラのいずれか)があるとき、ファイルごとに 1 件(`source` は先頭の元ファイル、理由に件数)
- [X] T016 [US2] H1・H2 が通ることを確認する

## Phase 6: User Story 3 - コメントと上限 (P3)

- [X] T017 [US3] `SKILL/scripts/find_related.py` に P0 の `comment`(分類が実装のみの元ファイル自身)を実装し、(近接度, パス, 元ファイル)の並びと、P1〜P3 の異なる文書数による `max_candidates` の上限と `truncated` を実装する(P0 は数えない)
- [X] T018 [US3] K1・X1・X2 とこれまでのすべての `FindRelatedTests` が通ることを確認する
- [X] T019 [US3] `SKILL/scripts/stop_gate.py` の `unaddressed_related` を更新する: `kind == "comment"` を読み飛ばし、文面を種別ごと(`next to changed X` / `mentions changed X` / `change history; user-visible change X`)にし、`truncated > 0` のとき `(+N more not listed: raise related.max_candidates)` を付ける。文面の先頭を `Documents related to changed files were neither updated nor named in the final message` にする(S1 のテストが期待する語を壊さない)
- [X] T020 [US3] G1〜G4 と既存の `StopGateTests` のすべて(S1・S3 を含む)が通ることを確認する

## Phase 7: Polish

- [X] T021 全テストを実行し、既存 112 件を含めてすべて通ることを確認する
- [X] T022 [P] `check_links.py --root . --changed` を実行し、エラー 0 を確認する
- [X] T023 [P] `quickstart.md` の手順 2 を実行し、期待どおりになることを確認する
- [X] T024 仮定 A1 の実測: このリポジトリで `find_related.py --root . --base main`(および履歴の複数のコミット範囲)を実行し、候補数の分布と、上位の候補の妥当性を記録する。許容外なら B1 として報告する
- [X] T025 `git diff -- SKILL/scripts/common.py` が加算的であることを最終確認する。完了報告の項目を整理する(`SKILL.md` は S4、README は S6 を `Unresolved` に)

## Dependencies

Phase 1 → 2 → 3 → 4 → 5 → 6 → 7。`find_related.py` と `stop_gate.py` を触るタスクは並行しない。T022 と T023 は並行可能。

## Evidence(実装記録)

- **T001(基準)**: 既存 112 件が通る。
- **T009(失敗の記録)**: 追加した 18 件のうち 13 件が実装前に失敗した(FindRelatedTests 10 件、ConfigTests 1 件、StopGateTests 2 件の計 13 件(失敗 10、エラー 3))。残る 5 件(M3・M4・M5・H1 の否定側・G2)は、実装前から通る回帰の番人。合計 130 件で、既存 112 件は通ったまま。
- **B3(再計画)**: `common.py` の `_check_type` は `string` と `array` 以外を常に通すため、`related` の検証には加算的な拡張が必要だった。追加は `integer` / `object` の分岐と `_check_members` のみで、削除・変更した行は 0(`git diff` で確認)。
- **実装の不具合と修復**: `stop_gate.py` の関数置換で、先頭の位置の取り違えにより関数が重複した。テストが旧い文面を検出して発覚し、重複部分を削除して全テストを通した。
- **T024(A1 の実測)**: 上記 spec の「A1 の実測結果」を参照。再計画として、変更履歴をプロジェクト直下に限る規則と、そのテスト H3(実装前に失敗を確認)を追加した。合計 132 件。
- **T021〜T023, T025**: 全 132 件が通った(約 36 秒)。`check_links.py --changed` はエラー 0。`quickstart.md` 手順 2 は期待どおり。`common.py` の差分に削除行はない。
- **既知の限界**: 名前参照は文字列の一致で、意味を解析しない。履歴文書(凍結された仕様)が多いプロジェクトでは、`exclude_globs` の調整が前提。
