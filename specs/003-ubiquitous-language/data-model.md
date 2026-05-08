# Data Model: Ubiquitous Language Auto-Builder

**Feature**: 003-ubiquitous-language
**Date**: 2026-05-08

## Overview

このフィーチャーはプログラムコードではなく Claude Code スキルシステム（Markdown playbook）として実装される。「データモデル」はファイル構造・スキーマ・状態遷移ルールを指す。

---

## 1. UL アーティファクト（BC ごとのファイル）

**格納先**: `.specify/ubiquitous-language/<bc-name>.md`

### ファイルヘッダ

```markdown
# Ubiquitous Language: <BC 名>

**Bounded Context**: `<bc-name>`
**Project**: <プロジェクト名>
**Last Updated**: YYYY-MM-DD (<lifecycle event or "conversational">)
**Entry Count**: N / 30 (budget)
**Status**: active | needs-review
```

### UL テーブルスキーマ

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| 用語 | string | yes | 業務で使う正式名称（原語） |
| 定義 | string | yes | 何を意味するか。状態・振る舞いまで含む |
| 文脈（BC） | string | yes | どの境界づけられた文脈で使うか |
| 状態/ルール | string | stateful terms: yes | 重要な制約・状態遷移（矢印記法で 1 行） |
| 例 | string | yes | 含まれるもの |
| 反例 | string | yes | 含まれないもの |
| 実装名 | string | yes | クラス/メソッド/テーブル/API/イベント/UI ラベル名 |
| 出典 | string | no | domain-expert / developer-derived / <文書名> |
| 更新イベント | string | auto | 最終更新が発生したライフサイクルイベント名 |

**Markdown 表現例**:

```markdown
| 用語 | 定義 | 文脈（BC） | 状態/ルール | 例 | 反例 | 実装名 |
|------|------|-----------|-----------|-----|------|--------|
| 確定済み注文 | 支払い承認が完了し在庫引当の対象になる注文 | 販売 | 注文作成済み→確定済み→在庫引当済み | 決済完了直後の注文 | 支払い保留中の注文 | `ConfirmedOrder`, `Order.confirm()`, `OrderConfirmed` (event) |
```

### バジェットルール

- 1 BC あたり最大 30 エントリ（設定で変更可）
- 超過時はスキルが BC 分割または統合を提案
- エントリが不完全（例/反例/実装名のいずれか欠落）の場合は `[NEEDS DOMAIN INPUT]` マーカー付き

---

## 2. コンテキストマップ

**格納先**: `.specify/ubiquitous-language/context-map.md`

### スキーマ

```markdown
# Context Map

| 用語 | BC-A | BC-B | 関係種別 | 備考 |
|------|------|------|---------|------|
| 顧客 | SalesAccount | BillingParty | same-name-different-meaning | 営業は商談中法人、請求は請求先法人 |
| 契約 | Contract (Sales) | Agreement (Legal) | synonym | 同概念・異名 |
```

**関係種別 enum**:
- `same-name-different-meaning`: 同名・異義（BC ごとに定義が違う）
- `synonym`: 異名・同義（同じ概念を異なる名前で呼ぶ）
- `identical`: 完全同一（BC をまたいで同義・同名）
- `refines`: BC-B の定義が BC-A の定義を細分化している

---

## 3. ウォッチリスト設定

**格納先**: `.specify/ubiquitous-language/watchlist.md`（オプション。未存在時はスキル内デフォルトを使用）

```markdown
# Vague-Term Watchlist

## Default (Japanese)
データ, 情報, 処理, 管理, ステータス, フラグ, 有効, 完了, 対象, ユーザー

## Project-specific additions
<!-- プロジェクト固有の追加 -->

## Project-specific overrides (remove from default)
<!-- デフォルトから除外 -->
```

---

## 4. 収集キュー（セッション内 transient）

キューはファイルに永続化しない。スキル playbook 内のワーキングメモリとして管理する。

| フィールド | 説明 |
|---|---|
| `candidate_term` | 検出された候補語 |
| `source_text` | 検出元テキスト（引用） |
| `trigger_type` | `vague-term` / `new-concept` / `drift` / `missing-state` |
| `detected_at` | 検出したライフサイクルイベントまたは会話番号 |

バッチ提示のトリガー:
- 新規業務語出現がない会話ターン（= 自然な区切り）
- speckit ライフサイクルイベント開始時

---

## 5. Ontology Header（コンテキスト長圧縮用）

セッション開始時に注入する要約形式。スキルが自動生成。

```markdown
## Ubiquitous Language Reference (BC: 販売)
| 用語 | 1行定義 |
|------|---------|
| 確定済み注文 | 支払い承認済みで在庫引当対象の注文 |
| キャンセル可能注文 | 出荷指示前かつキャンセル期限内の注文 |
...
（最大 30 エントリ / BC）
```

---

## 6. 状態遷移

### UL エントリのライフサイクル

```
[下書き / NEEDS DOMAIN INPUT]
  ↓ ユーザーが例・反例・実装名を確認
[完全エントリ]
  ↓ 実装名ドリフト検知
[ドリフト警告] → ユーザーが解決 → [完全エントリ]
  ↓ プロジェクト削除決定
[アーカイブ]
```

### UL ファイルのライフサイクル

```
[不在]
  ↓ ブートストラップ (FR-001)
[初期 UL (< 30 エントリ)]
  ↓ 継続収集
[成長中 UL]
  ↓ 30 エントリ超
[BC 分割提案] → ユーザーが承認 → [複数 BC に分割]
  ↓ プロジェクト成熟
[安定 UL (Ontology Header 利用可)]
```

---

## 7. 実装名ドリフト検知ルール

比較対象:
1. UL エントリの「実装名」フィールド（カンマ区切りの名前リスト）
2. AI 生成アーティファクト内のコード識別子（クラス名・メソッド名・API パス・イベント名パターン）

検知条件:
- 完全一致: ドリフトなし
- 部分一致（例: UL=`Order.confirm()`, artifact=`order.confirm()`): 警告なし（大小文字・区切り文字の違いは無視）
- 意味的乖離（例: UL=`Order.confirm()`, artifact=`Order.process()`): ドリフト警告

検知できない範囲（v1 のスコープ外）:
- 実プロジェクトのソースコード走査
- DB テーブル名・カラム名の自動チェック
