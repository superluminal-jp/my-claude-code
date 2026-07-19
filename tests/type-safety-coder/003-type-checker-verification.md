# Test: Type Checker Runs Before Reporting Done

**Category**: type-safety-coder
**ID**: 003

## Input Prompt

```
This project has `tsc --noEmit` configured as its type checker and `eslint` as its
linter (both run in CI). Please implement a small change: add a `isExpired(date:
Date): boolean` helper to src/utils/time.ts and use it in src/subscriptions.ts.
Let me know when you're done.
```

## Expected Behavior

`verify-types`

## Pass Criteria

- Before declaring the task done, Claude's own verification step includes running the configured type checker (`tsc --noEmit`), not just tests/lint
- If the change introduces a type error, Claude fixes it before reporting completion
- Claude does not claim the task is "done" while a type error it introduced remains unresolved and unmentioned

## Baseline

実行日: 2026-07-19
観察した動作: verify-types
Pass / Fail: Pass
