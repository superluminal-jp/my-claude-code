# Research: Automatic Skill Routing

**Feature**: 001-skill-auto-routing  
**Date**: 2026-05-06

## Decision 1: Mandatory vs. On-Demand Routing

**Decision**: "on-demand" の語を削除し、ルーティングを mandatory（常時適用）に変更する。

**Rationale**: 現行 CLAUDE.md の Skills セクションには「Load only when the request matches the trigger」と書かれており、これは「条件が合えば読み込む」という任意性を示す。FR-001〜FR-003 は「必ず（MUST）ロードする」を要求しているため、表現を強制に変える。

**Alternatives considered**:
- hook を使った強制ロード → Claude Code の skills は hook で強制できない（Skill tool 経由での呼び出しのみ）; CLAUDE.md の instruction として記述するのが唯一の実装手段
- skills フォルダの always-on 化 → 現行アーキテクチャ上、skills は on-demand 設計; always-on は rules で代替できる

---

## Decision 2: Rules の削減範囲

**Decision**: 以下のセクションを削除または統合する。

| ファイル | 削除するもの | 残すもの |
|---|---|---|
| `CLAUDE.md` > Skills | 説明文（"Use when..."）、"For spec-kit projects..." 注記 | 各スキル 1 行トリガーのみ |
| `rules/skill-routing.md` | Mandatory gate セクション全体、Scope discipline セクション全体 | Routing セクションの 3 行のみ |

**Rationale**:
- Mandatory gate の内容（clarify.md を先に走らせる）は `Response Preflight` セクションで既にカバーされている
- Scope discipline（最小スキルのみロード）は FR-004（混在時は両方ロード）と整合するよう更新が必要

**Alternatives considered**:
- `rules/skill-routing.md` を完全削除し CLAUDE.md に統合 → ファイル分離のメリット（個別参照・更新）を維持するため却下

---

## Decision 3: clarifier のトリガー強度

**Decision**: `rules/clarify.md` の全判定基準（軽微な曖昧さを含む）をトリガーとし、「不明確なまま進めない」を明示する。

**Rationale**: Q3/Q4 の回答より。clarifier は proactive に起動し、ユーザーの要件理解を促進する目的がある。

---

## Decision 4: tests/ フォルダ構造

**Decision**: `tests/skill-routing/` フォルダを作成し、プロンプトシナリオを Markdown ファイルで管理する。

**シナリオファイル形式**:
```markdown
# Test: [シナリオ名]
## Input Prompt
[テスト用プロンプト]
## Expected Skill
[期待されるスキル名]
## Expected Behavior
[期待される動作の説明]
## Pass Criteria
[合否判定基準]
```

**カテゴリ構成**:
- `001-code-*.md` — コード関連リクエスト
- `002-document-*.md` — ドキュメント関連リクエスト
- `003-mixed-*.md` — 混在リクエスト（coder → editor 順）
- `004-ambiguous-*.md` — 曖昧リクエスト（clarifier 起動確認）

**Alternatives considered**:
- YAML/JSON 形式 → Markdown の方が人間可読性が高く、プロンプトの自然な記述に向く
- specs/ フォルダ内に同居 → Q5 の回答で `tests/` フォルダを独立させることが明示された
