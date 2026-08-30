---
name: "speckit-plan"
description: "計画テンプレートを使って実装計画のワークフローを実行し、設計成果物を生成する。"
argument-hint: "Optional guidance for the planning phase"
compatibility: "Requires spec-kit project structure with .specify/ directory"
metadata:
  author: "github-spec-kit"
  source: "templates/commands/plan.md"
user-invocable: true
disable-model-invocation: false
---


## ユーザー入力

```text
$ARGUMENTS
```

処理を進める前に、ユーザー入力を**必ず**考慮すること（空でない場合）。

## 実行前チェック

**拡張フックの確認（計画立案前）**:
- プロジェクトルートに `.specify/extensions.yml` が存在するか確認する。
- 存在する場合は読み込み、`hooks.before_plan` キー配下のエントリを探す
- YAMLが解析できない、または不正な場合は、フックの確認を黙って省略し通常どおり続行する
- `enabled` が明示的に `false` になっているフックは除外する。`enabled` フィールドがないフックはデフォルトで有効として扱う。
- 残った各フックについて、フックの `condition` 式を解釈・評価しようとしては**いけない**:
  - フックに `condition` フィールドがない、またはnull/空の場合は、そのフックを実行可能として扱う
  - フックに空でない `condition` が定義されている場合は、そのフックをスキップし、条件評価はHookExecutorの実装に委ねる
- フックのコマンド名からコマンド呼び出しを組み立てる際は、ドット（`.`）をハイフン（`-`）に置き換える。例: `speckit.git.commit` → `/speckit-git-commit`。
- 実行可能な各フックについて、その `optional` フラグに応じて以下を出力する:
  - **オプションのフック**（`optional: true`）:
    ```
    ## Extension Hooks

    **Optional Pre-Hook**: {extension}
    Command: `/{command}`
    Description: {description}

    Prompt: {prompt}
    To execute: `/{command}`
    ```
  - **必須のフック**（`optional: false`）:
    ```
    ## Extension Hooks

    **Automatic Pre-Hook**: {extension}
    Executing: `/{command}`
    EXECUTE_COMMAND: {command}

    Wait for the result of the hook command before proceeding to the Outline.
    ```
    上記のブロックを出力した後、実際にそのフックを呼び出し、続行する前に完了を待たなければ**ならない**。このエージェント／セッションで自分自身がそのコマンドを実行するのと同じ方法で実行すること（呼び出し方は上記の文字どおりの `{command}` IDとは異なる場合がある。例えば、skillsモードのエージェントでは `/skill:speckit-...` や `$speckit-...` として実行される）。ブロックを出力するだけではフックは実行されない。
- 登録されているフックがない場合、または `.specify/extensions.yml` が存在しない場合は、黙ってスキップする

## アウトライン

1. **セットアップ**: リポジトリのルートから `.specify/scripts/bash/setup-plan.sh --json` を実行し、JSONを解析してFEATURE_SPEC、IMPL_PLAN、SPECS_DIR、BRANCHを取得する。"I'm Groot" のような引数中のシングルクォートには、エスケープ構文を使用すること。例: 'I'\''m Groot'（可能であればダブルクォートで囲む: "I'm Groot"）。

2. **コンテキストの読み込み**: FEATURE_SPECと `.specify/memory/constitution.md` を読み込む。IMPL_PLANテンプレート（すでにコピー済み）を読み込む。

3. **計画ワークフローの実行**: IMPL_PLANテンプレートの構造に従って以下を行う:
   - Technical Contextを埋める（不明な点は「NEEDS CLARIFICATION」とマークする）
   - constitutionからConstitution Checkセクションを埋める
   - ゲートを評価する（正当化されない違反がある場合はERROR）
   - フェーズ0: research.md を生成する（すべてのNEEDS CLARIFICATIONを解消する）
   - フェーズ1: data-model.md、contracts/、quickstart.md を生成する
   - 設計後にConstitution Checkを再評価する

## 実行後の必須フック

**このセクションは、ユーザーに完了を報告する前に必ず完了させること。**

プロジェクトルートに `.specify/extensions.yml` が存在するか確認する。
- 存在しない場合、または `hooks.after_plan` 配下に登録されたフックがない場合は、Completion Reportへ進む。
- 存在する場合は読み込み、`hooks.after_plan` キー配下のエントリを探す。
- YAMLが解析できない、または不正な場合は、フックの確認を黙って省略しCompletion Reportへ進む。
- `enabled` が明示的に `false` になっているフックは除外する。`enabled` フィールドがないフックはデフォルトで有効として扱う。
- 残った各フックについて、フックの `condition` 式を解釈・評価しようとしては**いけない**:
  - フックに `condition` フィールドがない、またはnull/空の場合は、そのフックを実行可能として扱う
  - フックに空でない `condition` が定義されている場合は、そのフックをスキップし、条件評価はHookExecutorの実装に委ねる
- フックのコマンド名からコマンド呼び出しを組み立てる際は、ドット（`.`）をハイフン（`-`）に置き換える。例: `speckit.git.commit` → `/speckit-git-commit`。
- 実行可能な各フックについて、その `optional` フラグに応じて以下を出力する:
  - **必須のフック**（`optional: false`）— 各必須フックについて**必ず** `EXECUTE_COMMAND:` を出力すること:
    ```
    ## Extension Hooks

    **Automatic Hook**: {extension}
    Executing: `/{command}`
    EXECUTE_COMMAND: {command}
    ```
    上記のブロックを出力した後、実際にそのフックを呼び出し、続行する前に完了を待たなければ**ならない**。このエージェント／セッションで自分自身がそのコマンドを実行するのと同じ方法で実行すること（呼び出し方は上記の文字どおりの `{command}` IDとは異なる場合がある。例えば、skillsモードのエージェントでは `/skill:speckit-...` や `$speckit-...` として実行される）。ブロックを出力するだけではフックは実行されない。
  - **オプションのフック**（`optional: true`）:
    ```
    ## Extension Hooks

    **Optional Hook**: {extension}
    Command: `/{command}`
    Description: {description}

    Prompt: {prompt}
    To execute: `/{command}`
    ```

## Completion Report

コマンドはフェーズ1の設計が終わった時点で終了する。ブランチ、IMPL_PLANのパス、生成された成果物を報告する。

## フェーズ

### フェーズ0: アウトラインとリサーチ

1. 上記の**Technical Contextから不明点を抽出する**:
   - NEEDS CLARIFICATIONごとに → リサーチタスク
   - 依存関係ごとに → ベストプラクティスのタスク
   - 統合ごとに → パターンのタスク

2. **リサーチエージェントを生成し、割り当てる**:

   ```text
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. 以下の形式で `research.md` に**調査結果をまとめる**:
   - Decision: [何を選んだか]
   - Rationale: [なぜそれを選んだか]
   - Alternatives considered: [他に何を検討したか]

**出力**: すべてのNEEDS CLARIFICATIONが解消された research.md

### フェーズ1: 設計と契約

**前提条件:** `research.md` が完成していること

1. **機能仕様からエンティティを抽出**し `data-model.md` を作成する:
   - エンティティ名、フィールド、関連
   - 要件から導かれるバリデーションルール
   - 該当する場合は状態遷移

2. **インターフェース契約を定義する**（プロジェクトに外部インターフェースがある場合）→ `/contracts/`:
   - プロジェクトがユーザーや他のシステムに公開するインターフェースを特定する
   - プロジェクトの種類に適した契約フォーマットを文書化する
   - 例: ライブラリの場合は公開API、CLIツールの場合はコマンドスキーマ、Webサービスの場合はエンドポイント、パーサーの場合は文法、アプリケーションの場合はUI契約
   - プロジェクトが純粋に内部向け（ビルドスクリプト、使い捨てツールなど）の場合はスキップする

3. **クイックスタート検証ガイドを作成する** → `quickstart.md`:
   - その機能がエンドツーエンドで動作することを証明する、実行可能な検証シナリオを文書化する
   - 前提条件、セットアップコマンド、テスト／実行コマンド、期待される結果を含める
   - 契約やデータモデルの詳細を重複させるのではなく、リンクや参照を使う
   - 完全な実装コード、モデル／サービス／コントローラの本体、マイグレーション、完全なテストスイートは含めない
   - この成果物はあくまで検証／実行ガイドとして保つこと。実装の詳細は `tasks.md` および実装フェーズに属する

**出力**: data-model.md、/contracts/*、quickstart.md

## 主要ルール

- ファイルシステム操作には絶対パスを使用し、ドキュメント内の参照にはプロジェクト相対パスを使用する
- ゲートの失敗や未解消のclarificationがある場合はERRORとする

## 完了条件

- [ ] 計画ワークフローが実行され、設計成果物が生成されている
- [ ] 上記「実行後の必須フック」のルールに従って拡張フックが実行またはスキップされている
- [ ] ブランチ、計画のパス、生成された成果物とともに、ユーザーへ完了が報告されている
