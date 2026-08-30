---
name: speckit-git-remote
description: "GitHub連携のためにGitリモートURLを検出する"
compatibility: Requires spec-kit project structure with .specify/ directory
metadata:
  author: github-spec-kit
  source: git:commands/speckit.git.remote.md
---

# Gitリモートリポジトリのリモート URL を検出する

GitHub サービス(例:issueの作成)との連携のために、Git リモート URL を検出します。

## 前提条件

- `git rev-parse --is-inside-work-tree 2>/dev/null` を実行して Git が利用可能か確認する
- Git が利用できない場合は、警告を出力して空を返す:
  ```
  [specify] Warning: Git repository not detected; cannot determine remote URL
  ```

## 実行

リモート URL を取得するために、以下のコマンドを実行します。

```bash
git config --get remote.origin.url
```

## 出力

リモート URL を解析し、以下を判定します。

1. **リポジトリのオーナー**: URL から抽出する(例: `https://github.com/github/spec-kit.git` から `github`)
2. **リポジトリ名**: URL から抽出する(例: `https://github.com/github/spec-kit.git` から `spec-kit`)
3. **GitHub かどうか**: リモートが GitHub リポジトリを指しているかどうか

サポートされる URL 形式:
- HTTPS: `https://github.com/<owner>/<repo>.git`
- SSH: `git@github.com:<owner>/<repo>.git`

> [!CAUTION]
> リモート URL が実際に github.com を指している場合に限り、GitHub リポジトリとして報告すること。
> URL の形式が一致しない場合に、リモートが GitHub であると決めつけてはならない。

## 段階的縮退(Graceful Degradation)

Git がインストールされていない、ディレクトリが Git リポジトリではない、またはリモートが設定されていない場合:
- 空の結果を返す
- エラーにしない — 他のワークフローは Git リモート情報なしで継続すべきである
