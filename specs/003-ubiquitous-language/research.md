# Research: Ubiquitous Language Auto-Builder

**Feature**: 003-ubiquitous-language
**Date**: 2026-05-08

## Decision 1: スキル実装方式（SKILL.md playbook vs. 複数スキル分割）

**Decision**: 単一スキル `ubiquitous-language` （`.claude/skills/ubiquitous-language/SKILL.md`）として実装し、引数または検知モードで挙動を切り替える。

**Rationale**:
- 既存プロジェクトの `coder` `editor` `clarifier` はいずれも単一 SKILL.md で複数モードに対応している
- 分割すると `extensions.yml` のエントリが増殖し、フック管理が煩雑になる
- Claude Code の skill routing は SKILL.md 内の条件分岐で十分に対応できる

**Alternatives considered**:
- bootstrap / collect / validate の 3 スキル分割 → 管理オーバーヘッドが高く、単一 speckit フェーズ内で複数スキル呼び出しが不明確になるため却下

---

## Decision 2: 会話モードトリガーの実装

**Decision**: CLAUDE.md に常駐ルールとして追記する。「`.specify/ubiquitous-language/` が存在する場合、または会話中に業務イベント語・状態語が検出された場合、`ubiquitous-language` スキルをロードする」というルールを `Skills` セクションに 1 行追加する。

**Rationale**:
- 001-skill-auto-routing の研究結果より：「スキルを 'always-on' にするには CLAUDE.md の instruction として記述するのが唯一の実装手段」（hooks での強制ロードは不可）
- `.specify/` 存在チェックは会話内での `Bash` ツール呼び出しでできるが、毎回のオーバーヘッドを避けるため CLAUDE.md のルールで「プロジェクトコンテキストがある場合」に限定する
- speckit コマンド経由の場合は extensions.yml フックで別途トリガーする（二重起動を防ぐため `speckit-mode` と `conversational-mode` を相互排他にスキル内で処理する）

**Alternatives considered**:
- `UserPromptSubmit` フック化 → `.claude/hooks/` で実装可能だが、毎プロンプトで全文スキャンを走らせることになりノイズが増す。CLAUDE.md ルール + スキル内の自己判断で十分
- `CronCreate` による定期チェック → UL はリアルタイム収集が価値であり、cron は不適

---

## Decision 3: extensions.yml への UL フック追加方式

**Decision**: `before_specify`, `before_clarify`, `before_plan`, `before_tasks`, `before_analyze` に `ubiquitous-language.collect`（optional: true）フックを追加する。`after_*` には追加しない（収集後確認は次の会話冒頭で行うため）。

**Rationale**:
- `before_*` に置くことで「アーティファクト生成前に UL を最新化する」タイミングが保証される
- optional: true にすることで、UL がまだ存在しないプロジェクト（初回）でも中断なく進める
- `after_*` はコミット系（git.commit）の用途で使われており、責務が被る

**Hook definition**:
```yaml
command: ubiquitous-language.collect
enabled: true
optional: true
description: Collect and validate ubiquitous language before spec-kit phase
condition: null
```

---

## Decision 4: UL ファイルの格納場所とフォーマット

**Decision**: `.specify/ubiquitous-language/<bc-name>.md` に各 BC のUL テーブルを置く。コンテキストマップは `.specify/ubiquitous-language/context-map.md` に置く。ファイル名は BC 名をケバブケース化したもの（例: `sales.md`, `billing.md`, `support.md`）。

**Rationale**:
- `.specify/` はすでにプロジェクト設計資産の置き場所として確立されている
- スペックファイル（`specs/`）とは別管理にすることで、フィーチャーをまたいで共有できる
- Markdown テーブル形式は既存 `spec.md` と一貫しており、レビューツールで見やすい

**Alternatives considered**:
- `specs/` 配下に置く → フィーチャー固有に見えてしまい、プロジェクト横断の設計資産であることが伝わらない
- YAML/JSON 形式 → 人間が直接編集するユースケースに不向き

---

## Decision 5: コンテキスト長圧縮プラクティス（追加調査）

DDD ユビキタス言語に加え、AI 対話特有のコンテキスト長圧縮手法として以下を採用する。

**Decision**: 以下 5 つの追加プラクティスを SKILL.md の「コンテキスト長圧縮」セクションに組み込む。

| プラクティス | 内容 |
|---|---|
| **Ontology Header** | 会話セッション開始時に確定 UL 用語の要約テーブル（用語+1行定義のみ）を先頭コンテキストとして注入し、後続の長文説明を省略する |
| **Semantic Anchoring** | UL 用語が一度定義されたら、以後の生成物でその語を参照名として使い、同義の長文表現を避ける（ドリフト防止と圧縮の両立） |
| **Delta Notation** | UL の更新時は全体再提示ではなく差分（追加・変更・削除）のみを提示。「[+] 支払い承認済み: ...」形式 |
| **Frequency-Based Depth** | 高頻度 UL 用語は Ontology Header に短縮形を載せ、低頻度・複雑な用語は初回登場時のみ完全定義を展開する |
| **State-Machine Compression** | 状態遷移を Mermaid ライクな矢印記法（`確定済み→在庫引当済み→出荷指示済み`）で 1 行に収め、詳細は UL ファイルへのリンクで補完 |

**Rationale**:
- speckit 運用は長いマルチターン会話になりやすく、同じ業務概念の繰り返し説明が最大のコンテキスト消費源
- Ontology Header は RAG / prompt caching のような外部依存なしに実現できる純粋なプロンプト設計手法
- Delta Notation は UL の継続更新（ベストプラクティス #10）とコスト最小化の両立に最も効果的

**Alternatives considered**:
- 外部ベクトル DB への UL 格納 → このプロジェクトスコープ外（v1 は MCP なしで動く前提）
- 圧縮アルゴリズム（BPE 等）による語彙最小化 → Claude に直接適用できない

---

## Decision 6: テストシナリオ構成

**Decision**: `tests/ubiquitous-language/` フォルダを作成し、001-skill-auto-routing と同じシナリオファイル形式（Markdown）を踏襲する。

**カテゴリ構成**:
| ファイル | カバー範囲 |
|---|---|
| `001-bootstrap-new-project.md` | UL ファイル不在時のブートストラップ（US1） |
| `002-vague-term-detection.md` | 曖昧語ウォッチリスト検知（FR-010, FR-011） |
| `003-conversational-collection.md` | 通常会話中のパッシブ収集（FR-030, FR-031） |
| `004-bc-split-conflict.md` | 同名異義の BC 分割（FR-014, US3） |
| `005-drift-detection.md` | UL と実装名候補のドリフト検知（FR-016, FR-017） |
| `006-context-compression.md` | Ontology Header と Delta Notation の動作確認（FR-022, FR-023） |
| `007-state-transition-elicitation.md` | 状態遷移の引き出し（FR-009） |
| `008-size-budget-enforcement.md` | 30 語超えの BC 分割提案（FR-019） |
