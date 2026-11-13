// Records staff actions for later review. Entries are never edited after they are written.
export function record(action: string): string {
  return `${new Date().toISOString()} ${action}`;
}
