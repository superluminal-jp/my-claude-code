#!/usr/bin/env bash
# Smoke-test every uvx-based stdio MCP package tracked in .mcp.json.
#
# Closing stdin lets a healthy MCP server initialize and then exit cleanly on
# EOF. Import-time dependency failures instead produce a non-zero exit, which
# catches packages that Codex would report as a failed MCP handshake.

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MCP_JSON="$REPO_ROOT/.mcp.json"

if ! command -v jq >/dev/null 2>&1; then
  echo "error: jq is required but not found on PATH" >&2
  exit 1
fi

if ! command -v uvx >/dev/null 2>&1; then
  echo "error: uvx is required but not found on PATH" >&2
  exit 1
fi

packages="$(jq -r '
  .mcpServers
  | to_entries[]
  | select((.value.type // "stdio") == "stdio")
  | select(.value.command == "uvx")
  | .value.args[0] // empty
' "$MCP_JSON")"

failures=0
package_count=0
while IFS= read -r package; do
  [ -z "$package" ] && continue
  package_count=$((package_count + 1))

  if output="$(uvx "$package" </dev/null 2>&1)"; then
    printf 'PASS %s starts and exits cleanly on EOF\n' "$package"
  else
    printf 'FAIL %s did not start cleanly\n' "$package" >&2
    printf '%s\n' "$output" >&2
    failures=$((failures + 1))
  fi
done <<<"$packages"

if [ "$failures" -gt 0 ]; then
  printf 'MCP startup smoke test failed: %d package(s).\n' "$failures" >&2
  exit 1
fi

printf 'MCP startup smoke test passed: %d package(s).\n' "$package_count"
