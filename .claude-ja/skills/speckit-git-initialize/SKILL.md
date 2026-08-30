---
name: speckit-git-initialize
description: "初期コミットとともにGitリポジトリを初期化する"
compatibility: Requires spec-kit project structure with .specify/ directory
metadata:
  author: github-spec-kit
  source: git:commands/speckit.git.initialize.md
---

# Gitリポジトリの初期化

現在のプロジェクトディレクトリにGitリポジトリがまだ存在しない場合、それを初期化する。

## 実行

プロジェクトルートから適切なスクリプトを実行する。

- **Bash**: `.specify/extensions/git/scripts/bash/initialize-repo.sh`
- **PowerShell**: `.specify/extensions/git/scripts/powershell/initialize-repo.ps1`

拡張スクリプトが見つからない場合は、以下にフォールバックする。
- **Bash**: `git init && git add . && git commit -m "Initial commit from Specify template"`
- **PowerShell**: `git init; git add .; git commit -m "Initial commit from Specify template"`

このスクリプトは以下のチェックをすべて内部で処理する。
- Gitが利用できない場合はスキップする
- すでにGitリポジトリの内部にいる場合はスキップする
- `git init`、`git add .`、そして初期コミットメッセージ付きの`git commit`を実行する

## カスタマイズ

プロジェクト固有のGit初期化手順を追加するには、スクリプトを置き換える。
- カスタムの`.gitignore`テンプレート
- デフォルトブランチ名の設定（`git config init.defaultBranch`）
- Git LFSのセットアップ
- Gitフックのインストール
- コミット署名の設定
- Git Flowの初期化

## 出力

成功時:
- `[OK] Git repository initialized`

## 段階的縮退（Graceful Degradation）

Gitがインストールされていない場合:
- ユーザーに警告する
- リポジトリの初期化をスキップする
- プロジェクトはGitなしでも機能し続ける（`specs/`配下にスペックを作成することは引き続き可能）

Gitはインストールされているが、`git init`、`git add .`、または`git commit`が失敗した場合:
- エラーをユーザーに提示する
- 部分的に初期化された状態のリポジトリで処理を続行せず、このコマンドを停止する
