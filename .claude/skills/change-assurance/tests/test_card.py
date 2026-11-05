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
             report: dict | None = None, lang: str = "en") -> subprocess.CompletedProcess:
        doc = manifest or load("manifest-pass.json")
        if manifest_change is not None:
            manifest_change(doc["verification_manifest"])
        args = [sys.executable, "-B", str(CHECKER), "card", "--problem", str(FIXTURES / "problem-card.json"),
                "--graph", self.write("graph.json", graph) if graph else str(FIXTURES / "graph.json"),
                "--manifest", self.write("manifest.json", doc), "--lang", lang]
        if report is not None:
            args += ["--report", self.write("report.json", report)]
        return subprocess.run(args, capture_output=True, text=True, timeout=60)


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


if __name__ == "__main__":
    unittest.main()
