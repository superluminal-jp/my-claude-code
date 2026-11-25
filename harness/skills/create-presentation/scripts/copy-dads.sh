#!/usr/bin/env bash
# Copy into a presentation directory the DADS files its HTML files link, from
# the copy this skill carries, so that the material opens and can be shared
# without a clone of DADS.
#
# Usage: bash copy-dads.sh <presentation-directory>
# Replaces <presentation-directory>/dads/ as a whole: it holds the license,
# global.css, and each linked component file, and nothing to be edited.

set -euo pipefail

if [ $# -ne 1 ] || [ ! -d "$1" ]; then
  echo "Usage: bash copy-dads.sh <presentation-directory>" >&2
  exit 2
fi

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE="$SKILL_DIR/assets/dads"
TARGET="$(cd "$1" && pwd)/dads"

refs="$(cat "$1"/*.html 2>/dev/null | grep -oE 'dads/components/[a-z0-9-]+/[A-Za-z0-9_.-]+\.(css|js)' | LC_ALL=C sort -u || true)"
if [ -z "$refs" ]; then
  echo "No HTML file in $1 links a DADS component." >&2
  exit 1
fi

stage="$(mktemp -d "$(dirname "$TARGET")/.dads-new.XXXXXX")"
trap 'rm -rf "$stage"' EXIT
cp "$SOURCE/LICENSE" "$SOURCE/global.css" "$stage/"
missing=0
for ref in $refs; do
  rel="${ref#dads/}"
  if [ ! -f "$SOURCE/$rel" ]; then
    echo "Not in this skill's copy of DADS: $rel" >&2
    missing=1
    continue
  fi
  mkdir -p "$stage/$(dirname "$rel")"
  cp "$SOURCE/$rel" "$stage/$rel"
done
[ "$missing" -eq 0 ] || exit 1

rm -rf "$TARGET"
mv "$stage" "$TARGET"
trap - EXIT
echo "Copied $(printf '%s\n' $refs | wc -l | tr -d ' ') DADS file(s), global.css, and the license to $TARGET"
