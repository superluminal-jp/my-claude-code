"""Shared helpers: run the bundled scripts as a person would, in a temporary folder."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
SCRIPTS = SKILL / "scripts"
TEMPLATES = SKILL / "templates"


def run(script: str, *args: str) -> subprocess.CompletedProcess:
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    return subprocess.run(
        [sys.executable, "-B", str(SCRIPTS / script), *args],
        capture_output=True, text=True, env=env, check=False,
    )


def snapshot(root: Path) -> dict:
    """Every path under root with its content, to show that nothing changed."""
    found = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            found[relative] = ("link", os.readlink(path))
        elif path.is_dir():
            found[relative] = ("dir", None)
        else:
            found[relative] = ("file", path.read_bytes())
    return found


class TempRepo(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name).resolve() / "repo"
        self.root.mkdir()

    def scaffold(self, *args: str) -> subprocess.CompletedProcess:
        return run("scaffold.py", args[0], "--root", str(self.root), *args[1:])

    def check(self, *args: str) -> subprocess.CompletedProcess:
        return run("check_artifacts.py", "--root", str(self.root), *args)

    def check_json(self, *args: str) -> tuple[int, dict]:
        result = self.check("--format", "json", *args)
        return result.returncode, json.loads(result.stdout)

    def names(self, folder: Path) -> list[str]:
        return sorted(p.name for p in folder.iterdir())
