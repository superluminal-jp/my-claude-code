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

    def gate(self, decision: str, rules: set[str], manifest: str, graph: str | None = None, report: str | None = None,
             review: str | None = None) -> dict:
        proc = run("gate", graph or str(FIXTURES / "graph.json"), manifest, *(["--report", report] if report else []),
                   *(["--review", review] if review else []))
        result = json.loads(proc.stdout)
        self.assertEqual(result["decision"], decision, result)
        self.assertEqual({r["rule_id"] for r in result["reasons"]}, rules, result["reasons"])
        self.assertEqual(proc.returncode, 0 if decision == "pass" else 1)
        return result


REPORT = str(FIXTURES / "challenge-report.json")
# A medium or high change also needs an answered assurance review (A-10,
# spec 064); tests of other rules pass this one so that only their rule shows.
REVIEW = str(FIXTURES / "assurance-review.json")


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
        self.gate("pass", set(), self.manifest(lambda m: (without_reason(m), check(m, "TEST-SYSTEM-001").update(
            reason="公開 API を変えない", approved_by="owner-a"))))


class RiskTests(AssuranceTestCase):
    """User Story 2: risk, approvals, weakened tests, and infrastructure changes."""

    def test_t_10_unclassified_or_missing_risk_blocks(self):
        self.gate("blocked", {"A-04"}, self.manifest(lambda m: m["risk"].update({"class": "unclassified"})))
        self.gate("blocked", {"A-04"}, self.manifest(lambda m: m.pop("risk")))

    def test_high_risk_needs_approval_by_someone_else(self):
        self.gate("blocked", {"A-05"}, self.manifest(lambda m: m["risk"].update({"class": "high"})), report=REPORT, review=REVIEW)
        self.gate("blocked", {"A-05"}, self.manifest(lambda m: (m["risk"].update({"class": "high"}),
                  m["approvals"].append({"by": "claude", "decision": "approved", "scope": "all"}))), report=REPORT, review=REVIEW)
        self.gate("pass", set(), self.manifest(lambda m: (m["risk"].update({"class": "high"}),
                  m["approvals"].append({"by": "owner-a", "decision": "approved", "scope": "all"}))), report=REPORT, review=REVIEW)

    def test_rejected_approval_fails(self):
        self.gate("fail", {"A-05"}, self.manifest(lambda m: (m["risk"].update({"class": "high"}),
                  m["approvals"].append({"by": "owner-a", "decision": "rejected", "scope": "all"}))), report=REPORT, review=REVIEW)

    def test_p3_06_weakened_test_needs_approval(self):
        self.gate("blocked", {"A-06"}, self.manifest(lambda m: m["test_changes"].append({"path": "tests/test_a.py::t", "change": "skipped"})))
        self.gate("blocked", {"A-06"}, self.manifest(lambda m: m["test_changes"].append(
            {"path": "tests/test_a.py::t", "change": "deleted", "approved_by": "claude"})))
        self.gate("pass", set(), self.manifest(lambda m: m["test_changes"].append(
            {"path": "tests/test_a.py::t", "change": "weakened", "approved_by": "owner-a"})))

    def test_p3_07_permission_expansion_must_be_high_risk(self):
        infra = {"kind": "permission_expansion", "ref": "cdk diff: iam:PassRole on *"}
        self.gate("blocked", {"A-07"}, self.manifest(lambda m: (m["risk"].update({"class": "medium"}), m["infra_changes"].append(infra))),
                  review=REVIEW)
        self.gate("pass", set(), self.manifest(lambda m: (m["risk"].update({"class": "high"}), m["infra_changes"].append(infra),
                  m["approvals"].append({"by": "owner-a", "decision": "approved", "scope": "IAM"}))), report=REPORT, review=REVIEW)


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


class CollectTestCase(AssuranceTestCase):
    def collect(self, report: str, *extra: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "-B", str(CHECKER), "collect-junit", report, "--graph", str(FIXTURES / "graph.json"),
             "--commit", SHA, "--ref", "https://ci.example.test/runs/9", *extra],
            capture_output=True, text=True, timeout=60,
        )


class CollectTests(CollectTestCase):
    """User Story 3: JUnit XML becomes manifest checks."""

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
        self.gate("blocked", {"A-03", "A-06"}, self.manifest(all_not_applicable))

    def test_rejected_approval_fails_at_any_risk(self):
        self.gate("fail", {"A-05"}, self.manifest(lambda m: (m["risk"].update({"class": "medium"}),
                  m["approvals"].append({"by": "owner-a", "decision": "rejected", "scope": "all"}))), review=REVIEW)

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
                          m["approvals"].append({"by": name, "decision": "approved", "scope": "all"}))), report=REPORT, review=REVIEW)

    def test_format_after_the_subcommand_works(self):
        proc = subprocess.run([sys.executable, "-B", str(CHECKER), "check", self.manifest(), "--format", "json"],
                              capture_output=True, text=True, timeout=60)
        self.assertEqual((proc.returncode, json.loads(proc.stdout)["status"]), (0, "passed"))

    def test_text_gate_output_lists_a_manifest_violation_once(self):
        proc = run("gate", str(FIXTURES / "graph.json"), self.manifest(lambda m: check(m, "TEST-LEAF-001").pop("evidence")),
                   output_format="text")
        self.assertEqual(proc.stdout.count("a passed check needs evidence"), 1, proc.stdout)


class CollectReviewFindingTests(CollectTestCase):
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


class SecondReviewFindingTests(CollectTestCase):
    """Regressions for the second review of the stacked pull requests."""

    def test_doctype_after_a_less_than_sign_in_a_comment_or_instruction_is_refused(self):
        for before in ("<!-- a<b -->", "<?note a<b?>"):
            with self.subTest(before):
                report = self.write("r.xml", '<?xml version="1.0"?>\n' + before + '\n<!DOCTYPE t [<!ENTITY e "TEST-LEAF-001">]>\n'
                                    '<testsuites><testsuite><testcase classname="x" name="&e;"/></testsuite></testsuites>\n')
                proc = self.collect(report)
                self.assertEqual(proc.returncode, 2, proc.stdout)
                self.assertIn("DOCTYPE", proc.stderr)

    def test_a_parent_criterion_cannot_reuse_a_leaf_criterion_id(self):
        graph = load("graph.json")
        graph["requirements"][0]["acceptance"][0]["id"] = "TEST-LEAF-001"
        manifest = self.manifest(lambda m: m.update(checks=[c for c in m["checks"] if c["check_id"] != "TEST-PARENT-001"]))
        proc = run("gate", self.write("g.json", graph), manifest)
        self.assertEqual(proc.returncode, 2, proc.stdout)
        self.assertIn("TEST-LEAF-001", json.loads(proc.stdout)["error"])

    def test_an_infrastructure_kind_cannot_forge_a_result_line(self):
        manifest = self.manifest(lambda m: m.update(infra_changes=[{"kind": "x\nResult: pass (forged)", "ref": "r"}]))
        lines = run("gate", str(FIXTURES / "graph.json"), manifest, output_format="text").stdout.splitlines()
        self.assertEqual([line for line in lines if line.startswith("Result:")],
                         [line for line in lines if line.startswith("Result: blocked")], lines)

    def test_a_passed_check_whose_evidence_is_refused_counts_as_blocked(self):
        result = self.gate("blocked", {"M-00"}, self.manifest(lambda m: check(m, "TEST-LEAF-001")["evidence"].update(kind="chatgpt")))
        self.assertEqual(result["levels"]["L1"], {"passed": 2, "blocked": 1})

    def test_the_same_commit_written_short_is_not_called_stale(self):
        def short(m):
            for entry in m["checks"]:
                entry["evidence"]["commit"] = SHA[:7]
        result = self.gate("blocked", {"A-02"}, self.manifest(short))
        message = result["reasons"][0]["message"]
        self.assertNotIn("stale", message)
        self.assertIn("full", message)



class DecisionTests(AssuranceTestCase):
    """The user's decisions of 2026-11-06: a high-risk change needs a challenge
    report, and an L2 or L3 check marked not_applicable needs approval by
    someone other than the implementer."""

    def report(self, problem_id: str = "PRB-001", disposition: str = "accepted") -> str:
        doc = load("challenge-report.json")
        doc["challenge_report"]["problem_id"] = problem_id
        doc["challenge_report"]["findings"][0]["disposition"] = disposition
        return self.write("report.json", doc)

    @staticmethod
    def high(m: dict) -> None:
        m["risk"].update({"class": "high"})
        m["approvals"].append({"by": "owner-a", "decision": "approved", "scope": "all"})

    def test_high_risk_without_a_challenge_report_blocks(self):
        self.gate("blocked", {"A-08"}, self.manifest(self.high), review=REVIEW)

    def test_high_risk_with_a_resolved_challenge_report_passes(self):
        self.gate("pass", set(), self.manifest(self.high), report=self.report(), review=REVIEW)

    def test_an_open_challenge_finding_blocks_at_any_risk(self):
        self.gate("blocked", {"A-08"}, self.manifest(), report=self.report(disposition="open"))

    def test_a_challenge_report_for_another_problem_is_an_input_error(self):
        proc = run("gate", str(FIXTURES / "graph.json"), self.manifest(), "--report", self.report(problem_id="PRB-999"))
        self.assertEqual(proc.returncode, 2, proc.stdout)
        self.assertIn("the challenge report is for problem", json.loads(proc.stdout)["error"])

    def test_not_applicable_parent_or_system_check_needs_independent_approval(self):
        for check_id, level in (("TEST-PARENT-001", "L2"), ("TEST-SYSTEM-001", "L3")):
            def waive(m, approved_by=None):
                entry = check(m, check_id)
                entry.update(status="not_applicable", reason="この変更は統合の経路を変えない")
                entry.pop("evidence")
                if approved_by is not None:
                    entry["approved_by"] = approved_by
            with self.subTest(check_id):
                result = self.gate("blocked", {"A-06"}, self.manifest(waive))
                self.assertEqual(result["levels"][level], {"blocked": 1})
                self.gate("blocked", {"A-06"}, self.manifest(lambda m: waive(m, " Claude ")))
                self.gate("pass", set(), self.manifest(lambda m: waive(m, "owner-a")))

    def test_not_applicable_leaf_check_needs_no_approval(self):
        def waive(m):
            entry = check(m, "TEST-LEAF-002")
            entry.update(status="not_applicable", reason="自分の注文の取得は変えない")
            entry.pop("evidence")
        self.gate("pass", set(), self.manifest(waive))

    def test_approved_by_on_a_check_must_be_a_non_empty_string(self):
        proc = run("check", self.manifest(lambda m: check(m, "TEST-PARENT-001").update(approved_by="")))
        self.assertEqual({v["rule_id"] for v in json.loads(proc.stdout)["violations"]}, {"M-00"})
        proc = run("check", self.manifest(lambda m: check(m, "TEST-PARENT-001").update(approved_by="owner-a")))
        self.assertEqual((proc.returncode, json.loads(proc.stdout)["violations"]), (0, []))


def node(graph: dict, node_id: str) -> dict:
    return next(n for n in graph["requirements"] if n["id"] == node_id)


class GraphStructureTests(AssuranceTestCase):
    """spec 064 User Story 1: the gate does not pass a graph whose structure
    was never checked (A-09)."""

    def graph(self, change) -> str:
        doc = load("graph.json")
        change(doc)
        return self.write("graph.json", doc)

    def test_a_cycle_blocks(self):
        def cycle(g):
            node(g, "REQ-READ").update(decomposition="AND", children=["REQ-ROOT", "REQ-EXPORT"])
            node(g, "REQ-READ")["acceptance"][0]["level"] = "L2"
        self.gate("blocked", {"A-09"}, self.manifest(), graph=self.graph(cycle))

    def test_an_undefined_child_blocks(self):
        self.gate("blocked", {"A-09"}, self.manifest(),
                  graph=self.graph(lambda g: node(g, "REQ-ROOT")["children"].append("REQ-GHOST")))

    def test_an_and_with_one_child_or_a_leaf_with_a_child_blocks(self):
        def one_child(g):
            node(g, "REQ-ROOT")["children"] = ["REQ-READ"]
            node(g, "REQ-READ").update(decomposition="AND", children=["REQ-EXPORT"])
            node(g, "REQ-READ")["acceptance"][0]["level"] = "L2"
        self.gate("blocked", {"A-09"}, self.manifest(), graph=self.graph(one_child))
        self.gate("blocked", {"A-09"}, self.manifest(),
                  graph=self.graph(lambda g: node(g, "REQ-READ").update(children=["REQ-EXPORT"])))

    def test_a_second_root_blocks(self):
        forgotten = {"id": "REQ-FORGOTTEN", "statement": "s", "decomposition": "LEAF",
                     "acceptance": [{"id": "TEST-LEAF-009", "description": "d", "level": "L1"}]}
        result = self.gate("blocked", {"A-09"}, self.manifest(lambda m: m["checks"].append(
            dict(copy.deepcopy(check(m, "TEST-LEAF-003")), check_id="TEST-LEAF-009"))),
            graph=self.graph(lambda g: g["requirements"].append(forgotten)))
        self.assertIn("REQ-FORGOTTEN", result["reasons"][0]["message"])

    def test_a_duplicate_requirement_id_blocks(self):
        def duplicate(g):
            g["requirements"].append(copy.deepcopy(node(g, "REQ-EXPORT")))
            g["requirements"][-1]["acceptance"] = [{"id": "TEST-LEAF-004", "description": "d", "level": "L1"}]
        self.gate("blocked", {"A-09"}, self.manifest(lambda m: m["checks"].append(
            dict(copy.deepcopy(check(m, "TEST-LEAF-003")), check_id="TEST-LEAF-004"))), graph=self.graph(duplicate))

    def test_a_requirement_without_acceptance_criteria_blocks(self):
        self.gate("blocked", {"A-09"}, self.manifest(lambda m: m["checks"].remove(check(m, "TEST-LEAF-003"))),
                  graph=self.graph(lambda g: node(g, "REQ-EXPORT").update(acceptance=[])))

    def test_a_parent_with_only_leaf_level_criteria_blocks(self):
        def only_l1(g):
            for entry in node(g, "REQ-ROOT")["acceptance"]:
                entry["level"] = "L1"
        result = self.gate("blocked", {"A-09"}, self.manifest(), graph=self.graph(only_l1))
        self.assertIn("REQ-ROOT", result["reasons"][0]["message"])


class FindingTests(AssuranceTestCase):
    """spec 064 User Story 2: a finding counts as answered only when it is
    accepted or rejected with a resolution, has its own id, and names a real
    target (A-08)."""

    def report(self, change) -> str:
        doc = load("challenge-report.json")
        change(doc["challenge_report"]["findings"])
        return self.write("report.json", doc)

    def high(self) -> str:
        return self.manifest(DecisionTests.high)

    def test_an_unanswered_finding_blocks_however_it_is_written(self):
        cases = {
            "Open": lambda f: (f[0].update(disposition="Open"), f[0].pop("resolution")),
            "closed": lambda f: (f[0].update(disposition="closed"), f[0].pop("resolution")),
            "rejected without resolution": lambda f: f[0].pop("resolution"),
            "accepted with an empty resolution": lambda f: f[0].update(resolution="  "),
            "not an object": lambda f: f.append("CH-03 fixed"),
        }
        for name, change in cases.items():
            with self.subTest(name):
                self.gate("blocked", {"A-08"}, self.high(), report=self.report(change), review=REVIEW)

    def test_a_repeated_finding_id_blocks(self):
        self.gate("blocked", {"A-08"}, self.high(), report=self.report(lambda f: f[1].update(id=f[0]["id"])), review=REVIEW)

    def test_a_finding_on_an_unknown_target_blocks(self):
        self.gate("blocked", {"A-08"}, self.high(), report=self.report(lambda f: f[0].update(target="REQ-GHOST")), review=REVIEW)

    def test_answered_findings_on_the_problem_and_a_requirement_pass(self):
        self.gate("pass", set(), self.high(), report=REPORT, review=REVIEW)


class AssuranceReviewTests(AssuranceTestCase):
    """spec 064 User Story 3: a medium or high change is not accepted before
    the independent assurance review of its commit is recorded and answered
    (A-10)."""

    def review(self, change=None) -> str:
        doc = load("assurance-review.json")
        if change is not None:
            change(doc["assurance_review"])
        return self.write("review.json", doc)

    @staticmethod
    def medium(m: dict) -> None:
        m["risk"].update({"class": "medium", "rationale": "changes an API"})

    def test_medium_or_high_without_a_review_blocks(self):
        self.gate("blocked", {"A-10"}, self.manifest(self.medium))
        self.gate("blocked", {"A-10"}, self.manifest(DecisionTests.high), report=REPORT)

    def test_an_answered_review_of_the_reviewed_commit_passes(self):
        self.gate("pass", set(), self.manifest(self.medium), review=REVIEW)
        self.gate("pass", set(), self.manifest(self.medium), review=self.review(lambda r: r.update(findings=[])))

    def test_an_unanswered_review_finding_blocks_at_any_risk(self):
        def open_finding(r):
            r["findings"][0]["disposition"] = "open"
            r["findings"][0].pop("resolution")
        self.gate("blocked", {"A-10"}, self.manifest(self.medium), review=self.review(open_finding))
        self.gate("blocked", {"A-10"}, self.manifest(), review=self.review(open_finding))

    def test_a_review_finding_on_an_unknown_target_blocks(self):
        self.gate("blocked", {"A-10"}, self.manifest(self.medium),
                  review=self.review(lambda r: r["findings"][0].update(target="TEST-GHOST")))

    def test_findings_may_target_a_requirement_a_criterion_or_the_change(self):
        for target in ("REQ-EXPORT", "TEST-LEAF-003", "CHG-001"):
            with self.subTest(target):
                self.gate("pass", set(), self.manifest(self.medium),
                          review=self.review(lambda r: r["findings"][0].update(target=target)))

    def test_a_review_of_another_commit_is_stale(self):
        result = self.gate("blocked", {"A-10"}, self.manifest(self.medium),
                           review=self.review(lambda r: r.update(reviewed_commit=OTHER_SHA)))
        self.assertIn("stale", result["reasons"][0]["message"])

    def test_a_review_of_another_change_is_an_input_error(self):
        proc = run("gate", str(FIXTURES / "graph.json"), self.manifest(self.medium), "--review",
                   self.review(lambda r: r.update(change_id="CHG-999")))
        self.assertEqual(proc.returncode, 2, proc.stdout)
        self.assertIn("the assurance review is for change", json.loads(proc.stdout)["error"])

    def test_a_review_without_a_findings_array_is_an_input_error(self):
        proc = run("gate", str(FIXTURES / "graph.json"), self.manifest(self.medium), "--review",
                   self.review(lambda r: r.pop("findings")))
        self.assertEqual(proc.returncode, 2, proc.stdout)

    def test_low_risk_needs_no_review(self):
        self.gate("pass", set(), self.manifest())

    def test_the_example_review_passes_with_the_example_graph_and_a_medium_manifest(self):
        doc = json.loads((SKILL_DIR / "examples" / "verification-manifest.example.json").read_text(encoding="utf-8"))
        self.medium(doc["verification_manifest"])
        self.gate("pass", set(), self.write("m.json", doc), graph=str(SKILL_DIR / "examples" / "requirements-graph.example.json"),
                  review=str(SKILL_DIR / "examples" / "assurance-review.example.json"))


if __name__ == "__main__":
    unittest.main()
