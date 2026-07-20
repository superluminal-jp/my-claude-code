# Test: docs/ Folder Update Auto-Routes to Executive Structure Rewriter

**Category**: document  
**ID**: 005

## Input Prompt

```
docs/configuration.md の内容を更新して
```

## Expected Skill

`minto-rewriter`

## Expected Behavior

`minto-rewriter` スキルが自動的にロードされ、既存の `docs/` フォルダ内文書が完成版へ書き換えられる。`coder` スキルへの誤ルーティングが発生しない。

## Pass Criteria

- `minto-rewriter` スキルが自動的にロードされる
- `docs/` フォルダへの参照が含まれるリクエストで `coder` が起動しない
- ユーザーの明示的な指定なしに文書編集が実行される

## Baseline (変更前の動作記録)

<!-- 変更前にこの欄を記録してから実装に進むこと -->
実行日: 2026-07-20
観察した動作: minto-rewriter
Pass / Fail: Pass
