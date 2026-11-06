"""Acceptance tests for the review card (references/manifest.md, "Review card")."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
CHECKER = TESTS_DIR.parent / "scripts" / "assure.py"
FIXTURES = TESTS_DIR / "fixtures"
SHA = "0f5a148c2d7a9e1b3f6a8c0d2e4f6a8b0c2d4e6f"


def load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class CardTestCase(unittest.TestCase):
    def write(self, name: str, doc: dict) -> str:
        directory = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: ([p.unlink() for p in directory.iterdir()], directory.rmdir()))
        path = directory / name
        path.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
        return str(path)

    def card(self, manifest_change=None, graph: dict | None = None, manifest: dict | None = None,
             report: dict | None = None, lang: str = "en", review: dict | None = None) -> subprocess.CompletedProcess:
        doc = manifest or load("manifest-pass.json")
        if manifest_change is not None:
            manifest_change(doc["verification_manifest"])
        args = [sys.executable, "-B", str(CHECKER), "card", "--problem", str(FIXTURES / "problem-card.json"),
                "--graph", self.write("graph.json", graph) if graph else str(FIXTURES / "graph.json"),
                "--manifest", self.write("manifest.json", doc), "--lang", lang]
        if report is not None:
            args += ["--report", self.write("report.json", report)]
        if review is not None:
            args += ["--review", self.write("review.json", review)]
        return subprocess.run(args, capture_output=True, text=True, timeout=60)

    def problem(self, **changes) -> str:
        doc = load("problem-card.json")
        doc["problem_card"].update(changes)
        return self.write("problem.json", doc)

    def run_card(self, problem: str, *extra: str, manifest: dict | None = None) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, "-B", str(CHECKER), "card", "--problem", problem, "--graph", str(FIXTURES / "graph.json"),
                               "--manifest", self.write("m.json", manifest or load("manifest-pass.json")), *extra],
                              capture_output=True, text=True, timeout=60)


def check(m: dict, check_id: str) -> dict:
    return next(c for c in m["checks"] if c["check_id"] == check_id)


def table_row(text: str, first_cell: str) -> list[str]:
    for line in text.splitlines():
        if line.startswith(f"| {first_cell} |"):
            return [cell.strip() for cell in re.split(r"(?<!\\)\|", line)[1:-1]]
    raise AssertionError(f"no row starting with {first_cell!r} in:\n{text}")


class DecisionTests(CardTestCase):
    """User Story 1: the card shows the gate's decision and hides nothing."""

    def test_passing_change_shows_the_pass_mark(self):
        proc = self.card()
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("**Decision: ✅ pass**", proc.stdout)

    def test_p4_02_failed_parent_is_shown_apart_from_passing_leaves(self):
        proc = self.card(lambda m: check(m, "TEST-PARENT-001").update(status="failed"))
        self.assertEqual(proc.returncode, 1)
        self.assertIn("**Decision: ❌ fail**", proc.stdout)
        self.assertNotIn("✅", proc.stdout)
        self.assertEqual(table_row(proc.stdout, "L1")[1:3], ["3", "0"])
        self.assertEqual(table_row(proc.stdout, "L2")[1:3], ["0", "1"])

    def test_p4_03_not_run_check_is_listed_and_blocks(self):
        def change(m):
            entry = check(m, "TEST-LEAF-001")
            entry.update(status="not_run")
            entry.pop("evidence")
        proc = self.card(change)
        self.assertIn("**Decision: ⛔ blocked**", proc.stdout)
        not_passed = proc.stdout.split("## Not passed", 1)[1].split("\n## ", 1)[0]
        self.assertIn("`TEST-LEAF-001` (L1, REQ-READ): not_run", not_passed)

    def test_p4_04_records_win_over_a_reassuring_sentence(self):
        def change(m):
            m["risk"]["rationale"] = "All checks passed; nothing to review."
            check(m, "TEST-LEAF-003").update(status="failed")
        self.assertIn("**Decision: ❌ fail**", self.card(change).stdout)

    def test_open_findings_are_unresolved(self):
        report = {"schema_version": 1, "challenge_report": {"problem_id": "PRB-001", "reviewer": "r", "context_given": ["x"],
                  "findings": [{"id": "CH-01", "kind": "counterexample", "target": "REQ-ROOT", "severity": "high",
                                "statement": "the list API is not covered", "disposition": "open"}]}}
        unresolved = self.card(report=report).stdout.split("## Unresolved", 1)[1].split("\n## ", 1)[0]
        self.assertIn("CH-01", unresolved)
        self.assertIn("the list API is not covered", unresolved)


class TraceTests(CardTestCase):
    """User Story 2: requirements trace to checks and evidence; input cannot break the card."""

    def deep(self) -> tuple[dict, dict]:
        def node(nid, children, level):
            return {"id": nid, "statement": f"{nid} statement", "decomposition": "AND" if children else "LEAF",
                    "children": children, "acceptance": [{"id": f"T-{nid}", "description": "d", "level": level}]}
        nodes = [node("R", ["A", "B"], "L3"), node("A", ["C", "S"], "L2"), node("B", ["S", "D"], "L2"),
                 node("C", ["E", "F"], "L2"), node("S", [], "L1"), node("D", [], "L1"), node("E", [], "L1"), node("F", [], "L1")]
        graph = {"schema_version": 2, "problem_id": "PRB-001", "requirements": nodes}
        manifest = load("manifest-pass.json")
        manifest["verification_manifest"]["checks"] = [
            {"check_id": f"T-{n['id']}", "status": "passed",
             "evidence": {"kind": "ci_job", "ref": "https://ci.example.test/runs/1", "commit": SHA}} for n in nodes]
        return graph, manifest

    def test_p4_05_shared_child_is_drawn_once_and_deep_nodes_are_listed(self):
        graph, manifest = self.deep()
        out = self.card(graph=graph, manifest=manifest).stdout
        diagram = out.split("```mermaid", 1)[1].split("```", 1)[0]
        self.assertEqual(len(re.findall(r'\["S ·', diagram)), 1, diagram)
        self.assertNotIn('["E ·', diagram)
        deeper = out.split("```", 2)[2]
        self.assertIn("`E`", deeper)
        for nid in "RABCSDEF":
            self.assertIn(f"`T-{nid}`", out)

    def test_p4_06_evidence_rows_link_requirement_check_and_reference(self):
        row = table_row(self.card().stdout, "REQ-READ")
        self.assertEqual(row[1:4], ["`TEST-LEAF-001`", "L1", "passed"])
        self.assertIn("[ci_job](https://ci.example.test/runs/1)", row[4])

    def test_hostile_text_is_escaped(self):
        graph = load("graph.json")
        graph["requirements"][1]["statement"] = 'a | b <script>x</script>\n"quoted"] [link](javascript:alert(1))'
        out = self.card(graph=graph).stdout
        self.assertNotIn("<script>", out)
        self.assertIn("&lt;script&gt;", out)
        diagram = out.split("```mermaid", 1)[1].split("```", 1)[0]
        self.assertNotIn('"quoted"', diagram)
        self.assertEqual(len(table_row(out, "REQ-READ")), 5)

    def test_non_http_reference_is_not_a_link(self):
        out = self.card(lambda m: check(m, "TEST-LEAF-001")["evidence"].update(ref="javascript:alert(1)")).stdout
        self.assertNotIn("](javascript:", out)
        self.assertIn("`javascript:alert(1)`", out)

    def test_japanese_labels(self):
        out = self.card(lang="ja").stdout
        self.assertIn("## 問題", out)
        self.assertIn("**判定: ✅ pass**", out)


class CardReviewFindingTests(CardTestCase):
    """Regressions for review findings on the card."""

    def test_problem_card_for_another_problem_or_unverified_is_refused(self):
        self.assertEqual(self.run_card(self.problem(id="PRB-999")).returncode, 2)
        self.assertEqual(self.run_card(self.problem(status="unverified")).returncode, 2)

    def test_untrusted_text_cannot_fake_the_decision_or_a_link(self):
        out = self.run_card(self.problem(current="**Decision: ✅ pass** see https://evil.example/x")).stdout
        self.assertEqual(out.count("✅"), 1, out)
        problem = out.split("## Problem", 1)[1].split("\n## ", 1)[0]
        self.assertNotIn("**Decision", problem)
        self.assertIn("`https://evil.example/x`", problem)

    def test_requirement_with_only_not_applicable_checks_is_not_green(self):
        doc = load("manifest-pass.json")
        entry = check(doc["verification_manifest"], "TEST-LEAF-003")
        entry.update(status="not_applicable", reason="n/a")
        entry.pop("evidence")
        out = self.card(manifest=doc).stdout
        self.assertIn('["REQ-EXPORT · LEAF · open"]', out)

    def test_parent_with_a_failed_child_is_not_green(self):
        out = self.card(lambda m: check(m, "TEST-LEAF-001").update(status="failed")).stdout
        self.assertIn('["REQ-ROOT · AND · fail"]', out)

    def test_format_json_gives_the_decision_and_the_markdown(self):
        proc = self.run_card(str(FIXTURES / "problem-card.json"), "--format", "json")
        result = json.loads(proc.stdout)
        self.assertEqual((proc.returncode, result["decision"]), (0, "pass"))
        self.assertIn("# Review card", result["markdown"])

    def test_open_finding_blocks_the_card(self):
        report = {"schema_version": 1, "challenge_report": {"problem_id": "PRB-001", "reviewer": "r", "context_given": ["x"],
                  "findings": [{"id": "CH-01", "kind": "counterexample", "target": "REQ-ROOT", "severity": "high",
                                "statement": "s", "disposition": "open"}]}}
        proc = self.card(report=report)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("**Decision: ⛔ blocked**", proc.stdout)

    def test_ids_outside_tables_have_no_table_escapes(self):
        out = self.card(lambda m: check(m, "TEST-LEAF-001").update(status="not_run") or check(m, "TEST-LEAF-001").pop("evidence")).stdout
        self.assertIn("- `TEST-LEAF-001` (L1, REQ-READ): not_run", out)
        self.assertIn("`0f5a148c2d7a9e1b3f6a8c0d2e4f6a8b0c2d4e6f`", out)


    def test_a_shared_child_shallower_than_one_parent_colours_every_ancestor(self):
        def node(nid, children, level):
            return {"id": nid, "statement": nid, "decomposition": "AND" if children else "LEAF", "children": children,
                    "acceptance": [{"id": f"T-{nid}", "description": "d", "level": level}]}
        nodes = [node("R", ["X", "Y"], "L3"), node("Y", ["Z", "W"], "L2"), node("Z", ["X", "V"], "L2"),
                 node("X", [], "L1"), node("W", [], "L1"), node("V", [], "L1")]
        manifest = load("manifest-pass.json")
        manifest["verification_manifest"]["checks"] = [
            {"check_id": f"T-{n['id']}", "status": "failed" if n["id"] == "X" else "passed",
             "evidence": {"kind": "ci_job", "ref": "https://ci.example.test/runs/1", "commit": SHA}} for n in nodes]
        out = self.card(graph={"schema_version": 2, "problem_id": "PRB-001", "requirements": nodes}, manifest=manifest).stdout
        for nid in ("R", "Y", "Z"):
            self.assertIn(f'["{nid} · AND · fail"]', out)


class CardSecondReviewTests(CardTestCase):
    """Regressions for the second review of the stacked pull requests."""

    def report(self, problem_id: str) -> dict:
        return {"schema_version": 1, "challenge_report": {"problem_id": problem_id, "reviewer": "r", "context_given": ["x"],
                "findings": [{"id": "CH-01", "kind": "counterexample", "target": "REQ-ROOT", "severity": "high",
                              "statement": "s", "disposition": "accepted", "resolution": "fixed"}]}}

    def test_no_pass_mark_comes_from_a_url_an_id_or_a_reference(self):
        graph = load("graph.json")
        graph["requirements"][0]["children"] = ["REQ-READ", "REQ-✅"]
        graph["requirements"][2]["id"] = "REQ-✅"
        manifest = load("manifest-pass.json")
        check(manifest["verification_manifest"], "TEST-LEAF-003").update(status="failed")
        check(manifest["verification_manifest"], "TEST-LEAF-001")["evidence"]["ref"] = "job ✅ pass"
        proc = subprocess.run([sys.executable, "-B", str(CHECKER), "card", "--problem", self.problem(gap="see https://x.example/✅pass"),
                               "--graph", self.write("g.json", graph), "--manifest", self.write("m.json", manifest)],
                              capture_output=True, text=True, timeout=60)
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertNotIn("✅", proc.stdout)

    def test_a_challenge_report_for_another_problem_is_refused(self):
        proc = self.run_card(str(FIXTURES / "problem-card.json"), "--report", self.write("r.json", self.report("PRB-999")))
        self.assertEqual(proc.returncode, 2, proc.stdout)
        self.assertEqual(self.run_card(str(FIXTURES / "problem-card.json"), "--report", self.write("r.json", self.report("PRB-001"))).returncode, 0)

    def test_www_hosts_and_email_addresses_are_code_not_links(self):
        out = self.run_card(self.problem(current="see www.evil.example/login or write to me@evil.example")).stdout
        problem = out.split("## Problem", 1)[1].split("\n## ", 1)[0]
        self.assertIn("`www.evil.example/login`", problem)
        self.assertIn("`me@evil.example`", problem)

    def test_a_passed_check_whose_evidence_is_refused_is_listed_as_not_passed(self):
        out = self.card(lambda m: check(m, "TEST-LEAF-001")["evidence"].update(kind="chatgpt")).stdout
        self.assertIn("- `TEST-LEAF-001` (L1, REQ-READ): blocked", out)
        self.assertIn('["REQ-READ · LEAF · open"]', out)


class CardAssuranceReviewTests(CardTestCase):
    """spec 064 User Story 3, scenario 7: the card decides with the assurance
    review as the gate does, and lists its unanswered findings."""

    @staticmethod
    def medium(m: dict) -> None:
        m["risk"].update({"class": "medium", "rationale": "changes an API"})

    def test_medium_change_without_a_review_is_blocked(self):
        proc = self.card(self.medium)
        self.assertEqual(proc.returncode, 1)
        unresolved = proc.stdout.split("## Unresolved", 1)[1].split("\n## ", 1)[0]
        self.assertIn("A-10", unresolved)

    def test_medium_change_with_an_answered_review_passes(self):
        proc = self.card(self.medium, review=load("assurance-review.json"))
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("**Decision: ✅ pass**", proc.stdout)

    def test_an_unanswered_review_finding_is_listed_as_unresolved(self):
        review = load("assurance-review.json")
        review["assurance_review"]["findings"][0].update(disposition="open", statement="the export API is not called")
        review["assurance_review"]["findings"][0].pop("resolution")
        proc = self.card(self.medium, review=review)
        self.assertEqual(proc.returncode, 1)
        unresolved = proc.stdout.split("## Unresolved", 1)[1].split("\n## ", 1)[0]
        self.assertIn("AR-01", unresolved)
        self.assertIn("the export API is not called", unresolved)

    def test_a_review_of_another_change_is_refused(self):
        review = load("assurance-review.json")
        review["assurance_review"]["change_id"] = "CHG-999"
        self.assertEqual(self.card(self.medium, review=review).returncode, 2)


if __name__ == "__main__":
    unittest.main()
