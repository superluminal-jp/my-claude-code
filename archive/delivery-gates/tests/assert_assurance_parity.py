#!/usr/bin/env python3
"""spec 064 FR-007: the assurance gate (verify-change) re-checks part of the
requirements graph structure that specify-requirements's checker owns (rule A-09).
The rules live in two places, so this check runs both checkers over every
requirements graph in specify-requirements's test fixtures:

- a graph that specify-requirements's checker accepts passes the gate;
- a graph it rejects under a rule the gate depends on does not pass the gate.

Each graph is given a manifest in which every acceptance criterion passed on
one commit at low risk, so only the graph can stop the gate. A fixture that
is not a readable JSON object with a requirements array, or whose schema
version is neither 1 nor 2, is skipped: those are input errors, not structure.

Usage: assert_assurance_parity.py REPO_ROOT. Exit 0 when every graph agrees,
1 otherwise.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# A-09 re-checks these; S-07 (an undefined level or a reused acceptance id) is
# refused by the gate as an input error (exit 2).
GATE_DEPENDS_ON = {"S-01", "S-02", "S-03", "S-04", "S-06", "S-07", "S-11", "S-12"}
SHA = "0f5a148c2d7a9e1b3f6a8c0d2e4f6a8b0c2d4e6f"


def strict_pairs(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
    keys = [key for key, _ in pairs]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate key")
    return dict(pairs)


def graph_v2(path: Path) -> Optional[Dict[str, Any]]:
    try:
        doc = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=strict_pairs)
    except ValueError:
        return None
    if not isinstance(doc, dict) or not isinstance(doc.get("requirements"), list):
        return None
    if doc.get("schema_version") == 1:
        return {"schema_version": 2, "problem_id": "PRB-PARITY", "requirements": doc["requirements"]}
    if doc.get("schema_version") == 2 and isinstance(doc.get("problem_id"), str) and doc["problem_id"].strip():
        return doc
    return None


def passing_manifest(graph: Dict[str, Any]) -> Dict[str, Any]:
    ids = []
    for node in graph["requirements"]:
        entries = node.get("acceptance") if isinstance(node, dict) else None
        for entry in entries if isinstance(entries, list) else []:
            if isinstance(entry, dict) and isinstance(entry.get("id"), str) and entry["id"] not in ids:
                ids.append(entry["id"])
    evidence = {"kind": "ci_job", "ref": "https://ci.example.test/runs/1", "commit": SHA}
    return {"schema_version": 1, "verification_manifest": {
        "change_id": "CHG-PARITY", "problem_id": graph["problem_id"], "reviewed_commit": SHA, "implementer": "claude",
        "risk": {"class": "low", "rationale": "parity check"}, "approvals": [],
        "checks": [{"check_id": i, "status": "passed", "evidence": dict(evidence)} for i in ids],
        "test_changes": [], "infra_changes": []}}


def run_json(*args: str) -> Tuple[int, Any]:
    proc = subprocess.run([sys.executable, "-B", "-I", *args], capture_output=True, text=True, timeout=120)
    try:
        return proc.returncode, json.loads(proc.stdout)
    except ValueError:
        return proc.returncode, None


def main(argv: List[str]) -> int:
    root = Path(argv[1]) if len(argv) > 1 else Path(__file__).resolve().parent.parent
    skills = root / "harness" / "skills"
    checker = skills / "specify-requirements" / "scripts" / "check_graph.py"
    gate = skills / "verify-change" / "scripts" / "assure.py"
    fixtures = skills / "specify-requirements" / "tests" / "fixtures"
    paths = sorted((fixtures / "requirements").glob("*.json")) + sorted((fixtures / "gate").glob("graph-*.json"))
    failures = compared = 0
    with tempfile.TemporaryDirectory() as tmp:
        for path in paths:
            graph = graph_v2(path)
            if graph is None:
                print(f"skip {path.name}: not a readable version 1 or 2 requirements graph")
                continue
            graph_file, manifest_file = Path(tmp) / "graph.json", Path(tmp) / "manifest.json"
            graph_file.write_text(json.dumps(graph), encoding="utf-8")
            manifest_file.write_text(json.dumps(passing_manifest(graph)), encoding="utf-8")
            code, result = run_json(str(checker), "--format", "json", str(graph_file))
            rules = {v["rule_id"] for v in result["violations"]} if code in (0, 1) and result else set()
            gate_code, gate_result = run_json(str(gate), "--format", "json", "gate", str(graph_file), str(manifest_file))
            passed = gate_code == 0
            if code == 0:
                expected, ok = "pass", passed
            elif rules & GATE_DEPENDS_ON:
                expected, ok = "not pass", not passed
            else:
                print(f"skip {path.name}: rejected only under {sorted(rules)}, which the gate does not depend on")
                continue
            compared += 1
            decision = gate_result.get("decision", gate_result.get("status")) if isinstance(gate_result, dict) else None
            print(f"{'ok  ' if ok else 'FAIL'} {path.name}: checker {sorted(rules) or 'passed'}, "
                  f"gate {decision} (exit {gate_code}), expected {expected}")
            failures += 0 if ok else 1
    print(f"{compared} graphs compared, {failures} disagreed")
    return 1 if failures or not compared else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
