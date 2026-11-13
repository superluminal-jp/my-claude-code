# @acme/shop

Part of [acme-platform](../../README.md).

## Purpose

Customer-facing web shop.

## Run and test

Build with `vite build` and test with `vitest run` (the `build` and `test` scripts). TODO(unfilled): how to run it locally.

## Boundaries

TODO(unfilled): what this product may depend on and what it must not depend on. Checked by: TODO(unfilled): the rule or test that enforces each boundary, or "not checked".

## Features

- [cart](src/features/cart/README.md): Keeps the items a customer intends to buy, in the browser session only.
- [checkout](src/features/checkout/README.md): Turns a cart into an order.
- [coupon](src/features/coupon/README.md): Applies a discount code to an order total.
