#!/usr/bin/env bash
# Copy the managed configuration in harness/ into ~/.claude/.
#
# Managed paths: CLAUDE.md, rules/, skills/, agents/. Each is replaced so that
# it matches harness/ exactly; a skill, rule, or agent removed here is removed
# there. Everything else under ~/.claude/ (settings.json, plugins, projects,
# ...) is left untouched.
#
# Usage: bash install.sh
# Set CLAUDE_CONFIG_DIR to install somewhere other than ~/.claude.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="$SCRIPT_DIR/harness"
TARGET_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
MANAGED_PATHS=(CLAUDE.md rules skills agents)

for rel in "${MANAGED_PATHS[@]}"; do
  if [ ! -e "$SOURCE_DIR/$rel" ]; then
    echo "Missing source: $SOURCE_DIR/$rel" >&2
    exit 1
  fi
done

mkdir -p "$TARGET_DIR"

# skills/synced/ sits inside a managed path but belongs to the Claude app,
# which syncs its own skills there. Move it aside while skills/ is replaced
# and put it back afterwards, also when a step in between fails.
# A run that was killed before it could put skills/synced/ back left it in a
# .install-keep.* directory. Recover it first, unless a newer one exists.
for stranded in "$TARGET_DIR"/.install-keep.*; do
  [ -d "$stranded" ] || continue
  if [ -e "$stranded/synced" ] && [ ! -e "$TARGET_DIR/skills/synced" ]; then
    mkdir -p "$TARGET_DIR/skills"
    mv "$stranded/synced" "$TARGET_DIR/skills/synced"
  fi
  rmdir "$stranded" 2>/dev/null || echo "Left in place, not empty: $stranded" >&2
done

keep_dir="$(mktemp -d "$TARGET_DIR/.install-keep.XXXXXX")"
restore_synced() {
  if [ -e "$keep_dir/synced" ]; then
    mkdir -p "$TARGET_DIR/skills"
    mv "$keep_dir/synced" "$TARGET_DIR/skills/synced"
  fi
  rmdir "$keep_dir" 2>/dev/null || true
}
# Runs on every exit, so a step that fails below still puts skills/synced/ back.
trap restore_synced EXIT
if [ -e "$TARGET_DIR/skills/synced" ]; then
  mv "$TARGET_DIR/skills/synced" "$keep_dir/synced"
fi

for rel in "${MANAGED_PATHS[@]}"; do
  rm -rf "${TARGET_DIR:?}/$rel"
  cp -R "$SOURCE_DIR/$rel" "$TARGET_DIR/$rel"
done
# Drop what is not configuration: Finder metadata, and the marker directories
# Claude Code leaves in a directory it has worked in.
find "$TARGET_DIR/rules" "$TARGET_DIR/skills" "$TARGET_DIR/agents" -name .DS_Store -delete
find "$TARGET_DIR/rules" "$TARGET_DIR/skills" "$TARGET_DIR/agents" -type d -name .claude -prune -exec rm -rf {} +

restore_synced
trap - EXIT

echo "Installed ${MANAGED_PATHS[*]} from $SOURCE_DIR to $TARGET_DIR"
