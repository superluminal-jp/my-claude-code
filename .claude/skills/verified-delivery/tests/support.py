"""Helpers shared by this skill's tests (not a test module itself)."""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path


def temp_dir(case: unittest.TestCase) -> Path:
    """A new directory that is removed when the test ends."""
    directory = Path(tempfile.mkdtemp())
    case.addCleanup(shutil.rmtree, directory)
    return directory


def temp_file(case: unittest.TestCase, name: str, content: str | dict) -> str:
    """Writes ``content`` (JSON when it is not a string) to a new file and
    returns its path; the file is removed when the test ends."""
    path = temp_dir(case) / name
    path.write_text(content if isinstance(content, str) else json.dumps(content, ensure_ascii=False), encoding="utf-8")
    return str(path)
