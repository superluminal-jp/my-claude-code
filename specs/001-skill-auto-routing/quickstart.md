# Quickstart: Automatic Skill Routing

**Feature**: 001-skill-auto-routing  
**Date**: 2026-05-06

## What Changes

| File | Change |
|---|---|
| `.claude/CLAUDE.md` | Skills セクションを mandatory ルーティングに書き換え（各スキル 1 行トリガー） |
| `.claude/rules/skill-routing.md` | Routing セクション 3 行のみ残し、Mandatory gate・Scope discipline を削除 |
| `tests/skill-routing/` | プロンプトテストシナリオフォルダを新規作成 |

## Implementation Steps

1. `.claude/CLAUDE.md` の Skills セクションを編集
   - "on-demand" → mandatory（必ず適用）に変更
   - 各スキルの説明文を削除し、トリガー条件 1 行のみに絞る
   - `clarifier` のトリガーを「軽微な曖昧さでも起動」に強化

2. `.claude/rules/skill-routing.md` を編集
   - Routing セクションの 3 行のみ残す
   - Mandatory gate セクション削除（Response Preflight に統合済み）
   - Scope discipline セクション削除（FR-004 の混在ルールと整合済み）

3. `tests/skill-routing/` フォルダを作成し、初期テストシナリオを追加
   - カテゴリ: code / document / mixed / ambiguous

## Test Execution

各シナリオファイルの `input_prompt` を Claude Code に入力し、`pass_criteria` に従って合否を判定する。全シナリオ合格で SC-001〜SC-003 を充足。

## Rollback

変更は Git で管理されているため、問題が発生した場合は `git revert` で即時復元可能。
