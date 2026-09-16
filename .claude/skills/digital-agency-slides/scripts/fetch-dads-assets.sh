#!/usr/bin/env bash
# Resolve the Digital Agency Design System's official HTML/CSS assets into a
# deck workspace at task time. Nothing official is vendored in this skill, so
# a deck always builds against the current upstream reference implementation.
#
# Usage:
#   bash fetch-dads-assets.sh <deck-dir> [component ...]
#
#   <deck-dir>   Directory holding the deck. Assets land in <deck-dir>/dads/.
#   component    Official component directory names (table, list, divider, ...).
#                Defaults to the set deck-template.html links.
#
# Writes:
#   <deck-dir>/dads/global.css                       design tokens + type utilities
#   <deck-dir>/dads/components/<name>/<name>.css     one per requested component
#   <deck-dir>/dads/SOURCE.md                        upstream URL, commit, licence
#
# The upstream code is MIT licensed. Reusing it unmodified in a published
# artifact requires the source notice reproduced in SOURCE.md; see
# references/asset-sourcing.md.

set -euo pipefail

REPO_URL="https://github.com/digital-go-jp/design-system-example-components-html.git"
REPO_WEB="https://github.com/digital-go-jp/design-system-example-components-html"
DEFAULT_COMPONENTS=(table list divider chip-label)

usage() {
  sed -n '2,25p' "$0" | sed 's/^# \{0,1\}//'
  exit "${1:-0}"
}

[ $# -ge 1 ] || usage 1
case "$1" in -h|--help) usage 0 ;; esac

DECK_DIR="$1"
shift
if [ $# -gt 0 ]; then
  COMPONENTS=("$@")
else
  COMPONENTS=("${DEFAULT_COMPONENTS[@]}")
fi

[ -d "$DECK_DIR" ] || { echo "fetch-dads-assets: no such directory: $DECK_DIR" >&2; exit 1; }

DADS_DIR="$DECK_DIR/dads"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

echo "fetch-dads-assets: cloning $REPO_WEB" >&2
git clone --quiet --depth 1 "$REPO_URL" "$WORK/src"

SRC="$WORK/src/src"
[ -f "$SRC/global.css" ] || {
  echo "fetch-dads-assets: upstream layout changed — src/global.css is gone." >&2
  echo "  Inspect $REPO_WEB and update this script before continuing." >&2
  exit 1
}

COMMIT="$(git -C "$WORK/src" rev-parse HEAD)"
FETCHED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

mkdir -p "$DADS_DIR/components"
cp "$SRC/global.css" "$DADS_DIR/global.css"
echo "  global.css" >&2

MISSING=()
for component in "${COMPONENTS[@]}"; do
  src_css="$SRC/components/$component/$component.css"
  if [ -f "$src_css" ]; then
    mkdir -p "$DADS_DIR/components/$component"
    cp "$src_css" "$DADS_DIR/components/$component/$component.css"
    echo "  components/$component/$component.css" >&2
  else
    MISSING+=("$component")
  fi
done

{
  echo "# Official DADS assets in this deck"
  echo
  echo "Fetched by \`scripts/fetch-dads-assets.sh\`. Do not hand-edit these files —"
  echo "re-run the script to refresh them."
  echo
  echo "- Source: <$REPO_WEB>"
  echo "- Commit: \`$COMMIT\`"
  echo "- Fetched: $FETCHED_AT"
  echo "- Licence: MIT (see the repository's LICENSE)"
  echo
  echo "## Attribution"
  echo
  echo "UI built by modifying these files needs no visible source notice. Publishing"
  echo "them unmodified does:"
  echo
  echo "> 出典：デジタル庁デザインシステムウェブサイト https://design.digital.go.jp/dads/ およびデジタル庁GitHub https://github.com/digital-go-jp"
  echo
  echo "Never present the result as a Digital Agency product or as endorsed by the"
  echo "Digital Agency."
} > "$DADS_DIR/SOURCE.md"

if [ ${#MISSING[@]} -gt 0 ]; then
  echo "fetch-dads-assets: not found upstream: ${MISSING[*]}" >&2
  echo "  Available components:" >&2
  (cd "$SRC/components" && ls -1) | sed 's/^/    /' >&2
  exit 1
fi

echo "fetch-dads-assets: wrote $DADS_DIR (commit ${COMMIT:0:12})" >&2
