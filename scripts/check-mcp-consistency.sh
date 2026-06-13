#!/usr/bin/env bash
# Verify MCP server definitions are consistent across the four places that
# describe them: .mcp.json (source of truth), install.sh (user-scope
# registration), .claude/settings.json (permission allowlist), and
# .claude/rules/mcp.md (human catalog).
#
# Checks, per server in .mcp.json:
#   - install.sh registers it (upsert_user_mcp <name>)
#   - settings.json allows it (permissions.allow has mcp__<name>__*)
#   - mcp.md lists it in the catalog
#   - http servers: the url in .mcp.json also appears in install.sh
#   - stdio servers: the pinned package@version in .mcp.json matches install.sh
# Plus the reverse: every name registered in install.sh exists in .mcp.json.
#
# Requires: jq. Exits 0 when consistent, 1 on any mismatch.

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MCP_JSON="$ROOT/.mcp.json"
INSTALL_SH="$ROOT/install.sh"
SETTINGS="$ROOT/.claude/settings.json"
MCP_MD="$ROOT/.claude/rules/mcp.md"

if ! command -v jq >/dev/null 2>&1; then
  echo "error: jq is required but not found on PATH" >&2
  exit 1
fi

errors=0
fail() {
  echo "MISMATCH: $*" >&2
  errors=$((errors + 1))
}

for f in "$MCP_JSON" "$INSTALL_SH" "$SETTINGS" "$MCP_MD"; do
  if [ ! -f "$f" ]; then
    echo "error: missing required file: $f" >&2
    exit 1
  fi
done

names="$(jq -r '.mcpServers | keys[]' "$MCP_JSON")"

while IFS= read -r name; do
  [ -z "$name" ] && continue

  # install.sh registration
  if ! grep -qE "upsert_user_mcp[[:space:]]+$name([[:space:]]|\\\\|$)" "$INSTALL_SH" &&
    ! grep -qE "remove -s user[[:space:]]+$name" "$INSTALL_SH"; then
    fail "$name not registered in install.sh"
  fi

  # settings.json permission allowlist
  if ! jq -e --arg p "mcp__${name}__*" '.permissions.allow | index($p)' "$SETTINGS" >/dev/null; then
    fail "$name missing from settings.json permissions.allow (expected mcp__${name}__*)"
  fi

  # mcp.md catalog
  if ! grep -qF "\`$name\`" "$MCP_MD"; then
    fail "$name not listed in $MCP_MD catalog"
  fi

  type="$(jq -r --arg n "$name" '.mcpServers[$n].type // "stdio"' "$MCP_JSON")"
  if [ "$type" = "http" ]; then
    url="$(jq -r --arg n "$name" '.mcpServers[$n].url // empty' "$MCP_JSON")"
    if [ -n "$url" ] && ! grep -qF "$url" "$INSTALL_SH"; then
      fail "$name url not found in install.sh ($url)"
    fi
  else
    pkg="$(jq -r --arg n "$name" '.mcpServers[$n].args[0] // empty' "$MCP_JSON")"
    if [ -n "$pkg" ] && ! grep -qF "$pkg" "$INSTALL_SH"; then
      fail "$name pinned package not found in install.sh ($pkg)"
    fi
  fi
done <<<"$names"

# Reverse: names registered in install.sh must exist in .mcp.json.
registered="$(grep -oE "upsert_user_mcp[[:space:]]+[a-z0-9-]+" "$INSTALL_SH" | awk '{print $2}' | sort -u)"
while IFS= read -r reg; do
  [ -z "$reg" ] && continue
  if ! grep -qx "$reg" <<<"$names"; then
    fail "$reg registered in install.sh but absent from .mcp.json"
  fi
done <<<"$registered"

if [ "$errors" -gt 0 ]; then
  echo "MCP consistency check failed: $errors mismatch(es)." >&2
  exit 1
fi

echo "MCP consistency OK: $(wc -l <<<"$names" | tr -d ' ') servers consistent across .mcp.json, install.sh, settings.json, mcp.md."
