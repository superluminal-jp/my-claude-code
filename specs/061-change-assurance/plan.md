# Implementation Plan: 実行の証拠で、葉・親・システムの検証を別々に判定する

**Branch**: `feat/change-assurance` | **Date**: 2026-11-06 | **Spec**: [spec.md](spec.md)

## Summary

新しい親スキル `.claude/skills/change-assurance/` に、検査器 `scripts/assure.py`(`check`、`gate`、`collect-junit`)、手順の `SKILL.md`、保証レビュー役の指示文 `references/reviewer.md`、形式の参照 `references/manifest.md`、例、テストを置く。テストは spec 059・060 と同じく、検査器をサブプロセスで起動する `unittest` である。

## Technical Context

**Language/Version**: Python 3(構文は 3.9 以上)。**Primary Dependencies**: 標準ライブラリだけ(XML は `xml.etree.ElementTree`。読む前に `<!DOCTYPE` と `<!ENTITY` を拒む)。**Testing**: パッケージの `tests/`、`tests/run-change-assurance-skill.sh`(新規。CI の必須ジョブに加える)、`tests/run-config-pyramid.sh`。**Constraints**: 読み取り専用。ほかのスキルのパスを参照しない(D3)。

## Constitution Check

`.specify/memory/constitution.md` は未記入の雛形である。代わりのゲート(`.claude/` の下にリポジトリ固有の事実を入れない、README の英日をそろえる、`install.sh` を変えない)は、いずれも合格。

## Project Structure

```text
.claude/skills/change-assurance/
├── SKILL.md                 # 親スキル(## Child skills に3つの子)
├── references/manifest.md   # 検証の記録の形式と規則
├── references/reviewer.md   # 保証レビュー役の指示文
├── scripts/assure.py
├── examples/                # pass になる要求グラフと検証の記録の1組
└── tests/                   # test_assure.py と fixtures/
tests/run-change-assurance-skill.sh
.github/workflows/ci.yml     # 上のスクリプトを加える(8本目)
tests/run-refinement-checker.sh  # T-04・T-05・T-06・T-10 の NOT RUN の行を、change-assurance で実装したと示す行に変える
```
