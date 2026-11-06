# Implementation Plan: 工程を飛ばしても、保証の判定が合格を出さないようにする

**Branch**: `feat/assurance-gate-hardening` | **Date**: 2026-11-06 | **Spec**: [spec.md](spec.md)

## Summary

`goal-refinement` の `scripts/check_graph.py` に規則 S-12 を加える。`change-assurance` の `scripts/assure.py` では、判定が要求グラフの文書をそのまま受け取り、A-09(構造)、A-08(反証の記録の指摘が答えられていること)、A-10(保証レビューの記録)を判定する。`gate` と `card` に `--review` を加える。2か所の構造の規則のずれは、リポジトリの `tests/assert_assurance_parity.py` が `goal-refinement` のテストの要求グラフで確かめる。

## Technical Context

Python 3(3.9 以上)、標準ライブラリだけ。読み取り専用。`assure.py` は `check_graph.py` を読み込まない(spec 058 FR-005、spec 061 D3)。

## Constitution Check

`.specify/memory/constitution.md` は未記入の雛形である。代わりのゲート(`.claude/` の下にリポジトリ固有の事実を入れない、README の英日をそろえる、`install.sh` を変えない)は、いずれも合格。
