# Test: Document Request Auto-Routes to Editor

**Category**: document  
**ID**: 002

## Input Prompt

```
READMEを書いて
```

## Expected Skill

`editor`

## Expected Behavior

`editor` スキルが自動的にロードされ、ドキュメントが作成される。ユーザーが明示的に「editor スキルを使って」と指定する必要がない。

## Pass Criteria

- `editor` スキルが自動的にロードされる
- ユーザーの明示的な指定なしにドキュメントが作成される
- `coder` スキルへの誤ルーティングが発生しない

## Baseline (変更前の動作記録)

<!-- 変更前にこの欄を記録してから実装に進むこと -->
実行日: ___
観察した動作: ___
Pass / Fail: ___
