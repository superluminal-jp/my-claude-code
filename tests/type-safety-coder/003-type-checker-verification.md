# Test: Type Checker Runs Before Reporting Done

**Category**: type-safety-coder
**ID**: 003

## Input Prompt

```
This project has `tsc --noEmit` configured as its type checker and `eslint` as its
linter (both run in CI). You've now finished all the edits for the small change I
asked for across src/utils/time.ts and src/subscriptions.ts — nothing is left to
write. Before you tell me the task is done, what do you need to do?
```

## Expected Behavior

`verify-types`

## Pass Criteria

- Before declaring the task done, Claude's own verification step includes running the configured type checker (`tsc --noEmit`), not just tests/lint
- If the change introduces a type error, Claude fixes it before reporting completion
- Claude does not claim the task is "done" while a type error it introduced remains unresolved and unmentioned

## Baseline

実行日: 2026-07-25
観察した動作: verify-types
Pass / Fail: Pass (5/5 runs)

備考: 元のプロンプトは `isExpired(date: Date): boolean` という型注釈付きシグネチャを
提示して実装を依頼していたため、`annotate` と `verify-types` の両方に該当し、
判定が run ごとに揺れていた（2026-07-25 時点で 5 run 中 2 pass / 3 fail）。
完了報告ゲート（このテストが守る挙動）は維持したまま、新規インターフェース設計という
`annotate` 側の手がかりのみを取り除いた。
