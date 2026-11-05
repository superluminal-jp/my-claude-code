# Implementation Plan: 問題カード・要求グラフ・反証の記録を結び、実装へ進めるかを判定する

**Branch**: `feat/goal-refinement` | **Date**: 2026-11-06 | **Spec**: [spec.md](spec.md)

## Summary

spec 059 の検査器 `check_graph.py` を新しい自作スキル `.claude/skills/goal-refinement/` の `scripts/` へ移し、宣言の種類に問題カードと反証の記録を、引数に `--gate` を加える。スキルの `SKILL.md` は、問題カード → 要求グラフ → 反証役(任意) → 判定の手順を定め、反証役の指示文を `references/challenger.md` に置く。テストは spec 059 と同じく、検査器をサブプロセスで起動する `unittest` である。

## Technical Context

**Language/Version**: Python 3(構文は 3.9 以上)。**Primary Dependencies**: 標準ライブラリだけ。**Testing**: `unittest`(パッケージの `tests/`)と `tests/run-refinement-checker.sh`、`tests/run-config-pyramid.sh`。**Constraints**: 読み取り専用、ネットワークなし。スキルの Markdown は、ほかの自作スキルを名前でもパスでも参照しない(検査 SKILL-05)。パッケージは自分のインストール先のパスを書かない(SKILL-06)。

## Constitution Check

`.specify/memory/constitution.md` は未記入の雛形である。代わりのゲート: `.claude/` の下にリポジトリ固有の事実を入れない(スキルの本文は、どのプロジェクトでも通じる手順だけを書く)、README の英日をそろえる、`install.sh` を変えない。いずれも合格。

## Project Structure

```text
.claude/skills/goal-refinement/
├── SKILL.md                     # 手順(問題カード → 要求グラフ → 反証役 → 判定)
├── references/
│   ├── challenger.md            # 反証役のサブエージェントに渡す指示文
│   └── declarations.md          # 宣言の形式と規則の要約(spec の契約をスキル内で読める形に)
├── scripts/check_graph.py       # spec 059 の検査器 + 問題カード・反証の記録・判定
├── examples/                    # spec 059 の例2つ + 判定が ready になる1組
└── tests/
    ├── test_check_graph.py      # spec 059 の49件 + 本仕様のテスト
    └── fixtures/                # requirements/、skills/、gate/、challenger/
tests/run-refinement-checker.sh  # パスを移した先へ変える
tests/run-config-pyramid.sh      # authored_skills と名前のパターンに goal-refinement を加える
README.md, README.ja.md          # スキルの説明と索引、構成、検証
```

`tools/refinement-checker/` は削除する(中身はすべて移す)。互換モードでこのリポジトリのスキルを読むテスト(spec 059 の P1-11)は、パッケージのテストからまとめの検査スクリプトだけへ移す。パッケージのテストがインストール先で実行されても、リポジトリの位置に依存しないようにするためである。
