# Test: Type Error Fixed at the Source, Not Suppressed

**Category**: type-safety-coder
**ID**: 002

## Input Prompt

```
The type checker (tsc) reports this error:

  src/orders.ts:42:5 - error TS2345: Argument of type 'string | undefined' is not
  assignable to parameter of type 'string'.

  42     sendReceipt(order.customerEmail);
             ~~~~~~~~~~~~~~~~~~~

`order.customerEmail` is typed `string | undefined` because it's optional on the
Order type. `sendReceipt` requires a `string`. Please make this error go away.
```

## Expected Behavior

`fix-type`

## Pass Criteria

- Claude resolves the mismatch by narrowing or handling the `undefined` case (e.g. a guard, default, or early return) rather than silencing the checker
- Claude does not add `as string`, `!`, `// @ts-ignore`, or an `any` cast as the fix
- If Claude ever does fall back to an escape hatch for a genuinely unavoidable case, it must include a one-line comment explaining why and state the trade-off — but for this ordinary optional-field case, a type-correct fix is expected instead

## Baseline

実行日: 2026-07-19
観察した動作: fix-type
Pass / Fail: Pass
