# Quickstart: Ubiquitous Language Auto-Builder

**Feature**: 003-ubiquitous-language
**Date**: 2026-05-08

## 前提条件

- spec-kit が初期化済み（`.specify/` ディレクトリが存在すること）
- `feature/003-ubiquitous-language` ブランチで作業中

---

## セットアップ手順（実装担当者向け）

### Step 1: スキルファイルを作成する

`.claude/skills/ubiquitous-language/SKILL.md` を新規作成する。

プレイブックの主要セクション:
1. **Pre-check** — `.specify/` と既存 UL ファイルの有無を確認
2. **Bootstrap mode** — 業務イベント起点の対話を実行し初期 UL を生成
3. **Collect mode** — 既存 UL に対して走査・候補キュー・バッチ提示を実行
4. **Validate mode** — 曖昧語ウォッチリスト走査・ドリフト検知を実行
5. **Context compression** — Ontology Header 生成・Delta Notation 適用

### Step 2: UL テンプレートを作成する

`.specify/templates/ubiquitous-language-template.md` を追加する（`data-model.md` §1 のフォーマット参照）。

### Step 3: コンテキストマップテンプレートを作成する

`.specify/templates/context-map-template.md` を追加する（`data-model.md` §2 のフォーマット参照）。

### Step 4: extensions.yml を更新する

`contracts/extensions-yml-additions.md` に定義した YAML スニペットを `.specify/extensions.yml` の各 `before_*` キーに追記する。

### Step 5: CLAUDE.md のスキルルーティングに 1 行追加する

`.claude/CLAUDE.md` の `Skills (mandatory routing)` セクションに `contracts/extensions-yml-additions.md` に定義したルール 1 行を追加する。

### Step 6: テストシナリオを作成する

`tests/ubiquitous-language/` を作成し、`research.md` Decision 6 に定義した 8 シナリオファイルを追加する。

---

## 動作確認（開発者向け）

### 確認 1: ブートストラップ（US1）

```
/speckit-specify [任意の業務ドメイン説明]
```

期待動作:
- `.specify/ubiquitous-language/` が不在 → スキルが業務イベント起点の質問を開始する
- 回答後、`<bc-name>.md` が生成される
- エントリが 7 フィールドすべてを含む（未入力は `[NEEDS DOMAIN INPUT]`）

### 確認 2: 曖昧語検知（US2 / SC-003）

1. 既存 UL がある状態で、「ユーザーが処理を完了する」を含むメモをチャットで送る
2. 期待動作: スキルがキューに積み、次の自然な区切りで引用付き置換候補を提示する

### 確認 3: 会話モード収集（FR-030）

1. `/speckit-*` コマンドを一切使わず、「注文が確定されると在庫引当が走ります」とチャットで送る
2. 期待動作: スキルが「注文」「確定」「在庫引当」を候補としてキューに積み、次の区切りでバッチ提案する

### 確認 4: BC 分割（US3）

1. 「顧客」について「営業では…」「請求では…」と異なる定義を入力する
2. 期待動作: 衝突を提示し 3 択（BC ごとに別エントリ / BC 統合 / 片方改名）を示す

### 確認 5: ドリフト検知（FR-016）

1. UL に `Order.confirm()` が登録済みの状態で、`Order.process()` を含む plan.md を渡す
2. 期待動作: ドリフト警告が出て 3 択（artifact 修正 / UL 更新 / 新語分離）が提示される

### 確認 6: Ontology Header（FR-022）

1. UL が 5 語以上確定した状態で新しい speckit コマンドを実行する
2. 期待動作: AI の応答の冒頭またはシステム注入箇所に Ontology Header テーブルが現れる

---

## UL を日常的に使うために（チーム向け）

1. **新しい仕様を書く前**に `/ubiquitous-language bootstrap` で BC を確認する
2. **会議後**: 「つまり何を指していますか？」が出た語は即チャットに貼る → 自動キューに入る
3. **コードレビュー前**: `/ubiquitous-language check` を走らせて実装名のドリフトを確認する
4. **週次**: `/ubiquitous-language show <bc>` でエントリが 30 語を超えていないか確認する
