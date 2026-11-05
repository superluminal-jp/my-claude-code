"""Acceptance tests for the bundled assurance checker (references/manifest.md).

Each test starts the checker as a subprocess and checks the result callers
depend on: the decision, the rule ids of the reasons, and the exit code. Each
negative case changes one thing in a passing manifest.
"""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
SKILL_DIR = TESTS_DIR.parent
CHECKER = SKILL_DIR / "scripts" / "assure.py"
FIXTURES = TESTS_DIR / "fixtures"
SHA = "0f5a148c2d7a9e1b3f6a8c0d2e4f6a8b0c2d4e6f"
OTHER_SHA = "1111111111111111111111111111111111111111"


def run(*args: str, output_format: str = "json") -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-B", str(CHECKER), "--format", output_format, *args],
        capture_output=True, text=True, timeout=60,
    )


def load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class AssuranceTestCase(unittest.TestCase):
    def write(self, name: str, content: str | dict) -> str:
        directory = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: [p.unlink() for p in directory.iterdir()] and None or directory.rmdir())
        path = directory / name
        path.write_text(content if isinstance(content, str) else json.dumps(content), encoding="utf-8")
        return str(path)

    def manifest(self, change=None) -> str:
        doc = load("manifest-pass.json")
        if change is not None:
            change(doc["verification_manifest"])
        return self.write("manifest.json", doc)

    def gate(self, decision: str, rules: set[str], manifest: str, graph: str | None = None) -> dict:
        proc = run("gate", graph or str(FIXTURES / "graph.json"), manifest)
        result = json.loads(proc.stdout)
        self.assertEqual(result["decision"], decision, result)
        self.assertEqual({r["rule_id"] for r in result["reasons"]}, rules, result["reasons"])
        self.assertEqual(proc.returncode, 0 if decision == "pass" else 1)
        return result


def check(doc: dict, check_id: str) -> dict:
    return next(c for c in doc["checks"] if c["check_id"] == check_id)


class LevelTests(AssuranceTestCase):
    """User Story 1: a passing leaf never makes a failing or missing parent pass."""

    def test_all_checks_with_current_evidence_pass(self):
        result = self.gate("pass", set(), self.manifest())
        self.assertEqual(result["levels"], {"L1": {"passed": 3}, "L2": {"passed": 1}, "L3": {"passed": 1}})

    def test_p3_01_failed_parent_check_fails_although_leaves_pass(self):
        self.gate("fail", {"A-03"}, self.manifest(lambda m: check(m, "TEST-PARENT-001").update(status="failed")))

    def test_p3_02_failed_system_check_fails(self):
        self.gate("fail", {"A-03"}, self.manifest(lambda m: check(m, "TEST-SYSTEM-001").update(status="failed")))

    def test_p3_03_failed_negative_leaf_check_fails(self):
        self.gate("fail", {"A-03"}, self.manifest(lambda m: check(m, "TEST-LEAF-001").update(status="failed")))

    def test_p3_04_evidence_for_another_commit_is_stale(self):
        result = self.gate("blocked", {"A-02"}, self.manifest(lambda m: check(m, "TEST-LEAF-002")["evidence"].update(commit=OTHER_SHA)))
        self.assertIn("stale", result["reasons"][0]["message"])
        self.assertEqual(result["levels"]["L1"], {"passed": 2, "blocked": 1})

    def test_p3_05_ai_review_alone_is_not_evidence(self):
        self.gate("blocked", {"A-02"}, self.manifest(lambda m: check(m, "TEST-SYSTEM-001")["evidence"].update(kind="ai_review")))

    def test_p3_08_check_whose_collection_failed_blocks(self):
        def change(m):
            entry = check(m, "TEST-LEAF-003")
            entry.update(status="blocked", reason="the CI job timed out")
            entry.pop("evidence")
        self.gate("blocked", {"A-03"}, self.manifest(change))

    def test_missing_and_unknown_checks_block(self):
        self.gate("blocked", {"A-01"}, self.manifest(lambda m: m["checks"].pop()))
        self.gate("blocked", {"A-01"}, self.manifest(lambda m: check(m, "TEST-LEAF-003").update(check_id="TEST-NOPE")))

    def test_manifest_for_another_problem_blocks(self):
        self.gate("blocked", {"A-01"}, self.manifest(lambda m: m.update(problem_id="PRB-999")))

    def test_not_applicable_needs_a_reason(self):
        def without_reason(m):
            entry = check(m, "TEST-SYSTEM-001")
            entry.update(status="not_applicable")
            entry.pop("evidence")
        self.gate("blocked", {"M-02"}, self.manifest(without_reason))
        self.gate("pass", set(), self.manifest(lambda m: (without_reason(m), check(m, "TEST-SYSTEM-001").update(reason="公開 API を変えない"))))


class RiskTests(AssuranceTestCase):
    """User Story 2: risk, approvals, weakened tests, and infrastructure changes."""

    def test_t_10_unclassified_or_missing_risk_blocks(self):
        self.gate("blocked", {"A-04"}, self.manifest(lambda m: m["risk"].update({"class": "unclassified"})))
        self.gate("blocked", {"A-04"}, self.manifest(lambda m: m.pop("risk")))

    def test_high_risk_needs_approval_by_someone_else(self):
        self.gate("blocked", {"A-05"}, self.manifest(lambda m: m["risk"].update({"class": "high"})))
        self.gate("blocked", {"A-05"}, self.manifest(lambda m: (m["risk"].update({"class": "high"}),
                  m["approvals"].append({"by": "claude", "decision": "approved", "scope": "all"}))))
        self.gate("pass", set(), self.manifest(lambda m: (m["risk"].update({"class": "high"}),
                  m["approvals"].append({"by": "owner-a", "decision": "approved", "scope": "all"}))))

    def test_rejected_approval_fails(self):
        self.gate("fail", {"A-05"}, self.manifest(lambda m: (m["risk"].update({"class": "high"}),
                  m["approvals"].append({"by": "owner-a", "decision": "rejected", "scope": "all"}))))

    def test_p3_06_weakened_test_needs_approval(self):
        self.gate("blocked", {"A-06"}, self.manifest(lambda m: m["test_changes"].append({"path": "tests/test_a.py::t", "change": "skipped"})))
        self.gate("blocked", {"A-06"}, self.manifest(lambda m: m["test_changes"].append(
            {"path": "tests/test_a.py::t", "change": "deleted", "approved_by": "claude"})))
        self.gate("pass", set(), self.manifest(lambda m: m["test_changes"].append(
            {"path": "tests/test_a.py::t", "change": "weakened", "approved_by": "owner-a"})))

    def test_p3_07_permission_expansion_must_be_high_risk(self):
        infra = {"kind": "permission_expansion", "ref": "cdk diff: iam:PassRole on *"}
        self.gate("blocked", {"A-07"}, self.manifest(lambda m: (m["risk"].update({"class": "medium"}), m["infra_changes"].append(infra))))
        self.gate("pass", set(), self.manifest(lambda m: (m["risk"].update({"class": "high"}), m["infra_changes"].append(infra),
                  m["approvals"].append({"by": "owner-a", "decision": "approved", "scope": "IAM"}))))


class ManifestShapeTests(AssuranceTestCase):
    def test_passing_manifest_has_no_violation(self):
        proc = run("check", self.manifest())
        self.assertEqual((proc.returncode, json.loads(proc.stdout)["status"]), (0, "passed"))

    def test_shape_errors_are_reported(self):
        cases = {
            "M-00": lambda m: m.update(owner="x"),
            "M-01": lambda m: m["checks"].append(copy.deepcopy(m["checks"][0])),
            "M-02": lambda m: check(m, "TEST-LEAF-001").pop("evidence"),
        }
        for rule, change in cases.items():
            with self.subTest(rule):
                proc = run("check", self.manifest(change))
                result = json.loads(proc.stdout)
                self.assertEqual(({v["rule_id"] for v in result["violations"]}, proc.returncode), ({rule}, 1))

    def test_bad_commit_and_unreadable_input_are_input_errors(self):
        for doc in ("not json", json.dumps({"schema_version": 1, "verification_manifest": []})):
            with self.subTest(doc[:10]):
                proc = run("check", self.write("m.json", doc))
                self.assertEqual((proc.returncode, json.loads(proc.stdout)["status"]), (2, "error"))
        proc = run("check", self.manifest(lambda m: m.update(reviewed_commit="main")))
        self.assertEqual({v["rule_id"] for v in json.loads(proc.stdout)["violations"]}, {"M-00"})


class CollectTests(AssuranceTestCase):
    """User Story 3: JUnit XML becomes manifest checks."""

    def collect(self, report: str, *extra: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "-B", str(CHECKER), "collect-junit", report, "--graph", str(FIXTURES / "graph.json"),
             "--commit", SHA, "--ref", "https://ci.example.test/runs/9", *extra],
            capture_output=True, text=True, timeout=60,
        )

    def test_test_cases_map_to_acceptance_ids(self):
        proc = self.collect(str(FIXTURES / "junit.xml"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        statuses = {c["check_id"]: c["status"] for c in json.loads(proc.stdout)}
        self.assertEqual(statuses, {"TEST-PARENT-001": "not_run", "TEST-SYSTEM-001": "not_run",
                                    "TEST-LEAF-001": "passed", "TEST-LEAF-002": "passed", "TEST-LEAF-003": "failed"})

    def test_collected_checks_carry_the_commit_and_ref(self):
        checks = json.loads(self.collect(str(FIXTURES / "junit.xml"), "--kind", "local_run").stdout)
        passed = next(c for c in checks if c["check_id"] == "TEST-LEAF-001")
        self.assertEqual(passed["evidence"], {"kind": "local_run", "ref": "https://ci.example.test/runs/9", "commit": SHA})

    def test_doctype_is_refused(self):
        proc = self.collect(str(FIXTURES / "junit-doctype.xml"))
        self.assertEqual(proc.returncode, 2)
        self.assertIn("DOCTYPE", proc.stderr)


class ReviewFindingTests(AssuranceTestCase):
    """Regressions for review findings: the gate must not pass without evidence."""

    def test_graph_without_criteria_blocks(self):
        graph = {"schema_version": 2, "problem_id": "PRB-001", "requirements": []}
        self.gate("blocked", {"A-01"}, self.manifest(lambda m: m.update(checks=[])), graph=self.write("g.json", graph))

    def test_requirement_without_any_passed_check_blocks(self):
        def all_not_applicable(m):
            for entry in m["checks"]:
                entry.update(status="not_applicable", reason="n/a")
                entry.pop("evidence")
        self.gate("blocked", {"A-03"}, self.manifest(all_not_applicable))

    def test_rejected_approval_fails_at_any_risk(self):
        self.gate("fail", {"A-05"}, self.manifest(lambda m: (m["risk"].update({"class": "medium"}),
                  m["approvals"].append({"by": "owner-a", "decision": "rejected", "scope": "all"}))))

    def test_commit_with_a_trailing_newline_is_not_a_commit(self):
        def change(m):
            m["reviewed_commit"] = SHA + "\n"
            for entry in m["checks"]:
                entry["evidence"]["commit"] = SHA + "\n"
        proc = run("check", self.manifest(change))
        self.assertIn("M-00", {v["rule_id"] for v in json.loads(proc.stdout)["violations"]})

    def test_self_approval_with_other_case_or_spaces_is_not_independent(self):
        for name in ("Claude", " claude ", "CLAUDE"):
            with self.subTest(name):
                self.gate("blocked", {"A-05"}, self.manifest(lambda m: (m["risk"].update({"class": "high"}),
                          m["approvals"].append({"by": name, "decision": "approved", "scope": "all"}))))

    def test_format_after_the_subcommand_works(self):
        proc = subprocess.run([sys.executable, "-B", str(CHECKER), "check", self.manifest(), "--format", "json"],
                              capture_output=True, text=True, timeout=60)
        self.assertEqual((proc.returncode, json.loads(proc.stdout)["status"]), (0, "passed"))

    def test_text_gate_output_lists_a_manifest_violation_once(self):
        proc = run("gate", str(FIXTURES / "graph.json"), self.manifest(lambda m: check(m, "TEST-LEAF-001").pop("evidence")),
                   output_format="text")
        self.assertEqual(proc.stdout.count("a passed check needs evidence"), 1, proc.stdout)


class CollectReviewFindingTests(CollectTests):
    def report(self, cases: str) -> str:
        return self.write("r.xml", f'<?xml version="1.0"?>\n<testsuites><testsuite name="s">{cases}</testsuite></testsuites>\n')

    def statuses(self, report: str) -> dict:
        proc = self.collect(report)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return {c["check_id"]: c for c in json.loads(proc.stdout)}

    def test_doctype_text_inside_cdata_is_accepted(self):
        cases = '<testcase classname="t" name="a[TEST-LEAF-001]"><system-out><![CDATA[<!DOCTYPE html><html></html>]]></system-out></testcase>'
        self.assertEqual(self.statuses(self.report(cases))["TEST-LEAF-001"]["status"], "passed")

    def test_passed_and_skipped_mix_is_not_run_with_an_accurate_reason(self):
        cases = '<testcase classname="t" name="a[TEST-LEAF-001]"/><testcase classname="t" name="b[TEST-LEAF-001]"><skipped/></testcase>'
        entry = self.statuses(self.report(cases))["TEST-LEAF-001"]
        self.assertEqual(entry["status"], "not_run")
        self.assertIn("1 passed, 1 skipped", entry["reason"])

    def test_id_inside_a_dotted_longer_id_does_not_count(self):
        cases = '<testcase classname="t" name="c[TEST-LEAF-003.extra]"/>'
        self.assertEqual(self.statuses(self.report(cases))["TEST-LEAF-003"]["status"], "not_run")


if __name__ == "__main__":
    unittest.main()
