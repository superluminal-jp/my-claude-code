// Turns a cart into an order. Payment is handled by an external provider.
export function placeOrder(cart: string[]): { items: string[] } {
  if (cart.length === 0) throw new Error("empty cart");
  return { items: cart };
}
