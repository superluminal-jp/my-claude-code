---
name: "speckit-implement"
description: "tasks.md に定義されたすべてのタスクを処理・実行することで、実装計画を実行する"
argument-hint: "Optional implementation guidance or task filter"
compatibility: "Requires spec-kit project structure with .specify/ directory"
metadata:
  author: "github-spec-kit"
  source: "templates/commands/implement.md"
user-invocable: true
disable-model-invocation: false
---


## User Input

```text
$ARGUMENTS
```

処理を進める前に、ユーザー入力を（空でない場合は）必ず考慮しなければなりません。

## 事前実行チェック

**拡張フックの確認（実装前）**:
- プロジェクトルートに `.specify/extensions.yml` が存在するか確認する。
- 存在する場合は、それを読み込み、`hooks.before_implement` キー配下のエントリを探す。
- YAML がパースできない、または不正な場合は、フックのチェックを黙ってスキップし、通常どおり続行する。
- `enabled` が明示的に `false` であるフックは除外する。`enabled` フィールドがないフックはデフォルトで有効として扱う。
- 残った各フックについて、フックの `condition` 式を解釈・評価しようとしては**ならない**：
  - フックに `condition` フィールドがない、または null／空である場合は、そのフックを実行可能として扱う
  - フックが空でない `condition` を定義している場合は、そのフックをスキップし、条件評価は HookExecutor の実装に委ねる
- フックのコマンド名からコマンド呼び出しを構築する際は、ドット（`.`）をハイフン（`-`）に置き換える。例えば `speckit.git.commit` → `/speckit-git-commit`。
- 実行可能な各フックについて、`optional` フラグに応じて以下を出力する：
  - **オプションフック**（`optional: true`）：
    ```
    ## Extension Hooks

    **Optional Pre-Hook**: {extension}
    Command: `/{command}`
    Description: {description}

    Prompt: {prompt}
    To execute: `/{command}`
    ```
  - **必須フック**（`optional: false`）：
    ```
    ## Extension Hooks

    **Automatic Pre-Hook**: {extension}
    Executing: `/{command}`
    EXECUTE_COMMAND: {command}

    Wait for the result of the hook command before proceeding to the Outline.
    ```
    上記のブロックを出力した後、実際にそのフックを呼び出し、続行する前に完了を待たなければなりません。このエージェント／セッションで自分自身がコマンドを実行するのと同じ方法で実行してください（呼び出し方は上記に示した文字どおりの `{command}` の ID とは異なる場合があります。例えばスキルモードのエージェントでは `/skill:speckit-...` や `$speckit-...` として実行されます）。ブロックを出力するだけではフックは実行されません。
- フックが一つも登録されていない、または `.specify/extensions.yml` が存在しない場合は、黙ってスキップする。

## 概要（Outline）

1. リポジトリのルートから `.specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks` を実行し、FEATURE_DIR と AVAILABLE_DOCS のリストをパースする。すべてのパスは絶対パスでなければならない。"I'm Groot" のような引数中のシングルクォートには、エスケープ構文を使用すること：例 'I'\''m Groot'（可能なら二重引用符でも良い："I'm Groot"）。

2. **チェックリストの状態を確認する**（FEATURE_DIR/checklists/ が存在する場合）：
   - checklists/ ディレクトリ内のすべてのチェックリストファイルをスキャンする
   - 各チェックリストについて、以下をカウントする：
     - 総項目数：`- [ ]` または `- [X]` または `- [x]` にマッチするすべての行
     - 完了項目数：`- [X]` または `- [x]` にマッチする行
     - 未完了項目数：`- [ ]` にマッチする行
   - ステータス表を作成する：

     ```text
     | Checklist | Total | Completed | Incomplete | Status |
     |-----------|-------|-----------|------------|--------|
     | ux.md     | 12    | 12        | 0          | ✓ PASS |
     | test.md   | 8     | 5         | 3          | ✗ FAIL |
     | security.md | 6   | 6         | 0          | ✓ PASS |
     ```

   - 全体のステータスを算出する：
     - **PASS**：すべてのチェックリストで未完了項目が 0 件
     - **FAIL**：1 つ以上のチェックリストに未完了項目がある

   - **いずれかのチェックリストが未完了の場合**：
     - 未完了項目数とともに表を表示する
     - **停止**し、「一部のチェックリストが未完了です。それでも実装を進めますか？（yes/no）」と尋ねる
     - 続行する前にユーザーの返答を待つ
     - ユーザーが「no」「wait」「stop」と答えた場合は実行を中止する
     - ユーザーが「yes」「proceed」「continue」と答えた場合はステップ 3 に進む

   - **すべてのチェックリストが完了している場合**：
     - すべてのチェックリストが合格したことを示す表を表示する
     - 自動的にステップ 3 に進む

3. 実装コンテキストを読み込み、分析する：
   - **必須**：完全なタスクリストと実行計画のために tasks.md を読む
   - **必須**：技術スタック、アーキテクチャ、ファイル構成のために plan.md を読む
   - **存在する場合**：エンティティと関係性のために data-model.md を読む
   - **存在する場合**：API 仕様とテスト要件のために contracts/ を読む
   - **存在する場合**：技術的な決定事項と制約のために research.md を読む
   - **存在する場合**：ガバナンス上の制約のために .specify/memory/constitution.md を読む
   - **存在する場合**：統合シナリオのために quickstart.md を読む

4. **プロジェクトセットアップの検証**：
   - **必須**：実際のプロジェクト構成に基づいて ignore ファイルを作成・検証する：

   **検出と作成のロジック**：
   - 以下のコマンドが成功するかどうかでリポジトリが git リポジトリかどうかを判定する（成功すれば .gitignore を作成・検証する）：

     ```sh
     git rev-parse --git-dir 2>/dev/null
     ```

   - Dockerfile* が存在する、または plan.md に Docker の記載がある → .dockerignore を作成・検証する
   - .eslintrc* が存在する → .eslintignore を作成・検証する
   - eslint.config.* が存在する → 設定の `ignores` エントリが必要なパターンをカバーしていることを確認する
   - .prettierrc* が存在する → .prettierignore を作成・検証する
   - .npmrc または package.json が存在する → （公開する場合）.npmignore を作成・検証する
   - terraform ファイル（*.tf）が存在する → .terraformignore を作成・検証する
   - .helmignore が必要（helm チャートが存在する）→ .helmignore を作成・検証する

   **ignore ファイルが既に存在する場合**：必須パターンが含まれているか検証し、不足している重要なパターンのみを追記する
   **ignore ファイルが存在しない場合**：検出した技術に対応する完全なパターンセットで新規作成する

   **技術ごとの共通パターン**（plan.md の技術スタックから）：
   - **Node.js/JavaScript/TypeScript**: `node_modules/`, `dist/`, `build/`, `*.log`, `.env*`
   - **Python**: `__pycache__/`, `*.pyc`, `.venv/`, `venv/`, `dist/`, `*.egg-info/`
   - **Java**: `target/`, `*.class`, `*.jar`, `.gradle/`, `build/`
   - **C#/.NET**: `bin/`, `obj/`, `*.user`, `*.suo`, `packages/`
   - **Go**: `*.exe`, `*.test`, `vendor/`, `*.out`
   - **Ruby**: `.bundle/`, `log/`, `tmp/`, `*.gem`, `vendor/bundle/`
   - **PHP**: `vendor/`, `*.log`, `*.cache`, `*.env`
   - **Rust**: `target/`, `debug/`, `release/`, `*.rs.bk`, `*.rlib`, `*.prof*`, `.idea/`, `*.log`, `.env*`
   - **Kotlin**: `build/`, `out/`, `.gradle/`, `.idea/`, `*.class`, `*.jar`, `*.iml`, `*.log`, `.env*`
   - **C++**: `build/`, `bin/`, `obj/`, `out/`, `*.o`, `*.so`, `*.a`, `*.exe`, `*.dll`, `.idea/`, `*.log`, `.env*`
   - **C**: `build/`, `bin/`, `obj/`, `out/`, `*.o`, `*.a`, `*.so`, `*.exe`, `*.dll`, `autom4te.cache/`, `config.status`, `config.log`, `.idea/`, `*.log`, `.env*`
   - **Swift**: `.build/`, `DerivedData/`, `*.swiftpm/`, `Packages/`
   - **R**: `.Rproj.user/`, `.Rhistory`, `.RData`, `.Ruserdata`, `*.Rproj`, `packrat/`, `renv/`
   - **共通**: `.DS_Store`, `Thumbs.db`, `*.tmp`, `*.swp`, `.vscode/`, `.idea/`

   **ツール固有のパターン**：
   - **Docker**: `node_modules/`, `.git/`, `Dockerfile*`, `.dockerignore`, `*.log*`, `.env*`, `coverage/`
   - **ESLint**: `node_modules/`, `dist/`, `build/`, `coverage/`, `*.min.js`
   - **Prettier**: `node_modules/`, `dist/`, `build/`, `coverage/`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`
   - **Terraform**: `.terraform/`, `*.tfstate*`, `*.tfvars`, `.terraform.lock.hcl`
   - **Kubernetes/k8s**: `*.secret.yaml`, `secrets/`, `.kube/`, `kubeconfig*`, `*.key`, `*.crt`

5. tasks.md の構造をパースし、以下を抽出する：
   - **タスクフェーズ**：Setup、Tests、Core、Integration、Polish
   - **タスクの依存関係**：順次実行 vs 並列実行のルール
   - **タスクの詳細**：ID、説明、ファイルパス、並列マーカー [P]
   - **実行フロー**：順序と依存関係の要件

6. タスク計画に従って実装を実行する：
   - **フェーズごとの実行**：各フェーズを完了させてから次に進む
   - **依存関係の尊重**：順次タスクは順番どおりに実行し、並列タスク [P] は同時に実行できる
   - **TDD アプローチに従う**：対応する実装タスクの前にテストタスクを実行する
   - **ファイル単位での調整**：同じファイルに影響するタスクは順次実行しなければならない
   - **検証チェックポイント**：次に進む前に各フェーズの完了を確認する

7. 実装実行のルール：
   - **セットアップを最初に**：プロジェクト構造、依存関係、設定を初期化する
   - **コードの前にテスト**：契約、エンティティ、統合シナリオのテストが必要な場合は記述する
   - **コア開発**：モデル、サービス、CLI コマンド、エンドポイントを実装する
   - **統合作業**：データベース接続、ミドルウェア、ロギング、外部サービス
   - **仕上げと検証**：単体テスト、パフォーマンス最適化、ドキュメント作成

8. 進捗管理とエラー処理：
   - 各タスク完了後に進捗を報告する
   - 非並列タスクが失敗した場合は実行を停止する
   - 並列タスク [P] については、成功したタスクは続行し、失敗したものを報告する
   - デバッグ用にコンテキストを含む明確なエラーメッセージを提供する
   - 実装を進められない場合は次のステップを提案する
   - **重要**：完了したタスクについては、tasks ファイル内でそのタスクを必ず [X] としてマークすること。

9. 完了の検証：
   - 必要なすべてのタスクが完了していることを確認する
   - 実装された機能が元の仕様と一致していることを確認する
   - テストが通り、カバレッジが要件を満たしていることを検証する
   - 実装が技術計画に従っていることを確認する

注：このコマンドは、tasks.md に完全なタスク分解が存在することを前提とする。タスクが不完全または欠落している場合は、まず `/speckit-tasks` を実行してタスクリストを再生成するよう提案すること。

## 必須の事後実行フック

**ユーザーに完了を報告する前に、このセクションを必ず完了させなければなりません。**

プロジェクトルートに `.specify/extensions.yml` が存在するか確認する。
- 存在しない場合、または `hooks.after_implement` 配下にフックが登録されていない場合は、完了報告（Completion Report）にスキップする。
- 存在する場合は、それを読み込み、`hooks.after_implement` キー配下のエントリを探す。
- YAML がパースできない、または不正な場合は、フックのチェックを黙ってスキップし、完了報告に進む。
- `enabled` が明示的に `false` であるフックは除外する。`enabled` フィールドがないフックはデフォルトで有効として扱う。
- 残った各フックについて、フックの `condition` 式を解釈・評価しようとしては**ならない**：
  - フックに `condition` フィールドがない、または null／空である場合は、そのフックを実行可能として扱う
  - フックが空でない `condition` を定義している場合は、そのフックをスキップし、条件評価は HookExecutor の実装に委ねる
- フックのコマンド名からコマンド呼び出しを構築する際は、ドット（`.`）をハイフン（`-`）に置き換える。例えば `speckit.git.commit` → `/speckit-git-commit`。
- 実行可能な各フックについて、`optional` フラグに応じて以下を出力する：
  - **必須フック**（`optional: false`）— **必須フックごとに `EXECUTE_COMMAND:` を必ず出力しなければならない**：
    ```
    ## Extension Hooks

    **Automatic Hook**: {extension}
    Executing: `/{command}`
    EXECUTE_COMMAND: {command}
    ```
    上記のブロックを出力した後、実際にそのフックを呼び出し、続行する前に完了を待たなければなりません。このエージェント／セッションで自分自身がコマンドを実行するのと同じ方法で実行してください（呼び出し方は上記に示した文字どおりの `{command}` の ID とは異なる場合があります。例えばスキルモードのエージェントでは `/skill:speckit-...` や `$speckit-...` として実行されます）。ブロックを出力するだけではフックは実行されません。
  - **オプションフック**（`optional: true`）：
    ```
    ## Extension Hooks

    **Optional Hook**: {extension}
    Command: `/{command}`
    Description: {description}

    Prompt: {prompt}
    To execute: `/{command}`
    ```

## 完了報告（Completion Report）

完了した作業の概要とともに最終ステータスを報告する。

## 完了の定義（Done When）

- [ ] tasks.md 内のすべてのタスクが完了し、`[X]` としてマークされている
- [ ] 実装が仕様、計画、テストカバレッジに照らして検証されている
- [ ] 上記「必須の事後実行フック」のルールに従って拡張フックがディスパッチまたはスキップされている
- [ ] 完了した作業の概要とともにユーザーに完了が報告されている
