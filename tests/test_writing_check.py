#!/usr/bin/env python3
"""Check the writing-check plugin: its manifest, its hook, and its script.

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
PLUGIN = REPO / "harness" / "plugins" / "writing-check"
SCRIPT = PLUGIN / "scripts" / "remind.py"
REMINDER = PLUGIN / "reminder.md"


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
        self.assertEqual(entries, {"writing-check": "./harness/plugins/writing-check"})

    def test_plugin_manifest_names_the_plugin(self) -> None:
        manifest = load(PLUGIN / ".claude-plugin" / "plugin.json")
        self.assertEqual(manifest["name"], "writing-check")
        self.assertTrue(manifest["description"])


class Hooks(unittest.TestCase):
    def setUp(self) -> None:
        self.hooks = load(PLUGIN / "hooks" / "hooks.json")

    def test_only_a_submitted_prompt_is_hooked(self) -> None:
        # The answer is not reviewed when the turn ends, so no Stop hook and
        # no list of written documents for one to read.
        self.assertEqual(set(self.hooks["hooks"]), {"UserPromptSubmit"})

    def test_a_prompt_brings_the_reminder_without_a_model_call(self) -> None:
        (handler,) = handlers(self.hooks, "UserPromptSubmit")
        self.assertEqual(handler["type"], "command")
        self.assertEqual(
            handler["command"], 'python3 "${CLAUDE_PLUGIN_ROOT}/scripts/remind.py"'
        )


class Reminder(unittest.TestCase):
    """The text put before Claude when a prompt is submitted."""

    def remind(self, stdin: str, script: Path = SCRIPT) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(script)],
            input=stdin, capture_output=True, text=True, check=False,
        )

    def test_the_reminder_reaches_claude_as_added_context(self) -> None:
        # The reminder does not depend on the hook input, so a broken input
        # still brings it.
        for stdin in (json.dumps({"session_id": "s", "prompt": "hello"}), "not json", ""):
            result = self.remind(stdin)
            self.assertEqual((result.returncode, result.stderr), (0, ""), stdin)
            self.assertEqual(
                json.loads(result.stdout),
                {
                    "hookSpecificOutput": {
                        "hookEventName": "UserPromptSubmit",
                        "additionalContext": REMINDER.read_text(encoding="utf-8").strip(),
                    }
                },
            )

    def test_a_missing_reminder_does_not_disturb_the_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            scripts = Path(tmp) / "plugin" / "scripts"
            scripts.mkdir(parents=True)
            copy = scripts / SCRIPT.name
            copy.write_bytes(SCRIPT.read_bytes())
            result = self.remind("{}", script=copy)
        self.assertEqual((result.returncode, result.stdout, result.stderr), (0, "", ""))

    def test_the_reminder_points_at_the_rules_and_stays_short(self) -> None:
        text = REMINDER.read_text(encoding="utf-8")
        # It is read with every prompt, so its size is a cost of every turn.
        self.assertLessEqual(len(text), 1200)
        # The criteria stay in the installed rules: the reminder names them,
        # and each is one this repository installs.
        self.assertIn("field of the work from the conversation", text)
        named = set(re.findall(r"rules/([a-z-]+\.md)", text))
        self.assertEqual(named, {"communication.md", "standards.md", "safety.md"})
        for name in named:
            self.assertTrue((REPO / "harness" / "rules" / name).is_file(), name)

    def test_the_reminder_does_not_promise_a_review(self) -> None:
        # No reviewer runs when the turn ends, so the reminder must not say one does.
        self.assertNotIn("reviewer", REMINDER.read_text(encoding="utf-8").lower())


if __name__ == "__main__":
    unittest.main(verbosity=1)
