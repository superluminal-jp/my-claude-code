#!/usr/bin/env python3
"""Read-only decision for a pilot that compares the current review (arm A)
with the evidence-based one (arm B).

Formats and rules: references/pilot.md in this skill. The decision follows
the preregistration only: adopt when the median reduction of human minutes
per original request meets the preregistered target AND every preregistered
quality gate holds for arm B. Time saved never offsets a broken gate.

Exit codes: 0 adopt, 1 not_adopted, insufficient, or record violations,
2 input that cannot be interpreted (or a failure of the checker itself).
"""

from __future__ import annotations

import argparse
import datetime
import importlib.util
import json
import math
import statistics
import sys
import traceback
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple


def _load_assure() -> Any:
    """Loads assure.py from this file's own directory by its path, so the
    script also runs under ``python3 -I`` or PYTHONSAFEPATH, and writes no
    bytecode cache into the skill directory."""
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location("assure", Path(__file__).resolve().with_name("assure.py"))
    if spec is None or spec.loader is None:
        raise ImportError("assure.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["assure"] = module
    spec.loader.exec_module(module)
    return module


try:
    _assure = _load_assure()
except Exception as exc:  # a checker that cannot start must not look like exit code 1
    print(f"error: cannot load assure.py next to pilot.py ({type(exc).__name__})", file=sys.stderr)
    sys.exit(2)
FORMATS, InputError, Report, _Parser = _assure.FORMATS, _assure.InputError, _assure.Report, _assure._Parser
escape_unsafe, is_text, load_json, requested_format, show = (
    _assure.escape_unsafe, _assure.is_text, _assure.load_json, _assure.requested_format, _assure.show)

EXIT_ADOPT, EXIT_NOT_ADOPT, EXIT_INPUT_ERROR = 0, 1, 2
ARMS = ("A", "B")
PREREG_FIELDS = frozenset({"registered_at", "target_reduction", "minimum_cases_per_arm", "time_items", "quality_gates"})
CASE_FIELDS = frozenset({"case_id", "request_id", "arm", "stratum", "completed", "started_at", "minutes", "quality"})


def parse_date(value: Any) -> Optional[datetime.date]:
    if not isinstance(value, str):
        return None
    try:
        return datetime.date.fromisoformat(value)
    except ValueError:
        return None


def is_number(value: Any) -> bool:
    """A finite number; JSON's non-standard NaN and Infinity are not."""
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def load_body(path: str, key: str, what: str, kind: type) -> Any:
    document = load_json(path, what)
    if not isinstance(document, dict) or set(document) != {"schema_version", key} or type(document["schema_version"]) is not int or document["schema_version"] != 1:
        raise InputError(f"{what} must have exactly schema_version 1 and {key}")
    if not isinstance(document[key], kind):
        raise InputError(f"{key} must be {'an object' if kind is dict else 'an array'}")
    return document[key]


def check_records(reg: Dict[str, Any], cases: List[Any]) -> List[Dict[str, Any]]:
    """E-00 (shape) and E-01 (one sample per original request and arm)."""
    report = Report()
    for key in sorted(set(reg) - PREREG_FIELDS):
        report.add("E-00", -1, None, f"preregistration has an undefined field {show(key)}")
    if parse_date(reg.get("registered_at")) is None:
        report.add("E-00", -1, None, "registered_at must be a date (YYYY-MM-DD)")
    target = reg.get("target_reduction")
    if not is_number(target) or not 0 < target < 1:
        report.add("E-00", -1, None, "target_reduction must be a number between 0 and 1")
    if type(reg.get("minimum_cases_per_arm")) is not int or reg["minimum_cases_per_arm"] < 1:
        report.add("E-00", -1, None, "minimum_cases_per_arm must be a positive integer")
    for name in ("time_items", "quality_gates"):
        values = reg.get(name)
        if not isinstance(values, list) or not values or not all(is_text(v) for v in values) or len(set(values)) != len(values):
            report.add("E-00", -1, None, f"{name} must be a non-empty array of distinct strings")
    # Only string entries go into the sets; anything else is reported above.
    items = {v for v in reg.get("time_items", []) if isinstance(v, str)} if isinstance(reg.get("time_items"), list) else set()
    gates = {v for v in reg.get("quality_gates", []) if isinstance(v, str)} if isinstance(reg.get("quality_gates"), list) else set()
    case_ids, requests = set(), set()
    for position, entry in enumerate(cases):
        if not isinstance(entry, dict):
            report.add("E-00", position, None, f"case #{position + 1} is not an object")
            continue
        node = entry.get("case_id") if is_text(entry.get("case_id")) else None
        for key in sorted(set(entry) - CASE_FIELDS):
            report.add("E-00", position, node, f"undefined field {show(key)}")
        for name in ("case_id", "request_id", "stratum"):
            if not is_text(entry.get(name)):
                report.add("E-00", position, node, f"{name} must be a non-empty string")
        if entry.get("arm") not in ARMS:
            report.add("E-00", position, node, "arm must be A or B")
        if not isinstance(entry.get("completed"), bool):
            report.add("E-00", position, node, "completed must be true or false")
        if parse_date(entry.get("started_at")) is None:
            report.add("E-00", position, node, "started_at must be a date (YYYY-MM-DD)")
        minutes = entry.get("minutes")
        if (not isinstance(minutes, dict) or set(minutes) != items or not all(is_number(v) and v >= 0 for v in minutes.values())
                or not math.isfinite(sum(minutes.values()))):
            report.add("E-00", position, node, "minutes must give a non-negative number for exactly the preregistered time items")
        quality = entry.get("quality")
        needs_quality = entry.get("arm") == "B" and entry.get("completed") is True
        if (quality is not None or needs_quality) and (
            not isinstance(quality, dict) or set(quality) != gates or not all(isinstance(v, bool) for v in quality.values())
        ):
            report.add("E-00", position, node, "quality must give true or false for exactly the preregistered gates")
        # Only valid values are compared, so a missing id is not reported as a
        # duplicate and an unhashable value cannot crash the check.
        if node is not None:
            if node in case_ids:
                report.add("E-01", position, node, "case_id is used twice")
            case_ids.add(node)
        if entry.get("arm") in ARMS and is_text(entry.get("request_id")):
            request = (entry["arm"], entry["request_id"])
            if request in requests:
                report.add("E-01", position, node, f"request {show(entry['request_id'])} is counted twice in arm {entry['arm']}; one original request is one sample")
            requests.add(request)
    return report.violations()


def exact(value: Any) -> Fraction:
    """The number as written in the record: 0.2 is one fifth, not the nearest
    binary fraction, so a reduction exactly at the target meets it."""
    return Fraction(repr(value)) if isinstance(value, float) else Fraction(value)


def total(entry: Dict[str, Any]) -> Fraction:
    return sum((exact(v) for v in entry["minutes"].values()), Fraction(0))


def median_or_none(values: List[Fraction]) -> Optional[Fraction]:
    return statistics.median(values) if values else None


def as_float(value: Optional[Fraction]) -> Optional[float]:
    return None if value is None else float(value)


def decide(reg: Dict[str, Any], cases: List[Dict[str, Any]]) -> Dict[str, Any]:
    reasons: List[Tuple[str, str]] = []
    arms: Dict[str, Dict[str, Any]] = {}
    for arm in ARMS:
        done = [total(c) for c in cases if c["arm"] == arm and c["completed"]]
        everything = [total(c) for c in cases if c["arm"] == arm]
        arms[arm] = {"completed": len(done), "incomplete": len(everything) - len(done),
                     "median": median_or_none(done), "median_with_incomplete": median_or_none(everything)}
        if len(done) < reg["minimum_cases_per_arm"]:
            reasons.append(("insufficient", f"arm {arm} has {len(done)} completed cases; the preregistration needs {reg['minimum_cases_per_arm']}"))
    first_case = min(datetime.date.fromisoformat(c["started_at"]) for c in cases) if cases else None
    if first_case is not None and datetime.date.fromisoformat(reg["registered_at"]) > first_case:
        reasons.append(("insufficient", f"the preregistration ({reg['registered_at']}) is later than the first case ({first_case}); the rule may have been set after seeing results"))
    strata = []
    names = sorted({c["stratum"] for c in cases if c["completed"]})
    for name in names:
        per_arm = {arm: [total(c) for c in cases if c["completed"] and c["stratum"] == name and c["arm"] == arm] for arm in ARMS}
        if not per_arm["A"] or not per_arm["B"]:
            only = "A" if per_arm["A"] else "B"
            reasons.append(("insufficient", f"stratum {show(name)} has completed cases in arm {only} only, so the arms are not comparable"))
            continue
        a, b = statistics.median(per_arm["A"]), statistics.median(per_arm["B"])
        strata.append({"stratum": name, "median_A": float(a), "median_B": float(b),
                       "reduction": float(1 - b / a) if a else None, "b_slower": b > a})
    quality_failures = [{"case_id": c["case_id"], "gate": gate}
                        for c in cases if c["arm"] == "B" and isinstance(c.get("quality"), dict)
                        for gate in reg["quality_gates"] if c["quality"].get(gate) is False]
    reduction = None
    a_median, b_median = arms["A"]["median"], arms["B"]["median"]
    if a_median:
        reduction = 1 - b_median / a_median if b_median is not None else None
    elif a_median == 0:
        reasons.append(("insufficient", "the median of arm A is 0 minutes, so no reduction can be computed"))
    if not any(kind == "insufficient" for kind, _ in reasons):
        if quality_failures:
            reasons.append(("not_adopted", f"{len(quality_failures)} quality gate result(s) failed in arm B; time saved does not offset them"))
        if reduction is not None and reduction < exact(reg["target_reduction"]):
            reasons.append(("not_adopted", f"the median reduction {float(reduction):.3f} is below the preregistered target {reg['target_reduction']}"))
        # A pooled median can improve while every stratum gets slower when
        # cases are spread unevenly over strata, so a slower stratum blocks adoption.
        for stratum in strata:
            if stratum["b_slower"]:
                reasons.append(("not_adopted", f"arm B is slower than arm A in stratum {show(stratum['stratum'])}"))
    kinds = {kind for kind, _ in reasons}
    decision = "insufficient" if "insufficient" in kinds else ("not_adopted" if kinds else "adopt")
    for data in arms.values():
        data["median"], data["median_with_incomplete"] = as_float(data["median"]), as_float(data["median_with_incomplete"])
    return {"decision": decision, "reduction": as_float(reduction), "target_reduction": reg["target_reduction"], "arms": arms,
            "strata": strata, "quality_failures": quality_failures,
            "reasons": [{"kind": kind, "message": message} for kind, message in reasons]}


def emit(result: Dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return
    if result.get("status") == "error":
        print(f"error: {result['error']}", file=sys.stderr)
        return
    for violation in result.get("violations", []):
        print(f"{violation['rule_id']}: {violation['message']}")
    if result.get("decision") is None:
        print("Result: the records violate the format; no decision")
        return
    for arm, data in result["arms"].items():
        print(f"Arm {arm}: {data['completed']} completed, {data['incomplete']} incomplete; median {data['median']} min "
              f"(with incomplete {data['median_with_incomplete']} min)")
    for stratum in result["strata"]:
        mark = "  <- B slower" if stratum["b_slower"] else ""
        cut = "n/a" if stratum["reduction"] is None else f"{stratum['reduction']:.3f}"
        print(f"Stratum {escape_unsafe(stratum['stratum'])}: A {stratum['median_A']} min, B {stratum['median_B']} min, reduction {cut}{mark}")
    for failure in result["quality_failures"]:
        print(f"Quality gate failed: {escape_unsafe(failure['case_id'])} {escape_unsafe(failure['gate'])}")
    for reason in result["reasons"]:
        print(f"{reason['kind']}: {reason['message']}")
    reduction = "n/a" if result["reduction"] is None else f"{result['reduction']:.3f}"
    print(f"Result: {result['decision']} (median reduction {reduction}, target {result['target_reduction']}; synthetic or real data is not checked)")


def run(argv: Sequence[str], output_format: str) -> int:
    # The same parser as assure.py: an argument error is reported in the
    # requested format with argparse's message; --help exits 0 with help only.
    _Parser.output_format = output_format
    parser = _Parser(prog="pilot.py", description="Decide a pilot from its preregistration (read-only).")
    parser.add_argument("--format", choices=FORMATS, default="text")
    parser.add_argument("preregistration")
    parser.add_argument("cases")
    args = parser.parse_args(argv)
    base = {"output_version": 1, "input_file": [args.preregistration, args.cases], "status": "error", "error": None}
    try:
        reg = load_body(args.preregistration, "pilot_preregistration", "the preregistration", dict)
        cases = load_body(args.cases, "pilot_cases", "the case records", list)
    except InputError as exc:
        emit(dict(base, error=str(exc)), args.format)
        return EXIT_INPUT_ERROR
    violations = check_records(reg, cases)
    if violations:
        emit(dict(base, status="failed", decision=None, violations=violations), args.format)
        return EXIT_NOT_ADOPT
    result = dict(base, violations=[], **decide(reg, cases))
    result["status"] = "passed" if result["decision"] == "adopt" else "failed"
    emit(result, args.format)
    return EXIT_ADOPT if result["decision"] == "adopt" else EXIT_NOT_ADOPT


def main(argv: Optional[Sequence[str]] = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    output_format = requested_format(arguments)
    try:
        return run(arguments, output_format)
    except Exception as exc:
        traceback.print_exc()
        emit({"status": "error", "error": f"internal error: {type(exc).__name__}"}, output_format)
        return EXIT_INPUT_ERROR


if __name__ == "__main__":
    sys.exit(main())
