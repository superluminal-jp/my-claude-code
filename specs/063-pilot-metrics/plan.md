# Implementation Plan: 介入時間の削減と品質の維持を、事前に固定した基準で判定する

**Branch**: `feat/pilot-metrics` | **Date**: 2026-11-06 | **Spec**: [spec.md](spec.md)

## Summary

`change-assurance` に `scripts/pilot.py` と `references/pilot.md` を加える。`pilot.py` は同じディレクトリの `assure.py` から入力の読み込み(大きさの上限、重複キーの拒否など)を取り込み、事前登録と案件の記録を検査し(E-00、E-01)、方式ごとの中央値、削減率、層ごとの比較、品質の条件の違反、未完了の件数から `adopt`・`not_adopted`・`insufficient` を返す。テストは合成のデータで、`tests/test_pilot.py` にある。

## Technical Context

Python 3(3.9 以上)、標準ライブラリだけ(`statistics.median`、`datetime.date.fromisoformat`)。読み取り専用。

## Constitution Check

`.specify/memory/constitution.md` は未記入の雛形である。代わりのゲート(`.claude/` の下にリポジトリ固有の事実を入れない、README の英日をそろえる、`install.sh` を変えない)は、いずれも合格。
