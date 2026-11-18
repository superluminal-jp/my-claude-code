"""Acceptance tests for scripts/review_prep.py (references/reviewer.md).

Each test builds a small git repository in a temporary directory: a base
commit, a change commit with its problem card and requirements graph, and a
records commit with the verification manifest and its evidence. The script
runs as a subprocess in that repository, as the procedure runs it.
"""

from __future__ import annotations

import copy
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "review_prep.py"
RECORDS = "records/change-1"

GRAPH = {"schema_version": 2, "problem_id": "PRB-1", "requirements": [
    {"id": "REQ-ROOT", "statement": "the root", "decomposition": "AND", "children": ["REQ-A", "REQ-B"],
     "acceptance": [{"id": "T-PARENT", "description": "both together", "level": "L2"}]},
    {"id": "REQ-A", "statement": "a", "decomposition": "LEAF", "acceptance": [{"id": "T-A", "description": "a works", "level": "L1"}]},
    {"id": "REQ-B", "statement": "b", "decomposition": "LEAF", "acceptance": [{"id": "T-B", "description": "b works", "level": "L1"}]}]}
CARD = {"schema_version": 1, "problem_card": {"id": "PRB-1", "ideal": "i", "current": "c", "gap": "g", "significance": "s",
                                               "status": "verified", "evidence": [{"source": "x", "observation": "y"}]}}


class Repo:
    def __init__(self, case: unittest.TestCase):
        self.root = Path(tempfile.mkdtemp())
        case.addCleanup(shutil.rmtree, self.root, True)
        self.git("init", "-q", "-b", "main")

    def git(self, *args: str) -> str:
        return subprocess.run(
            ["git", "-c", "user.name=t", "-c", "user.email=t@example.test", "-c", "commit.gpgsign=false",
             "-c", "core.hooksPath=/dev/null", *args],
            cwd=self.root, check=True, capture_output=True, text=True, timeout=60).stdout.strip()

    def write(self, rel: str, content) -> None:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content if isinstance(content, str) else json.dumps(content, indent=2, ensure_ascii=False), encoding="utf-8")

    def commit(self, message: str) -> str:
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message)
        return self.git("rev-parse", "HEAD")

    def manifest(self, reviewed: str, risk: str = "medium", refs: tuple[str, ...] = (f"{RECORDS}/evidence/run.txt",)) -> None:
        checks = [{"check_id": f"T-{i}", "status": "passed", "evidence": {"kind": "local_run", "ref": ref, "commit": reviewed}}
                  for i, ref in enumerate(refs)]
        checks.append({"check_id": "T-CI", "status": "passed",
                       "evidence": {"kind": "ci_job", "ref": "https://ci.example.test/runs/1", "commit": reviewed}})
        self.write(f"{RECORDS}/verification-manifest.json", {"schema_version": 1, "verification_manifest": {
            "change_id": "CHG-1", "problem_id": "PRB-1", "reviewed_commit": reviewed, "implementer": "claude",
            "risk": {"class": risk, "rationale": "r"}, "approvals": [], "checks": checks, "test_changes": [], "infra_changes": []}})

    def first_round(self, graph: dict = GRAPH) -> tuple[str, str]:
        """base, then the change commit (code, card, graph, and a script that
        makes evidence), then its records commit; returns (base, change)."""
        self.write("src/app.py", "VALUE = 1\n")
        self.write(".gitignore", "*.log\n")
        base = self.commit("base")
        self.write("src/app.py", "VALUE = 2\n")
        self.write(f"{RECORDS}/problem-card.json", CARD)
        self.write(f"{RECORDS}/requirements-graph.json", graph)
        self.write(f"{RECORDS}/evidence/make.sh", "python3 -m unittest > run.txt\n")
        change = self.commit("change")
        self.manifest(change)
        self.write(f"{RECORDS}/evidence/run.txt", "all 3 tests passed\n")
        self.commit("records")
        return base, change

    def next_round(self, graph: dict | None = None, card: dict | None = None, risk: str = "medium") -> str:
        """A fix commit (code, and the graph or card if given), then its records commit; returns the fix commit."""
        self.write("src/app.py", "VALUE = 3\n")
        if graph is not None:
            self.write(f"{RECORDS}/requirements-graph.json", graph)
        if card is not None:
            self.write(f"{RECORDS}/problem-card.json", card)
        fix = self.commit("fix")
        self.manifest(fix, risk=risk)
        self.write(f"{RECORDS}/evidence/run.txt", "all 4 tests passed\n")
        self.commit("records again")
        return fix


def run(repo: Repo, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(SCRIPT), *args], cwd=repo.root, capture_output=True, text=True, timeout=120)


def out_dir(case: unittest.TestCase) -> Path:
    parent = Path(tempfile.mkdtemp())
    case.addCleanup(shutil.rmtree, parent, True)
    return parent / "bundle"


class CheckTests(unittest.TestCase):
    """check: what can be found without a reviewer is found before the review."""

    def check(self, repo: Repo) -> subprocess.CompletedProcess:
        return run(repo, "check", "--records", RECORDS)

    def test_records_that_follow_the_procedure_have_no_violation(self):
        repo = Repo(self)
        repo.first_round()
        proc = self.check(repo)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("Result: passed", proc.stdout)

    def test_a_change_outside_the_record_directory_after_the_reviewed_commit_is_a_violation(self):
        repo = Repo(self)
        repo.first_round()
        repo.write("src/other.py", "x = 1\n")
        repo.commit("a code change after the review")
        proc = self.check(repo)
        self.assertEqual(proc.returncode, 1, proc.stdout)
        self.assertIn("P-02 src/other.py", proc.stdout)

    def test_missing_untracked_or_ignored_evidence_is_a_violation(self):
        cases = {"missing": (f"{RECORDS}/evidence/none.txt", None, "does not exist"),
                 "untracked": (f"{RECORDS}/evidence/new.txt", "new\n", "is not tracked"),
                 "ignored": (f"{RECORDS}/evidence/run.log", "log\n", "is ignored")}
        for name, (ref, content, expected) in cases.items():
            with self.subTest(name):
                repo = Repo(self)
                _, change = repo.first_round()
                repo.manifest(change, refs=(ref,))
                repo.commit("records naming another evidence file")
                if content is not None:
                    repo.write(ref, content)
                proc = self.check(repo)
                self.assertEqual(proc.returncode, 1, proc.stdout)
                self.assertIn(f"P-03 {ref}: {expected}", proc.stdout)

    def test_a_reviewed_commit_that_is_no_commit_or_not_behind_head_is_a_violation(self):
        repo = Repo(self)
        repo.first_round()
        repo.manifest("1111111111111111111111111111111111111111")
        repo.commit("records naming no commit")
        proc = self.check(repo)
        self.assertEqual(proc.returncode, 1, proc.stdout)
        self.assertIn("P-01 1111111111111111111111111111111111111111: reviewed_commit is not a commit of this repository",
                      proc.stdout)
        main = repo.git("rev-parse", "HEAD")
        repo.git("checkout", "-q", "-b", "elsewhere")
        repo.write("src/elsewhere.py", "x = 1\n")
        elsewhere = repo.commit("a commit off the main line")
        repo.git("checkout", "-q", "main")
        repo.manifest(elsewhere)
        repo.commit("records naming a commit HEAD does not contain")
        proc = self.check(repo)
        self.assertNotEqual(main, elsewhere)
        self.assertIn(f"P-01 {elsewhere}: reviewed_commit is not behind HEAD", proc.stdout)

    def test_a_script_in_the_record_directory_changed_after_the_review_is_a_violation(self):
        repo = Repo(self)
        repo.first_round()
        repo.write(f"{RECORDS}/evidence/make.sh", "echo all passed > run.txt\n")
        repo.commit("the evidence script changed after the review")
        proc = self.check(repo)
        self.assertEqual(proc.returncode, 1, proc.stdout)
        self.assertIn(f"P-02 {RECORDS}/evidence/make.sh", proc.stdout)

    def test_a_file_moved_into_the_record_directory_after_the_review_is_a_violation(self):
        repo = Repo(self)
        repo.first_round()
        repo.git("mv", "src/app.py", f"{RECORDS}/evidence/app.txt")
        repo.commit("code moved into the record directory")
        proc = self.check(repo)
        self.assertEqual(proc.returncode, 1, proc.stdout)
        self.assertIn("P-02 src/app.py", proc.stdout)

    def test_a_requirement_record_changed_after_the_review_is_a_violation(self):
        for name in ("requirements-graph.json", "problem-card.json", "challenge-report.json"):
            with self.subTest(name):
                repo = Repo(self)
                repo.first_round()
                repo.write(f"{RECORDS}/{name}", {"weakened": True})
                repo.commit(f"{name} changed in a records commit")
                proc = self.check(repo)
                self.assertEqual(proc.returncode, 1, proc.stdout)
                self.assertIn(f"P-02 {RECORDS}/{name}", proc.stdout)

    def test_evidence_that_is_only_staged_or_differs_from_its_commit_is_a_violation(self):
        ref = f"{RECORDS}/evidence/run.txt"
        cases = {"staged only": (f"{RECORDS}/evidence/staged.txt", "is staged but not committed"),
                 "changed after its commit": (ref, "differs from its committed version")}
        for name, (path, expected) in cases.items():
            with self.subTest(name):
                repo = Repo(self)
                _, change = repo.first_round()
                if path != ref:
                    repo.manifest(change, refs=(path,))
                    repo.commit("records naming a staged file")
                    repo.write(path, "staged\n")
                    repo.git("add", path)
                else:
                    repo.write(path, "rewritten after the commit\n")
                proc = self.check(repo)
                self.assertEqual(proc.returncode, 1, proc.stdout)
                self.assertIn(f"P-03 {path}: {expected}", proc.stdout)

    def test_a_requirement_record_changed_but_not_committed_is_a_violation(self):
        repo = Repo(self)
        repo.first_round()
        repo.write(f"{RECORDS}/requirements-graph.json", {"weakened": True})
        proc = self.check(repo)
        self.assertEqual(proc.returncode, 1, proc.stdout)
        self.assertIn(f"P-03 {RECORDS}/requirements-graph.json: differs from its committed version", proc.stdout)

    def test_a_reference_that_climbs_out_with_dot_dot_is_a_violation(self):
        repo = Repo(self)
        _, change = repo.first_round()
        ref = f"../{repo.root.name}/src/app.py"
        repo.manifest(change, refs=(ref,))
        repo.commit("records naming a path with ..")
        proc = self.check(repo)
        self.assertEqual(proc.returncode, 1, proc.stdout)
        self.assertIn(f"P-03 {ref}: is not a plain path inside the repository", proc.stdout)

    def test_url_evidence_is_not_opened(self):
        repo = Repo(self)
        repo.first_round()
        proc = self.check(repo)
        self.assertNotIn("ci.example.test", proc.stdout)


class BundleTests(unittest.TestCase):
    """bundle: the reviewer gets the change and this round's evidence, not the records."""

    def test_the_first_round_bundle_holds_the_change_and_not_the_records(self):
        repo = Repo(self)
        base, change = repo.first_round()
        out = out_dir(self)
        proc = run(repo, "bundle", "--records", RECORDS, "--base", base, "--out", str(out))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        diff = (out / "change.diff").read_text(encoding="utf-8")
        self.assertIn("src/app.py", diff)
        self.assertIn("+VALUE = 2", diff)
        self.assertEqual([line for line in diff.splitlines() if line.startswith("diff --git") and RECORDS in line],
                         [f"diff --git a/{RECORDS}/evidence/make.sh b/{RECORDS}/evidence/make.sh"])
        self.assertIn("T-PARENT", (out / "graph.diff").read_text(encoding="utf-8"))
        self.assertEqual(json.loads((out / "requirements-graph.json").read_text(encoding="utf-8")), GRAPH)
        manifest = json.loads((repo.root / RECORDS / "verification-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(json.loads((out / "manifest.json").read_text(encoding="utf-8")), manifest)
        self.assertIn(f"+++ b/{RECORDS}/evidence/make.sh", diff)  # a script in the record directory is part of the change
        self.assertEqual((out / "evidence" / RECORDS / "evidence" / "run.txt").read_text(encoding="utf-8"), "all 3 tests passed\n")
        self.assertEqual(sorted(p.relative_to(out / "evidence").as_posix() for p in (out / "evidence").rglob("*") if p.is_file()),
                         [f"{RECORDS}/evidence/run.txt"])
        self.assertEqual((out / "excluded.txt").read_text(encoding="utf-8").split(),
                         [f"{RECORDS}/problem-card.json", f"{RECORDS}/requirements-graph.json"])
        scope = json.loads((out / "scope.json").read_text(encoding="utf-8"))
        self.assertEqual((scope["scope"], scope["range"]), ("whole", [repo.git("rev-parse", base), change]))

    def test_an_out_directory_inside_the_repository_or_not_empty_is_refused(self):
        repo = Repo(self)
        base, _ = repo.first_round()
        inside = repo.root / "bundle"
        proc = run(repo, "bundle", "--records", RECORDS, "--base", base, "--out", str(inside))
        self.assertEqual(proc.returncode, 2, proc.stdout)
        self.assertFalse(inside.exists())
        full = out_dir(self)
        full.mkdir()
        (full / "keep.txt").write_text("x", encoding="utf-8")
        proc = run(repo, "bundle", "--records", RECORDS, "--base", base, "--out", str(full))
        self.assertEqual(proc.returncode, 2, proc.stdout)
        self.assertEqual([p.name for p in full.iterdir()], ["keep.txt"])

    def test_the_bundle_copies_the_committed_records_and_writes_only_under_out(self):
        repo = Repo(self)
        base, change = repo.first_round()
        repo.write(f"{RECORDS}/evidence/run.txt", "rewritten after the commit\n")
        repo.write(f"{RECORDS}/verification-manifest.json", {"not": "committed"})
        out = out_dir(self)
        proc = run(repo, "bundle", "--records", RECORDS, "--base", base, "--out", str(out))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual((out / "evidence" / RECORDS / "evidence" / "run.txt").read_text(encoding="utf-8"), "all 3 tests passed\n")
        self.assertEqual(json.loads((out / "manifest.json").read_text(encoding="utf-8"))["verification_manifest"]["reviewed_commit"], change)

    def test_a_reference_that_climbs_out_writes_nothing_outside_the_evidence_directory(self):
        repo = Repo(self)
        base, change = repo.first_round()
        # Two levels up from out/evidence reach out's parent, outside --out.
        climbing = f"../../{repo.root.parent.name}/{repo.root.name}/src/app.py"
        repo.manifest(change, refs=(climbing, f"{RECORDS}/evidence/run.txt"))
        repo.commit("records naming a path with ..")
        out = out_dir(self)
        proc = run(repo, "bundle", "--records", RECORDS, "--base", base, "--out", str(out))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual([p for p in out.parent.iterdir()], [out])
        self.assertEqual(sorted(p.relative_to(out).as_posix() for p in out.rglob("*") if p.is_file()),
                         sorted(["change.diff", "graph.diff", "requirements-graph.json", "manifest.json", "excluded.txt",
                                 "scope.json", f"evidence/{RECORDS}/evidence/run.txt"]))

    def test_the_previous_review_is_copied_into_the_bundle(self):
        repo = Repo(self)
        base, change = repo.first_round()
        fix = repo.next_round()
        review = out_dir(self).parent / "review-1.json"
        review.write_text('{"assurance_review": {"findings": []}}', encoding="utf-8")
        out = out_dir(self)
        proc = run(repo, "bundle", "--records", RECORDS, "--base", base, "--out", str(out), "--previous", change,
                   "--previous-review", str(review))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual((out / "previous-review.json").read_text(encoding="utf-8"), review.read_text(encoding="utf-8"))
        self.assertIn(fix[:7], proc.stdout)


class ScopeTests(unittest.TestCase):
    """bundle --previous: the whole diff only when the structure or the risk changed."""

    def scope(self, graph: dict | None = None, card: dict | None = None, risk: str = "medium") -> tuple[dict, str, str, str]:
        repo = Repo(self)
        base, change = repo.first_round()
        fix = repo.next_round(graph=graph, card=card, risk=risk)
        out = out_dir(self)
        proc = run(repo, "bundle", "--records", RECORDS, "--base", base, "--out", str(out), "--previous", change)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        return json.loads((out / "scope.json").read_text(encoding="utf-8")), repo.git("rev-parse", base), change, fix

    def test_a_change_to_text_fields_only_is_a_fix_round_from_the_previous_commit(self):
        graph = copy.deepcopy(GRAPH)
        graph["requirements"][0]["statement"] = "the root, said better"
        graph["requirements"][0]["assumptions"] = ["an assumption"]
        graph["requirements"][0]["counterexamples"] = ["a counterexample"]
        graph["requirements"][1]["acceptance"][0]["description"] = "a works, said better"
        scope, _, change, fix = self.scope(graph)
        self.assertEqual((scope["scope"], scope["range"], scope["reasons"]), ("fixes", [change, fix], []))

    def test_a_change_to_a_selection_condition_only_is_a_fix_round(self):
        with_or = copy.deepcopy(GRAPH)
        with_or["requirements"][0].update(decomposition="OR", selection={"REQ-A": "when a", "REQ-B": "when b"})
        reworded = copy.deepcopy(with_or)
        reworded["requirements"][0]["selection"]["REQ-A"] = "when a, said better"
        repo = Repo(self)
        base, change = repo.first_round(with_or)
        fix = repo.next_round(graph=reworded)
        out = out_dir(self)
        proc = run(repo, "bundle", "--records", RECORDS, "--base", base, "--out", str(out), "--previous", change)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        scope = json.loads((out / "scope.json").read_text(encoding="utf-8"))
        self.assertEqual((scope["scope"], scope["range"]), ("fixes", [change, fix]))

    def test_a_structural_change_makes_a_whole_round_from_the_base(self):
        def added_requirement(g):
            g["requirements"][0]["children"].append("REQ-C")
            g["requirements"].append({"id": "REQ-C", "statement": "c", "decomposition": "LEAF",
                                      "acceptance": [{"id": "T-C", "description": "c", "level": "L1"}]})
        changes = {
            "a requirement added": added_requirement,
            "a criterion added": lambda g: g["requirements"][1]["acceptance"].append({"id": "T-A2", "description": "x", "level": "L1"}),
            "a criterion replaced": lambda g: g["requirements"][0]["acceptance"].append({"id": "T-SYS", "description": "s", "level": "L3"})
            or g["requirements"][0]["acceptance"].pop(0),
            "a criterion removed": lambda g: g["requirements"][0]["acceptance"].clear(),
            "a level changed": lambda g: g["requirements"][0]["acceptance"][0].update(level="L3"),
            "a stage added": lambda g: g["requirements"][0]["acceptance"][0].update(stage="post_deploy"),
            "a decomposition changed": lambda g: g["requirements"][0].update(decomposition="OR", selection={"REQ-A": "x", "REQ-B": "y"}),
            "an origin added": lambda g: g["requirements"][1].update(origin={"kind": "instruction", "by": "owner", "ref": "issue 1"}),
        }
        for name, change in changes.items():
            with self.subTest(name):
                graph = copy.deepcopy(GRAPH)
                change(graph)
                scope, base, _, fix = self.scope(graph)
                self.assertEqual((scope["scope"], scope["range"]), ("whole", [base, fix]))
                self.assertTrue(scope["reasons"])

    def test_a_changed_problem_card_or_risk_class_makes_a_whole_round(self):
        card = copy.deepcopy(CARD)
        card["problem_card"]["gap"] = "another gap"
        self.assertEqual(self.scope(card=card)[0]["scope"], "whole")
        scope = self.scope(risk="high")[0]
        self.assertEqual(scope["scope"], "whole")
        self.assertTrue(any("medium" in r and "high" in r for r in scope["reasons"]), scope["reasons"])

    def test_a_previous_round_without_records_makes_a_whole_round(self):
        repo = Repo(self)
        repo.write("src/app.py", "VALUE = 1\n")
        base = repo.commit("base")
        repo.write("src/app.py", "VALUE = 2\n")
        previous = repo.commit("a commit no manifest names")
        repo.write(f"{RECORDS}/problem-card.json", CARD)
        repo.write(f"{RECORDS}/requirements-graph.json", GRAPH)
        change = repo.commit("change")
        repo.manifest(change)
        repo.write(f"{RECORDS}/evidence/run.txt", "ok\n")
        repo.commit("records")
        out = out_dir(self)
        proc = run(repo, "bundle", "--records", RECORDS, "--base", base, "--out", str(out), "--previous", previous)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        scope = json.loads((out / "scope.json").read_text(encoding="utf-8"))
        self.assertEqual(scope["scope"], "whole")
        self.assertEqual(len(scope["reasons"]), 3, scope["reasons"])  # no graph, no card, no manifest for it


if __name__ == "__main__":
    unittest.main()
