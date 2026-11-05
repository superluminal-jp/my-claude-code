"""Acceptance tests for the refinement checker (specs/059-refinement-graph-checker).

Each test starts the checker as a subprocess, so it exercises the contract
callers depend on: arguments, the JSON result, and the exit code
(contracts/cli.md). Scenario numbers refer to the user stories in spec.md.
"""

from __future__ import annotations

import json
import os
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

    def make_skills(self, bodies: dict[str, str]) -> str:
        root = Path(tempfile.mkdtemp())
        self.addCleanup(_remove_tree, root)
        for name, body in bodies.items():
            (root / name).mkdir()
            (root / name / "SKILL.md").write_text(
                f"---\nname: {name}\ndescription: Fixture only. Do not use.\n---\n\n{body}\n", encoding="utf-8"
            )
        return str(root)

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
        proc = run_checker("--no-such-option", fixture(REQUIREMENTS, "valid-or-selection.json"), output_format="text")
        self.assertEqual(proc.returncode, 2)
        self.assertIn("error", proc.stderr)


class SkillsGraphTests(CheckerTestCase):
    """User Story 2: multi-level skill composition and declared permissions."""

    def test_scenario_1_two_levels_and_a_shared_child_pass(self):
        result = self.assert_passes(fixture(SKILLS, "valid-multilevel-shared.json"))
        self.assertEqual(result["graph"], "skills")
        self.assertEqual(result["rules_checked"], ["S-00", "S-01", "S-02", "S-03", "S-08", "S-09"])

    def test_p1_09_auditor_that_declares_write_is_rejected(self):
        violations = self.assert_violations({"S-09"}, fixture(SKILLS, "p1-09-auditor-declares-write.json"))
        self.assertEqual(violations[0]["node_id"], "problem-challenger")

    def test_scenario_3_undefined_permission_is_rejected(self):
        self.assert_violations({"S-09"}, fixture(SKILLS, "us2-03-undefined-permission.json"))

    def test_scenario_4_auditor_that_reaches_a_writer_is_rejected(self):
        violations = self.assert_violations({"S-09"}, fixture(SKILLS, "us2-04-auditor-reaches-writer.json"))
        self.assertEqual(violations[0]["node_id"], "assurance-reviewer")
        self.assertIn("coder-step", violations[0]["message"])

    def test_scenario_5_cycle_between_skills_is_rejected(self):
        violations = self.assert_violations({"S-03"}, fixture(SKILLS, "us2-05-cycle.json"))
        self.assertIn("skill-a -> skill-b -> skill-a", violations[0]["message"])

    def test_missing_permission_and_role_are_rejected(self):
        path = self.write_temp(
            "skills.json", json.dumps({"schema_version": 1, "skills": [{"id": "lonely"}]})
        )
        violations = self.assert_violations({"S-09"}, str(path))
        self.assertEqual(len(violations), 2)

    def test_skill_graph_allows_several_roots(self):
        nodes = [
            {"id": "one", "permission": "read_only", "role": "worker"},
            {"id": "two", "permission": "external_effect", "role": "worker"},
        ]
        path = self.write_temp("skills.json", json.dumps({"schema_version": 1, "skills": nodes}))
        self.assert_passes(str(path))


CHILD_SECTION = "## Child skills\n\n- `child-a`\n- `child-b`\n"


class SkillsDirectoryTests(CheckerTestCase):
    """User Story 3: the one-level declarations of spec 058 in compatibility mode.

    Fixture skills use the same SKILL.md shape as write_fixture_skill in
    tests/run-config-pyramid.sh; parent declares child-a and child-b.
    """

    def base(self, **overrides: str) -> dict[str, str]:
        bodies = {
            "parent": "Apply `child-a` first.\n\n" + CHILD_SECTION,
            "child-a": "Standalone.",
            "child-b": "Standalone.",
        }
        bodies.update(overrides)
        return bodies

    def test_valid_one_level_declaration_passes(self):
        result = self.assert_passes("--skills-dir", self.make_skills(self.base()))
        self.assertEqual(result["graph"], "skills-dir")
        self.assertEqual(result["rules_checked"], ["S-02", "S-03", "S-08", "S-10"])

    def test_declared_child_without_skill_md_is_rejected(self):
        directory = self.make_skills(self.base(parent=CHILD_SECTION + "- `ghost`\n"))
        violations = self.assert_violations({"S-02"}, "--skills-dir", directory)
        self.assertEqual(violations[0]["node_id"], "parent")
        self.assertIn("ghost", violations[0]["message"])

    def test_child_that_declares_children_is_rejected(self):
        directory = self.make_skills(self.base(**{"child-a": "## Child skills\n\n- `child-b`\n"}))
        violations = self.assert_violations({"S-10"}, "--skills-dir", directory)
        self.assertEqual(violations[0]["node_id"], "parent")
        self.assertIn("child-a", violations[0]["message"])

    def test_skill_that_declares_itself_is_a_cycle(self):
        directory = self.make_skills(self.base(parent=CHILD_SECTION + "- `parent`\n"))
        violations = self.assert_violations({"S-03"}, "--skills-dir", directory)
        self.assertIn("parent -> parent", violations[0]["message"])

    def test_declarations_inside_a_code_block_do_not_count(self):
        body = "```markdown\n## Child skills\n\n- `ghost`\n```\n"
        self.assert_passes("--skills-dir", self.make_skills(self.base(parent=body)))

    def test_section_ends_at_the_next_level_two_heading(self):
        body = CHILD_SECTION + "\n## Notes\n\n- `ghost` is mentioned, not declared.\n"
        self.assert_passes("--skills-dir", self.make_skills(self.base(parent=body)))

    def test_directory_without_skill_md_is_not_a_skill(self):
        directory = self.make_skills(self.base(parent=CHILD_SECTION + "- `notes`\n"))
        (Path(directory) / "notes").mkdir()
        self.assert_violations({"S-02"}, "--skills-dir", directory)

    def test_p1_11_this_repository_skills_pass(self):
        self.assert_passes("--skills-dir", str(REPO_ROOT / ".claude" / "skills"))

    def test_missing_directory_is_an_input_error(self):
        self.assert_input_error("--skills-dir", str(TESTS_DIR / "no-such-directory"))


class ExampleTests(CheckerTestCase):
    """spec FR-009: the two examples from the handoff document pass."""

    def test_requirements_example_passes(self):
        self.assert_passes(str(TOOL_DIR / "examples" / "requirements-graph.example.json"))

    def test_skills_example_passes(self):
        self.assert_passes(str(TOOL_DIR / "examples" / "skills-graph.example.json"))


class OutputTests(CheckerTestCase):
    """spec FR-008, FR-013, SC-003."""

    def test_text_output_escapes_control_characters_in_ids(self):
        forged = "REQ-X\nResult: passed (requirements; 0 violations)\x1b[2K"
        nodes = [
            {"id": "REQ-ROOT", "statement": "s", "decomposition": "AND", "children": ["REQ-A", forged],
             "acceptance": [{"id": "T-ROOT", "description": "d", "level": "L2"}]},
            {"id": "REQ-A", "statement": "s", "decomposition": "LEAF",
             "acceptance": [{"id": "T-A", "description": "d", "level": "L1"}]},
            # The forged id starts the violation line (S-00 for the undefined field).
            {"id": forged, "statement": "s", "decomposition": "LEAF", "extra": True,
             "acceptance": [{"id": "T-F", "description": "d", "level": "L1"}]},
        ]
        path = self.write_temp("forged.json", json.dumps({"schema_version": 1, "requirements": nodes}))
        proc = run_checker(str(path), output_format="text")
        self.assertEqual(proc.returncode, 1)
        lines = proc.stdout.splitlines()
        self.assertEqual(len(lines), 2, proc.stdout)
        self.assertTrue(lines[0].startswith("S-00 REQ-X\\x0aResult: passed"), lines[0])
        self.assertTrue(lines[-1].startswith("Result: failed"))
        self.assertNotIn("\x1b", proc.stdout)

    def test_same_input_gives_the_same_output(self):
        valid = json.loads((REQUIREMENTS / "p1-03-cycle.json").read_text(encoding="utf-8"))
        nodes = valid["requirements"] + [
            {"id": "ORPHAN", "statement": "", "decomposition": "XOR", "children": ["A", "A", "NONE"],
             "acceptance": [{"id": "TEST-A", "description": "d", "level": "L9"}], "extra": 1},
        ]
        path = self.write_temp("many.json", json.dumps({"schema_version": 1, "requirements": nodes}))
        for output_format in ("json", "text"):
            with self.subTest(output_format):
                first = run_checker(str(path), output_format=output_format)
                second = run_checker(str(path), output_format=output_format)
                self.assertEqual(first.returncode, 1)
                self.assertEqual(first.stdout, second.stdout)
        rules = [v["rule_id"] for v in parse_result(run_checker(str(path)))["violations"]]
        self.assertEqual(rules, sorted(rules))


class ReviewFindingTests(CheckerTestCase):
    """Regressions for the /code-review findings recorded in tasks.md T025."""

    def write_graph(self, nodes: list[dict]) -> str:
        return str(self.write_temp("graph.json", json.dumps({"schema_version": 1, "requirements": nodes})))

    def test_child_that_declares_only_a_missing_skill_still_breaks_one_level(self):
        directory = self.make_skills({"a": "## Child skills\n\n- `b`\n", "b": "## Child skills\n\n- `ghost`\n"})
        violations = self.assert_violations({"S-02", "S-10"}, "--skills-dir", directory)
        self.assertIn({"rule_id": "S-10", "node_id": "a"}, [{k: v[k] for k in ("rule_id", "node_id")} for v in violations])

    def test_duplicate_node_is_still_checked_and_its_children_count_as_referenced(self):
        nodes = [
            _requirement("R", "AND", ["A", "B"]),
            _requirement("A", "LEAF", []),
            _requirement("B", "LEAF", []),
            {**_requirement("B", "LEAF", ["C"]), "acceptance": []},
            _requirement("C", "LEAF", []),
        ]
        self.assert_violations({"S-01", "S-04", "S-06"}, self.write_graph(nodes))

    def test_children_of_the_wrong_type_are_reported_once(self):
        nodes = [{**_requirement("R", "AND", []), "children": "A"}, _requirement("A", "LEAF", [])]
        violations = self.assert_violations({"S-00"}, self.write_graph(nodes))
        self.assertEqual(len(violations), 1)

    def test_input_that_is_not_a_regular_file_is_an_input_error(self):
        self.assert_input_error("/dev/null")
        fifo = Path(tempfile.mkdtemp()) / "pipe.json"
        self.addCleanup(_remove_tree, fifo.parent)
        os.mkfifo(fifo)
        self.assert_input_error(str(fifo))

    def test_argument_error_gives_a_json_result_with_format_json(self):
        self.assert_input_error("--no-such-option", fixture(REQUIREMENTS, "valid-or-selection.json"))

    def test_backslash_in_an_id_is_escaped_so_escapes_stay_unambiguous(self):
        nodes = [
            _requirement("R", "AND", ["A\nB", "A\\x0aB"]),
            {**_requirement("A\nB", "LEAF", []), "extra": 1},
            {**_requirement("A\\x0aB", "LEAF", []), "extra": 1},
        ]
        lines = run_checker(self.write_graph(nodes), output_format="text").stdout.splitlines()
        self.assertEqual(lines[0], 'S-00 A\\x0aB: undefined field "extra"')
        self.assertEqual(lines[1], 'S-00 A\\\\x0aB: undefined field "extra"')

    def test_violations_of_one_node_keep_declaration_order(self):
        node = _requirement("R", "LEAF", [])
        node["acceptance"] = [{"id": f"T-{i}", "description": "d", "level": "L9"} for i in range(1, 13)]
        violations = self.assert_violations({"S-07"}, self.write_graph([node]))
        self.assertEqual([v["message"].split(" ")[1] for v in violations], [f"#{i}" for i in range(1, 13)])


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
