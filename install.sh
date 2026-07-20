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

# 1b. Deploy AGENTS.md to Codex CLI's global config (mirrors the .claude/ sync
# above). Source is .codex/AGENTS.md, not this repo's root AGENTS.md — the
# root file is reserved for content specific to working in this repository
# (read by Codex as project-scope, never expanded); the shared/user-scope
# prose lives under .codex/ alongside the rest of the Codex source tree (spec
# 014 research.md R0/R1).
CODEX_TARGET_DIR="$HOME/.codex"
AGENTS_MD_SRC="$SCRIPT_DIR/.codex/AGENTS.md"
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
# advisor/domain-model/ubiquitous-language were intentionally removed from
# .claude/skills/ in 33c82eb ("prune rules/hooks" — "unused after the
# restructure"); listing them here would make sync_path("skills") delete
# them from ~/.claude/skills on every install.sh run while this list still
# tried to symlink them, producing broken links (spec 014 research.md R0/R2).
CUSTOM_SKILLS="adr clarifier coder digital-agency-frontend minto-builder minto-reviewer minto-rewriter"
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
    ("prompt-secret-adapter.sh", "UserPromptSubmit", None),
]

import os
lines = [begin]
for filename, event, matcher in ADAPTERS:
    script_path = os.path.join(hooks_dir, filename)
    if not os.path.isfile(script_path):
        continue
    lines.append(f"[[hooks.{event}]]")
    # UserPromptSubmit does not support matchers; Codex ignores one if present.
    if matcher is not None:
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

# 1e. Deploy repository-managed Codex command rules without touching Codex's
# own default.rules or any other user-owned rules.
CODEX_RULES_SRC="$SCRIPT_DIR/.codex/rules/guardrails.rules"
CODEX_RULES_DST="$CODEX_TARGET_DIR/rules/guardrails.rules"
if [ -f "$CODEX_RULES_SRC" ]; then
  mkdir -p "$(dirname "$CODEX_RULES_DST")"
  cp "$CODEX_RULES_SRC" "$CODEX_RULES_DST"
  echo "Synced Codex guardrail rules -> $CODEX_RULES_DST"
fi

# 1f. Deploy the compatibility custom prompt. Codex custom prompts are
# deprecated upstream in favor of skills, but remain supported and are the
# required counterpart for this repository's existing /verify-config command.
CODEX_PROMPT_SRC="$SCRIPT_DIR/.codex/prompts/verify-config.md"
CODEX_PROMPT_DST="$CODEX_TARGET_DIR/prompts/verify-config.md"
if [ -f "$CODEX_PROMPT_SRC" ]; then
  mkdir -p "$(dirname "$CODEX_PROMPT_DST")"
  cp "$CODEX_PROMPT_SRC" "$CODEX_PROMPT_DST"
  echo "Synced Codex verify-config prompt -> $CODEX_PROMPT_DST"
fi

# 1g. Mirror the repository MCP catalog into a separate marker-delimited
# block in Codex's config.toml. Header values must be environment references;
# actual credential values are never copied into config.toml.
CODEX_MCP_BEGIN="# >>> my-claude-code managed MCP servers (do not edit by hand; see install.sh) >>>"
CODEX_MCP_END="# <<< my-claude-code managed MCP servers <<<"
mkdir -p "$(dirname "$CODEX_CONFIG")"
touch "$CODEX_CONFIG"
python3 - "$SCRIPT_DIR/.mcp.json" "$CODEX_CONFIG" "$CODEX_MCP_BEGIN" "$CODEX_MCP_END" <<'PYEOF'
import json
import os
import re
import sys

catalog_path, config_path, begin, end = sys.argv[1:5]
with open(catalog_path) as f:
    servers = json.load(f)["mcpServers"]

with open(config_path) as f:
    existing = f.readlines()

kept = []
skipping = False
for line in existing:
    if line.strip() == begin:
        skipping = True
        continue
    if line.strip() == end:
        skipping = False
        continue
    if not skipping:
        kept.append(line)

while kept and not kept[-1].strip():
    kept.pop()

server_header = re.compile(
    r'^\s*\[mcp_servers\.(?:"([^"]+)"|([A-Za-z0-9_-]+))(?:\.[^]]+)?\]\s*(?:#.*)?$'
)
non_managed_servers = set()
for line in kept:
    match = server_header.match(line)
    if match:
        non_managed_servers.add(match.group(1) or match.group(2))

def quote(value):
    return json.dumps(value)

managed = [begin]
for name, definition in servers.items():
    if name in non_managed_servers:
        print(f"Preserved non-managed Codex MCP server '{name}'; managed catalog entry skipped")
        continue
    managed.append(f"[mcp_servers.{name}]")
    if definition.get("type") == "http":
        managed.append(f"url = {quote(definition['url'])}")
        env_headers = {}
        for header, value in definition.get("headers", {}).items():
            match = re.fullmatch(r"\$\{([A-Z][A-Z0-9_]*)\}", value)
            if not match:
                raise SystemExit(f"Refusing non-environment MCP header for {name}")
            env_headers[header] = match.group(1)
        if env_headers:
            pairs = ", ".join(f"{quote(key)} = {quote(value)}" for key, value in env_headers.items())
            managed.append(f"env_http_headers = {{ {pairs} }}")
            if any(not os.environ.get(variable) for variable in env_headers.values()):
                managed.append("enabled = false")
    else:
        managed.append(f"command = {quote(definition['command'])}")
        if definition.get("args"):
            managed.append(f"args = {json.dumps(definition['args'])}")
        if definition.get("env"):
            managed.append(f"[mcp_servers.{name}.env]")
            for key, value in definition["env"].items():
                managed.append(f"{key} = {quote(value)}")
    managed.append("")
managed.append(end)

with open(config_path, "w") as f:
    if kept:
        f.writelines(kept)
        f.write("\n\n")
    f.write("\n".join(managed) + "\n")
PYEOF

if [ -z "${GOOGLE_DEV_KNOWLEDGE_API_KEY:-}" ]; then
  echo "Configured google-developer-knowledge MCP as disabled: GOOGLE_DEV_KNOWLEDGE_API_KEY is not set" >&2
fi
echo "Synced Codex MCP catalog -> $CODEX_CONFIG"

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

echo "Codex hook trust: start Codex and use /hooks to review and trust new or changed user hooks before relying on guardrails."
echo "Done. ~/.claude and user-scope MCP are synced to this repository state."
