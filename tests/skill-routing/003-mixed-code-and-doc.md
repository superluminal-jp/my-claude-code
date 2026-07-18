# Test: Mixed Code and Document Request Routes to Both Skills

**Category**: mixed  
**ID**: 003

## Input Prompt

```
実装してREADMEも更新して
```

## Expected Skill

`coder` → `executive-structure-rewriter`

## Expected Behavior

`coder` スキルが先にロードされてコード変更が行われ、続いて `executive-structure-rewriter` スキルがロードされて既存の README が更新される。

## Pass Criteria

- `coder` スキルが最初にロードされる
- コード変更完了後に `executive-structure-rewriter` スキルがロードされる
- 両方のアウトプット（コード変更 + ドキュメント更新）が完了する
- スキルのロード順序が `coder` → `executive-structure-rewriter` であることを確認

## Baseline (変更前の動作記録)

<!-- 変更前にこの欄を記録してから実装に進むこと -->
実行日: ___
観察した動作: ___
Pass / Fail: ___
