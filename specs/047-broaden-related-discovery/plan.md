# Implementation Plan: 近接候補の発見を広げる(スライス S2)

**Branch**: `047-broaden-related-discovery` | **Date**: 2026-10-17 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/047-broaden-related-discovery/spec.md`(権威: [meta-spec.md](../043-related-doc-discovery/meta-spec.md)、契約 C1(拡張)・C3、仮定 A1・A3、分岐 B1・B3)

## Summary

`find_related.py` の `find_candidates` を拡張し、名前参照(P2)、変更履歴(P3)、コメント(P0、助言)を返し、`related.max_candidates` による上限と `truncated` を加える。`stop_gate.py` は P0 を強制せず、種別ごとの文面と省略件数を示す。設定の検証のため、`common.py` の `_check_type` と `load_config` を加算的に拡張し(分岐 B3 の再計画)、スキーマに `related` を追加する。

## Technical Context

**Language/Version**: Python 3.9 以上(標準ライブラリのみ: `re`、`pathlib`)

**Primary Dependencies**: なし。S1 の `find_related.find_candidates`、`stop_gate.unaddressed_related`、`common` を拡張する

**Storage**: なし(読み取り専用)

**Testing**: `unittest`(`tests/test_scripts.py`)。`FindRelatedTests`、`ConfigTests`、`StopGateTests` を拡張する

**Target Platform**: macOS / Linux(Git を前提)

**Project Type**: CLI スクリプト群を持つスキル

**Performance Goals**: 文書数 × 変更ファイル数の正規表現照合。文書は 1 回だけ読み、1 MiB 超は読まない。ゲートの 30 秒以内に収まる規模(数千ファイル)を想定

**Constraints**: 読み取り専用。`common.py` は FR-009 の加算的拡張のみ。既存 112 件を維持(S1 のテスト補助の更新を除く)

**Scale/Scope**: ファイル数 〜数千、1 回の変更 〜数十ファイル

## Constitution Check

`.specify/memory/constitution.md` は未記入のテンプレートで、適用される制約はない。CLAUDE.md とグローバル規則を実質のゲートとする。

| ゲート | 判定 |
|---|---|
| 最小で一貫した変更 | 合格: 範囲は spec の FR-001〜FR-011。`common.py` は設定検証に必要な加算的拡張のみ |
| 失敗するチェックを先に用意 | 合格: 下記「テスト先行」 |
| 契約の同期 | 合格(予定): 契約の拡張は `contracts/candidate-report.md` に記録。`SKILL.md` は S4、README は S6 |
| 既存挙動の維持 | 合格(予定): S1・S3 のテストが通ること。補助の更新のみ例外 |

設計後の再確認: 違反なし。B3 の発動は spec に記録済みで、再計画の範囲内。

## Project Structure

### Documentation (this feature)

```text
specs/047-broaden-related-discovery/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/candidate-report.md
├── checklists/requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
.claude/skills/maintaining-living-documentation/
├── scripts/
│   ├── find_related.py          # 変更: P2・P3・P0、上限、truncated
│   ├── stop_gate.py             # 変更: P0 を除外、種別の文面、省略件数
│   └── common.py                # 変更(B3): 整数と入れ子オブジェクトの検証(加算的)
├── schemas/config.schema.json   # 変更: related を追加
└── tests/test_scripts.py        # 変更: 追加テストと S1 補助の更新
```

**Structure Decision**: 既存の構成を踏襲する。新しいファイルは作らない。

## 設計の要点

1. **名前参照(P2)**: 文書(`is_candidate_document` を満たし、変更されておらず、`list_files` に含まれる)を 1 回だけ読む(1 MiB 超・読み取り失敗は除外、キャッシュする)。元ファイルごとに、トークン = [パス全体, ファイル名(`len >= min_name_length` のとき)] を、`(?<![\w.-])TOKEN(?![\w-])`(大文字小文字を区別)で照合する。同じ組が P1 でもある場合は P1 のみ。
2. **変更履歴(P3)**: `is_changelog(path)` かつ文書の拡張子でないものも含め(`CHANGELOG` など)、`list_files` から変更履歴ファイルを選ぶ。変更集合のどれかが変更履歴なら出さない。利用者に見える変更(分類が実装、仕様、設定、インフラのいずれかを含む元ファイル)が 1 件以上あれば、変更履歴ファイルごとに 1 件(`source` は先頭の元ファイル、理由に件数)。
3. **コメント(P0)**: 分類が `{"implementation"}` のみの元ファイルごとに、自身を指す 1 件(種別 `comment`)。上限に数えない。
4. **上限と並び**: P1/P2/P3 のレコードを (近接度, パス, 元ファイル) で並べ、異なるパスで `max_candidates` まで残す。`truncated` は省かれた異なるパスの数。最終出力は P0 → P1 → P2 → P3 の順(各々パス、元ファイル順)。
5. **ゲート**: `unaddressed_related` は `kind == "comment"` を読み飛ばし、`truncated > 0` のとき「(+N more not listed: raise related.max_candidates)」を付ける。文面は種別に応じて `next to changed X` / `mentions changed X` / `change history; user-visible change X`。
6. **設定の検証(B3)**: `_check_type` に `integer`(真偽値を除く、`minimum` を尊重)と `object` を追加。`load_config` はオブジェクト型のキーについて、入れ子の未知のキーと各値の型を検証し、`related.max_candidates must be an integer >= 1` の形で報告する。既存のキーの検証は変えない。
7. **S1 のテスト補助**: `FindRelatedTests.pairs` を、`kind != "comment"` のみ取り出すよう更新する(P0 の追加に伴う)。

## テスト先行(実装前に書く、失敗を確認するテスト)

| ID | 検証 | 対応 |
|---|---|---|
| M1 | パス全体を挙げる未変更の文書が `mention`・P2・理由付きで出る | FR-002, US1-1 |
| M2 | ファイル名だけの言及は最小長以上で成立。短い名前はパス全体のときだけ | FR-002, US1-2 |
| M3 | 単語の一部(`reinstall.sh`、`install.shx`)は不成立 | US1-3 |
| M4 | 同じディレクトリで名前も挙げる文書は `sibling` の 1 件のみ | US1-4 |
| M5 | 変更済み、除外設定、決定記録、変更履歴は名前参照の対象外 | FR-003 |
| M6 | 削除されたファイルの名前の言及が成立 | エッジ |
| M7 | 読み取れない文書(不正な文字コード)と 1 MiB 超の文書は読み飛ばされ、エラーにならない | FR-003 |
| H1 | 変更履歴の候補(P3)が出る。変更履歴も変更済みなら出ない。変更履歴が無い、テスト・文書のみの変更では出ない | FR-004, US2 |
| H2 | 変更履歴の候補は文書ごとに 1 件で、理由に件数を含む | エッジ |
| K1 | 実装ファイルの `comment`(P0)が出る。設定・テスト・文書のみでは出ない | FR-005, US3-1 |
| X1 | `max_candidates` で近接度が高い順に残り、`truncated` が省かれた文書数。P0 は数えない | FR-007 |
| X2 | `min_name_length` の変更で名前参照の成立が変わる | FR-006 |
| C1 | `related` の正しい設定が受理され、文字列、0、真偽値、未知のキー、オブジェクトでない値が理由付きで拒否される | FR-006, US3-5 |
| C2 | 既存のキーの検証が変わらない(`ConfigTests` の既存テスト) | FR-009 |
| G1 | 名前参照の未処分でブロック、更新または言及で通る | FR-008, US1-5 |
| G2 | P0 のみでは問題にならない | FR-008, US3-2 |
| G3 | 変更履歴の未処分でブロック | FR-008 |
| G4 | 省略件数が文面に出る | US3-4 |

## 実装の順序

1. テスト(M1〜G4)と S1 補助の更新を追加し、失敗を記録する
2. `common.py` の拡張とスキーマの `related` を実装し、C1・C2 を通す
3. `find_related.py` を実装し、M・H・K・X を通す
4. `stop_gate.py` を実装し、G1〜G4 を通す
5. 全体(既存を含む)、`check_links.py --changed`、`quickstart.md`、`common.py` の差分が加算的であることを確認

## リスクと分岐

- **A1(ノイズ)**: 実装後に、このリポジトリの履歴に対して候補数を計測し、`min_name_length` と上限の既定値の妥当性を確かめる。許容外なら B1(再計画または再仕様)。
- **B3**: `common.py` の変更は、設定検証の加算的拡張に限る。既存の関数のシグネチャや戻り値の契約を変える必要が生じたら停止して報告する(再分解)。
- **性能**: 文書が非常に多い場合の遅延。1 MiB 超の除外と 1 回読みで抑える。

## Complexity Tracking

違反なし。
