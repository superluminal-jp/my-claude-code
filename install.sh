#!/usr/bin/env bash
# Copy the managed configuration in harness/ into ~/.claude/.
#
# Managed paths: CLAUDE.md, rules/, agents/. Each is replaced so that it
# matches harness/ exactly; a rule or agent removed here is removed there.
# Everything else under ~/.claude/ (settings.json, skills/, plugins,
# projects, ...) is left untouched.
#
# harness/plugins/ is not copied: ~/.claude/plugins/ holds Claude Code's own
# record of installed plugins. Claude Code reads the plugin in place once it
# is installed with `claude plugin install`; see README.md.
#
# Usage: bash install.sh
# Set CLAUDE_CONFIG_DIR to install somewhere other than ~/.claude.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="$SCRIPT_DIR/harness"
TARGET_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
MANAGED_PATHS=(CLAUDE.md rules agents)

for rel in "${MANAGED_PATHS[@]}"; do
  if [ ! -e "$SOURCE_DIR/$rel" ]; then
    echo "Missing source: $SOURCE_DIR/$rel" >&2
    exit 1
  fi
done

mkdir -p "$TARGET_DIR"

# Build the new copy beside the target first, so that a copy that fails
# leaves the installed files as they were.
stage_dir="$(mktemp -d "$TARGET_DIR/.install-new.XXXXXX")"
trap 'rm -rf "$stage_dir"' EXIT
for rel in "${MANAGED_PATHS[@]}"; do
  cp -R "$SOURCE_DIR/$rel" "$stage_dir/$rel"
done
# Drop what is not configuration: Finder metadata, and the marker directories
# Claude Code leaves in a directory it has worked in.
find "$stage_dir" -name .DS_Store -delete
find "$stage_dir" -type d -name .claude -prune -exec rm -rf {} +

for rel in "${MANAGED_PATHS[@]}"; do
  rm -rf "${TARGET_DIR:?}/$rel"
  mv "$stage_dir/$rel" "$TARGET_DIR/$rel"
done

echo "Installed ${MANAGED_PATHS[*]} from $SOURCE_DIR to $TARGET_DIR"
