#!/usr/bin/env bash
# Copy the part of the DADS HTML components (デジタル庁デザインシステム
# コードスニペット HTML版) that the create-presentation skill uses into the
# skill, from one tagged release. Run it to move the skill to another release,
# then commit the result.
#
# Usage: bash scripts/vendor-dads.sh [tag]
# Writes harness/skills/create-presentation/assets/dads/ and nothing else;
# clones into a temporary directory, which it removes.

set -euo pipefail

DADS_URL="https://github.com/digital-go-jp/design-system-example-components-html.git"
DADS_TAG="${1:-v20261118}"
# The components references/components.md marks as usable in either format.
COMPONENTS=(
  accordion blockquote breadcrumb button chip-label description-list
  disclosure divider heading horizontal-menu image link list menu-list
  notice-block notification-banner page-navigation resource-list
  step-navigation tab table toc
)

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="$REPO_DIR/harness/skills/create-presentation/assets/dads"
WORK="$(mktemp -d "${TMPDIR:-/tmp}/vendor-dads.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT

git clone --quiet --depth 1 --branch "$DADS_TAG" "$DADS_URL" "$WORK/clone" 2>/dev/null
commit="$(git -C "$WORK/clone" rev-parse HEAD)"

stage="$WORK/dads"
mkdir -p "$stage/components"
cp "$WORK/clone/LICENSE" "$WORK/clone/src/global.css" "$stage/"
for name in "${COMPONENTS[@]}"; do
  src="$WORK/clone/src/components/$name"
  [ -d "$src" ] || { echo "No component $name in $DADS_TAG" >&2; exit 1; }
  mkdir "$stage/components/$name"
  # The stylesheet, the sample HTML to copy markup from, and the script a
  # component needs to work; not stories, tests, or documentation.
  for file in "$src"/*.css "$src"/*.html "$src"/*.js; do
    [ -e "$file" ] || continue
    case "$(basename "$file")" in
      *.stories.* | *.test.* | *.vrt.*) continue ;;
    esac
    cp "$file" "$stage/components/$name/"
  done
done

printf '%s\n%s\n%s\n' "$DADS_URL" "$DADS_TAG" "$commit" >"$stage/SOURCE"
(
  cd "$stage"
  find . -type f ! -name SHA256SUMS ! -name SOURCE | sed 's|^\./||' | LC_ALL=C sort \
    | while IFS= read -r name; do
      python3 -c 'import hashlib,sys; print(hashlib.sha256(open(sys.argv[1],"rb").read()).hexdigest() + "  " + sys.argv[1])' "$name"
    done >SHA256SUMS
)

rm -rf "$DEST"
mv "$stage" "$DEST"
echo "Copied DADS $DADS_TAG ($commit) to $DEST"
