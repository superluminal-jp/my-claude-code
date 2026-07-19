# Test: Boundary Data Validated Before Use as a Typed Value

**Category**: type-safety-coder
**ID**: 004

## Input Prompt

```
We call an external payments API and get back parsed JSON like:

  const response = await fetch(url).then(r => r.json());

We need `response.transactionId` and `response.amount` typed as `string` and
`number` respectively to pass to our internal `recordTransaction(id: string,
amount: number)` function. Please write the code to call the API and record the
transaction.
```

## Expected Behavior

`validate-boundary`

## Pass Criteria

- Claude validates or narrows the parsed JSON response's shape (e.g. a type guard, schema check, or explicit field checks) before treating `transactionId`/`amount` as typed values
- Claude does not directly cast the untyped `response` object (e.g. `as { transactionId: string; amount: number }`) and pass its fields straight into `recordTransaction` without any runtime check
- Claude does not add redundant validation elsewhere for values that never cross this external boundary

## Baseline

実行日: 2026-07-19
観察した動作: validate-boundary
Pass / Fail: Pass
