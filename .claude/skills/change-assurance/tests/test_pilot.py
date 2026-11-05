"""Acceptance tests for the pilot decision (references/pilot.md).

All data here is synthetic: it tests the arithmetic and the rules, and is not
the result of any experiment.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

CHECKER = Path(__file__).resolve().parent.parent / "scripts" / "pilot.py"
ITEMS = ["request", "rereading", "instructions", "reading", "review", "rework", "approval"]
GATES = ["required_ci_kept", "no_new_missed_known_defect", "parent_failure_rejected", "no_unapproved_high_risk"]


def prereg(**changes) -> dict:
    body = {"registered_at": "2026-11-10", "target_reduction": 0.2, "minimum_cases_per_arm": 3,
            "time_items": ITEMS, "quality_gates": GATES}
    body.update(changes)
    return {"schema_version": 1, "pilot_preregistration": body}


def case(case_id: str, arm: str, total: float, stratum: str = "api", completed: bool = True,
         started_at: str = "2026-11-12", quality: dict | None = None, request_id: str | None = None) -> dict:
    minutes = dict.fromkeys(ITEMS, 0)
    minutes["review"] = total
    out = {"case_id": case_id, "request_id": request_id or f"R-{case_id}", "arm": arm, "stratum": stratum,
           "completed": completed, "started_at": started_at, "minutes": minutes}
    if arm == "B":
        out["quality"] = quality if quality is not None else dict.fromkeys(GATES, True)
    return out


def baseline() -> list[dict]:
    return ([case(f"A{i}", "A", t) for i, t in enumerate((40, 50, 60))]
            + [case(f"B{i}", "B", t) for i, t in enumerate((30, 35, 40))])


class PilotTestCase(unittest.TestCase):
    def decide(self, cases: list[dict], registration: dict | None = None) -> tuple[int, dict]:
        directory = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: ([p.unlink() for p in directory.iterdir()], directory.rmdir()))
        reg = directory / "prereg.json"
        reg.write_text(json.dumps(registration or prereg()), encoding="utf-8")
        records = directory / "cases.json"
        records.write_text(json.dumps({"schema_version": 1, "pilot_cases": cases}), encoding="utf-8")
        proc = subprocess.run([sys.executable, "-B", str(CHECKER), "--format", "json", str(reg), str(records)],
                              capture_output=True, text=True, timeout=60)
        return proc.returncode, json.loads(proc.stdout)


class DecisionTests(PilotTestCase):
    """User Story 1: the preregistered rule decides adoption."""

    def test_p5_02_thirty_percent_with_quality_kept_is_adopted(self):
        code, result = self.decide(baseline())
        self.assertEqual((code, result["decision"]), (0, "adopt"), result)
        self.assertAlmostEqual(result["reduction"], 0.30)
        self.assertEqual((result["arms"]["A"]["median"], result["arms"]["B"]["median"]), (50, 35))

    def test_ten_percent_is_not_adopted(self):
        cases = baseline()[:3] + [case(f"B{i}", "B", 45) for i in range(3)]
        code, result = self.decide(cases)
        self.assertEqual((code, result["decision"]), (1, "not_adopted"))

    def test_p5_03_a_broken_quality_gate_is_not_adopted_despite_the_time(self):
        cases = baseline()
        cases[4]["quality"]["parent_failure_rejected"] = False
        code, result = self.decide(cases)
        self.assertEqual(result["decision"], "not_adopted")
        self.assertEqual(result["quality_failures"], [{"case_id": "B1", "gate": "parent_failure_rejected"}])

    def test_preregistration_after_the_first_case_is_insufficient(self):
        code, result = self.decide(baseline(), prereg(registered_at="2026-11-13"))
        self.assertEqual((code, result["decision"]), (1, "insufficient"))

    def test_too_few_completed_cases_is_insufficient(self):
        cases = baseline()
        cases[5]["completed"] = False
        self.assertEqual(self.decide(cases)[1]["decision"], "insufficient")


class SampleTests(PilotTestCase):
    """User Story 2: skew and missing data are shown, not hidden."""

    def test_p5_01_one_request_counted_twice_in_an_arm_is_a_violation(self):
        cases = baseline() + [case("B9", "B", 20, request_id="R-B0")]
        code, result = self.decide(cases)
        self.assertEqual((code, result["decision"]), (1, None))
        self.assertEqual({v["rule_id"] for v in result["violations"]}, {"E-01"})

    def test_p5_01_time_items_must_match_the_preregistration(self):
        cases = baseline()
        cases[0]["minutes"]["waiting_for_ai"] = 5
        code, result = self.decide(cases)
        self.assertEqual({v["rule_id"] for v in result["violations"]}, {"E-00"})

    def test_p5_04_strata_are_compared_and_slower_strata_are_named(self):
        cases = baseline() + [case("A7", "A", 20, "ui"), case("B7", "B", 30, "ui")]
        result = self.decide(cases)[1]
        by_stratum = {s["stratum"]: s for s in result["strata"]}
        self.assertTrue(by_stratum["ui"]["b_slower"])
        self.assertFalse(by_stratum["api"]["b_slower"])

    def test_p5_05_a_stratum_in_one_arm_only_is_insufficient(self):
        cases = baseline() + [case("B7", "B", 30, "iac")]
        result = self.decide(cases)[1]
        self.assertEqual(result["decision"], "insufficient")
        self.assertTrue(any("iac" in r["message"] for r in result["reasons"]))

    def test_p5_06_incomplete_cases_are_counted_and_shown(self):
        cases = baseline() + [case("A9", "A", 120, completed=False)]
        result = self.decide(cases)[1]
        self.assertEqual(result["arms"]["A"]["incomplete"], 1)
        self.assertEqual(result["arms"]["A"]["median"], 50)
        self.assertEqual(result["arms"]["A"]["median_with_incomplete"], 55)


if __name__ == "__main__":
    unittest.main()
