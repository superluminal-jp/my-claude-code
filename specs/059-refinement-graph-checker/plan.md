# Implementation Plan: 要求とスキルの多段の関係を宣言し、その構造を読み取り専用の検査器で検査する

**Branch**: `feat/refinement-graph-checker` | **Date**: 2026-11-06 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/059-refinement-graph-checker/spec.md`

## Summary

検査器は、Python 3 の標準ライブラリだけで書いた1つのコマンド `tools/refinement-checker/check_graph.py` として実装する。宣言ファイル(JSON)または互換モードのスキルのディレクトリを読み、spec の規則 S-00〜S-11 を判定して、違反の一覧と終了コード 0・1・2 を返す。受け入れテストは、検査器をサブプロセスとして起動する `unittest` のテストで、spec の受け入れシナリオ P1-01〜P1-12 と User Story 2 の負例を1つずつ確かめる。リポジトリの検査スクリプトの慣例に合わせ、`tests/run-refinement-checker.sh` がそのテストと例の検査をまとめて実行し、CI の必須ジョブ `test` がそのスクリプトを呼ぶ。設計の判断とその代替案は [research.md](research.md) にある。

## Technical Context

**Language/Version**: Python 3。構文は 3.9 以上で動く範囲に限る(macOS 標準の `python3` と CI の `ubuntu-latest` の両方で動かすため)。

**Primary Dependencies**: なし(標準ライブラリの `argparse`、`json`、`pathlib`、`re`、`sys` だけ)。

**Storage**: なし。入力のファイルを読むだけで、何も書かない。

**Testing**: 標準ライブラリの `unittest`。検査器をサブプロセスとして起動し、終了コードと JSON の出力を確かめる。実行は `tests/run-refinement-checker.sh` から行う。

**Target Platform**: macOS(保守者の手元)と GitHub Actions の `ubuntu-latest`(CI)。

**Project Type**: 単一のコマンドラインツール。

**Performance Goals**: このリポジトリの規模(スキル約30、要求グラフ数十ノード)で1秒未満。10,000 ノードの直鎖でも再帰の上限で異常終了しないよう、グラフの探索は反復で行う。

**Constraints**: 読み取り専用。ネットワークに接続しない。入力の内容をコードとして実行しない。入力の大きさを 5 MiB に制限する。`.claude/`、`install.sh`、`tests/run-config-pyramid.sh` を変えない(spec FR-012)。

**Scale/Scope**: 規則 12 個(S-00〜S-11)、受け入れシナリオ12個、例2つ。

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` は記入されていない雛形であり、批准された原則はない。このため、代わりにリポジトリの `CLAUDE.md` と既存の ADR が定める制約をゲートとして確かめる。

| ゲート | 出典 | 設計時 | 設計後 |
|---|---|---|---|
| `.claude/` の下は利用者レベルの設定そのものであり、リポジトリ固有の事実を入れない | `CLAUDE.md` | 合格。検査器は `.claude/` の外に置く | 合格 |
| `~/.claude/` を直接編集しない | `CLAUDE.md` | 合格。`install.sh` を実行しない | 合格 |
| 管理パスやインストーラの振る舞いを変えたら `README.md` と `README.ja.md` をそろえる | `CLAUDE.md` | 管理パスもインストーラも変えない。ただしファイル構成・検証・CI の節は変わるため、両方を更新する | 合格(tasks.md の更新の作業) |
| 用途・配布先・実行主体を追えないスクリプトを残さない | ADR-0007 | 合格。検査器の README に3点を書く(spec D2) | 合格 |

違反はないため、Complexity Tracking は空である。

## Project Structure

### Documentation (this feature)

```text
specs/059-refinement-graph-checker/
├── spec.md              # 仕様(正)
├── plan.md              # 本ファイル
├── research.md          # 設計の判断と代替案
├── data-model.md        # 宣言ファイルの要素と検証の規則
├── quickstart.md        # 動作を確かめる手順
├── contracts/
│   └── cli.md           # コマンドの引数、入力の形式、出力の形式、終了コード
├── checklists/
│   └── requirements.md  # 仕様の品質の点検
└── tasks.md             # 作業の一覧(/speckit-tasks の出力)
```

### Source Code (repository root)

```text
tools/refinement-checker/
├── check_graph.py               # 検査器(読み取り専用のコマンド)
├── README.md                    # 用途・実行主体・配布先・使い方・規則・限界(英語)
├── README.ja.md                 # 同じ内容の日本語版
├── examples/
│   ├── requirements-graph.example.json   # 引き継ぎ書 §20.3 A の例
│   └── skills-graph.example.json         # 引き継ぎ書 §20.3 B の例
└── tests/
    ├── test_check_graph.py      # 受け入れテスト(サブプロセスで起動)
    └── fixtures/
        ├── requirements/*.json  # User Story 1 のシナリオ1〜14の正例と負例
        └── skills/*.json        # User Story 2 の正例と負例

tests/run-refinement-checker.sh  # 上のテスト・例・互換モードの検査をまとめて実行
.github/workflows/ci.yml         # ジョブ test に1ステップを加える
README.md, README.ja.md          # ファイル構成・検証・CI の節を更新
```

**Structure Decision**: 単一のツールのディレクトリ `tools/refinement-checker/` に、コマンド、文書、例、テストをまとめる。Phase 2 でスキルのパッケージへ移す場合は、このディレクトリを丸ごと移せばよい。互換モードのテストに使う架空のスキルは、spec 058 の検査と同じく一時ディレクトリに作り、リポジトリに `SKILL.md` を増やさない。

## Complexity Tracking

Constitution Check に違反はない。
