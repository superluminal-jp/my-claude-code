---
name: "speckit-taskstoissues"
description: "利用可能な設計成果物に基づき、既存のタスクをフィーチャー用の実行可能かつ依存関係順に並んだGitHub issueへ変換する。"
argument-hint: "Optional filter or label for GitHub issues"
compatibility: "Requires spec-kit project structure with .specify/ directory"
metadata:
  author: "github-spec-kit"
  source: "templates/commands/taskstoissues.md"
user-invocable: true
disable-model-invocation: false
---


## User Input

```text
$ARGUMENTS
```

進める前に、ユーザー入力が空でなければそれを必ず考慮しなければなりません。

## Pre-Execution Checks

**拡張フックの確認（tasks-to-issues変換の前）**:
- プロジェクトルートに `.specify/extensions.yml` が存在するか確認する。
- 存在する場合は、それを読み込み、`hooks.before_taskstoissues` キー配下のエントリを探す。
- YAMLが解析できない、または不正な場合は、フックの確認を静かにスキップし、通常どおり続行する。
- `enabled` が明示的に `false` になっているフックは除外する。`enabled` フィールドがないフックはデフォルトで有効として扱う。
- 残った各フックについて、フックの `condition` 式を解釈・評価しようとしては**ならない**:
  - フックに `condition` フィールドがない、またはnull/空の場合、そのフックは実行可能として扱う。
  - フックが空でない `condition` を定義している場合は、そのフックをスキップし、条件評価はHookExecutorの実装に委ねる。
- フックのコマンド名からコマンド呼び出しを組み立てる際は、ドット（`.`）をハイフン（`-`）に置き換える。例えば、`speckit.git.commit` → `/speckit-git-commit`。
- 実行可能な各フックについて、その `optional` フラグに応じて次を出力する:
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
    上記のブロックを出力した後、実際にそのフックを呼び出し、続行する前に完了を待たなければなりません。このエージェント／セッションで自分自身がコマンドを実行するのと同じ方法で実行してください（実際の呼び出しは、上記に示したリテラルな `{command}` idとは異なる場合があります。例えば、skillsモードのエージェントでは `/skill:speckit-...` や `$speckit-...` として実行されます）。ブロックを出力するだけではフックは実行されません。
- フックが登録されていない場合、または `.specify/extensions.yml` が存在しない場合は、静かにスキップする。

## Outline

1. リポジトリルートから `.specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks` を実行し、FEATURE_DIRとAVAILABLE_DOCSのリストを解析する。すべてのパスは絶対パスでなければならない。"I'm Groot" のような引数中のシングルクォートについては、エスケープ構文を使用する: 例 'I'\''m Groot'（または可能なら二重引用符を使う: "I'm Groot"）。
1. **存在する場合**: `.specify/memory/constitution.md` を読み込み、プロジェクトの原則とガバナンス上の制約を把握する。
1. 実行したスクリプトの出力から、**tasks**へのパスを抽出する。
1. 次を実行してGitリモートを取得する:

```bash
git config --get remote.origin.url
```

> [!CAUTION]
> リモートがGitHubのURLである場合にのみ、次のステップに進んでください。

1. **重複排除のため既存issueを取得する**: 何かを作成する前に、`tasks.md` から処理対象となるタスクID（それぞれ `T` に3桁の数字が続く形式、例: `T001`）の集合を組み立てる。次に、GitHub MCPサーバーの `list_issues` ツールを使って、これらのIDを既にカバーしているissueを探す。`state` の値は渡さないこと。これを省略すると、ツールはオープンとクローズの両方のissueを返す。呼び出し回数を抑えるために `perPage: 100` を指定し、このツールはカーソルベースのページネーションを使うため、`after` パラメータ（直前のレスポンスの `endCursor` を使用）でページを要求する。各issueのタイトルについて、タスクIDのパターン `\bT\d{3}\b`（単語境界を使うことで、`ST001` や `T0010` のようなトークンが誤ってマッチしないようにする。これは `T001 ...`、`T001: ...`、`[T001] ...` のように書かれたタイトルも認識する）と照合し、対象タスクIDのいずれかに一致した場合、そのIDには既にissueがあるとマークする。すべてのタスクIDが照合済みになった時点、あるいはそれ以上ページがなくなった時点で、ページネーションを止める。これにより、すべてのタスクIDの対応関係が判明した後にリポジトリのissue履歴全体を取得し続けることを避ける。この方法は、issue履歴が大きいリポジトリでの呼び出し回数を抑えつつ、`tasks.md` が再生成された後やスキルが再度呼び出された後にコマンドを再実行した場合の重複作成も防ぐ。
1. リスト内の各タスクについて、GitHub MCPサーバーを使い、Gitリモートに対応するリポジトリに新しいissueを作成する。`tasks.md` 内のタスク行はMarkdownのチェックボックスから始まるため、まず先頭の `- [ ]`（および `[P]` / `[US#]` マーカー）を取り除き、タスクIDとその説明を復元する。issueは `T001: <description>` という単一の正規化されたタイトル形式で作成し、IDを一度だけ記載してからタスクの説明を続ける（例えば、行 `- [ ] T001 Create project structure` はタイトル `T001: Create project structure` になる）。
   - 前のステップで取得した既存issueの集合に既にIDが存在するタスクは**スキップ**し、それを報告する（例: `T001 already has an issue, skipping`）。
   - 一致するissueがまだ存在しないタスクについてのみissueを作成する。

> [!CAUTION]
> いかなる状況においても、リモートURLと一致しないリポジトリにissueを作成してはなりません。

## Post-Execution Checks

**拡張フックの確認（tasks-to-issues変換の後）**:
プロジェクトルートに `.specify/extensions.yml` が存在するか確認する。
- 存在する場合は、それを読み込み、`hooks.after_taskstoissues` キー配下のエントリを探す。
- YAMLが解析できない、または不正な場合は、フックの確認を静かにスキップし、通常どおり続行する。
- `enabled` が明示的に `false` になっているフックは除外する。`enabled` フィールドがないフックはデフォルトで有効として扱う。
- 残った各フックについて、フックの `condition` 式を解釈・評価しようとしては**ならない**:
  - フックに `condition` フィールドがない、またはnull/空の場合、そのフックは実行可能として扱う。
  - フックが空でない `condition` を定義している場合は、そのフックをスキップし、条件評価はHookExecutorの実装に委ねる。
- フックのコマンド名からコマンド呼び出しを組み立てる際は、ドット（`.`）をハイフン（`-`）に置き換える。例えば、`speckit.git.commit` → `/speckit-git-commit`。
- 実行可能な各フックについて、その `optional` フラグに応じて次を出力する:
  - **オプションのフック**（`optional: true`）:
    ```
    ## Extension Hooks

    **Optional Hook**: {extension}
    Command: `/{command}`
    Description: {description}

    Prompt: {prompt}
    To execute: `/{command}`
    ```
  - **必須のフック**（`optional: false`）:
    ```
    ## Extension Hooks

    **Automatic Hook**: {extension}
    Executing: `/{command}`
    EXECUTE_COMMAND: {command}
    ```
    上記のブロックを出力した後、実際にそのフックを呼び出し、続行する前に完了を待たなければなりません。このエージェント／セッションで自分自身がコマンドを実行するのと同じ方法で実行してください（実際の呼び出しは、上記に示したリテラルな `{command}` idとは異なる場合があります。例えば、skillsモードのエージェントでは `/skill:speckit-...` や `$speckit-...` として実行されます）。ブロックを出力するだけではフックは実行されません。
- フックが登録されていない場合、または `.specify/extensions.yml` が存在しない場合は、静かにスキップする。
