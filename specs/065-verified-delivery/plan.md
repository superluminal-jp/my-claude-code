# Implementation Plan: 2つのスキルを目的に合う名前に変え、検査器のレビューの指摘14件を直す

**Branch**: `refactor/verified-delivery` | **Date**: 2026-11-06 | **Spec**: [spec.md](spec.md)

## Summary

名前の変更は `git mv` と、`specs/` と `archive/` を除いたファイルの旧名の置換で行う。過去の仕様のディレクトリへのリンク(`specs/061-change-assurance/` など)は置換しない。指摘のうち振る舞いを変える9件は、回帰テストを先に加えてから直す。`assure.py` には `person_key`(F1)と `load_body`(F12)を加え、`pilot.py` は `load_body` を `assure.py` から取り込む。`check_graph.py` と `tests/run-config-pyramid.sh` の awk は、同じ CommonMark のフェンスの規則で `## Child skills` を読む(F9)。awk は区間式を使わずに書く。古い mawk にはないためである。

## Technical Context

Python 3(3.9 以上)、標準ライブラリだけ。読み取り専用。

## Constitution Check

`.specify/memory/constitution.md` は未記入の雛形である。代わりのゲート(`.claude/` の下にリポジトリ固有の事実を入れない、README の英日をそろえる、`install.sh` を変えない)は、いずれも合格。
