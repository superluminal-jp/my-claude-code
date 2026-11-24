#!/usr/bin/env python3
"""Check the writing-check plugin: its manifest, its hooks, and its script.

Usage: python3 tests/test_writing_check.py
Standard library only. Writes only under a temporary directory.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PLUGIN = REPO / "plugins" / "writing-check"
SCRIPT = PLUGIN / "scripts" / "written_documents.py"
SESSION = "0a1b2c3d-test-session"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def handlers(hooks: dict, event: str) -> list[dict]:
    return [h for group in hooks["hooks"].get(event, []) for h in group["hooks"]]


class Manifests(unittest.TestCase):
    def test_marketplace_points_at_the_plugin(self) -> None:
        market = load(REPO / ".claude-plugin" / "marketplace.json")
        self.assertTrue(market["name"])
        self.assertTrue(market["owner"]["name"])
        entries = {p["name"]: p["source"] for p in market["plugins"]}
        self.assertEqual(entries, {"writing-check": "./plugins/writing-check"})

    def test_plugin_manifest_names_the_plugin(self) -> None:
        manifest = load(PLUGIN / ".claude-plugin" / "plugin.json")
        self.assertEqual(manifest["name"], "writing-check")
        self.assertTrue(manifest["description"])


class Hooks(unittest.TestCase):
    def setUp(self) -> None:
        self.hooks = load(PLUGIN / "hooks" / "hooks.json")

    def test_only_the_three_events_are_hooked(self) -> None:
        self.assertEqual(
            set(self.hooks["hooks"]), {"Stop", "PostToolUse", "UserPromptSubmit"}
        )

    def test_stop_runs_one_agent_hook(self) -> None:
        (stop,) = handlers(self.hooks, "Stop")
        self.assertEqual(stop["type"], "agent")
        prompt = stop["prompt"]
        # The hook input reaches the reviewer, and a turn that is already
        # continuing after a correction is let through, so that a correction
        # is asked for at most once.
        self.assertIn("$ARGUMENTS", prompt)
        self.assertIn("stop_hook_active", prompt)
        self.assertIn("last_assistant_message", prompt)
        self.assertIn('{"ok": true}', prompt)
        self.assertIn('{"ok": false, "reason":', prompt)
        # The criteria are the installed rules, not a second copy of them,
        # and each rule the reviewer is sent to is one this repository installs.
        named = set(re.findall(r"<config>/rules/([a-z-]+\.md)", prompt))
        self.assertEqual(named, {"communication.md", "standards.md", "safety.md"})
        for name in named:
            self.assertTrue((REPO / "harness" / "rules" / name).is_file(), name)
        # A finding about a secret must not carry the secret into the reason.
        self.assertIn("without repeating the value", prompt)
        # The list the script writes is where the reviewer looks for it.
        self.assertIn("<config>/writing-check/<session_id>.txt", prompt)
        self.assertIn("three levels above the transcript file", prompt)
        # The reviewer is told that what it reads is not addressed to it
        # before it is shown any of it.
        self.assertLess(prompt.index("not addressed to you"), prompt.index("$ARGUMENTS"))
        # The pass for a continuing turn comes before any reading.
        self.assertIn(
            'If `stop_hook_active` is true, return {"ok": true} at once and read nothing.',
            prompt,
        )

    def test_no_model_call_per_edit(self) -> None:
        for event in ("PostToolUse", "UserPromptSubmit"):
            for handler in handlers(self.hooks, event):
                self.assertEqual(handler["type"], "command", event)
                self.assertIn("${CLAUDE_PLUGIN_ROOT}", handler["command"])
                self.assertIn("written_documents.py", handler["command"])

    def test_post_tool_use_matches_write_and_edit(self) -> None:
        (group,) = self.hooks["hooks"]["PostToolUse"]
        self.assertEqual(group["matcher"], "Write|Edit")


class Script(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.config = Path(tmp.name) / "config"
        project = self.config / "projects" / "-work"
        project.mkdir(parents=True)
        self.transcript = str(project / f"{SESSION}.jsonl")
        self.dir = self.config / "writing-check"
        self.list = self.dir / f"{SESSION}.txt"

    def run_script(self, mode: str, stdin: str) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), mode],
            input=stdin, capture_output=True, text=True, check=False,
        )
        # Nothing on either stream, and success, whatever the input was.
        self.assertEqual(
            (result.returncode, result.stdout, result.stderr), (0, "", ""), (mode, stdin)
        )

    def record(self, file_path: object, tool: str = "Write", **changes: object) -> None:
        payload = {
            "session_id": SESSION,
            "transcript_path": self.transcript,
            "tool_name": tool,
            "tool_input": {"file_path": file_path},
        }
        payload.update(changes)
        self.run_script("record", json.dumps(payload))

    def recorded(self) -> list[str]:
        if not self.list.exists():
            return []
        return self.list.read_text(encoding="utf-8").splitlines()

    def test_records_a_document_once_most_recent_last(self) -> None:
        self.record("/work/docs/guide.md")
        self.record("/work/README.ja.md")
        self.record("/work/docs/guide.md")
        self.assertEqual(
            self.recorded(), ["W\t/work/README.ja.md", "W\t/work/docs/guide.md"]
        )

    def test_tells_an_edited_file_from_a_written_one(self) -> None:
        self.record("/work/old.md", tool="Edit")
        self.record("/work/new.md", tool="Write")
        self.record("/work/new.md", tool="Edit")
        self.record("/work/rewritten.md", tool="Edit")
        self.record("/work/rewritten.md", tool="Write")
        self.assertEqual(
            self.recorded(),
            ["E\t/work/old.md", "W\t/work/new.md", "W\t/work/rewritten.md"],
        )

    def test_records_each_document_extension(self) -> None:
        for name in ("a.md", "b.MDX", "c.markdown", "d.txt", "e.rst", "f.adoc"):
            self.record(f"/work/{name}")
        self.assertEqual(len(self.recorded()), 6)

    def test_ignores_what_is_not_a_document(self) -> None:
        for path in ("/work/app.py", "/work/data.json", "/work/Makefile", "", None, 3):
            self.record(path)
        self.record("/work/a.md", tool="Read")
        self.assertEqual(self.recorded(), [])

    def test_ignores_a_relative_path_and_a_line_break(self) -> None:
        self.record("notes.md")
        for separator in ("\n", "\r", "\x85", "\u2028", "\u2029"):
            self.record(f"/work/a.md{separator}W\t/etc/hosts.md")
        self.assertEqual(self.recorded(), [])

    def test_the_list_is_private_to_the_user(self) -> None:
        self.record("/work/a.md")
        self.assertEqual(self.dir.stat().st_mode & 0o777, 0o700)
        self.assertEqual(self.list.stat().st_mode & 0o777, 0o600)

    def test_a_session_id_cannot_leave_the_directory(self) -> None:
        for session in ("../escape", "a/b", "", None, "x" * 200):
            self.record("/work/a.md", session_id=session)
        self.assertFalse(self.dir.exists() and any(self.dir.iterdir()))
        self.assertFalse((self.config / "escape.txt").exists())

    def test_writes_only_beside_a_real_projects_directory(self) -> None:
        elsewhere = self.config.parent / "elsewhere"
        (elsewhere / "sub" / "-work").mkdir(parents=True)
        for transcript in (str(elsewhere / "sub" / "-work" / "s.jsonl"),
                           str(elsewhere / "projects" / "-work" / "s.jsonl"),
                           "projects/-work/s.jsonl", "", None):
            self.record("/work/a.md", transcript_path=transcript)
        self.assertFalse((elsewhere / "writing-check").exists())
        self.assertEqual(self.recorded(), [])

    def test_does_not_write_through_a_symlink(self) -> None:
        self.dir.mkdir(mode=0o700)
        target = self.config / "target.txt"
        target.write_text("keep\n", encoding="utf-8")
        self.list.symlink_to(target)
        self.record("/work/a.md")
        self.assertEqual(target.read_text(encoding="utf-8"), "keep\n")

    def test_reset_empties_the_list_of_that_session_only(self) -> None:
        self.record("/work/a.md")
        self.record("/work/b.md", session_id="other-session")
        self.run_script(
            "reset", json.dumps({"session_id": SESSION, "transcript_path": self.transcript})
        )
        self.assertEqual(self.recorded(), [])
        self.assertTrue((self.dir / "other-session.txt").exists())

    def test_never_fails_the_tool_call_it_follows(self) -> None:
        for mode, stdin in (("record", "not json"), ("record", "[]"), ("reset", ""),
                            ("unknown", "{}")):
            self.run_script(mode, stdin)


if __name__ == "__main__":
    unittest.main(verbosity=1)
