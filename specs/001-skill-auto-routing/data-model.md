# Data Model: Automatic Skill Routing

**Feature**: 001-skill-auto-routing  
**Date**: 2026-05-06

## Overview

この機能はソースコードやデータベースを持たない設定変更である。「データモデル」に相当するのは、ルーティングルールのスキーマと、テストシナリオの構造定義。

---

## Skill Routing Rule

各ルールの最小表現:

| Field | Type | Description |
|---|---|---|
| `trigger` | string | ルーティングを発動させるリクエストカテゴリ |
| `skill` | string | ロードするスキル名（`coder` / `editor` / `clarifier`） |
| `priority` | integer | 複数スキルが該当する場合のロード順（小さい値が先） |

**Rules table** (FR-001〜FR-005):

| trigger | skill | priority |
|---|---|---|
| コード実装・修正・リファクタリング・テスト・デバッグ | `coder` | 1 |
| ドキュメント・スライド・チャート・翻訳・文章編集 | `editor` | 2 |
| 任意の曖昧さ（intent/scope/acceptance/constraint gap） | `clarifier` | 0 (最優先) |

**Note**: `clarifier` は priority 0 で他スキルより先に起動を検討する。ただし spec-kit スラッシュコマンド（`/speckit-*`）は対象外（FR-006）。

---

## Prompt Test Scenario

`tests/skill-routing/` に蓄積するシナリオファイルのスキーマ:

| Field | Type | Required | Description |
|---|---|---|---|
| `title` | string | yes | シナリオの名称 |
| `input_prompt` | string | yes | テスト用入力プロンプト |
| `expected_skill` | string or list | yes | 期待されるスキル名（混在時はリスト） |
| `expected_order` | list | no | 混在時のロード順（例: ["coder", "editor"]） |
| `expected_behavior` | string | yes | 期待される動作の説明 |
| `pass_criteria` | string | yes | 合否判定の基準（観察可能な事実ベース） |
| `category` | enum | yes | `code` / `document` / `mixed` / `ambiguous` |

---

## State Transitions

ルーティング判定の状態遷移:

```
Request received
  └─ spec-kit slash command? → [対象外: 各コマンドの playbook に従う]
  └─ 曖昧さあり? → clarifier (優先)
       └─ 曖昧さ解消後 → 再判定
  └─ コード変更を含む? → coder
       └─ ドキュメント変更も含む? → editor (coder完了後)
  └─ ドキュメントのみ? → editor
```
