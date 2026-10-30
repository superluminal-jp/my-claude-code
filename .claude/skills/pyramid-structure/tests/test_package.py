"""Package-level tests: plugin manifest, eval suite shape, and CLI validation when available.

Run from the skill directory: python3 -B -m unittest discover -s tests -v
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
CASES = sorted(p.parent for p in (ROOT / "evals").glob("*/case.yaml"))


def front_matter(path: Path) -> str:
    m = re.match(r"^---\n(.*?)\n---\n", path.read_text(encoding="utf-8"), re.S)
    return m.group(1) if m else ""


class Manifest(unittest.TestCase):
    def test_manifest_names_and_describes_the_skill(self) -> None:
        manifest = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "pyramid-structure")
        self.assertTrue(manifest["description"])
        self.assertTrue(manifest["version"])

    def test_declares_no_hooks(self) -> None:
        manifest = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertNotIn("hooks", manifest)
        self.assertFalse((ROOT / "hooks").exists())


class EvalSuite(unittest.TestCase):
    def test_suite_has_cases(self) -> None:
        self.assertGreaterEqual(len(CASES), 5)

    def test_every_case_has_prompt_and_graders(self) -> None:
        for case in CASES:
            with self.subTest(case=case.name):
                self.assertTrue((case / "prompt.md").is_file())
                self.assertTrue(list((case / "graders").glob("*.md")))

    def test_every_case_checks_that_the_skill_fired(self) -> None:
        for case in CASES:
            with self.subTest(case=case.name):
                fronts = [front_matter(g) for g in (case / "graders").glob("*.md")]
                self.assertTrue(
                    any("type: tool_used" in f and "tool: Skill" in f and "pyramid-structure" in f for f in fronts)
                )

    def test_every_case_checks_that_the_checker_ran_in_the_plugin_arm_only(self) -> None:
        for case in CASES:
            with self.subTest(case=case.name):
                fronts = [front_matter(g) for g in (case / "graders").glob("*.md")]
                self.assertTrue(
                    any("tool: Bash" in f and "check" in f and "py" in f and "arm: with-only" in f for f in fronts)
                )

    def test_no_case_pins_the_model_under_test(self) -> None:
        # The model under test is chosen per run with --model, so one suite measures any model.
        for case in CASES:
            with self.subTest(case=case.name):
                self.assertNotRegex(front_matter(case / "prompt.md"), r"(?m)^model:")
                self.assertNotRegex((case / "case.yaml").read_text(encoding="utf-8"), r"(?m)^\s*model:")


@unittest.skipUnless(shutil.which("claude"), "Claude Code CLI not installed")
class CliValidation(unittest.TestCase):
    def validate(self, path: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["claude", "plugin", "validate", "--strict", str(path)],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )

    def test_cli_accepts_the_plugin(self) -> None:
        result = self.validate(ROOT)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_cli_accepts_skill_md_as_a_skill(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            target = Path(d) / "skills" / "pyramid-structure"
            shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns(".claude-plugin", "__pycache__"))
            result = self.validate(Path(d) / "skills")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
