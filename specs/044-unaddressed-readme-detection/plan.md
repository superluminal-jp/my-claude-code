# Implementation Plan: 未処分の兄弟 README の検出(スライス S1)

**Branch**: `044-unaddressed-readme-detection` | **Date**: 2026-10-17 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/044-unaddressed-readme-detection/spec.md`(権威: [meta-spec.md](../043-related-doc-discovery/meta-spec.md)、契約 C1・C2、仮定 A2・A3、分岐 B2・B3)

## Summary

変更されたコードに対し、同じディレクトリの文書を近接候補(P1)として読み取り専用で列挙する新しいコマンド `find_related.py` を追加し、Stop ゲートが「変更も言及もされていない候補」を問題として報告するようにする。SKILL.md の影響評価の手順にコマンドと処分の最小限の約束を加える。`common.py` は変更しない(仮定 A3)。

## Technical Context

**Language/Version**: Python 3.9 以上(標準ライブラリのみ。`from __future__ import annotations` を使う既存スクリプトに合わせる)

**Primary Dependencies**: なし。既存の `scripts/common.py` の `changed_files`、`classify`、`excluded`、`load_config`、`list_files`、`is_changelog`、`Change` を無変更で再利用する

**Storage**: なし(読み取り専用。ゲートの状態は既存のとおりシステム一時ディレクトリ)

**Testing**: `unittest`(`tests/test_scripts.py`)。既存の `TempDirTestCase`、`init_repo`、`commit_all`、`write`、`run_script`、`StopGateTests.hook` を再利用する

**Target Platform**: Git を持つ macOS / Linux。Git が無い環境では `find_related.py` は明確なエラー、ゲートは何もしない(既存の fail-open)

**Project Type**: CLI スクリプト群を持つ Claude Code スキル(単一プロジェクト)

**Performance Goals**: ゲートの既存のタイムアウト 30 秒以内(`hooks.json`)。候補の列挙は `git ls-files` 1 回と、ディレクトリ単位の集合演算で足りる

**Constraints**: 書き込み禁止、ネットワーク禁止、読み取り専用の Git のみ。SKILL.md は 500 行未満。既存の単体テスト 67 件を維持

**Scale/Scope**: 1 ディレクトリの Markdown が数件の規模を前提にする。上限は設けない(S2)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` は未記入のテンプレートで、適用される制約はない。代わりに、このリポジトリの CLAUDE.md とグローバル規則(最小変更、変更前の失敗するチェック、契約の同期)を実質のゲートとする。

| ゲート | 判定 |
|---|---|
| 最小で一貫した変更(スコープ外を含めない) | 合格: FR-010 と本計画の範囲で P0・P2・設定・上限などを除外 |
| 自動化できる契約の変更は、失敗するチェックを先に用意 | 合格: 下記「テスト先行」で失敗するテストを列挙し、tasks で先行させる |
| 契約文書の同期 | 合格(予定): SKILL.md は本スライスで更新。スキル README は S6 に委ねる(meta-spec の範囲) |
| 外部への影響 | 該当なし: 読み取り専用、プッシュ・マージなし |

設計後の再確認: 上記のままで違反なし。複雑さの追跡は不要。

## Project Structure

### Documentation (this feature)

```text
specs/044-unaddressed-readme-detection/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── find-related-cli.md
│   └── gate-problem.md
├── checklists/requirements.md
└── tasks.md             # /speckit-tasks で作成
```

### Source Code (repository root)

```text
.claude/skills/maintaining-living-documentation/
├── scripts/
│   ├── find_related.py      # 新規: 候補の列挙(関数 find_candidates と CLI)
│   ├── stop_gate.py         # 変更: evaluate() に未処分の候補の検査を追加
│   └── common.py            # 変更しない(仮定 A3)
├── SKILL.md                 # 変更: 手順 3 にコマンドと C2 の最小の約束
└── tests/test_scripts.py    # 変更: FindRelatedTests、StopGateTests、SkillDefinitionTests に追加
```

**Structure Decision**: 既存のスキルの構成(`scripts/` に読み取り専用 CLI を 1 本ずつ、`tests/` に単一のテストファイル)を踏襲する。新しいパッケージやディレクトリは作らない。

## 設計の要点

1. **`find_candidates(root, config, changes) -> dict`**(C1 の辞書を返す純粋関数)
   - 元になる変更ファイル: 除外対象でなく、`classify` に `documentation` を含まないもの(削除・名前変更を含む。名前変更は新しいパスのディレクトリを使う)
   - 候補: `list_files(root, config)` の結果(`.gitignore` と除外設定を尊重)のうち、元ファイルと同じディレクトリ(再帰しない)にある文書(判定は research R1)
   - 除外: 変更集合に含まれるパス(処分済み)、元ファイル自身
   - 出力: `changed`(変更されたパスの昇順)、`candidates`(`source`、`path`、`kind="sibling"`、`proximity="P1"`、`reason`。元ファイルと候補の組ごとに 1 レコード、`(path, source)` の昇順)、`truncated=0`
2. **CLI**: `find_related.py --root R [--base REF] [--json]`。`audit.py` と同じ終了コード(0 成功、2 使い方・設定・Git のエラー)。人間向け出力は元ファイルごとの要約
3. **ゲート**: `evaluate()` が、報告必須の検査の後に `unaddressed_related(...)` を呼ぶ。候補のパスが変更集合にも `last_message` にも現れなければ問題として追加する。`last_message is None` の場合は検査しない(FR-005、エッジケース)。強制の度合い、ブロック回数、再入の扱いは既存の `on_stop` に任せ、変更しない
4. **SKILL.md**: 手順 3 に `find_related.py` のコマンドを 1 行、処分の最小限の約束(更新する、または理由とともにパスを最終メッセージに書く)を 1〜2 文で追加。完了報告の書式は変更しない(`Created:` は S4)

## テスト先行(実装前に書く、失敗を確認するテスト)

`tests/test_scripts.py` に追加する。実装前は、`find_related.py` が無いことと、ゲートが候補を見ないことにより失敗する。

**FindRelatedTests**(新しいクラス。リポジトリには `src/x.py`、`src/README.md`、`src/design.md`、ルートの `app.py` を用意)

| ID | 検証 | 対応 |
|---|---|---|
| F1 | `src/x.py` の変更で、`src/README.md` と `src/design.md` が `kind="sibling"`、`proximity="P1"`、理由付きで列挙される。C1 のキーがそろう | FR-001, FR-002, US2-1 |
| F2 | 変更済みの文書は候補に含まれない | FR-003, US2-2 |
| F3 | `exclude_globs` の対象と `.gitignore` の対象は候補にならない | FR-003 |
| F4 | 文書だけの変更では候補が空になる | FR-001(文書以外が対象) |
| F5 | ルート直下のコードの変更で、ルート直下の README が候補になる | エッジケース |
| F6 | 1 つの文書が複数の変更ファイルの候補になる場合、元ファイルごとに別のレコードになり、出力は再実行しても同一 | SC-002 |
| F7 | `--base` を指定すると、コミット済みの変更も対象になる | US2-3 |
| F8 | Git でない場所は終了コード 2 で、Git の必要性を示すメッセージ。実行前後で作業ツリーが一致する | FR-004, SC-003 |
| F9 | 名前変更・削除されたコードファイルの同じディレクトリの文書も候補になる(削除された文書は候補にならない) | エッジケース |
| F10 | テキスト出力が終了コード 0 で、候補のパスを含む | CLI |

**StopGateTests**(`src/` を持つリポジトリを使う派生クラス、またはヘルパーで用意)

| ID | 検証 | 対応 |
|---|---|---|
| G1 | 未処分の `src/README.md` があると `block` し、理由に `src/README.md` が含まれる | US1-1, FR-005, FR-007 |
| G2 | README を更新すると通る | US1-2 |
| G3 | 未変更でも、最終メッセージにパスがあれば通る | US1-3 |
| G4 | 完了報告があっても、候補が未処分なら `block` する(報告だけでは通らない) | B2 の既知の限界を固定 |
| G5 | `LIVING_DOCS_GATE=warn` で `systemMessage` のみ、`off` で何も出さない | US1-4 |
| G6 | `stop_hook_active` の再入ではブロックしない | FR-006 |
| G7 | ブロック回数の上限後は警告のみになる | FR-006 |
| G8 | `last_assistant_message` が無いと、候補の問題は報告されない | エッジケース |
| G9 | ゲート前から存在する変更では動作しない(既存の基準) | FR-006 |

**SkillDefinitionTests**

| ID | 検証 | 対応 |
|---|---|---|
| D1 | SKILL.md が `find_related.py` のコマンドと、処分の最小限の約束(更新または最終メッセージでのパスの言及)を含む | FR-008, US3-1 |
| D2 | 既存の定義検査(500 行未満、規則とスキルの一致)が通る | US3-2, SC-005 |

## 実装の順序

1. 上記のテストを追加し、失敗(エラーまたは不一致)を記録する
2. `find_related.py` を実装し、F1〜F10 を通す
3. `stop_gate.py` を拡張し、G1〜G9 を通す
4. SKILL.md を更新し、D1・D2 を通す
5. 全体(既存 67 件を含む)を実行し、`check_links.py --changed` を実行する

## リスクと分岐

- **B3(`common.py` の変更が必要になった場合)**: 実装を止め、証拠(必要になった関数と理由)とともに報告する。meta-spec の分岐 B3 に従い、再計画または再分解を判断する。現時点の読解では、`changed_files`、`list_files`、`classify`、`excluded` で足りる見込み
- **B2(形式的な言及で通る)**: G4 と G3 は、報告だけでは通らないが、パスの言及さえあれば通ることを固定する。構造化された処分行の要求は、B2 が偽になった場合の再仕様に委ねる
- **ノイズ(A1 の予兆)**: 設定ファイルやロックファイルの変更でも、同じディレクトリの文書が候補になる。S1 では仕様どおり対象を絞らない。実測は S2 で行う
- **既存テストへの影響**: 既存の `StopGateTests` のリポジトリはルートに `app.py` と `docs/guide.md` のみで、ルート直下の README 系の文書が無いため、新しい検査の対象にならない見込み。実装後に全件実行して確認する

## Complexity Tracking

違反なし。記入不要。
