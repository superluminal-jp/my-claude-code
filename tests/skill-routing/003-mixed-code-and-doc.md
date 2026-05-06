# Test: Mixed Code and Document Request Routes to Both Skills

**Category**: mixed  
**ID**: 003

## Input Prompt

```
実装してREADMEも更新して
```

## Expected Skill

`coder` → `editor`（この順序で両スキルをロード）

## Expected Behavior

`coder` スキルが先にロードされてコード変更が行われ、続いて `editor` スキルがロードされてドキュメントが更新される。

## Pass Criteria

- `coder` スキルが最初にロードされる
- コード変更完了後に `editor` スキルがロードされる
- 両方のアウトプット（コード変更 + ドキュメント更新）が完了する
- スキルのロード順序が `coder` → `editor` であることを確認

## Baseline (変更前の動作記録)

<!-- 変更前にこの欄を記録してから実装に進むこと -->
実行日: ___
観察した動作: ___
Pass / Fail: ___
