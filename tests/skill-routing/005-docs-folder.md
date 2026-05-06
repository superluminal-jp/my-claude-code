# Test: docs/ Folder Request Auto-Routes to Editor

**Category**: document  
**ID**: 005

## Input Prompt

```
docs/configuration.md の内容を更新して
```

## Expected Skill

`editor`

## Expected Behavior

`editor` スキルが自動的にロードされ、`docs/` フォルダ内のファイルへの変更が行われる。`coder` スキルへの誤ルーティングが発生しない。

## Pass Criteria

- `editor` スキルが自動的にロードされる
- `docs/` フォルダへの参照が含まれるリクエストで `coder` が起動しない
- ユーザーの明示的な指定なしにドキュメント編集が実行される

## Baseline (変更前の動作記録)

<!-- 変更前にこの欄を記録してから実装に進むこと -->
実行日: 2026-05-06
観察した動作: editor
Pass / Fail: Pass
