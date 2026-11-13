// Keeps the items a customer intends to buy, in the browser session only.
export function addItem(cart: string[], sku: string): string[] {
  return [...cart, sku];
}
