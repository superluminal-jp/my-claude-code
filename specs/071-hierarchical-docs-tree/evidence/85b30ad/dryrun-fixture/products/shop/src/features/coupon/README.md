# coupon

Part of [@acme/shop](../../../README.md).

## Purpose

Applies a discount code to an order total.

## Out of scope

TODO(unfilled): what this feature deliberately does not handle, and where that is handled instead.

## Design rationale

TODO(unfilled): why it is built this way. Link the decision record of a significant choice.

## Invariants

- A code can be used once per order. Checked by: not checked (no test covers it, and `applyCoupon` does not enforce it).

## Start here

[coupon.ts](coupon.ts)


## Last verified against the code

c3d95e0 plus the uncommitted coupon change
