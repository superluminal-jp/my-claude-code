#!/usr/bin/env bash
# note_write_guard.py unit test runner
# Usage: bash tests/run-note-write-guard.sh
#
# Plain stdlib unittest run over the apple-notes skill's note_write_guard.py
# -- it does not call osascript, so it needs no model, no network, no
# dependencies, and no macOS.
#
# The Apple Events layer (write_note.js's --overwrite-stdin/--delete) is not
# covered here -- it can only be validated on a Mac with Notes.app and an
# Automation grant. See specs/033-apple-notes-reminders-port/quickstart.md.
#
# Exit codes: 0 = all tests passed; 1 = at least one test failed.

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$REPO_ROOT" || exit 1

python3 -m unittest discover -s tests -p "test_note_write_guard.py" -v
