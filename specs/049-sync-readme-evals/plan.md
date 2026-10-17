# Implementation Plan: 公開文書の同期と振る舞い eval(スライス S6)

**Branch**: `049-sync-readme-evals` | **Date**: 2026-10-17 | **Spec**: [spec.md](spec.md)

## Summary

スキル側の `README.md` を S1〜S5 の挙動に同期し、重複した「Local modifications」を 1 つに統合し、`evals/` に 3 ケースの足場を追加する。構造を検査する単体テスト(`EvalCaseTests`、`ReadmeTests`)を先に追加する。スクリプト・スキーマ・`SKILL.md`・`rule.md` は変更しない。eval は実行しない。

## Technical Context

**Language/Version**: Markdown、YAML、bash(`fixture.sh`)。テストは Python 3.9 以上の標準ライブラリ

**Testing**: `unittest`(新しい 2 クラス)、`check_links.py --changed`、CLI があれば `claude plugin validate`(既存のテストに含まれる)

**Constraints**: README の既存の節の順序と、無関係な記述を変えない。eval は既存の形式(`schema_version: "1.1"`、`graders/*.md` の front matter)に合わせる。`fixture.sh` は実行可能。既存 136 件を維持

## Constitution Check

`.specify/memory/constitution.md` は未記入のテンプレート。CLAUDE.md とグローバル規則を実質のゲートとする。

| ゲート | 判定 |
|---|---|
| 最小で一貫した変更 | 合格: README、`evals/`、テストのみ |
| 失敗するチェックを先に用意 | 合格: テストを先に追加し、失敗を記録する |
| 事実の記述 | 合格: 差分の一覧は実際に変更したファイルに基づく。eval の有効性は未検証と明記 |
| リポジトリ直下の README との同期 | 該当なし: 管理対象パスとインストーラの挙動は変わらない |

## 設計の要点

1. **eval ケース**(いずれも `case.yaml`: `schema_version: "1.1"`、`name`、`context.scaffold_script: fixture.sh`)
   - `updates-adjacent-doc`: `tools/convert.py` と、そのオプションを説明する `tools/README.md` がある。依頼は `--quiet` フラグの追加。採点: `tools/README.md` に `--quiet`、報告に `Documentation impact`、スキルが呼ばれた。
   - `creates-doc-for-new-contract`: 文書の無い `pkg/` と、パッケージに触れない最小のルート `README.md`。依頼は新しい公開モジュール `pkg/purge.py`(`purge(directory, days)`)の追加。採点: Markdown を書いた(`Write` の `file_path` が `.md` で内容に `purge`)、決定記録(`docs/decisions/**`、`docs/adr/**`)と `CHANGELOG.md` が作られていない、報告に `Documentation impact`。
   - `no-creation-for-internal-refactor`: `pkg/text.py` の非公開の補助関数 `_norm` と、ルート `README.md`。依頼は名前変更 `_norm` → `_normalize`。採点: Markdown を書かない(`Write`)・編集しない(`Edit`)、報告に `Documentation impact: none`。
2. **README の更新箇所**: Layout(`find_related.py`、`tests/`、`evals/`)、Scripts の表と注記(`find_related.py`)、Optional project configuration(`related`)、Making it mandatory の表と How the gate behaves(新しい検査、助言のコメント、上限、報告の理由の質)、Known limits(新しい小節)、Evals(6 ケース、足場のみの旨)、Local modifications(統合)。
3. **テスト**
   - `EvalCaseTests`: 6 ケースのディレクトリが存在し、`case.yaml` の `name` がディレクトリ名と一致、`prompt.md` の front matter に `description`、`fixture.sh` が実行可能、一時ディレクトリで実行すると Git リポジトリと 1 件の初期コミットができる、`graders/*.md` が 1 件以上で各ファイルに `type:` がある。
   - `ReadmeTests`: 「## Local modifications」が 1 つ、その節に既存の項目(`Numbering`、`Language`、`Local convention`)と新しい項目(`find_related.py`、`stop_gate.py`、`common.py`、`related`、`Layers, placement, and proximity`、`GoogleSWE2020` など)の語句がある、README が `find_related.py`、`related.max_candidates`、`related.min_name_length`、`Known limits` に言及する。

## テスト先行

`EvalCaseTests` と `ReadmeTests` を先に追加し、失敗(新しいケースと README の更新が無い)を記録する。その後、eval の 3 ケース、README の順に実装して通す。

## リスクと分岐

- **A4**: 足場の妥当性は実行するまで未検証。README と最終報告に明記する。偽(Δ ≤ 0)なら S4 の再仕様、またはユーザーへの相談(B4)。
- **README の誤記**: 挙動の記述は、実装済みの仕様(spec 044・045・047・048)に基づき、テストが語句を確認する。

## Complexity Tracking

違反なし。
