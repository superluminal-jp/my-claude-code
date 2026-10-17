---

description: "Task list for 050: アプリケーションログの実装と検査スキル(secure-logging)"
---

# Tasks: アプリケーションログの実装と検査スキル(secure-logging)

**Input**: [spec.md](spec.md)、[plan.md](plan.md)、[research.md](research.md)、[data-model.md](data-model.md)、[contracts/inspection-report.md](contracts/inspection-report.md)、[quickstart.md](quickstart.md)

**Tests**: 契約テスト(`tests/run-secure-logging-skill.sh`)を先に作り、失敗を記録してから試作を直す(plan.md の「テスト先行」)。検査の挙動(SC-001、SC-004、SC-005)は自動テストにせず、quickstart の手動手順で確認する。

`SKILL` = `.claude/skills/secure-logging`。試作はすでに作業ツリーにある(未コミット)。各タスクは plan.md の差分表に従い、保持するものには触れない。`SKILL/SKILL.md` と `SKILL/references/logging-checklist.md` を触るタスクは並行しない。

## Phase 1: Setup

- [X] T001 ブランチが `050-secure-logging-skill` であることと、試作が作業ツリーにあることを確認し、`bash tests/run-config-pyramid.sh` が全件通ることを基準として記録する

## Phase 2: Foundational(失敗するテストを先に書く)

- [X] T002 `tests/run-secure-logging-skill.sh` を新規作成する。`tests/run-digital-agency-frontend-skill.sh` の `check`/`contains` 形式に合わせ、次を確かめる: `SKILL/SKILL.md` の front matter(`name: secure-logging`、`description`)、`description` が基盤運用・無関係な可観測性・ログに触れない変更を除外していること、`SKILL.md` が 200 行未満、`references/logging-checklist.md` の全項目行(`LOG-` で始まる)の最終列に節名または要件ID付きの根拠があること(`CS` 単独は不可)、`CWE-223` を根拠として含まないこと、除外した規格(ISO/IEC 27002、PCI DSS、NIST SP 800-53)が除外として明記されていること、NIST SP 800-92 が草案・背景のみと明記され項目の根拠に現れないこと、`LOG-OPS-*` の行に `Pass` を促す語が無いこと
- [X] T003 `bash tests/run-secure-logging-skill.sh` を実行し、少なくとも根拠の節名(FR-007)と `CWE-223`(FR-008)の検査が失敗することを確認して、失敗した項目名を記録する

**Checkpoint**: 失敗が記録されている。以降のタスクで直して通す。

## Phase 3: User Story 1 - 検査が証拠付きで判定できる (Priority: P1) 🎯 MVP

**Goal**: 検査モードが、仕様の FR-001〜FR-009、FR-013、FR-014、FR-018 と Edge Cases を満たす。

**Independent Test**: `tests/run-secure-logging-skill.sh` の根拠・除外・草案の検査が通り、quickstart の手動手順 1〜2 で、検証用サンプルの欠陥がすべて場所付きの不合格として報告される。

- [X] T004 [P] [US1] `tests/fixtures/secure-logging/defective_auth.py.fixture` を新規作成する。秘密情報の出力(パスワードとトークンの見本値をそのままログへ)、利用者入力を改行の無害化なしでログへ、認証失敗を記録しない分岐、を小さな関数に含める
- [X] T005 [P] [US1] `tests/fixtures/secure-logging/expected.md` を新規作成する。T004 の欠陥ごとに、期待される不合格の項目ID(`LOG-DATA-1`、`LOG-INJ-1`、`LOG-EVT-1`)と該当行を列挙し、group B が Pass にならないことも期待として書く
- [X] T006 [US1] `SKILL/references/logging-checklist.md` の `LOG-EVT-4` と `LOG-EVT-6` の根拠を節名付きに直す(`CS Which events to log`)。他に節名なしの `CS` 単独があれば同様に直す(FR-007)
- [X] T007 [US1] `SKILL/references/logging-checklist.md` の `LOG-EVT-8` から `Top10 (CWE-223)` を外し、根拠を `CWE-778` と `Top10` に限る。Sources の `Top10` 行の注記は、CWE-221 と 223 の本文は読んでいないため要件の根拠にしない旨を残す(FR-008)
- [X] T008 [US1] `SKILL/SKILL.md` の工程 1 に、対象の既定(差分があれば差分、無ければ全体。仮定を報告に書く)を追記する(Edge Cases)
- [X] T009 [US1] `SKILL/SKILL.md` に、ログ機構が無いコードベース(検査は不足を不合格、実装は利用可能な標準機構から選ぶ)、ログ呼び出しが無い変更(該当なし)、含めていない規格の対応付けの依頼(含めていない理由を示し、対応付けは行わない)を追記する(Edge Cases)
- [X] T010 [US1] `bash tests/run-secure-logging-skill.sh` を実行し、T003 で失敗した検査が通ることを確認する

**Checkpoint**: 検査モードが単独で成立する。ここで止めても MVP として使える。

## Phase 4: User Story 2 - 実装がテスト先行で進む (Priority: P2)

**Goal**: 実装モードが FR-010〜FR-012 を満たす。

**Independent Test**: quickstart の手動手順 3 で、完了報告に先行して失敗していたテストが示され、見本値がログに現れない。

- [X] T011 [US2] `SKILL/SKILL.md` の工程 4 の後に、工程 5(検査)を必ず再実行し、その結果と実行したテストの結果を報告に含める旨を明記する(FR-012)。工程の番号と「レビューは工程 2 と 5 のみ」の記述に矛盾が出ないことを確認する
- [X] T012 [US2] `SKILL/SKILL.md` の工程 4 に、自動化できない契約の場合は現状の観測と確認方法を記録する旨が残っていること、既存のログ機構を維持する旨が残っていることを確認する。欠けていれば追記する(FR-010、FR-011)

**Checkpoint**: 実装モードが検査モードと矛盾なく成立する。

## Phase 5: User Story 3 - 出典の規律と規約への適合 (Priority: P3)

**Goal**: FR-015〜FR-017 を満たす。

**Independent Test**: `bash tests/run-config-pyramid.sh` が全件通り、両方の README にスキルと新しいテストが載っている。

- [X] T013 [US3] `tests/run-config-pyramid.sh` の `ROUTE-12` を、`description` が領域別の補助であること(`overlay`)と併用の旨(`alongside` と `supplements`)の両方を含む正規表現に厳格化する(FR-016)
- [X] T014 [P] [US3] `README.md` の Verification に `bash tests/run-secure-logging-skill.sh` を追記する(FR-017)
- [X] T015 [P] [US3] `README.ja.md` の Verification に `bash tests/run-secure-logging-skill.sh` を追記する(FR-017)
- [X] T016 [US3] `bash tests/run-config-pyramid.sh` を実行し、新スキルを含めて全件通ることを確認する。SKILL-05(他スキルの名指し)、SKILL-06(インストール先パスの固定記述)も通ること

## Phase 6: Polish

- [X] T017 `bash tests/run-secure-logging-skill.sh`、`bash tests/run-config-pyramid.sh`、`bash tests/run-install.sh` を実行し、結果を記録する
- [X] T018 `python3 /Users/taikiogihara/.claude/skills/maintaining-living-documentation/scripts/check_links.py --changed` を実行し、エラー 0 件を確認する。`find_related.py` が示す関連文書について、更新するか、変更不要の理由を最終報告に書く
- [X] T019 quickstart の手動手順は未実行であることを `quickstart.md` の末尾に「未検証」として記す(実行したら日付と結果に置き換える)。最終報告でも SC-001、SC-004、SC-005 を未検証と明記する

## Dependencies

- T001 → T002 → T003 → すべての修正タスク
- T006、T007(同じファイル)→ T010。T008、T009、T011、T012(同じファイル `SKILL.md`)は順に実行する
- T004、T005 は T010 の前に済ませる(手動手順の入力)
- T013 → T016。T014、T015 は T016 と独立
- T017〜T019 は最後

## Parallel Opportunities

- T004 と T005(別ファイル)
- T014 と T015(別ファイル)
- T006・T007(チェックリスト)と T008・T009(SKILL.md)は別ファイルだが、T010 でまとめて確認する。同時に進めてよい

## Implementation Strategy

1. Phase 1〜2 でテストを先に作り、失敗を記録する。
2. Phase 3 で検査モードを確定する(MVP)。
3. Phase 4 で実装モードの整合を取り、Phase 5 でリポジトリ規約と README を整える。
4. Phase 6 で全体を確認し、自動で確かめられなかったものを未検証と明記する。
