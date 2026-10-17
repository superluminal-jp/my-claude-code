# Implementation Plan: アプリケーションログの実装と検査スキル(secure-logging)

**Branch**: `050-secure-logging-skill` | **Date**: 2026-10-17 | **Spec**: [spec.md](spec.md)

## Summary

`secure-logging` スキル(`SKILL.md` と、項目ID付きの `references/logging-checklist.md`)を、仕様 050 を満たす形で確定する。未コミットの試作は出発点とし、FR ごとに「満たす/不足/誤り」を判定して、保持・修正・追加に分ける(下の差分表)。スキルの契約を確かめる bash テストを先に追加して失敗を記録し、その後で試作を直す。検査の挙動(SC-001、SC-004、SC-005)は LLM の振る舞いなので自動テストにせず、既知の欠陥を仕込んだ検証用コードと手順(quickstart)で確認し、結果は未検証と明記する。

## Technical Context

**Language/Version**: Markdown(スキル本体、チェックリスト)、bash(契約テスト)、検証用のサンプルコードは Python 3 の小さなファイル

**Primary Dependencies**: なし。既存の `tests/run-config-pyramid.sh` の枠組み、`check_links.py`

**Storage**: ファイルのみ

**Testing**: `tests/run-secure-logging-skill.sh`(新規、契約テスト)、`tests/run-config-pyramid.sh`(既存、新スキルを登録済み)、`check_links.py --changed`

**Target Platform**: `install.sh` が `~/.claude/` へ同期するユーザーレベルのスキル

**Project Type**: 設定リポジトリ内のスキルパッケージ(ライブラリでも CLI でもない)

**Performance Goals**: なし

**Constraints**: スキル層の規約(他スキルの名指し禁止、インストール先パスの固定記述禁止)。`SKILL.md` は 200 行未満。出典は確認済みの一次情報のみ。

**Scale/Scope**: スキル 1 件、参照文書 1 件、テスト 1 件、README 2 件

## Constitution Check

`.specify/memory/constitution.md` は未記入のテンプレートであるため、リポジトリの `CLAUDE.md` と設計文書(`docs/claude-config-design.md`)を実質のゲートとする。

| ゲート | 判定 |
|---|---|
| 最小で一貫した変更 | 合格: 新スキル、テスト、README、テスト登録のみ。既存スキルは変更しない |
| 失敗するチェックを先に用意 | 合格: 契約テストを先に追加し、失敗を記録してから試作を直す |
| 事実の記述・出典 | 合格: 出典は確認済みのものに限り、除外した規格を明記する。挙動の検証は未検証と明記する |
| スキル層の規約 | 合格見込み: 構造テスト SKILL-05、SKILL-06 で確認する |
| README の同期 | 合格見込み: 英語・日本語の両方を更新する(FR-017) |

設計後の再評価: 違反なし。Complexity Tracking は不要。

## 試作と仕様の差分(FR ごとの判定)

判定は、試作のファイルを仕様と突き合わせた結果。「満たす」は保持、「不足」は追加、「誤り」は修正。

| FR | 判定 | 根拠(試作の状態) | 計画 |
|---|---|---|---|
| FR-001 | 満たす | `description` が領域別の補助として併用を述べる | 保持 |
| FR-002 | 満たす | `description` が基盤運用、無関係な可観測性、ログに触れない変更を除外 | 保持 |
| FR-003 | 満たす | チェックリストが group A / group B に分かれる | 保持 |
| FR-004 | 満たす | 状態表に Pass/Fail/N-A/Unverified、Pass/Fail に `file:line` | 保持 |
| FR-005 | 満たす | group B は Unverified、設定がリポジトリにある場合のみ例外 | 保持 |
| FR-006 | 満たす | LOG-EVT/ATT/DATA/INJ/ERR/CFG/TST が必須項目を網羅 | 保持 |
| FR-007 | 不足 | LOG-EVT-4、LOG-EVT-6 の根拠が節名なしの `CS` のみ | 節名を補う(例: `CS Which events to log`) |
| FR-008 | 誤り | LOG-EVT-8 が `Top10 (CWE-223)` を根拠にする。CWE-223 の本文は読んでおらず、FR-008 の CWE 一覧(117/532/778/779)にも無い | `CWE-223` への言及を外し、根拠を `CWE-778` と `Top10` に限る |
| FR-009 | 満たす | 除外した規格と理由を明記 | 保持 |
| FR-010 | 満たす | 実装手順 4.1 が先行テストと、自動化できない場合の記録を要求 | 保持 |
| FR-011 | 満たす | Scope に既存の機構を保つ旨がある | 保持 |
| FR-012 | 不足 | 工程 4 の後に検査(工程 5)へ進む旨が弱く、再検査を明示していない | 実装モードで工程 4 の後に工程 5 を必ず再実行する旨を明記する |
| FR-013 | 満たす | 報告の順序が結論→表→変更→証拠→未検査 | 保持 |
| FR-014 | 満たす | 観測・要件・推論の区別を要求 | 保持 |
| FR-015 | 満たす | 構造テスト SKILL-05、SKILL-06 が通る | 保持(最終確認を再実行) |
| FR-016 | 誤り | ROUTE-12 の正規表現が `(overlay\|alongside).*` で、ほぼ何にも一致し検査にならない | 「併用」と「補助」の両方を含む形に厳格化する |
| FR-017 | 満たす | README.md、README.ja.md の両方に追記済み | 保持。新しい契約テストの記載を両方に足す |
| FR-018 | 満たす | LOG-DATA-1/2 と完了確認に含まれる | 保持 |

仕様の Edge Cases に対する試作の差分:

| Edge Case | 判定 | 計画 |
|---|---|---|
| ログ機構が無いコードベース | 不足 | `SKILL.md` に、検査では不足を不合格、実装では標準機構から選ぶ旨を追加する |
| ログ呼び出しが無い変更 | 不足 | 該当なしと報告する旨を追加する |
| 対象の既定(差分優先、無ければ全体) | 不足 | 工程 1 に既定と、仮定を報告に書く旨を追加する |
| 一次情報の版の更新 | 不足 | 重要な項目は使う前に出典を読み直す旨は既にある。版の確認日をチェックリストに残す(保持) |
| 含めていない規格の対応付けの依頼 | 不足 | 含めていない理由を示し、対応付けは行わない旨を追加する |

成功基準の検証手段の差分:

| SC | 判定 | 計画 |
|---|---|---|
| SC-001、SC-005 | 不足(検証手段が無い) | `tests/fixtures/secure-logging/` に既知の欠陥を仕込んだサンプルと期待一覧を追加し、quickstart の手動手順で確認する。自動化はしない |
| SC-002、SC-003 | 不足 | 契約テストで、全項目に根拠があること、group B に「合格」と読める記述が無いことを確かめる |
| SC-004 | 不足 | 手動手順で、実装の依頼の完了報告に先行テストが示されることを確認する |
| SC-006、SC-007 | 満たす | 既存のテストとリンク検査で確認する |

## 設計の要点

1. **契約テスト**(`tests/run-secure-logging-skill.sh`): `SKILL.md` の front matter、`description` の除外句、チェックリストの全項目に根拠の列、除外した規格の明記、草案の NIST が要件の根拠に使われていないこと、group B の項目に Pass の判定を促す語が無いこと、`SKILL.md` の行数が 200 未満であること。
2. **検証用サンプル**(`tests/fixtures/secure-logging/`): 秘密情報の出力、改行の未処理、認証失敗の未記録を含む小さな Python ファイルと、期待される不合格項目の一覧(`expected.md`)。
3. **構造テストの強化**: ROUTE-12 を厳格化する。
4. **README**: 両方に新しい契約テストの実行コマンドを `Verification` に追加する。

## Project Structure

### Documentation (this feature)

```text
specs/050-secure-logging-skill/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── inspection-report.md
├── checklists/
│   └── requirements.md
└── tasks.md             # /speckit-tasks の出力
```

### Source Code (repository root)

```text
.claude/skills/secure-logging/
├── SKILL.md                              # 修正: FR-012、Edge Cases
└── references/
    └── logging-checklist.md              # 修正: FR-007、FR-008

tests/
├── run-secure-logging-skill.sh           # 新規
├── run-config-pyramid.sh                 # 修正: ROUTE-12
└── fixtures/secure-logging/
    ├── defective_auth.py.fixture                 # 新規
    └── expected.md                       # 新規

README.md                                 # 修正: Verification
README.ja.md                              # 修正: Verification
```

**Structure Decision**: 既存の設定リポジトリの構造に従う。スキルは `.claude/skills/<name>/`、テストは `tests/`、検証用の入力は `tests/fixtures/`。

## Complexity Tracking

違反なし。
