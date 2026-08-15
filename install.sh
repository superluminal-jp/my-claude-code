#!/usr/bin/env bash
# Synchronize the managed .claude/ configuration into the user's ~/.claude/
# and upsert the repository's MCP servers. Re-running is idempotent.
#
# Claude Code only. This installer deploys NO Codex CLI configuration and never
# touches ~/.codex or ~/.agents — Codex configuration is produced by the
# developer with OpenAI's official /import flow. See README.md § "Codex CLI
# support" and docs/adr/0004-adopt-official-codex-import.md.
# Requires: claude CLI, uvx. Optional: GOOGLE_DEV_KNOWLEDGE_API_KEY.
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

# 0. Preflight checks
for cmd in claude uvx; do
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
  for managed_path in \
    hooks \
    rules \
    skills \
    agents \
    commands \
    CLAUDE.md \
    settings.json; do
    sync_path "$managed_path"
  done

  # speckit-* skills are generated locally per-project by `specify init`
  # (gitignored, never committed — see docs/adr/0001-remove-vendored-speckit-skills.md).
  # Strip generated and OS metadata from the managed user-scope copy.
  rm -rf "$TARGET_DIR"/skills/speckit-* "$TARGET_DIR/skills/.DS_Store"

  cp "$SCRIPT_DIR/install.sh" "$TARGET_DIR/install.sh"
  echo "Synced managed paths from $SOURCE_DIR -> $TARGET_DIR"
fi

# 1a. scripts/guardrails/ no longer exists in this repository (removed
# entirely, along with its dedicated tests and scripts/check-mcp-consistency.sh
# — see specs/027-remove-scripts/). This step stays as the uninstall path: it
# clears any ~/.claude/scripts/guardrails/ left by an install made before
# that removal, the same pattern used for "hooks" in install.sh above.
rm -rf "$TARGET_DIR/scripts/guardrails"

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

# 4. Install codex-plugin-cc (Codex review/rescue from Claude Code)
if ! claude plugin marketplace list 2>/dev/null | grep -q "openai-codex"; then
  claude plugin marketplace add openai/codex-plugin-cc
else
  claude plugin marketplace update openai-codex >/dev/null 2>&1 || true
fi
if ! claude plugin list 2>/dev/null | grep -q "codex@openai-codex"; then
  claude plugin install codex@openai-codex
fi

echo "Done. ~/.claude and user-scope MCP are synced to this repository state."
