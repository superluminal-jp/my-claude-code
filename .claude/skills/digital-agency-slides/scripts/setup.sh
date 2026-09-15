#!/usr/bin/env bash
# Install what scripts/deck.py needs, into a project-local virtual environment.
# Nothing is installed machine-wide.
#
# Usage:
#   bash setup.sh [venv-dir]      # default: .venv in the current directory
#
# Then run the tooling through that environment:
#   .venv/bin/python <skill>/scripts/deck.py lint deck.html

set -euo pipefail

VENV="${1:-.venv}"

command -v python3 >/dev/null || { echo "setup: python3 not found" >&2; exit 1; }

if [ ! -d "$VENV" ]; then
  echo "setup: creating $VENV" >&2
  python3 -m venv "$VENV"
fi

"$VENV/bin/pip" install --quiet --upgrade pip
"$VENV/bin/pip" install --quiet --requirement "$(dirname "$0")/requirements.txt"

# Chromium is what measures the layout, so it must match the Playwright build.
# Honour a preinstalled browser set rather than downloading a second copy.
if [ -n "${PLAYWRIGHT_BROWSERS_PATH:-}" ] && [ -d "${PLAYWRIGHT_BROWSERS_PATH}" ]; then
  echo "setup: using preinstalled browsers at $PLAYWRIGHT_BROWSERS_PATH" >&2
else
  "$VENV/bin/python" -m playwright install chromium
fi

cat >&2 <<MSG

setup: ready.
  Deck tooling:  $VENV/bin/python $(dirname "$0")/deck.py --help
  Japanese text renders and measures correctly only if Noto Sans JP is
  installed on this machine; otherwise pass --font to remap it.
MSG
