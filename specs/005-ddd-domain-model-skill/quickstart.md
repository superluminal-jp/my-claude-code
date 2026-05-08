# Quickstart: domain-model スキル

## 前提条件

- Claude Code がインストールされていること
- `.claude/CLAUDE.md` に `domain-model` スキルのエントリが追加されていること

## セットアップ（1 回のみ）

`.claude/CLAUDE.md` の skills セクションに以下を追加する:

```markdown
- `domain-model` — activate when conversation contains DDD structural patterns (aggregates, entities, value objects, domain events, invariants) or when user asks to create/update a domain model; passively queues candidates; surfaces at natural pauses
```

## 使い方

### パターン A: 会話しながら自動収集（受動モード）

```
ユーザー: 注文は複数の明細を持つ。注文IDで一意に識別される。
         在庫がゼロの場合は注文できない。

→ スキルが候補をキューに積む（会話は中断されない）

（次のターンで新規語彙がなければ）

スキル: 以下の候補を検出しました。確認をお願いします:
        - 「注文」 → 集約候補
        - 「注文ID」 → エンティティ候補（識別子）
        - 「在庫がゼロの場合は注文できない」 → 不変条件候補
```

### パターン B: 明示的にモデルを作成する

```
ユーザー: 注文コンテキストのドメインモデルを作成して

スキル: （Bootstrap フロー開始）
        このコンテキストの集約（整合性の単位）は何ですか？
        例: 注文、請求書、カート
```

### パターン C: UL があるプロジェクトで起動する

```
docs/ubiquitous-language.md が存在する状態でスキルを起動すると:
→ UL のエントリをドメインモデル候補として提案
→ ドメインイベントは UL の命名を使用（上書き不可）
```

## 生成されるファイル

```
docs/models/
  index.md                     # BC 一覧 + コンテキスト間関係図
  order.md                     # 注文コンテキストのモデル例
  inventory.md                 # 在庫コンテキストのモデル例
```

## 注意事項

- ファイルへの書き込みは常に **差分確認 → 明示承認** の後に実行される
- `docs/ubiquitous-language.md` は読み取り専用（このスキルは書き込まない）
- 1 つの Bounded Context = 1 ファイル（複数コンテキストの混在は禁止）
