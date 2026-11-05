# Implementation Plan: 判定の結果と証拠を、1画面のレビューカードに表示する

**Branch**: `feat/review-card` | **Date**: 2026-11-06 | **Spec**: [spec.md](spec.md)

## Summary

`change-assurance` の `scripts/assure.py` に `card` を加える。カードは同じファイルの `run_gate` の結果(判定、水準ごとの件数、理由、検査ごとの状態)をそのまま使い、問題カード、要求グラフ、検査の証拠、反証の記録の `open` の指摘を Markdown に並べる。テストは `tests/test_card.py`(サブプロセスで起動する `unittest`)。

## Technical Context

Python 3(3.9 以上)、標準ライブラリだけ。読み取り専用。出力は標準出力だけ。入力の文は `md()`・`code()`・`mermaid_text()` で無害にする。

## Constitution Check

`.specify/memory/constitution.md` は未記入の雛形である。代わりのゲート(`.claude/` の下にリポジトリ固有の事実を入れない、README の英日をそろえる、`install.sh` を変えない)は、いずれも合格。
