#!/usr/bin/env python3
"""spec 069: one made-up change taken through two assurance review rounds with
verify-change's scripts/review_prep.py, in a temporary git repository:
check before the first round, the first round's bundle, a fix that changes
only the graph's text (a fix round), a fix that adds an acceptance criterion
(a whole round), and a commit outside the record directory after the review.

Usage: assert_review_prep_flow.py REPO_ROOT. Prints one line per check and
exits 0 when every check holds, 1 otherwise. Writes only to temporary
directories.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, List

RECORDS = "specs/001-flow"
GRAPH = {"schema_version": 2, "problem_id": "PRB-FLOW", "requirements": [
    {"id": "REQ-ROOT", "statement": "orders are private", "decomposition": "AND", "children": ["REQ-READ", "REQ-LIST"],
     "acceptance": [{"id": "T-PARENT", "description": "read and list together", "level": "L2"}]},
    {"id": "REQ-READ", "statement": "read is private", "decomposition": "LEAF", "acceptance": [{"id": "T-READ", "description": "404 to others", "level": "L1"}]},
    {"id": "REQ-LIST", "statement": "list is private", "decomposition": "LEAF", "acceptance": [{"id": "T-LIST", "description": "own orders only", "level": "L1"}]}]}
CARD = {"schema_version": 1, "problem_card": {"id": "PRB-FLOW", "ideal": "i", "current": "c", "gap": "g", "significance": "s",
                                               "status": "verified", "evidence": [{"source": "x", "observation": "y"}]}}


def main(argv: List[str]) -> int:
    root = (Path(argv[1]) if len(argv) > 1 else Path(__file__).parent.parent).resolve()
    script = root / "harness" / "skills" / "verify-change" / "scripts" / "review_prep.py"
    work = Path(tempfile.mkdtemp())
    repo = work / "repo"
    repo.mkdir()
    failures: List[str] = []

    def expect(name: str, ok: bool, detail: Any = "") -> None:
        print(f"{'ok  ' if ok else 'FAIL'} {name}" + ("" if ok else f": {detail}"))
        if not ok:
            failures.append(name)

    def git(*args: str) -> str:
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.test", "-c", "commit.gpgsign=false",
                               "-c", "core.hooksPath=/dev/null", *args], cwd=repo, check=True, capture_output=True,
                              text=True, timeout=60).stdout.strip()

    def write(rel: str, content: Any) -> None:
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content if isinstance(content, str) else json.dumps(content, indent=2), encoding="utf-8")

    def commit(message: str) -> str:
        git("add", "-A")
        git("commit", "-q", "-m", message)
        return git("rev-parse", "HEAD")

    def records(reviewed: str, note: str) -> None:
        write(f"{RECORDS}/verification-manifest.json", {"schema_version": 1, "verification_manifest": {
            "change_id": "CHG-FLOW", "problem_id": "PRB-FLOW", "reviewed_commit": reviewed, "implementer": "claude",
            "risk": {"class": "medium", "rationale": "r"}, "approvals": [], "test_changes": [], "infra_changes": [],
            "checks": [{"check_id": c, "status": "passed", "evidence": {"kind": "local_run", "ref": f"{RECORDS}/evidence/tests.txt", "commit": reviewed}}
                       for c in ("T-PARENT", "T-READ", "T-LIST")]}})
        write(f"{RECORDS}/evidence/tests.txt", note)
        commit(f"records for {reviewed[:7]}")

    def run(*args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, "-B", str(script), *args], cwd=repo, capture_output=True, text=True, timeout=120)

    def bundle(*extra: str) -> tuple[subprocess.CompletedProcess, Path]:
        out = work / f"bundle-{len(list(work.glob('bundle-*')))}"
        return run("bundle", "--records", RECORDS, "--base", base, "--out", str(out), *extra), out

    try:
        git("init", "-q", "-b", "main")
        write("src/orders.py", "def read(user, order):\n    return order\n")
        base = commit("base")
        write("src/orders.py", "def read(user, order):\n    return order if order.owner == user else None\n")
        write(f"{RECORDS}/problem-card.json", CARD)
        write(f"{RECORDS}/requirements-graph.json", GRAPH)
        first = commit("change: read checks the owner")
        records(first, "3 passed\n")

        proc = run("check", "--records", RECORDS)
        expect("check before the first round finds no record error", proc.returncode == 0, proc.stdout)
        proc, out = bundle()
        diff = (out / "change.diff").read_text(encoding="utf-8") if proc.returncode == 0 else ""
        expect("the first round's bundle holds the code change and no record file",
               "src/orders.py" in diff and RECORDS not in diff and (out / "evidence" / RECORDS / "evidence" / "tests.txt").is_file(),
               proc.stdout + proc.stderr)

        graph = json.loads(json.dumps(GRAPH))
        graph["requirements"][1]["statement"] = "reading another user's order returns nothing"
        write(f"{RECORDS}/requirements-graph.json", graph)
        write("src/orders.py", "def read(user, order):\n    return order if order.owner == user else None  # private\n")
        second = commit("fix: words of REQ-READ")
        records(second, "3 passed again\n")
        proc, out = bundle("--previous", first)
        scope = json.loads((out / "scope.json").read_text(encoding="utf-8")) if proc.returncode == 0 else {}
        graph_diff = (out / "graph.diff").read_text(encoding="utf-8") if proc.returncode == 0 else ""
        expect("a fix that changes only the graph's text is a fix round from the previous reviewed commit",
               scope.get("scope") == "fixes" and scope.get("range") == [first, second] and "returns nothing" in graph_diff, scope)

        graph["requirements"][2]["acceptance"].append({"id": "T-LIST-EMPTY", "description": "an empty list for a new user", "level": "L1"})
        write(f"{RECORDS}/requirements-graph.json", graph)
        third = commit("fix: a criterion for the empty list")
        records(third, "4 passed\n")
        proc, out = bundle("--previous", second)
        scope = json.loads((out / "scope.json").read_text(encoding="utf-8")) if proc.returncode == 0 else {}
        expect("a fix that adds an acceptance criterion is a whole round from the base",
               scope.get("scope") == "whole" and scope.get("range") == [git("rev-parse", base), third]
               and any("REQ-LIST" in r for r in scope.get("reasons", [])), scope)

        write("src/orders.py", "def read(user, order):\n    return order\n")
        commit("a code change slipped in after the review")
        proc = run("check", "--records", RECORDS)
        expect("check finds a code change committed after the reviewed commit",
               proc.returncode == 1 and "P-02 src/orders.py" in proc.stdout, proc.stdout)
    finally:
        shutil.rmtree(work, ignore_errors=True)

    print(f"{'all checks hold' if not failures else f'{len(failures)} checks failed'} (R0-A1: two review rounds with review_prep.py)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
