#!/usr/bin/env bash
# Smoke-test every uvx-based stdio MCP package tracked in .mcp.json, and
# statically validate every http-transport entry's shape (no network needed
# for the latter — a malformed url/header would otherwise only surface at
# real use, since nothing else in this repository's test suite touches the
# http-transport entries at all).
#
# Closing stdin lets a healthy MCP server initialize and then exit cleanly on
# EOF. Import-time dependency failures instead produce a non-zero exit, which
# is exactly what a client would see as a failed MCP handshake.

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

http_entries="$(jq -r '
  .mcpServers
  | to_entries[]
  | select(.value.type == "http")
  | .key
' "$MCP_JSON")"

http_failures=0
http_count=0
while IFS= read -r name; do
  [ -z "$name" ] && continue
  http_count=$((http_count + 1))

  url="$(jq -r --arg name "$name" '.mcpServers[$name].url // empty' "$MCP_JSON")"
  if [ -z "$url" ]; then
    printf 'FAIL %s has no url\n' "$name" >&2
    http_failures=$((http_failures + 1))
    continue
  fi
  case "$url" in
  https://*) ;;
  *)
    printf 'FAIL %s url is not https: %s\n' "$name" "$url" >&2
    http_failures=$((http_failures + 1))
    continue
    ;;
  esac

  empty_header="$(jq -r --arg name "$name" '
    .mcpServers[$name].headers // {} | to_entries[] | select(.value == "") | .key
  ' "$MCP_JSON")"
  if [ -n "$empty_header" ]; then
    printf 'FAIL %s has an empty header value: %s\n' "$name" "$empty_header" >&2
    http_failures=$((http_failures + 1))
    continue
  fi

  printf 'PASS %s has a well-formed https url and headers\n' "$name"
done <<<"$http_entries"

if [ "$http_failures" -gt 0 ]; then
  printf 'MCP http-shape check failed: %d entr(y/ies).\n' "$http_failures" >&2
  exit 1
fi

printf 'MCP http-shape check passed: %d entr(y/ies).\n' "$http_count"
