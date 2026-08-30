---
name: "speckit-analyze"
description: "タスク生成後に spec.md、plan.md、tasks.md 全体にわたる非破壊的なクロスアーティファクト整合性・品質分析を実行する。"
argument-hint: "Optional focus areas for analysis"
compatibility: "Requires spec-kit project structure with .specify/ directory"
metadata:
  author: "github-spec-kit"
  source: "templates/commands/analyze.md"
user-invocable: true
disable-model-invocation: false
---


## User Input

```text
$ARGUMENTS
```

処理を進める前に、ユーザー入力（空でない場合）を必ず考慮しなければなりません。

## Pre-Execution Checks

**拡張フックの確認（分析前）**:
- プロジェクトルートに `.specify/extensions.yml` が存在するか確認する。
- 存在する場合は読み込み、`hooks.before_analyze` キー配下のエントリを探す。
- YAML がパースできない、または不正な場合は、フックの確認を黙ってスキップし通常どおり続行する。
- `enabled` が明示的に `false` であるフックは除外する。`enabled` フィールドがないフックはデフォルトで有効とみなす。
- 残った各フックについて、フックの `condition` 式を解釈・評価しようとしては**ならない**:
  - フックに `condition` フィールドがない、または null/空の場合、そのフックは実行可能とみなす
  - フックが空でない `condition` を定義している場合、そのフックはスキップし、条件評価は HookExecutor の実装に任せる
- フックのコマンド名からコマンド呼び出しを構築する際は、ドット（`.`）をハイフン（`-`）に置き換える。例えば `speckit.git.commit` → `/speckit-git-commit`。
- 実行可能な各フックについて、`optional` フラグに応じて以下を出力する:
  - **オプションフック**（`optional: true`）:
    ```
    ## Extension Hooks

    **Optional Pre-Hook**: {extension}
    Command: `/{command}`
    Description: {description}

    Prompt: {prompt}
    To execute: `/{command}`
    ```
  - **必須フック**（`optional: false`）:
    ```
    ## Extension Hooks

    **Automatic Pre-Hook**: {extension}
    Executing: `/{command}`
    EXECUTE_COMMAND: {command}

    Wait for the result of the hook command before proceeding to the Goal.
    ```
    上記ブロックを出力した後、実際にフックを呼び出し、完了を待ってから続行しなければ**なりません**。このエージェント／セッションで自分自身がコマンドを実行するのと同じ方法で実行してください（呼び出し方法は上記の文字どおりの `{command}` id とは異なる場合があります。例えばスキルモードのエージェントでは `/skill:speckit-...` や `$speckit-...` として実行します）。ブロックを出力するだけではフックは実行されません。
- フックが1つも登録されていない、または `.specify/extensions.yml` が存在しない場合は、黙ってスキップする

## Goal

実装前に、3つのコアアーティファクト（`spec.md`、`plan.md`、`tasks.md`）全体にわたる不整合、重複、曖昧さ、仕様不足の項目を特定する。このコマンドは `/speckit-tasks` が完全な `tasks.md` を正常に生成した後にのみ実行しなければなりません。

## Operating Constraints

**厳密に読み取り専用**: いかなるファイルも変更しては**なりません**。構造化された分析レポートを出力する。任意の是正計画を提示する（フォローアップの編集コマンドが手動で呼び出される前に、ユーザーが明示的に承認する必要がある）。

**憲法（Constitution）の権威**: プロジェクトの憲法（`.specify/memory/constitution.md`）は、この分析の範囲内において**交渉の余地がない**。憲法との矛盾は自動的に CRITICAL となり、spec、plan、または tasks の調整を必要とする——原則の希釈化、再解釈、あるいは黙認は許されない。原則そのものを変更する必要がある場合は、`/speckit-analyze` の外部で、別途明示的な憲法の更新として行わなければならない。

## Execution Steps

### 1. Initialize Analysis Context

リポジトリのルートから `.specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks` を一度実行し、JSON をパースして FEATURE_DIR と AVAILABLE_DOCS を取得する。絶対パスを導出する:

- SPEC = FEATURE_DIR/spec.md
- PLAN = FEATURE_DIR/plan.md
- TASKS = FEATURE_DIR/tasks.md

必要なファイルのいずれかが見つからない場合はエラーメッセージを出して中止する（不足している前提コマンドを実行するようユーザーに指示する）。
"I'm Groot" のような引数中のシングルクォートについては、エスケープ構文を使用する: 例 'I'\''m Groot'（可能であればダブルクォートを使用: "I'm Groot"）。

### 2. Load Artifacts (Progressive Disclosure)

各アーティファクトから最小限必要なコンテキストのみを読み込む:

**spec.md から:**

- 概要／コンテキスト
- 機能要件（Functional Requirements）
- 成功基準（Success Criteria）（測定可能な成果——例: パフォーマンス、セキュリティ、可用性、ユーザーの成功、ビジネスへの影響）
- ユーザーストーリー
- エッジケース（存在する場合）

**plan.md から:**

- アーキテクチャ／技術スタックの選択
- データモデルへの参照
- フェーズ
- 技術的制約

**tasks.md から:**

- タスク ID
- 説明
- フェーズのグルーピング
- 並列マーカー [P]
- 参照されているファイルパス

**constitution から:**

- 原則の検証のために `.specify/memory/constitution.md` を読み込む

### 3. Build Semantic Models

内部表現を作成する（出力に生のアーティファクトを含めないこと）:

- **要件インベントリ**: 各機能要件（FR-###）および成功基準（SC-###）について、安定したキーを記録する。存在する場合は明示的な FR-/SC- 識別子を主キーとして使用し、任意で読みやすさのために命令形フレーズのスラッグも導出する（例: "User can upload file" → `user-can-upload-file`）。構築が必要な作業を要する成功基準の項目（例: 負荷テスト基盤、セキュリティ監査ツール）のみを含め、ローンチ後の成果指標やビジネス KPI（例: "サポートチケットを50%削減する"）は除外する。
- **ユーザーストーリー／アクションインベントリ**: 受け入れ基準を伴う個別のユーザーアクション
- **タスクカバレッジマッピング**: 各タスクを1つ以上の要件またはストーリーにマッピングする（ID や特定のキーフレーズといった明示的な参照パターン／キーワードによる推論）
- **憲法ルールセット**: 原則名と MUST/SHOULD の規範的記述を抽出する

### 4. Detection Passes (Token-Efficient Analysis)

シグナル強度の高い所見に焦点を当てる。所見は合計50件までとし、残りはオーバーフローサマリーに集約する。

#### A. Duplication Detection

- ほぼ重複している要件を特定する
- 統合のために品質の低い言い回しをマークする

#### B. Ambiguity Detection

- 測定可能な基準を欠く曖昧な形容詞（fast, scalable, secure, intuitive, robust）にフラグを立てる
- 未解決のプレースホルダー（TODO、TKTK、???、`<placeholder>` など）にフラグを立てる

#### C. Underspecification

- 動詞はあるが目的語や測定可能な成果が欠けている要件
- 受け入れ基準との整合が取れていないユーザーストーリー
- spec/plan で定義されていないファイルやコンポーネントを参照しているタスク

#### D. Constitution Alignment

- MUST 原則と矛盾する要件または plan の要素
- 憲法から義務付けられているセクションや品質ゲートの欠落

#### E. Coverage Gaps

- 関連するタスクがゼロの要件
- マッピングされた要件／ストーリーがないタスク
- 構築が必要な作業を要する成功基準（パフォーマンス、セキュリティ、可用性）でタスクに反映されていないもの

#### F. Inconsistency

- 用語のドリフト（同一概念がファイルごとに異なる名前で呼ばれている）
- plan には記載があるが spec には存在しないデータエンティティ（またはその逆）
- 依存関係の注記なしのタスク順序の矛盾（例: 基盤となるセットアップタスクより前に統合タスクがある）
- 矛盾する要件（例: 一方は Next.js を要求し、他方は Vue を指定している）

### 5. Severity Assignment

所見の優先順位付けには以下のヒューリスティクスを用いる:

- **CRITICAL**: 憲法の MUST に違反する、コアとなる spec アーティファクトが欠落している、または基本機能を妨げるカバレッジがゼロの要件
- **HIGH**: 重複または矛盾する要件、曖昧なセキュリティ／パフォーマンス属性、テスト不可能な受け入れ基準
- **MEDIUM**: 用語のドリフト、非機能タスクのカバレッジ欠落、仕様不足のエッジケース
- **LOW**: 文体・言い回しの改善、実行順序に影響しない軽微な冗長性

### 6. Produce Compact Analysis Report

以下の構造の Markdown レポートを出力する（ファイルへの書き込みは行わない）:

## Specification Analysis Report

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
| A1 | Duplication | HIGH | spec.md:L120-134 | Two similar requirements ... | Merge phrasing; keep clearer version |

（所見1件につき1行を追加する。カテゴリの頭文字を接頭辞とする安定した ID を生成する。）

**カバレッジサマリー表:**

| Requirement Key | Has Task? | Task IDs | Notes |
|-----------------|-----------|----------|-------|

**憲法整合性の問題:**（存在する場合）

**マッピングされていないタスク:**（存在する場合）

**メトリクス:**

- 要件の総数
- タスクの総数
- カバレッジ%（1件以上のタスクを持つ要件）
- 曖昧さの件数
- 重複の件数
- クリティカルな問題の件数

### 7. Provide Next Actions

レポートの末尾に、簡潔な Next Actions ブロックを出力する:

- CRITICAL な問題が存在する場合: `/speckit-implement` の前に解決することを推奨する
- LOW/MEDIUM のみの場合: ユーザーは先に進んでよいが、改善提案を提示する
- 具体的なコマンドの提案を提供する: 例えば "Run /speckit-specify with refinement"、"Run /speckit-plan to adjust architecture"、"Manually edit tasks.md to add coverage for 'performance-metrics'"

### 8. Offer Remediation

ユーザーに尋ねる: "Would you like me to suggest concrete remediation edits for the top N issues?"（自動的には適用しないこと。）

### 9. Check for extension hooks

レポート出力後、プロジェクトルートに `.specify/extensions.yml` が存在するか確認する。
- 存在する場合は読み込み、`hooks.after_analyze` キー配下のエントリを探す
- YAML がパースできない、または不正な場合は、フックの確認を黙ってスキップし通常どおり続行する
- `enabled` が明示的に `false` であるフックは除外する。`enabled` フィールドがないフックはデフォルトで有効とみなす。
- 残った各フックについて、フックの `condition` 式を解釈・評価しようとしては**ならない**:
  - フックに `condition` フィールドがない、または null/空の場合、そのフックは実行可能とみなす
  - フックが空でない `condition` を定義している場合、そのフックはスキップし、条件評価は HookExecutor の実装に任せる
- フックのコマンド名からコマンド呼び出しを構築する際は、ドット（`.`）をハイフン（`-`）に置き換える。例えば `speckit.git.commit` → `/speckit-git-commit`。
- 実行可能な各フックについて、`optional` フラグに応じて以下を出力する:
  - **オプションフック**（`optional: true`）:
    ```
    ## Extension Hooks

    **Optional Hook**: {extension}
    Command: `/{command}`
    Description: {description}

    Prompt: {prompt}
    To execute: `/{command}`
    ```
  - **必須フック**（`optional: false`）:
    ```
    ## Extension Hooks

    **Automatic Hook**: {extension}
    Executing: `/{command}`
    EXECUTE_COMMAND: {command}
    ```
    上記ブロックを出力した後、実際にフックを呼び出し、完了を待ってから続行しなければ**なりません**。このエージェント／セッションで自分自身がコマンドを実行するのと同じ方法で実行してください（呼び出し方法は上記の文字どおりの `{command}` id とは異なる場合があります。例えばスキルモードのエージェントでは `/skill:speckit-...` や `$speckit-...` として実行します）。ブロックを出力するだけではフックは実行されません。
- フックが1つも登録されていない、または `.specify/extensions.yml` が存在しない場合は、黙ってスキップする

## Operating Principles

### Context Efficiency

- **最小限のシグナル強度の高いトークン**: 網羅的なドキュメント化ではなく、実行可能な所見に焦点を当てる
- **段階的開示（Progressive disclosure）**: アーティファクトを段階的に読み込む。すべての内容を分析に一度に投入しない
- **トークン効率の良い出力**: 所見テーブルは50行までに制限し、超過分は要約する
- **決定論的な結果**: 変更なしで再実行した場合、一貫した ID と件数が得られるべきである

### Analysis Guidelines

- **ファイルを絶対に変更しない**（これは読み取り専用の分析である）
- **欠落しているセクションを絶対にでっち上げない**（存在しない場合は、その旨を正確に報告する）
- **憲法違反を最優先する**（これらは常に CRITICAL である）
- **網羅的なルールよりも具体例を使う**（一般的なパターンではなく、具体的な事例を引用する）
- **問題がゼロの場合も適切に報告する**（カバレッジ統計とともに成功レポートを出す）

## Context

$ARGUMENTS
