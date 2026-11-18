#!/usr/bin/env python3
"""spec 068: one made-up change carried from decomposition to acceptance by
both bundled checkers, through what spec 068 added: a requirement directed by
a person (origin), a criterion verified only after deploy (stage), Jest's
--json results (collect-jest), a delta assurance review, the decision before
deploy (gate --stage pre_deploy), and the review card that shows both
decisions.

Usage: assert_delivery_flow.py REPO_ROOT. Prints one line per check and exits
0 when every check holds, 1 otherwise. Reads tests/fixtures/delivery-flow/ and
writes only to a temporary directory.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

SHA = "2b4d6f8a0c2e4a6b8d0f2a4c6e8b0d2f4a6c8e0b"
POST_DEPLOY = "FLOW-PROD-001"


def parsed(out: str) -> Dict[str, Any]:
    """A checker's JSON result with the fields the checks read filled in when
    it printed none, so a broken checker fails a check instead of raising."""
    try:
        result = json.loads(out)
    except ValueError:
        result = None
    result = result if isinstance(result, dict) else {}
    return {"decision": None, "challenge": None, "left_out": None, "reasons": []} | result


def run(*args: str) -> Tuple[int, str]:
    proc = subprocess.run([sys.executable, "-B", "-I", *args], capture_output=True, text=True, timeout=120)
    return proc.returncode, proc.stdout


def main(argv: List[str]) -> int:
    root = Path(argv[1]) if len(argv) > 1 else Path(__file__).resolve().parent.parent
    skills = root / "harness" / "skills"
    check_graph = str(skills / "specify-requirements" / "scripts" / "check_graph.py")
    assure = str(skills / "verify-change" / "scripts" / "assure.py")
    flow = root / "tests" / "fixtures" / "delivery-flow"
    card, graph, report, review = (str(flow / name) for name in
                                   ("problem-card.json", "requirements-graph.json", "challenge-report.json", "assurance-review.json"))
    failures: List[str] = []

    def expect(name: str, ok: bool, detail: Any = "") -> None:
        print(f"{'ok  ' if ok else 'FAIL'} {name}" + ("" if ok else f": {detail}"))
        if not ok:
            failures.append(name)

    with tempfile.TemporaryDirectory() as tmp:
        def manifest(change: Callable[[Dict[str, Any]], None] = lambda checks: None) -> str:
            checks = {c["check_id"]: c for c in collected}
            change(checks)
            path = Path(tmp) / "manifest.json"
            path.write_text(json.dumps({"schema_version": 1, "verification_manifest": {
                "change_id": "CHG-FLOW", "problem_id": "PRB-FLOW", "reviewed_commit": SHA, "implementer": "claude",
                "risk": {"class": "medium", "rationale": "an import job and its schedule"}, "approvals": [],
                "checks": list(checks.values()), "test_changes": [], "infra_changes": []}}), encoding="utf-8")
            return str(path)

        def gate(path: str, *extra: str) -> Dict[str, Any]:
            code, out = run(assure, "--format", "json", "gate", graph, path, "--report", report, "--review", review, *extra)
            return parsed(out) | {"exit": code}

        code, out = run(check_graph, "--format", "json", "--gate", card, graph, report)
        decided = parsed(out)
        expect("decomposition gate is ready with the challenge recorded (origin is accepted)",
               code == 0 and decided["decision"] == "ready" and decided["challenge"] == "recorded", decided["reasons"])

        code, out = run(assure, "collect-jest", str(flow / "jest.json"), "--graph", graph, "--commit", SHA,
                        "--ref", "evidence/2b4d6f8/jest.json", "--kind", "local_run")
        try:
            collected = json.loads(out) if code == 0 else []
        except ValueError:
            collected = []
        statuses = {c.get("check_id"): c.get("status") for c in collected if isinstance(c, dict)}
        expect("collect-jest passes the three criteria the Jest run names and leaves the post-deploy one not_run",
               statuses == {"FLOW-PARENT-001": "passed", "FLOW-PROD-001": "not_run", "FLOW-LEAF-001": "passed", "FLOW-LEAF-002": "passed"},
               statuses)

        before_deploy = manifest()
        result = gate(before_deploy, "--stage", "pre_deploy")
        expect("[R4-A1] before deploy, the gate passes and leaves out only the post-deploy check",
               result["exit"] == 0 and result["decision"] == "pass" and result["left_out"] == [POST_DEPLOY], result)
        result = gate(before_deploy)
        expect("[R4-A1] for acceptance, the gate is blocked by the post-deploy check alone",
               result["exit"] == 1 and result["decision"] == "blocked"
               and [(r["rule_id"], r["message"]) for r in result["reasons"]] == [("A-03", f'"{POST_DEPLOY}" (L3) is not_run')],
               result["reasons"])
        code, text = run(assure, "card", "--problem", card, "--graph", graph, "--manifest", before_deploy,
                         "--report", report, "--review", review, "--lang", "ja")
        expect("[R4-A1] the card shows both decisions, offers the deploy decision, and names who directed REQ-DEV-HOURLY",
               code == 1 and "**判定: ⛔ blocked**" in text
               and f"**deploy の前の判定: pass**（まだ走っていない deploy の後の検査 1 件を除く: `{POST_DEPLOY}`）" in text
               and "deploy してよいかを決める。" in text and "— owner-a の指示（会話 2026-11-08 の質問2の回答）" in text, text)

        def failed(checks: Dict[str, Any]) -> None:
            checks[POST_DEPLOY] = {"check_id": POST_DEPLOY, "status": "failed",
                                   "evidence": {"kind": "human_review", "ref": "production observation, day 1", "commit": SHA}}
        result = gate(manifest(failed), "--stage", "pre_deploy")
        expect("[R4-A2] a failed post-deploy check fails the decision before deploy too",
               result["exit"] == 1 and result["decision"] == "fail" and result["left_out"] == [], result)

        def observed(checks: Dict[str, Any]) -> None:
            checks[POST_DEPLOY] = {"check_id": POST_DEPLOY, "status": "passed",
                                   "evidence": {"kind": "human_review", "ref": "production observation, day 1", "commit": SHA}}
        after_deploy = manifest(observed)
        result = gate(after_deploy)
        expect("after deploy, with the post-deploy evidence recorded, the gate passes",
               result["exit"] == 0 and result["decision"] == "pass", result["reasons"])
        code, text = run(assure, "card", "--problem", card, "--graph", graph, "--manifest", after_deploy,
                         "--report", report, "--review", review)
        expect("after deploy, the card shows the pass mark and both decisions pass",
               code == 0 and "**Decision: ✅ pass**" in text and "**Before deploy: pass**\n" in text
               and "Accept or return the change." in text, text)

    print(f"{'all checks hold' if not failures else f'{len(failures)} checks failed'} (R0-A1: the flow as a whole)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
