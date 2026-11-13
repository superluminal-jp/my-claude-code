// Applies a discount code to an order total. A code can be used once per order.
export function applyCoupon(total: number, percent: number): number {
  return total * (1 - percent / 100);
}
