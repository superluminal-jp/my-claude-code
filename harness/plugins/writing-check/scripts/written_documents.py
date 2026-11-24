#!/usr/bin/env python3
"""Keep the list of documents a Claude Code session wrote in the current turn.

Called by the hooks of the writing-check plugin with the hook input as JSON
on standard input:

  written_documents.py record   after Write or Edit: add the file to the list
  written_documents.py reset    when a prompt is submitted: empty the list

The list is <config>/writing-check/<session_id>.txt, where <config> is the
Claude configuration directory, taken from the input's `transcript_path`
(<config>/projects/<project>/<session>.jsonl). The reviewer that runs when
the turn ends derives the same path from the same input. Each line is a mode,
a tab, and an absolute path, the most recently written last:

  W  the whole file was written in this turn
  E  an existing file was edited in place; its other text may be older

The script prints nothing and always exits 0, because a failure here must not
disturb the tool call or the prompt it follows. Standard library only.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

DOCUMENT_SUFFIXES = {".md", ".mdx", ".markdown", ".txt", ".rst", ".adoc"}
SESSION_ID_RE = re.compile(r"[A-Za-z0-9_-]{1,128}")
MODES = {"Write": "W", "Edit": "E"}


def list_path(payload: object) -> Path | None:
    """Return the list file for the session, or None when it cannot be placed."""
    if not isinstance(payload, dict):
        return None
    session_id = payload.get("session_id")
    transcript = payload.get("transcript_path")
    if not isinstance(session_id, str) or not SESSION_ID_RE.fullmatch(session_id):
        return None
    if not isinstance(transcript, str) or not os.path.isabs(transcript):
        return None
    projects = Path(transcript).parent.parent
    if projects.name != "projects" or not projects.is_dir():
        return None
    return projects.parent / "writing-check" / f"{session_id}.txt"


def document_entry(payload: dict) -> tuple[str, str] | None:
    """Return (mode, path) when the tool wrote a document, else None."""
    mode = MODES.get(payload.get("tool_name"))  # type: ignore[arg-type]
    tool_input = payload.get("tool_input")
    if mode is None or not isinstance(tool_input, dict):
        return None
    file_path = tool_input.get("file_path")
    if not isinstance(file_path, str) or not os.path.isabs(file_path):
        return None
    # One entry is one line, so a path that would break the line is left out.
    if any(ord(char) < 32 or char in "\x85  " for char in file_path):
        return None
    if Path(file_path).suffix.lower() not in DOCUMENT_SUFFIXES:
        return None
    return mode, file_path


def record(payload: object) -> None:
    target = list_path(payload)
    entry = document_entry(payload) if target is not None else None  # type: ignore[arg-type]
    if target is None or entry is None:
        return
    mode, file_path = entry
    target.parent.mkdir(mode=0o700, exist_ok=True)
    flags = os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW
    with os.fdopen(os.open(target, flags, 0o600), "r+", encoding="utf-8") as handle:
        entries: dict[str, str] = {}
        for line in handle.read().split("\n"):
            old_mode, tab, old_path = line.partition("\t")
            if tab and old_mode in ("W", "E"):
                entries[old_path] = old_mode
        # A file written whole in this turn stays W when it is edited later.
        if entries.pop(file_path, mode) == "W":
            mode = "W"
        entries[file_path] = mode
        handle.seek(0)
        handle.truncate()
        handle.writelines(f"{m}\t{p}\n" for p, m in entries.items())


def reset(payload: object) -> None:
    target = list_path(payload)
    if target is not None:
        target.unlink(missing_ok=True)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        mode = sys.argv[1] if len(sys.argv) > 1 else ""
        if mode == "record":
            record(payload)
        elif mode == "reset":
            reset(payload)
    except Exception:  # noqa: BLE001 - see the module docstring
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
