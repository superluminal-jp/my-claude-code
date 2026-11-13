# checkout

Part of [@acme/shop](../../../README.md).

## Purpose

Turns a cart into an order.

## Out of scope

Payment, which an external provider handles. TODO(unfilled): which provider, and where the integration lives.

## Design rationale

TODO(unfilled): why it is built this way. Link the decision record of a significant choice.

## Invariants

- An empty cart is never turned into an order. Checked by: not checked (no test covers it).

## Start here

[checkout.ts](checkout.ts)


## Last verified against the code

97920c9
