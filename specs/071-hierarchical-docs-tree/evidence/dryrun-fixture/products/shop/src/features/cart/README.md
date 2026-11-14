# cart

Part of [@acme/shop](../../../README.md).

## Purpose

Keeps the items a customer intends to buy, in the browser session only.

## Out of scope

TODO(unfilled): what this feature deliberately does not handle, and where that is handled instead.

## Design rationale

TODO(unfilled): why it is built this way. Link the decision record of a significant choice.

## Invariants

- Adding an item keeps the items already in the cart. Checked by: the test "adding an item keeps earlier items" in [cart.test.ts](cart.test.ts).

## Start here

[cart.ts](cart.ts)

## Last verified against the code

4db85ed
