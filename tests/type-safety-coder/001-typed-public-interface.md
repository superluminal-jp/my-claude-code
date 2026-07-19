# Test: Type-Annotated Public Interface Added by Default

**Category**: type-safety-coder
**ID**: 001

## Input Prompt

```
This is a TypeScript project. Every existing exported function in src/ has explicit
parameter and return types, e.g.:

  export function formatPrice(amount: number, currency: string): string { ... }

Please add a new exported function `applyDiscount` to src/pricing.ts that takes a
price and a discount percentage and returns the discounted price. Don't ask me
about types separately — just implement it.
```

## Expected Behavior

`annotate`

## Pass Criteria

- Claude adds explicit parameter and return type annotations to `applyDiscount`, matching the project's existing convention (e.g. `number` params, `number` return)
- Claude does not ask a separate clarifying question about whether to add types — annotation is the default
- Claude does not introduce a different typing convention than the one already used in the file (e.g. no unrelated generic/interface invention)

## Baseline

実行日: 2026-07-19
観察した動作: annotate
Pass / Fail: Pass
