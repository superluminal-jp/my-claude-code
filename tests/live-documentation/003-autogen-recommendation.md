# Test: Auto-generation Recommended Instead of Hand-Written API Docs

**Category**: live-documentation
**ID**: 003

## Input Prompt

```
Please write the API reference documentation for this function:

def process_payment(
    amount: Decimal,
    currency: str,
    customer_id: str,
    idempotency_key: str | None = None,
) -> PaymentResult:
    """Process a payment transaction."""
    ...

The function already has type annotations and a docstring. Write me a Markdown API reference I can put in docs/api.md.
```

## Expected Behavior

`autogen`

## Pass Criteria

- Claude identifies that the function has complete type annotations and a docstring
- Claude recommends using an auto-generation tool (e.g., pdoc, sphinx-apidoc, or similar) rather than hand-writing the reference
- Claude declines to produce the hand-written Markdown API reference
- Claude does not write content that duplicates what is already in the source

## Baseline

実行日: 2026-05-26
観察した動作: autogen
Pass / Fail: Pass
