#!/usr/bin/env python3
"""Show that each rule of tests/assert_skill_contract.py can fail.

Every test builds a small valid skill tree under a temporary directory,
breaks exactly one thing, and expects the contract check to report the rule
that covers it. A rule that never fires here would be a check that cannot
tell a broken skill from a sound one.

Run: python3 -B -m unittest tests/test_skill_contract.py
Temporary directories come from tempfile, which honors $TMPDIR, so the tests
run inside the Bash sandbox.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

CONTRACT = Path(__file__).resolve().parent / "assert_skill_contract.py"

VALID = """---
name: {name}
description: Does one thing for the test. Use when the test asks. Do not use otherwise.
metadata:
  kind: {kind}
  permission: read_only
  sandbox: inside
---

# Title

One sentence of purpose.
{extra}
## Done when

- The thing is done.
"""


def write_skill(root: Path, name: str, kind: str = "worker", extra: str = "", text: str | None = None) -> Path:
    directory = root / name
    directory.mkdir(parents=True)
    body = text if text is not None else VALID.format(name=name, kind=kind, extra=extra)
    (directory / "SKILL.md").write_text(body, encoding="utf-8")
    return directory


def run_contract(root: Path) -> tuple[int, str]:
    proc = subprocess.run([sys.executable, "-B", str(CONTRACT), str(root)], capture_output=True, text=True)
    return proc.returncode, proc.stderr


class ContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="skill-contract-")
        self.root = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def assert_fails(self, rule: str, needle: str = "") -> None:
        code, err = run_contract(self.root)
        self.assertEqual(code, 1, err)
        lines = [line for line in err.splitlines() if line.startswith(f"FAIL {rule} ")]
        self.assertTrue(lines, f"expected a {rule} failure, got:\n{err}")
        if needle:
            self.assertTrue(any(needle in line for line in lines), f"no {rule} line mentions {needle!r}:\n{err}")

    def test_a_valid_tree_passes(self) -> None:
        write_skill(self.root, "do-thing")
        code, err = run_contract(self.root)
        self.assertEqual(code, 0, err)

    def test_c01_name_differs_from_directory(self) -> None:
        write_skill(self.root, "do-thing", text=VALID.format(name="other-thing", kind="worker", extra=""))
        self.assert_fails("C-01")

    def test_c01_name_is_not_hyphenated_lowercase(self) -> None:
        write_skill(self.root, "Do_Thing")
        self.assert_fails("C-01")

    def test_c02_description_over_the_specification_limit(self) -> None:
        long = "Use when asked. Do not use otherwise. " + "x" * 1024
        write_skill(self.root, "do-thing", text=VALID.format(name="do-thing", kind="worker", extra="").replace(
            "Does one thing for the test. Use when the test asks. Do not use otherwise.", long))
        self.assert_fails("C-02", "1..1024")

    def test_c02_description_without_an_exclusion(self) -> None:
        write_skill(self.root, "do-thing", text=VALID.format(name="do-thing", kind="worker", extra="").replace(
            " Do not use otherwise.", ""))
        self.assert_fails("C-02", "exclusion")

    def test_c03_when_to_use_and_model_are_not_allowed(self) -> None:
        text = VALID.format(name="do-thing", kind="worker", extra="").replace(
            "metadata:\n", "when_to_use: when asked\nmodel: haiku\nmetadata:\n")
        write_skill(self.root, "do-thing", text=text)
        self.assert_fails("C-03", "when_to_use")
        self.assert_fails("C-03", "model")

    def test_c04_undefined_kind_and_missing_sandbox(self) -> None:
        text = VALID.format(name="do-thing", kind="helper", extra="").replace("  sandbox: inside\n", "")
        write_skill(self.root, "do-thing", text=text)
        self.assert_fails("C-04", "kind")
        self.assert_fails("C-04", "sandbox")

    def test_c04_network_without_hosts(self) -> None:
        text = VALID.format(name="do-thing", kind="worker", extra="").replace("sandbox: inside", "sandbox: network")
        write_skill(self.root, "do-thing", text=text)
        self.assert_fails("C-04", "network-hosts")

    def test_c05_one_block_of_dense_prose(self) -> None:
        write_skill(self.root, "do-thing", extra="\n" + " ".join(["word"] * 151) + "\n")
        self.assert_fails("C-05", "151 words")

    def test_c06_no_done_when_section(self) -> None:
        text = VALID.format(name="do-thing", kind="worker", extra="").replace("## Done when", "## Notes")
        write_skill(self.root, "do-thing", text=text)
        self.assert_fails("C-06", "Done when")

    def test_c06_reference_not_named_in_skill(self) -> None:
        directory = write_skill(self.root, "do-thing", extra="\n## Bundled files\n\nNone named.\n")
        (directory / "references").mkdir()
        (directory / "references" / "detail.md").write_text("# Detail\n", encoding="utf-8")
        self.assert_fails("C-06", "references/detail.md")

    def test_c07_bare_mktemp_and_tmp_literal(self) -> None:
        directory = write_skill(self.root, "do-thing", extra="\n## Bundled files\n\n`scripts/run.sh`\n")
        (directory / "scripts").mkdir()
        (directory / "scripts" / "run.sh").write_text('work="$(mktemp -d)"\ncp x /tmp/out\n', encoding="utf-8")
        self.assert_fails("C-07", "mktemp")
        self.assert_fails("C-07", "/tmp literal")

    def test_c07_mktemp_with_tmpdir_passes(self) -> None:
        directory = write_skill(self.root, "do-thing", extra="\n## Bundled files\n\n`scripts/run.sh`\n")
        (directory / "scripts").mkdir()
        (directory / "scripts" / "run.sh").write_text('work="$(mktemp -d "${TMPDIR:-/tmp}/x.XXXXXX")"\n', encoding="utf-8")
        code, err = run_contract(self.root)
        self.assertEqual(code, 0, err)

    def test_c07_write_outside_the_repository_without_tmpdir(self) -> None:
        write_skill(self.root, "do-thing", extra="\nWrite the bundle to a new directory outside the repository.\n")
        self.assert_fails("C-07", "outside the repository")

    def test_c07_osascript_and_network_command_undeclared(self) -> None:
        directory = write_skill(self.root, "do-thing", extra="\n## Bundled files\n\n`scripts/run.sh`\n")
        (directory / "scripts").mkdir()
        (directory / "scripts" / "run.sh").write_text("osascript -e 'beep'\ncurl https://example.com\n", encoding="utf-8")
        self.assert_fails("C-07", "osascript")
        self.assert_fails("C-07", "network command")

    def test_c08_retired_name(self) -> None:
        write_skill(self.root, "do-thing", extra="\nSee the `coder` skill.\n")
        self.assert_fails("C-08", "retired")

    def test_c08_sibling_named_by_a_worker(self) -> None:
        write_skill(self.root, "do-thing", extra="\nThen apply `other-thing`.\n")
        write_skill(self.root, "other-thing")
        self.assert_fails("C-08", "'other-thing'")

    def test_c08_orchestrator_may_name_its_declared_children(self) -> None:
        children = "\n## Child skills\n\n- `do-thing`\n- `other-thing`\n\nApply `do-thing`, then `other-thing`.\n"
        write_skill(self.root, "run-all", kind="orchestrator", extra=children)
        write_skill(self.root, "do-thing")
        write_skill(self.root, "other-thing")
        code, err = run_contract(self.root)
        self.assertEqual(code, 0, err)

    def test_c08_orchestrator_names_an_undeclared_skill(self) -> None:
        children = "\n## Child skills\n\n- `do-thing`\n- `other-thing`\n\nAlso apply `third-thing`.\n"
        write_skill(self.root, "run-all", kind="orchestrator", extra=children)
        for name in ("do-thing", "other-thing", "third-thing"):
            write_skill(self.root, name)
        self.assert_fails("C-08", "'third-thing'")

    def test_c09_install_root_placeholder_and_repository_paths(self) -> None:
        extra = "\nRun `python3 <skill-dir>/scripts/x.py`, see `~/.claude/skills/x` and specs/012-thing.\n"
        write_skill(self.root, "do-thing", extra=extra)
        self.assert_fails("C-09", "placeholder")
        self.assert_fails("C-09", "install-root")
        self.assert_fails("C-09", "specs/")

    def test_c10_broken_link_but_not_a_link_inside_code(self) -> None:
        extra = "\nSee [the detail](references/missing.md).\n\n```text\n[example](not-a-file.md)\n```\n"
        write_skill(self.root, "do-thing", extra=extra)
        code, err = run_contract(self.root)
        self.assertEqual(code, 1, err)
        self.assertIn("references/missing.md", err)
        self.assertNotIn("not-a-file.md", err)

    def test_c11_orchestrator_with_one_child(self) -> None:
        write_skill(self.root, "run-all", kind="orchestrator", extra="\n## Child skills\n\n- `do-thing`\n")
        write_skill(self.root, "do-thing")
        self.assert_fails("C-11", "at least two")

    def test_c11_child_is_missing_or_is_an_orchestrator(self) -> None:
        write_skill(self.root, "run-all", kind="orchestrator", extra="\n## Child skills\n\n- `run-more`\n- `ghost-thing`\n")
        write_skill(self.root, "run-more", kind="orchestrator", extra="\n## Child skills\n\n- `do-thing`\n- `other-thing`\n")
        write_skill(self.root, "do-thing")
        write_skill(self.root, "other-thing")
        self.assert_fails("C-11", "'ghost-thing' is not a skill")
        self.assert_fails("C-11", "'run-more' is itself an orchestrator")

    def test_c11_worker_declares_children(self) -> None:
        write_skill(self.root, "do-thing", extra="\n## Child skills\n\n- `other-thing`\n")
        write_skill(self.root, "other-thing")
        self.assert_fails("C-11", "only an orchestrator")


if __name__ == "__main__":
    unittest.main()
