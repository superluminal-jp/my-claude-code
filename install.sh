#!/usr/bin/env bash
# Synchronize the managed .claude/ configuration into the user's ~/.claude/,
# upsert the repository's MCP servers, and install its required Claude Code
# plugins. Re-running is idempotent.
#
# Requires: claude CLI, uvx, jq. Optional: GOOGLE_DEV_KNOWLEDGE_API_KEY.
#
# Usage (from the cloned repo):
#   bash path/to/my-claude-code/install.sh
# Or, after a previous install:
#   ~/.claude/install.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="$SCRIPT_DIR/.claude"
TARGET_DIR="$HOME/.claude"

upsert_user_mcp() {
  local name="$1"
  shift

  # Ensure repo values win on re-install.
  claude mcp remove -s user "$name" >/dev/null 2>&1 || true
  claude mcp add -s user "$name" "$@"
}

sync_path() {
  local rel="$1"
  local src="$SOURCE_DIR/$rel"
  local dst="$TARGET_DIR/$rel"

  # Make target match source exactly for managed paths.
  rm -rf "$dst"
  if [ -d "$src" ]; then
    mkdir -p "$(dirname "$dst")"
    cp -R "$src" "$dst"
  elif [ -f "$src" ]; then
    mkdir -p "$(dirname "$dst")"
    cp "$src" "$dst"
  fi
}

sync_settings_json() {
  local src="$SOURCE_DIR/settings.json"
  local dst="$TARGET_DIR/settings.json"

  if [ ! -f "$dst" ]; then
    cp "$src" "$dst"
    return
  fi

  # Merge instead of replace: a key this repo declares (model, permissions,
  # hooks, ...) always takes the repo's value, recursing into shared objects
  # so e.g. permissions.deny stays enforced (docs/adr/0014) while a sibling
  # key under the same object survives. A top-level key the repo does not
  # declare - env, enabledPlugins, agentPushNotifEnabled, and anything else
  # a user or the CLI itself added - is left untouched. `jq`'s `*` merges
  # objects recursively and takes the right operand on any non-object
  # conflict, so the repo file goes second.
  local merged
  merged="$(jq -s '.[0] * .[1]' "$dst" "$src")"
  printf '%s\n' "$merged" >"$dst"
}

# 0. Preflight checks
for cmd in claude uvx jq; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Missing required command: $cmd" >&2
    exit 1
  fi
done

# 1. Sync managed .claude paths (prevents stale skills/rules)
if [ "$SCRIPT_DIR" != "$TARGET_DIR" ]; then
  mkdir -p "$TARGET_DIR"
  # Declared paths are replaced exactly. Missing sources are intentional
  # cleanup paths for artifacts managed by earlier repository versions;
  # everything else already under ~/.claude remains user-owned and untouched.
  # settings.json is handled separately below: it is merged, not replaced.
  for managed_path in \
    rules \
    skills \
    agents \
    commands \
    CLAUDE.md; do
    sync_path "$managed_path"
  done
  sync_settings_json

  # speckit-* skills are generated locally per-project by `specify init`
  # (gitignored, never committed — see docs/adr/0001-remove-vendored-speckit-skills.md).
  # Strip generated and OS metadata from the managed user-scope copy.
  rm -rf "$TARGET_DIR"/skills/speckit-* "$TARGET_DIR/skills/.DS_Store"

  cp "$SCRIPT_DIR/install.sh" "$TARGET_DIR/install.sh"
  echo "Synced managed paths from $SOURCE_DIR -> $TARGET_DIR"
fi

# 2. Ensure this installer is executable
chmod +x "$TARGET_DIR"/install.sh

# 3. Upsert user-scope MCP servers to match this repository
upsert_user_mcp aws-knowledge \
  --transport http \
  https://knowledge-mcp.global.api.aws

upsert_user_mcp aws-documentation \
  -e FASTMCP_LOG_LEVEL=ERROR \
  -e AWS_DOCUMENTATION_PARTITION=aws \
  -- uvx awslabs.aws-documentation-mcp-server@latest

upsert_user_mcp bedrock-agentcore \
  -e FASTMCP_LOG_LEVEL=ERROR \
  -- uvx awslabs.amazon-bedrock-agentcore-mcp-server@latest

upsert_user_mcp strands-agents \
  -e FASTMCP_LOG_LEVEL=ERROR \
  -- uvx strands-agents-mcp-server@latest

if [ -n "${GOOGLE_DEV_KNOWLEDGE_API_KEY:-}" ]; then
  upsert_user_mcp google-developer-knowledge \
    --transport http \
    https://developerknowledge.googleapis.com/mcp \
    --header "X-Goog-Api-Key: ${GOOGLE_DEV_KNOWLEDGE_API_KEY}"
else
  claude mcp remove -s user google-developer-knowledge >/dev/null 2>&1 || true
  echo "Skipping google-developer-knowledge MCP: GOOGLE_DEV_KNOWLEDGE_API_KEY is not set" >&2
fi

upsert_user_mcp microsoft-learn \
  --transport http \
  https://learn.microsoft.com/api/mcp

# 4. Install this repository's Claude Code plugins, all resolved from the
# claude-plugins-official marketplace catalog: frontend-design (UI/UX
# implementation guidance), code-review (multi-agent PR review, incl.
# `/code-review ultra`), skill-creator (scaffold/evaluate skills), github
# (GitHub's official issue/PR/repo MCP server), deploy-on-aws (AWS's
# architecture-diagram + deploy skills — adopted in full per
# docs/adr/0009-adopt-deploy-on-aws-plugin.md; its deploy/mutating-AWS-CLI
# capability requires confirmation on every use per `rules/permissions.md`,
# not a plugin-level gate), microsoft-docs (Microsoft's official docs MCP
# server; bundles its own `microsoft-learn` MCP entry, duplicating this
# repository's `.mcp.json` entry of the same name under a different source —
# same redundant-not-conflicting pattern as deploy-on-aws's `awsknowledge`,
# see README.md § Plugins). Mirrored in `.claude/settings.json`'s
# `enabledPlugins` for project-scope discovery; this step performs the actual
# user-scope install so it works across projects.
if ! claude plugin marketplace list 2>/dev/null | grep -q "claude-plugins-official"; then
  claude plugin marketplace add anthropics/claude-plugins-official
else
  claude plugin marketplace update claude-plugins-official >/dev/null 2>&1 || true
fi
for official_plugin in frontend-design code-review skill-creator github deploy-on-aws microsoft-docs; do
  if ! claude plugin list 2>/dev/null | grep -q "${official_plugin}@claude-plugins-official"; then
    claude plugin install "${official_plugin}@claude-plugins-official"
  fi
  claude plugin enable "${official_plugin}@claude-plugins-official" >/dev/null 2>&1 || true
done

echo "Done. ~/.claude and user-scope MCP are synced to this repository state."
