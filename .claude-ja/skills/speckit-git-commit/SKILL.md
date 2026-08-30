---
name: speckit-git-commit
description: "Spec Kit コマンドの完了後に変更を自動コミットする"
compatibility: Requires spec-kit project structure with .specify/ directory
metadata:
  author: github-spec-kit
  source: git:commands/speckit.git.commit.md
---

# 変更の自動コミット

Spec Kit コマンドの完了後に、すべての変更を自動的にステージングしコミットします。

## 動作

このコマンドは、コアコマンドの後(または前)にフックとして呼び出されます。次の処理を行います。

1. フックのコンテキストからイベント名を判定する(例: `after_specify` フックとして呼び出された場合、イベントは `after_specify` になり、`before_plan` の場合はイベントは `before_plan` になる)
2. `.specify/extensions/git/git-config.yml` の `auto_commit` セクションを確認する
3. 該当するイベントキーを調べ、自動コミットが有効かどうかを確認する
4. イベント固有のキーが存在しない場合は `auto_commit.default` にフォールバックする
5. コマンドごとの `message` が設定されていればそれを使用し、なければデフォルトメッセージを使用する
6. 有効であり、かつ未コミットの変更がある場合、`git add .` と `git commit` を実行する

## 実行

このコマンドをトリガーしたフックからイベント名を判定し、次のスクリプトを実行します。

- **Bash**: `.specify/extensions/git/scripts/bash/auto-commit.sh <event_name>`
- **PowerShell**: `.specify/extensions/git/scripts/powershell/auto-commit.ps1 <event_name>`

`<event_name>` は実際のフックイベント(例: `after_specify`、`before_plan`、`after_implement`)に置き換えてください。

## 設定

`.specify/extensions/git/git-config.yml` にて:

```yaml
auto_commit:
  default: false          # Global toggle — set true to enable for all commands
  after_specify:
    enabled: true          # Override per-command
    message: "[Spec Kit] Add specification"
  after_plan:
    enabled: false
    message: "[Spec Kit] Add implementation plan"
```

## グレースフルデグラデーション

- Git が利用できない場合、またはカレントディレクトリがリポジトリでない場合: 警告を出してスキップする
- 設定ファイルが存在しない場合: スキップする(デフォルトで無効)
- コミットすべき変更がない場合: メッセージを出してスキップする
