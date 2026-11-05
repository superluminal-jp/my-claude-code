"""Acceptance tests for the refinement checker (specs/059-refinement-graph-checker).

Each test starts the checker as a subprocess, so it exercises the contract
callers depend on: arguments, the JSON result, and the exit code
(contracts/cli.md). Scenario numbers refer to the user stories in spec.md.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
TOOL_DIR = TESTS_DIR.parent
REPO_ROOT = TOOL_DIR.parent.parent
CHECKER = TOOL_DIR / "check_graph.py"
REQUIREMENTS = TESTS_DIR / "fixtures" / "requirements"
SKILLS = TESTS_DIR / "fixtures" / "skills"


def run_checker(*args: str, output_format: str = "json") -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-B", str(CHECKER), "--format", output_format, *args],
        capture_output=True,
        text=True,
        timeout=120,
    )


def parse_result(proc: subprocess.CompletedProcess) -> dict | None:
    try:
        return json.loads(proc.stdout)
    except ValueError:
        return None


class CheckerTestCase(unittest.TestCase):
    """Assertions shared by every scenario."""

    def run_json(self, *args: str) -> tuple[subprocess.CompletedProcess, dict]:
        proc = run_checker(*args)
        result = parse_result(proc)
        self.assertIsNotNone(result, f"no JSON result; stderr: {proc.stderr.strip()}")
        return proc, result

    def assert_violations(self, expected_rules: set[str], *args: str) -> list[dict]:
        """The input fails with exactly the expected rules (spec SC-001)."""
        proc, result = self.run_json(*args)
        rules = {violation["rule_id"] for violation in result["violations"]}
        self.assertEqual(rules, expected_rules, result["violations"])
        self.assertEqual(result["status"], "failed")
        self.assertEqual(proc.returncode, 1)
        return result["violations"]

    def assert_passes(self, *args: str) -> dict:
        proc, result = self.run_json(*args)
        self.assertEqual(result["violations"], [])
        self.assertEqual(result["status"], "passed")
        self.assertEqual(proc.returncode, 0)
        return result

    def assert_input_error(self, *args: str) -> dict:
        """Exit code 2 together with a JSON error result, so a missing checker
        (which also exits 2) cannot satisfy this assertion."""
        proc, result = self.run_json(*args)
        self.assertEqual(result["status"], "error")
        self.assertTrue(result["error"])
        self.assertIsNone(result["graph"])
        self.assertEqual(proc.returncode, 2)
        return result

    def write_temp(self, name: str, content: str | bytes) -> Path:
        directory = Path(tempfile.mkdtemp())
        self.addCleanup(_remove_tree, directory)
        path = directory / name
        if isinstance(content, bytes):
            path.write_bytes(content)
        else:
            path.write_text(content, encoding="utf-8")
        return path


def _remove_tree(path: Path) -> None:
    for child in sorted(path.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if child.is_dir() and not child.is_symlink():
            child.rmdir()
        else:
            child.unlink()
    path.rmdir()


def fixture(directory: Path, name: str) -> str:
    return str(directory / name)


class RequirementsGraphTests(CheckerTestCase):
    """User Story 1: structural errors in a requirement decomposition."""

    def test_p1_01_duplicate_id_is_rejected(self):
        violations = self.assert_violations({"S-01"}, fixture(REQUIREMENTS, "p1-01-duplicate-id.json"))
        self.assertEqual(violations[0]["node_id"], "REQ-B")

    def test_p1_02_undefined_child_is_reported_with_parent_and_child(self):
        violations = self.assert_violations({"S-02"}, fixture(REQUIREMENTS, "p1-02-missing-child.json"))
        self.assertEqual(violations[0]["node_id"], "REQ-ROOT")
        self.assertIn("REQ-MISSING", violations[0]["message"])

    def test_p1_03_cycle_is_reported_with_its_path(self):
        violations = self.assert_violations({"S-03"}, fixture(REQUIREMENTS, "p1-03-cycle.json"))
        self.assertEqual(len(violations), 1)
        self.assertIn("A -> B -> C -> A", violations[0]["message"])

    def test_p1_04_leaf_with_children_is_rejected(self):
        violations = self.assert_violations({"S-04"}, fixture(REQUIREMENTS, "p1-04-leaf-with-child.json"))
        self.assertEqual(violations[0]["node_id"], "REQ-A")

    def test_p1_04_and_with_one_child_is_rejected(self):
        violations = self.assert_violations({"S-04"}, fixture(REQUIREMENTS, "p1-04-and-one-child.json"))
        self.assertEqual(violations[0]["node_id"], "REQ-ROOT")

    def test_p1_05_or_child_without_selection_condition_is_rejected(self):
        violations = self.assert_violations({"S-05"}, fixture(REQUIREMENTS, "p1-05-or-missing-selection.json"))
        self.assertIn("REQ-B", violations[0]["message"])

    def test_p1_06_parent_without_acceptance_is_rejected(self):
        violations = self.assert_violations(
            {"S-06"}, fixture(REQUIREMENTS, "p1-06-parent-without-acceptance.json")
        )
        self.assertEqual(violations[0]["node_id"], "REQ-ROOT")

    def test_p1_07_levels_l1_l2_l3_pass(self):
        result = self.assert_passes(fixture(REQUIREMENTS, "valid-p1-07-levels.json"))
        self.assertEqual(result["graph"], "requirements")
        self.assertEqual(
            result["rules_checked"],
            ["S-00", "S-01", "S-02", "S-03", "S-04", "S-05", "S-06", "S-07", "S-08", "S-11"],
        )

    def test_p1_07_undefined_level_is_rejected(self):
        self.assert_violations({"S-07"}, fixture(REQUIREMENTS, "p1-07-invalid-level.json"))

    def test_p1_08_shared_child_passes(self):
        self.assert_passes(fixture(REQUIREMENTS, "valid-p1-08-shared-child.json"))

    def test_or_with_a_condition_for_every_child_passes(self):
        self.assert_passes(fixture(REQUIREMENTS, "valid-or-selection.json"))

    def test_p1_10_invalid_json_is_an_input_error(self):
        self.assert_input_error(fixture(REQUIREMENTS, "p1-10-invalid-json.json"))

    def test_p1_10_unsupported_schema_version_is_an_input_error(self):
        self.assert_input_error(fixture(REQUIREMENTS, "p1-10-unsupported-schema-version.json"))

    def test_scenario_10_undefined_field_is_rejected(self):
        self.assert_violations({"S-00"}, fixture(REQUIREMENTS, "us1-10-undefined-field.json"))

    def test_scenario_11_duplicate_key_is_an_input_error(self):
        self.assert_input_error(fixture(REQUIREMENTS, "us1-11-duplicate-key.json"))

    def test_scenario_12_duplicate_acceptance_id_is_rejected(self):
        self.assert_violations({"S-07"}, fixture(REQUIREMENTS, "us1-12-duplicate-acceptance-id.json"))

    def test_scenario_13_selection_on_an_and_node_is_rejected(self):
        self.assert_violations({"S-05"}, fixture(REQUIREMENTS, "us1-13-selection-on-and.json"))

    def test_scenario_14_forgotten_child_becomes_a_second_root(self):
        violations = self.assert_violations({"S-11"}, fixture(REQUIREMENTS, "us1-14-second-root.json"))
        self.assertIn("REQ-FORGOTTEN", violations[0]["message"])

    def test_scenario_15_graph_ten_thousand_levels_deep_passes(self):
        depth = 10_000
        nodes = []
        for i in range(depth):
            children = [f"N{i + 1}", f"L{i}"] if i < depth - 1 else []
            nodes.append(_requirement(f"N{i}", "AND" if children else "LEAF", children))
            if children:
                nodes.append(_requirement(f"L{i}", "LEAF", []))
        path = self.write_temp("deep.json", json.dumps({"schema_version": 1, "requirements": nodes}))
        self.assert_passes(str(path))

    def test_scenario_15_deeply_nested_json_is_an_input_error(self):
        path = self.write_temp("nested.json", "[" * 100_000 + "]" * 100_000)
        self.assert_input_error(str(path))

    def test_inputs_that_cannot_be_interpreted_exit_with_code_2(self):
        valid = json.loads((REQUIREMENTS / "valid-or-selection.json").read_text(encoding="utf-8"))
        cases = {
            "top level is an array": json.dumps([valid]),
            "both graphs": json.dumps({**valid, "skills": []}),
            "neither graph": json.dumps({"schema_version": 1}),
            "graph is not an array": json.dumps({"schema_version": 1, "requirements": {}}),
            "undefined top-level field": json.dumps({**valid, "change_id": "CHG-1"}),
            "schema_version is a boolean": json.dumps({**valid, "schema_version": True}),
            "schema_version is missing": json.dumps({"requirements": valid["requirements"]}),
        }
        for label, text in cases.items():
            with self.subTest(label):
                self.assert_input_error(str(self.write_temp("case.json", text)))
        with self.subTest("not UTF-8"):
            self.assert_input_error(str(self.write_temp("latin1.json", b'{"schema_version": 1, "x": "\xff"}')))
        with self.subTest("larger than 5 MiB"):
            self.assert_input_error(str(self.write_temp("big.json", " " * (5 * 1024 * 1024 + 1))))
        with self.subTest("file does not exist"):
            self.assert_input_error(str(REQUIREMENTS / "does-not-exist.json"))
        with self.subTest("both FILE and --skills-dir"):
            self.assert_input_error(fixture(REQUIREMENTS, "valid-or-selection.json"), "--skills-dir", str(TESTS_DIR))
        with self.subTest("neither FILE nor --skills-dir"):
            self.assert_input_error()

    def test_undefined_option_exits_with_code_2(self):
        proc = run_checker("--no-such-option", fixture(REQUIREMENTS, "valid-or-selection.json"))
        self.assertEqual(proc.returncode, 2)
        self.assertIn("error", proc.stderr)


def _requirement(node_id: str, decomposition: str, children: list[str]) -> dict:
    return {
        "id": node_id,
        "statement": f"requirement {node_id}",
        "decomposition": decomposition,
        "children": children,
        "acceptance": [{"id": f"T-{node_id}", "description": "check", "level": "L2" if children else "L1"}],
    }


if __name__ == "__main__":
    unittest.main()
