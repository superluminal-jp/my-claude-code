#!/usr/bin/env bash
# Clone the DADS HTML components (デジタル庁デザインシステム コードスニペット HTML版)
# next to this directory, at the tag the files here were written against.
#
# Usage: bash presentation/setup.sh

set -euo pipefail

DADS_URL="https://github.com/digital-go-jp/design-system-example-components-html.git"
DADS_TAG="v20261118"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="$ROOT_DIR/design-system-example-components-html"

if [ -e "$DEST" ]; then
  current="$(git -C "$DEST" describe --tags --exact-match 2>/dev/null || true)"
  if [ "$current" = "$DADS_TAG" ]; then
    echo "DADS $DADS_TAG is already at $DEST"
    exit 0
  fi
  echo "$DEST exists but is not at $DADS_TAG (found: ${current:-unknown})." >&2
  echo "Remove it and run this script again, or update DADS_TAG here." >&2
  exit 1
fi

git clone --depth 1 --branch "$DADS_TAG" "$DADS_URL" "$DEST"
echo "Cloned DADS $DADS_TAG to $DEST"
