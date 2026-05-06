# Test: Code Request Auto-Routes to Coder

**Category**: code  
**ID**: 001

## Input Prompt

```
バグを修正して
```

## Expected Skill

`coder`

## Expected Behavior

`coder` スキルが自動的にロードされ、コードの変更が行われる。ユーザーが明示的に「coder スキルを使って」と指定する必要がない。

## Pass Criteria

- `coder` スキルが自動的にロードされる
- ユーザーの明示的な指定なしにコード変更が実行される
- `/speckit-*` スラッシュコマンドへの誤ルーティングが発生しない

## Baseline (変更前の動作記録)

<!-- 変更前にこの欄を記録してから実装に進むこと -->
実行日: ___
観察した動作: ___
Pass / Fail: ___
