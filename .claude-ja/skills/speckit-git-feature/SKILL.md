---
name: speckit-git-feature
description: "連番またはタイムスタンプによる採番でフィーチャーブランチを作成する"
compatibility: Requires spec-kit project structure with .specify/ directory
metadata:
  author: github-spec-kit
  source: git:commands/speckit.git.feature.md
---

# フィーチャーブランチの作成

指定された仕様のために新しい git フィーチャーブランチを作成し、そのブランチに切り替える。このコマンドが扱うのは**ブランチ作成のみ**であり、spec ディレクトリとそのファイルはコアの `/speckit-specify` ワークフローによって作成される。

## ユーザー入力

```text
$ARGUMENTS
```

処理を進める前に、ユーザー入力を**必ず**考慮すること（空でない場合）。

## 環境変数によるオーバーライド

ユーザーが（環境変数、引数、またはリクエスト内で）明示的に `GIT_BRANCH_NAME` を指定した場合は、スクリプトを呼び出す前に `GIT_BRANCH_NAME` 環境変数を設定し、その値をスクリプトに渡すこと。`GIT_BRANCH_NAME` が設定されている場合:
- スクリプトはプレフィックス/サフィックスの生成をすべて行わず、指定された値をそのままブランチ名として使用する
- `--short-name`、`--number`、`--timestamp` の各フラグは無視される
- 最終パスセグメントが数値またはタイムスタンプ形式のフィーチャーマーカーで始まる場合（例: `042-name`、`feat/042-name`、`jdoe/app/042-name`）、そこから `FEATURE_NUM` が抽出される。それ以外の場合はブランチ名全体が `FEATURE_NUM` に設定される

## 前提条件

- `git rev-parse --is-inside-work-tree 2>/dev/null` を実行して Git が利用可能であることを確認する
- Git が利用できない場合は、ユーザーに警告してブランチ作成をスキップする

## ブランチ採番モード

以下の順序で設定を確認し、ブランチの採番方式を決定する:

1. `.specify/extensions/git/git-config.yml` の `branch_numbering` の値を確認する
2. `.specify/init-options.json` の `feature_numbering` の値を確認する（コアから継承）
3. `.specify/init-options.json` の `branch_numbering` の値を確認する（非推奨・後方互換のためのもの — 将来のリリースで削除予定）
4. 上記のいずれも存在しない場合は `sequential`（連番）をデフォルトとする

## ブランチ名テンプレート

`.specify/extensions/git/git-config.yml` に任意設定の `branch_template` の値がないか確認する。空または未設定の場合は、デフォルトのブランチ形式 `{number}-{slug}` を使用する。設定されている場合、`{slug}` は `{number}` より前に現れてはならず、その最終パスセグメントは `{number}-` で始まらなければならない。スクリプトは以下のトークンを展開する:

- `{author}`: サニタイズされた Git 設定の author（`user.name`、フォールバック時はメールアドレスのローカル部分）
- `{app}`: サニタイズされた Spec Kit 初期化ディレクトリ名
- `{number}`: 連番またはタイムスタンプ
- `{slug}`: 生成された短いブランチスラッグ

モノレポの場合、`{author}/{app}/{number}-{slug}` のようなテンプレートを使うと、プロジェクトごとのフィーチャー採番を維持しつつ `jdoe/web/008-guided-tour` のような名前を生成できる。

スクリプトは、単純な名前空間の省略記法として `branch_prefix` も受け付ける。これは `<branch_prefix>/{number}-{slug}` に展開される。

## 実行

ブランチ用の簡潔な短い名前（2〜4語）を生成する:
- フィーチャーの説明を分析し、最も意味のあるキーワードを抽出する
- 可能な限り「動詞-名詞」形式を使用する（例: "add-user-auth"、"fix-payment-bug"）
- 技術用語や略語（OAuth2、API、JWT など）はそのまま保持する

プラットフォームに応じて、適切なスクリプトを実行する:

- **Bash**: `.specify/extensions/git/scripts/bash/create-new-feature-branch.sh --json --short-name "<short-name>" "<feature description>"`
- **Bash（タイムスタンプ）**: `.specify/extensions/git/scripts/bash/create-new-feature-branch.sh --json --timestamp --short-name "<short-name>" "<feature description>"`
- **PowerShell**: `.specify/extensions/git/scripts/powershell/create-new-feature-branch.ps1 -Json -ShortName "<short-name>" "<feature description>"`
- **PowerShell（タイムスタンプ）**: `.specify/extensions/git/scripts/powershell/create-new-feature-branch.ps1 -Json -Timestamp -ShortName "<short-name>" "<feature description>"`

**重要**:
- `--number` は渡さないこと — スクリプトが次に使うべき正しい番号を自動的に決定する
- 出力を確実にパースできるよう、JSON フラグ（Bash では `--json`、PowerShell では `-Json`）を必ず含めること
- このスクリプトは1つのフィーチャーにつき一度だけ実行しなければならない
- JSON 出力には `BRANCH_NAME` と `FEATURE_NUM` が含まれる
- `branch_template` を手動で展開しないこと。スクリプトが git 拡張の設定を読み込み、一貫して適用する

## グレースフルデグレーション

Git がインストールされていない、または現在のディレクトリが Git リポジトリでない場合:
- ブランチ作成はスキップされ、次の警告が表示される: `[specify] Warning: Git repository not detected; skipped branch creation`
- 呼び出し元が参照できるよう、スクリプトはそれでも `BRANCH_NAME` と `FEATURE_NUM` を出力する

## 出力

スクリプトは以下を含む JSON を出力する:
- `BRANCH_NAME`: ブランチ名（例: `003-user-auth`、`20260319-143022-user-auth`、または `jdoe/web/003-user-auth`）
- `FEATURE_NUM`: 使用された数値またはタイムスタンプのプレフィックス
