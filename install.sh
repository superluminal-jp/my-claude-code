#!/usr/bin/env bash
# Install this .claude/ tree into the user's ~/.claude/ and sync MCP servers.
# Idempotent: re-running refreshes hooks/rules/skills/settings and upserts MCP servers.
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

# 0. Preflight checks
for cmd in claude uvx jq; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Missing required command: $cmd" >&2
    exit 1
  fi
done

# 1. Sync managed .claude paths (prevents stale skills/rules/hooks)
if [ "$SCRIPT_DIR" != "$TARGET_DIR" ]; then
  mkdir -p "$TARGET_DIR"
  sync_path "hooks"
  sync_path "rules"
  sync_path "skills"
  # speckit-* skills are generated locally per-project by `specify init`
  # (gitignored, never committed — see docs/adr/0001-remove-vendored-speckit-skills.md).
  # If a local `specify init` has populated $SOURCE_DIR/skills/speckit-*, the
  # blanket skills sync above would otherwise re-vendor them into the shared
  # user-scope install; strip them so ~/.claude/skills never carries Spec Kit.
  rm -rf "$TARGET_DIR"/skills/speckit-*
  sync_path "commands"
  sync_path "CLAUDE.md"
  sync_path "settings.json"
  cp "$SCRIPT_DIR/install.sh" "$TARGET_DIR/install.sh"
  echo "Synced managed paths from $SOURCE_DIR -> $TARGET_DIR"
fi

# 1a. Sync the shared guardrail scripts (repo-root scripts/guardrails/, not
# under .claude/ — they're consumed by both Claude Code's hooks and Codex
# CLI's adapters, so they're deployed here as a sibling of hooks/rules/skills
# rather than nested under either tool's own directory). Both
# .claude/hooks/*.sh and .codex/hooks/*.sh resolve this same installed copy
# once deployed, so guardrail behavior stays correct regardless of which
# project you're currently working in.
GUARDRAILS_SRC="$SCRIPT_DIR/scripts/guardrails"
GUARDRAILS_DST="$TARGET_DIR/scripts/guardrails"
if [ -d "$GUARDRAILS_SRC" ]; then
  rm -rf "$GUARDRAILS_DST"
  mkdir -p "$GUARDRAILS_DST"
  cp -R "$GUARDRAILS_SRC"/. "$GUARDRAILS_DST/"
  chmod +x "$GUARDRAILS_DST"/*.sh
  echo "Synced shared guardrail scripts -> $GUARDRAILS_DST"
fi

# 1b. Deploy AGENTS.md to Codex CLI's global config (mirrors the .claude/ sync above)
CODEX_TARGET_DIR="$HOME/.codex"
AGENTS_MD_SRC="$SCRIPT_DIR/AGENTS.md"
AGENTS_MD_DST="$CODEX_TARGET_DIR/AGENTS.md"
if [ -f "$AGENTS_MD_SRC" ]; then
  mkdir -p "$CODEX_TARGET_DIR"
  if [ -s "$AGENTS_MD_DST" ] && ! cmp -s "$AGENTS_MD_SRC" "$AGENTS_MD_DST"; then
    cp "$AGENTS_MD_DST" "$AGENTS_MD_DST.bak"
    echo "Note: $AGENTS_MD_DST had different content; previous version saved to $AGENTS_MD_DST.bak" >&2
  fi
  cp "$AGENTS_MD_SRC" "$AGENTS_MD_DST"
  echo "Synced AGENTS.md -> $AGENTS_MD_DST"
fi

# 1c. Symlink this repo's custom skills into Codex CLI's global skill discovery
# path ($HOME/.agents/skills), pointing at the copy sync_path("skills") just
# placed under ~/.claude/skills — not back at this repository's working tree,
# so the link survives even if this clone is later moved or deleted.
# speckit-* skills are excluded: they're per-project generated artifacts (see
# the speckit-* stripping above), not part of this repo's global skill set.
CODEX_SKILLS_DIR="$HOME/.agents/skills"
CUSTOM_SKILLS="adr advisor clarifier coder domain-model minto-builder minto-reviewer minto-rewriter ubiquitous-language"
if [ -d "$TARGET_DIR/skills" ]; then
  mkdir -p "$CODEX_SKILLS_DIR"
  for skill in $CUSTOM_SKILLS; do
    ln -sfn "$TARGET_DIR/skills/$skill" "$CODEX_SKILLS_DIR/$skill"
  done
  echo "Symlinked custom skills -> $CODEX_SKILLS_DIR"
fi

# 1d. Deploy and register this repo's Codex CLI hook adapters in
# ~/.codex/config.toml. Uses a marker-delimited managed block so re-running
# this installer replaces the block instead of duplicating entries
# (idempotent) and never touches the rest of the user's config.toml. Each
# adapter is registered only if its script exists under .codex/hooks/, so
# this loop needs no changes as more adapters are added.
CODEX_CONFIG="$HOME/.codex/config.toml"
CODEX_HOOKS_SRC_DIR="$SCRIPT_DIR/.codex/hooks"
CODEX_HOOKS_DST_DIR="$HOME/.codex/hooks"
CODEX_HOOKS_BEGIN="# >>> my-claude-code managed hooks (do not edit by hand; see install.sh) >>>"
CODEX_HOOKS_END="# <<< my-claude-code managed hooks <<<"

if [ -d "$CODEX_HOOKS_SRC_DIR" ] && [ -n "$(ls -A "$CODEX_HOOKS_SRC_DIR"/*.sh 2>/dev/null)" ]; then
  mkdir -p "$CODEX_HOOKS_DST_DIR"
  cp "$CODEX_HOOKS_SRC_DIR"/*.sh "$CODEX_HOOKS_DST_DIR/"
  chmod +x "$CODEX_HOOKS_DST_DIR"/*.sh

  mkdir -p "$(dirname "$CODEX_CONFIG")"
  touch "$CODEX_CONFIG"

  # Strip any previous managed block before regenerating it.
  python3 - "$CODEX_CONFIG" "$CODEX_HOOKS_BEGIN" "$CODEX_HOOKS_END" <<'PYEOF'
import sys
path, begin, end = sys.argv[1:4]
with open(path) as f:
    lines = f.readlines()
out, skipping = [], False
for line in lines:
    if line.strip() == begin:
        skipping = True
        continue
    if line.strip() == end:
        skipping = False
        continue
    if not skipping:
        out.append(line)
with open(path, "w") as f:
    f.writelines(out)
PYEOF

  python3 - "$CODEX_CONFIG" "$CODEX_HOOKS_DST_DIR" "$CODEX_HOOKS_BEGIN" "$CODEX_HOOKS_END" <<'PYEOF'
import sys
config_path, hooks_dir, begin, end = sys.argv[1:5]

# (adapter script filename, hook event, matcher)
ADAPTERS = [
    ("destructive-command-adapter.sh", "PreToolUse", "Bash"),
    ("pre-edit-adapter.sh", "PreToolUse", "apply_patch|Edit|Write"),
    ("post-edit-adapter.sh", "PostToolUse", "apply_patch|Edit|Write"),
]

import os
lines = [begin]
for filename, event, matcher in ADAPTERS:
    script_path = os.path.join(hooks_dir, filename)
    if not os.path.isfile(script_path):
        continue
    lines.append(f"[[hooks.{event}]]")
    lines.append(f'matcher = "{matcher}"')
    lines.append(f"[[hooks.{event}.hooks]]")
    lines.append('type = "command"')
    lines.append(f'command = "{script_path}"')
lines.append(end)

with open(config_path, "a") as f:
    f.write("\n" + "\n".join(lines) + "\n")
PYEOF

  echo "Registered Codex CLI hook adapters -> $CODEX_CONFIG"
fi

# 2. Ensure hook scripts and this installer are executable
chmod +x "$TARGET_DIR"/hooks/*.sh
chmod +x "$TARGET_DIR"/install.sh

# 3. Upsert user-scope MCP servers to match this repository
upsert_user_mcp aws-knowledge \
  --transport http \
  https://knowledge-mcp.global.api.aws

upsert_user_mcp aws-documentation \
  -e FASTMCP_LOG_LEVEL=ERROR \
  -e AWS_DOCUMENTATION_PARTITION=aws \
  -- uvx awslabs.aws-documentation-mcp-server@1.1.20

upsert_user_mcp bedrock-agentcore \
  -e FASTMCP_LOG_LEVEL=ERROR \
  -- uvx awslabs.amazon-bedrock-agentcore-mcp-server@0.0.16

upsert_user_mcp strands-agents \
  -e FASTMCP_LOG_LEVEL=ERROR \
  -- uvx strands-agents-mcp-server@0.2.7

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

# 4. Configure Spec Kit git extension (enable auto-commit if .specify is present)
# Spec Kit is opt-in per project (`specify init`); this only tunes this repo's
# own local .specify/, it does not propagate to ~/.claude or any other project.
SPECKIT_GIT_CONFIG="$SCRIPT_DIR/.specify/extensions/git/git-config.yml"
if [ -f "$SPECKIT_GIT_CONFIG" ]; then
  python3 - "$SPECKIT_GIT_CONFIG" <<'PYEOF'
import sys, re

path = sys.argv[1]
with open(path) as f:
    content = f.read()

content = re.sub(r'^( *default: )false', r'\1true', content, flags=re.MULTILINE)
content = re.sub(r'^( *enabled: )false', r'\1true', content, flags=re.MULTILINE)

with open(path, 'w') as f:
    f.write(content)

print(f"[install] Spec Kit git auto-commit enabled: {path}")
PYEOF
fi

# 5. Install codex-plugin-cc (Codex review/rescue from Claude Code)
if ! claude plugin marketplace list 2>/dev/null | grep -q "openai-codex"; then
  claude plugin marketplace add openai/codex-plugin-cc
else
  claude plugin marketplace update openai-codex >/dev/null 2>&1 || true
fi
if ! claude plugin list 2>/dev/null | grep -q "codex@openai-codex"; then
  claude plugin install codex@openai-codex
fi

echo "Done. ~/.claude and user-scope MCP are synced to this repository state."
