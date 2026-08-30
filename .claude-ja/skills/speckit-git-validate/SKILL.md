---
name: speckit-git-validate
description: "現在のブランチがフィーチャーブランチの命名規則に従っているかを検証する"
compatibility: Requires spec-kit project structure with .specify/ directory
metadata:
  author: github-spec-kit
  source: git:commands/speckit.git.validate.md
---

# フィーチャーブランチの検証

現在の Git ブランチが、期待されるフィーチャーブランチの命名規則に従っているかを検証する。

## 前提条件

- `git rev-parse --is-inside-work-tree 2>/dev/null` を実行して、Git が利用可能かどうかを確認する
- Git が利用できない場合は、警告を出力して検証をスキップする:
  ```
  [specify] Warning: Git repository not detected; skipped branch validation
  ```

## 検証ルール

現在のブランチ名を取得する:

```bash
git rev-parse --abbrev-ref HEAD
```

ブランチ名の最後のパスセグメントは、次のいずれかのフィーチャーマーカーで始まっていなければならない:

1. **連番形式**: `[0-9]{3,}-`（例: `001-feature-name`、`042-fix-bug`、`1000-big-feature`、`jdoe/web/008-guided-tour`）
2. **タイムスタンプ形式**: `[0-9]{8}-[0-9]{6}-`（例: `20260319-143022-feature-name`、`jdoe/web/20260319-143022-feature-name`）

## 実行

フィーチャーブランチ上にある場合（いずれかのパターンに一致する場合）:
- 出力: `✓ On feature branch: <branch-name>`
- `specs/` 配下に対応する spec ディレクトリが存在するかを確認する:
  - 連番形式のブランチの場合、ブランチの名前空間プレフィックスに関わらず、数値部分に一致する `specs/<prefix>-*` を探す
  - タイムスタンプ形式のブランチの場合、ブランチの名前空間プレフィックスに関わらず、`YYYYMMDD-HHMMSS` 部分に一致する `specs/<prefix>-*` を探す
- spec ディレクトリが存在する場合: `✓ Spec directory found: <path>`
- spec ディレクトリが見つからない場合: `⚠ No spec directory found for prefix <prefix>`

フィーチャーブランチ上にない場合:
- 出力: `✗ Not on a feature branch. Current branch: <branch-name>`
- 出力: `Feature branches should be named like: 001-feature-name, 20260319-143022-feature-name, or <namespace>/001-feature-name`

## グレースフルデグラデーション（段階的な機能低下）

Git がインストールされていない場合、またはディレクトリが Git リポジトリでない場合:
- フォールバックとして環境変数 `SPECIFY_FEATURE` を確認する
- 設定されていれば、その値を命名パターンに照らして検証する
- 設定されていなければ、警告を出して検証をスキップする
