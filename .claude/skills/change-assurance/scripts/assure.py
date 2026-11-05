#!/usr/bin/env python3
"""Read-only assurance checker for a verification manifest.

Formats and rules: references/manifest.md in this skill. The checker reads
its inputs and nothing else: it writes no file, opens no network connection,
starts no process, and never executes input content. A ``pass`` means the
records are consistent with the rules; whether a recorded evidence reference
really shows that result is up to the system that produced it.

Exit codes: 0 pass (or no violation), 1 fail, blocked, or violations,
2 input that cannot be interpreted (or a failure of the checker itself).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
import sys
import traceback
import unicodedata
import xml.etree.ElementTree as ElementTree
import xml.parsers.expat as expat
from typing import Any, Dict, List, NoReturn, Optional, Sequence, Tuple

OUTPUT_VERSION = 1
MAX_INPUT_BYTES = 5 * 1024 * 1024
EXIT_OK, EXIT_NOT_OK, EXIT_INPUT_ERROR = 0, 1, 2
FORMATS = ("text", "json")

LEVELS = ("L1", "L2", "L3")
STATUSES = ("passed", "failed", "not_run", "blocked", "not_applicable")
EVIDENCE_KINDS = ("ci_job", "local_run", "scanner", "human_review", "ai_review")
RISK_CLASSES = ("low", "medium", "high", "unclassified")
DECISIONS = ("approved", "rejected")
TEST_CHANGES = ("deleted", "skipped", "weakened")
INFRA_CHANGES = ("permission_expansion", "public_exposure", "resource_deletion", "resource_replacement")
MANIFEST_FIELDS = frozenset(
    {"change_id", "problem_id", "reviewed_commit", "implementer", "risk", "approvals", "checks", "test_changes", "infra_changes"}
)
CHECK_FIELDS = frozenset({"check_id", "status", "evidence", "reason"})
EVIDENCE_FIELDS = frozenset({"kind", "ref", "commit"})
MANIFEST_RULES = ["M-00", "M-01", "M-02"]
GATE_RULES = ["A-01", "A-02", "A-03", "A-04", "A-05", "A-06", "A-07"]
COMMIT = re.compile(r"^[0-9a-f]{7,40}$")
_UNSAFE_CATEGORIES = frozenset({"Cc", "Cf", "Zl", "Zp"})


class InputError(Exception):
    """The input cannot be interpreted; the checker exits with code 2."""


def show(value: Any) -> str:
    text = json.dumps(value, ensure_ascii=False)
    text = text if len(text) <= 60 else text[:57] + "..."
    return "".join(f"\\u{ord(c):04x}" if unicodedata.category(c) in _UNSAFE_CATEGORIES else c for c in text)


def escape_unsafe(text: str) -> str:
    out = []
    for char in text:
        if char == "\\":
            out.append("\\\\")
        elif unicodedata.category(char) in _UNSAFE_CATEGORIES:
            code = ord(char)
            out.append(f"\\x{code:02x}" if code < 0x100 else f"\\u{code:04x}")
        else:
            out.append(char)
    return "".join(out)


def is_text(value: Any) -> bool:
    return isinstance(value, str) and value.strip() != ""


def same_person(a: Any, b: Any) -> bool:
    """Names match regardless of case and surrounding spaces, so a self-approval
    cannot pass as independent by spelling the name differently."""
    return isinstance(a, str) and isinstance(b, str) and a.strip().casefold() == b.strip().casefold()


def read_text(path: str, what: str) -> str:
    # O_NONBLOCK keeps a FIFO from blocking the open; only regular files are
    # read, and the read is bounded even when the reported size is wrong.
    try:
        fd = os.open(path, os.O_RDONLY | getattr(os, "O_NONBLOCK", 0))
    except OSError as exc:
        raise InputError(f"cannot read {what}: {exc.strerror or exc}") from None
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise InputError(f"{what} is not a regular file")
        with os.fdopen(fd, "rb") as handle:
            fd = -1
            data = handle.read(MAX_INPUT_BYTES + 1)
    except OSError as exc:
        raise InputError(f"cannot read {what}: {exc.strerror or exc}") from None
    finally:
        if fd != -1:
            os.close(fd)
    if len(data) > MAX_INPUT_BYTES:
        raise InputError(f"{what} is larger than {MAX_INPUT_BYTES} bytes")
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        raise InputError(f"{what} is not valid UTF-8") from None


def _reject_duplicate_keys(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
    obj: Dict[str, Any] = {}
    for key, value in pairs:
        if key in obj:
            raise InputError(f"duplicate key {show(key)} in a JSON object")
        obj[key] = value
    return obj


def load_json(path: str, what: str) -> Any:
    try:
        return json.loads(read_text(path, what), object_pairs_hook=_reject_duplicate_keys)
    except json.JSONDecodeError as exc:
        raise InputError(f"{what}: invalid JSON at line {exc.lineno} column {exc.colno}: {exc.msg}") from None
    except RecursionError:
        raise InputError(f"{what}: JSON nesting is too deep to read") from None


class Report:
    """Violations in a fixed order: by rule, then position, then detection."""

    def __init__(self) -> None:
        self._items: List[Tuple[str, int, int, Optional[str], str]] = []

    def add(self, rule_id: str, position: int, node_id: Optional[str], message: str) -> None:
        self._items.append((rule_id, position, len(self._items), node_id, message))

    def violations(self) -> List[Dict[str, Any]]:
        return [
            {"rule_id": rule, "node_id": node, "message": message}
            for rule, _, _, node, message in sorted(self._items, key=lambda item: item[:3])
        ]


# --- inputs --------------------------------------------------------------------


def load_manifest(path: str) -> Dict[str, Any]:
    document = load_json(path, "the verification manifest")
    if not isinstance(document, dict) or set(document) != {"schema_version", "verification_manifest"}:
        raise InputError("the manifest must have exactly schema_version and verification_manifest")
    if type(document["schema_version"]) is not int or document["schema_version"] != 1:
        raise InputError(f"schema_version must be the integer 1 (got {show(document['schema_version'])})")
    if not isinstance(document["verification_manifest"], dict):
        raise InputError("verification_manifest must be an object")
    return document["verification_manifest"]


def load_graph(path: str) -> Tuple[str, List[Tuple[str, str, str]]]:
    return graph_parts(load_json(path, "the requirements graph"))


def graph_parts(document: Any) -> Tuple[str, List[Tuple[str, str, str]]]:
    """Reads what the gate needs from a version 2 requirements graph: its
    problem id and every acceptance criterion as (id, level, requirement id), in order. The
    graph's own structure is checked by its own checker, before this gate."""
    if not isinstance(document, dict) or document.get("schema_version") != 2 or not is_text(document.get("problem_id")):
        raise InputError("the requirements graph must be version 2 with a problem_id")
    nodes = document.get("requirements")
    if not isinstance(nodes, list):
        raise InputError("the requirements graph has no requirements array")
    criteria: List[Tuple[str, str, str]] = []
    owners: Dict[str, str] = {}
    for node in nodes:
        entries = node.get("acceptance") if isinstance(node, dict) else None
        if not isinstance(entries, list):
            raise InputError("every requirement needs an acceptance array; check the graph with its own checker first")
        for entry in entries:
            if not isinstance(entry, dict) or not is_text(entry.get("id")) or entry.get("level") not in LEVELS:
                raise InputError("every acceptance criterion needs an id and a level; check the graph with its own checker first")
            # One check answers one criterion: a reused id would let a leaf's
            # check stand for a parent's own check.
            if entry["id"] in owners:
                raise InputError(f"acceptance id {show(entry['id'])} is used by more than one criterion; check the graph with its own checker first")
            owners[entry["id"]] = str(node.get("id"))
            criteria.append((entry["id"], entry["level"], str(node.get("id"))))
    return document["problem_id"], criteria


# --- the manifest's own rules (M-00 to M-02) --------------------------------------


def _check_list(body: Dict[str, Any], name: str, fields: Dict[str, Tuple[Any, bool]], report: Report) -> List[Dict[str, Any]]:
    """Checks an optional array of objects; ``fields`` maps each field to
    (allowed values or None for any non-empty string, required)."""
    entries = body.get(name, [])
    if not isinstance(entries, list):
        report.add("M-00", -1, None, f"{name} must be an array")
        return []
    good = []
    for index, entry in enumerate(entries):
        label = f"{name} #{index + 1}"
        if not isinstance(entry, dict):
            report.add("M-00", -1, None, f"{label} is not an object")
            continue
        ok = True
        for key in sorted(set(entry) - set(fields)):
            report.add("M-00", -1, None, f"{label} has an undefined field {show(key)}")
            ok = False
        for field, (allowed, required) in fields.items():
            if field not in entry:
                if required:
                    report.add("M-00", -1, None, f"{label} needs {field}")
                    ok = False
            elif (allowed is None and not is_text(entry[field])) or (allowed is not None and entry[field] not in allowed):
                report.add("M-00", -1, None, f"{label} has an invalid {field} {show(entry[field])}")
                ok = False
        if ok:
            good.append(entry)
    return good


def valid_evidence(evidence: Any) -> bool:
    return (isinstance(evidence, dict) and set(evidence) == EVIDENCE_FIELDS and evidence.get("kind") in EVIDENCE_KINDS
            and all(isinstance(evidence.get(k), str) for k in ("ref", "commit")) and bool(COMMIT.fullmatch(evidence["commit"])))


def check_manifest(body: Dict[str, Any]) -> List[Dict[str, Any]]:
    report = Report()
    for key in sorted(set(body) - MANIFEST_FIELDS):
        report.add("M-00", -1, None, f"undefined field {show(key)}")
    for name in ("change_id", "problem_id", "implementer"):
        if not is_text(body.get(name)):
            report.add("M-00", -1, None, f"{name} must be a non-empty string")
    if not isinstance(body.get("reviewed_commit"), str) or not COMMIT.fullmatch(body["reviewed_commit"]):
        report.add("M-00", -1, None, "reviewed_commit must be a commit SHA (7 to 40 lowercase hex digits)")
    if "risk" in body:
        risk = body["risk"]
        if not isinstance(risk, dict) or set(risk) != {"class", "rationale"} or risk.get("class") not in RISK_CLASSES or not isinstance(risk.get("rationale"), str):
            report.add("M-00", -1, None, "risk must be {class, rationale} with class low, medium, high, or unclassified")
    _check_list(body, "approvals", {"by": (None, True), "decision": (DECISIONS, True), "scope": (None, True)}, report)
    _check_list(body, "test_changes", {"path": (None, True), "change": (TEST_CHANGES, True), "approved_by": (None, False)}, report)
    _check_list(body, "infra_changes", {"kind": (INFRA_CHANGES, True), "ref": (None, True)}, report)
    checks = body.get("checks")
    if not isinstance(checks, list):
        report.add("M-00", -1, None, "checks must be an array")
        return report.violations()
    seen = set()
    for position, entry in enumerate(checks):
        label = f"check #{position + 1}"
        if not isinstance(entry, dict):
            report.add("M-00", position, None, f"{label} is not an object")
            continue
        check_id = entry.get("check_id")
        node = check_id if is_text(check_id) else None
        for key in sorted(set(entry) - CHECK_FIELDS):
            report.add("M-00", position, node, f"undefined field {show(key)}")
        if not isinstance(check_id, str):
            report.add("M-00", position, None, f"{label} needs a check_id")
        elif not check_id.strip() or check_id in seen:
            report.add("M-01", position, node, "check_id is empty or used twice")
        else:
            seen.add(check_id)
        status = entry.get("status")
        if status not in STATUSES:
            report.add("M-00", position, node, f"status must be one of {', '.join(STATUSES)} (got {show(status)})")
        if "reason" in entry and not isinstance(entry["reason"], str):
            report.add("M-00", position, node, "reason must be a string")
        if "evidence" in entry and not valid_evidence(entry["evidence"]):
            report.add("M-00", position, node, "evidence must be {kind, ref, commit} with a defined kind and a commit SHA")
        if status == "passed" and "evidence" not in entry:
            report.add("M-02", position, node, "a passed check needs evidence")
        if status == "not_applicable" and not is_text(entry.get("reason")):
            report.add("M-02", position, node, "a not_applicable check needs a reason")
    return report.violations()


# --- the gate (A-01 to A-07) -----------------------------------------------------


def run_gate(graph_path: str, manifest_path: str) -> Dict[str, Any]:
    problem_id, criteria = load_graph(graph_path)
    return evaluate_gate(problem_id, criteria, load_manifest(manifest_path))


def evaluate_gate(problem_id: str, criteria: List[Tuple[str, str, str]], body: Dict[str, Any]) -> Dict[str, Any]:
    violations = check_manifest(body)
    reasons: List[Tuple[str, str, str]] = []  # (rule, effect, message)

    def block(rule: str, message: str) -> None:
        reasons.append((rule, "blocked", message))

    for violation in violations:
        block(violation["rule_id"], f"manifest: {violation['message']}")
    if body.get("problem_id") != problem_id:
        block("A-01", f"the manifest is for problem {show(body.get('problem_id'))}, not {show(problem_id)}")
    checks: Dict[str, Dict[str, Any]] = {}
    for entry in body.get("checks") if isinstance(body.get("checks"), list) else []:
        if isinstance(entry, dict) and is_text(entry.get("check_id")):
            checks.setdefault(entry["check_id"], entry)
    known = {criterion for criterion, _, _ in criteria}
    if not criteria:
        block("A-01", "the requirements graph has no acceptance criterion, so nothing can be verified")
    for check_id in checks:
        if check_id not in known:
            block("A-01", f"check {show(check_id)} is not an acceptance criterion of the graph")
    reviewed = body.get("reviewed_commit")
    levels: Dict[str, Dict[str, int]] = {level: {} for level in LEVELS}
    by_requirement: Dict[str, List[str]] = {}
    per_check: List[Dict[str, Any]] = []
    for criterion, level, requirement in criteria:
        entry = checks.get(criterion)
        effective = "not_run"
        if entry is None:
            block("A-01", f"acceptance {show(criterion)} has no check (treated as not_run)")
        else:
            status = entry.get("status")
            evidence = entry.get("evidence") if isinstance(entry.get("evidence"), dict) else None
            effective = status if status in STATUSES else "blocked"
            if status == "passed":
                if evidence is None or not valid_evidence(evidence):
                    effective = "blocked"  # reported by M-02 or M-00
                elif evidence.get("kind") == "ai_review":
                    effective = "blocked"
                    block("A-02", f"{show(criterion)} is passed only by an AI review, which is not evidence")
                elif not is_text(evidence.get("ref")):
                    effective = "blocked"
                    block("A-02", f"{show(criterion)} has evidence with no reference")
                elif evidence.get("commit") != reviewed:
                    effective = "blocked"
                    commit = evidence.get("commit")
                    if isinstance(reviewed, str) and (reviewed.startswith(commit) or commit.startswith(reviewed)):
                        # A short prefix is not compared as a match: a commit
                        # with the same first digits can be made on purpose.
                        block("A-02", f"{show(criterion)} has evidence for commit {show(commit)}, written at another length "
                                      f"than reviewed_commit {show(reviewed)}; write both as the full SHA")
                    else:
                        block("A-02", f"{show(criterion)} has stale evidence for commit {show(commit)}")
            elif status == "failed":
                reasons.append(("A-03", "fail", f"{show(criterion)} ({level}) failed"))
            elif status in ("not_run", "blocked"):
                block("A-03", f"{show(criterion)} ({level}) is {status}")
            elif status == "not_applicable" and not is_text(entry.get("reason")):
                effective = "blocked"  # reported by M-02
        levels[level][effective] = levels[level].get(effective, 0) + 1
        by_requirement.setdefault(requirement, []).append(effective)
        per_check.append({"check_id": criterion, "level": level, "requirement": requirement, "status": effective,
                          "evidence": entry.get("evidence") if entry is not None and isinstance(entry.get("evidence"), dict) else None})
    for requirement, effective_statuses in by_requirement.items():
        if all(status == "not_applicable" for status in effective_statuses):
            block("A-03", f"requirement {show(requirement)} has no passed check: every one of its checks is not_applicable")

    risk = body.get("risk") if isinstance(body.get("risk"), dict) else {}
    risk_class = risk.get("class")
    implementer = body.get("implementer")
    if risk_class not in ("low", "medium", "high"):
        block("A-04", f"the risk is not classified (got {show(risk_class)}); classify it before deciding")
    approvals = [a for a in body.get("approvals", []) if isinstance(a, dict)] if isinstance(body.get("approvals"), list) else []
    if any(a.get("decision") == "rejected" for a in approvals):
        reasons.append(("A-05", "fail", "a person rejected this change"))
    elif risk_class == "high" and not any(
        a.get("decision") == "approved" and is_text(a.get("by")) and not same_person(a.get("by"), implementer) for a in approvals
    ):
        block("A-05", "a high-risk change needs approval by someone other than the implementer")
    test_changes = body.get("test_changes") if isinstance(body.get("test_changes"), list) else []
    for change in test_changes:
        if isinstance(change, dict) and (not is_text(change.get("approved_by")) or same_person(change.get("approved_by"), implementer)):
            block("A-06", f"the {show(change.get('change'))} test {show(change.get('path'))} has no approval by someone other than the implementer")
    infra = body.get("infra_changes") if isinstance(body.get("infra_changes"), list) else []
    if infra and risk_class != "high":
        kinds = sorted({show(c.get("kind")) for c in infra if isinstance(c, dict)})
        block("A-07", f"infrastructure changes ({', '.join(kinds)}) make this a high-risk change; escalate the risk class")

    decision = "fail" if any(effect == "fail" for _, effect, _ in reasons) else ("blocked" if reasons else "pass")
    return {
        "graph": "assurance",
        "decision": decision,
        "levels": levels,
        "reasons": [{"rule_id": rule, "effect": effect, "message": message} for rule, effect, message in reasons],
        "rules_checked": MANIFEST_RULES + GATE_RULES,
        "violations": [dict(v, input="manifest") for v in violations],
        "checks": per_check,
    }


# --- JUnit XML (J-01, J-02) ------------------------------------------------------


def refuse_declarations(text: str) -> None:
    """J-01: refuses a document type declaration, so no entity can be defined
    or expanded. The XML parser itself finds the declaration, so text in a
    comment, an instruction, or CDATA is not mistaken for one or hides one."""
    def refuse(*_: Any) -> NoReturn:
        raise InputError("the JUnit report has a DOCTYPE or ENTITY declaration, which is refused")

    parser = expat.ParserCreate()
    parser.StartDoctypeDeclHandler = refuse
    parser.EntityDeclHandler = refuse
    try:
        parser.Parse(text, True)
    except expat.ExpatError as exc:
        raise InputError(f"the JUnit report is not well-formed XML: {exc}") from None


def collect_junit(report_path: str, graph_path: str, commit: str, ref: str, kind: str) -> List[Dict[str, Any]]:
    if not COMMIT.fullmatch(commit):
        raise InputError("--commit must be a commit SHA (7 to 40 lowercase hex digits)")
    if not is_text(ref):
        raise InputError("--ref must not be empty")
    _, criteria = load_graph(graph_path)
    text = read_text(report_path, "the JUnit report")
    refuse_declarations(text)
    try:
        root = ElementTree.fromstring(text)
    except ElementTree.ParseError as exc:
        raise InputError(f"the JUnit report is not well-formed XML: {exc}") from None
    cases = []
    for case in root.iter("testcase"):
        if case.find("failure") is not None or case.find("error") is not None:
            outcome = "failed"
        elif case.find("skipped") is not None:
            outcome = "skipped"
        else:
            outcome = "passed"
        ids = {p.get("value") for p in case.iter("property") if p.get("name") == "acceptance_id"}
        cases.append((f"{case.get('classname', '')} {case.get('name', '')}", ids, outcome))
    evidence = {"kind": kind, "ref": ref, "commit": commit}
    out = []
    for criterion, _, _ in criteria:
        token = re.compile(r"(?<![A-Za-z0-9_.-])" + re.escape(criterion) + r"(?![A-Za-z0-9_.-])")
        outcomes = [outcome for label, ids, outcome in cases if criterion in ids or token.search(label)]
        if "failed" in outcomes:
            out.append({"check_id": criterion, "status": "failed", "evidence": dict(evidence)})
        elif outcomes and all(outcome == "passed" for outcome in outcomes):
            out.append({"check_id": criterion, "status": "passed", "evidence": dict(evidence)})
        else:
            if outcomes:
                why = f"{outcomes.count('passed')} passed, {outcomes.count('skipped')} skipped test cases"
            else:
                why = "no test case names this acceptance id"
            out.append({"check_id": criterion, "status": "not_run", "reason": f"{why} in the JUnit report"})
    return out


# --- review card -----------------------------------------------------------------

LABELS = {
    "en": {
        "title": "Review card", "decision": "Decision",
        "note": "From the assurance gate. It checks that the records are consistent, not that the change is secure.",
        "problem": "Problem", "current": "Current", "ideal": "Ideal", "gap": "Gap",
        "change": "Change and risk", "commit": "Reviewed commit", "implementer": "Implementer", "risk": "Risk",
        "approvals": "Approvals", "none": "none", "levels": "Checks by level", "level": "Level",
        "not_passed": "Not passed", "unresolved": "Unresolved", "decide": "Decisions for a person",
        "requirements": "Requirements", "deeper": "Deeper requirements (not drawn)", "evidence": "Evidence",
        "requirement": "Requirement", "check": "Check", "status": "Status",
        "accept": "Accept or return the change.",
        "risk_acceptance": "Accept or reject the residual risk of this high-risk change.",
        "return": "Return the change, or supply what the unresolved items name.",
    },
    "ja": {
        "title": "レビューカード", "decision": "判定",
        "note": "保証の判定による。記録どうしの整合を確かめるもので、変更が安全であることは示さない。",
        "problem": "問題", "current": "現状", "ideal": "理想", "gap": "差分",
        "change": "変更とリスク", "commit": "審査の対象のコミット", "implementer": "実装担当", "risk": "リスク",
        "approvals": "承認", "none": "なし", "levels": "水準ごとの検査", "level": "水準",
        "not_passed": "合格していない検査", "unresolved": "未解消の事項", "decide": "人が決めること",
        "requirements": "要求", "deeper": "図に描かない深い要求", "evidence": "証拠",
        "requirement": "要求", "check": "検査", "status": "状態",
        "accept": "変更を受け入れるか、差し戻すかを決める。",
        "risk_acceptance": "この高リスクの変更の残存リスクを受け入れるかを決める。",
        "return": "変更を差し戻すか、未解消の事項が求めるものを用意する。",
    },
}
MARKS = {"pass": "✅", "fail": "❌", "blocked": "⛔"}
SAFE_URL = re.compile(r"https?://[A-Za-z0-9._~:/?#@!$&'*+,;=%-]+")
MAX_DEPTH = 3  # levels drawn in the overview; deeper requirements are listed


MARK_WORDS = {"✅": "(check mark)", "❌": "(cross mark)", "⛔": "(no-entry mark)"}
URL_IN_TEXT = re.compile(r"https?://[^\s|]+")
MARKDOWN_SPECIALS = ("|", "<", ">", "[", "]", "*", "_", "`", "#", "~")


def _plain(text: str) -> str:
    for mark, word in MARK_WORDS.items():
        text = text.replace(mark, word)
    out = escape_unsafe(text)
    for char in MARKDOWN_SPECIALS:
        out = out.replace(char, {"<": "&lt;", ">": "&gt;"}.get(char, "\\" + char))
    return out


def md(text: Any) -> str:
    """Untrusted text for a Markdown line or table cell: no emphasis, heading,
    link, HTML, or decision mark can come from it, and a URL in it is shown as
    code so that it does not become a link."""
    raw, parts, last = str(text), [], 0
    for match in URL_IN_TEXT.finditer(raw):
        parts += [_plain(raw[last:match.start()]), code(match.group(0))]
        last = match.end()
    parts.append(_plain(raw[last:]))
    return "".join(parts)


def code(text: Any) -> str:
    """Untrusted text as a code span outside a table."""
    value = escape_unsafe(str(text)).replace("`", "'")
    return f"`{value}`" if value else "—"


def cell_code(text: Any) -> str:
    """A code span inside a table cell, where | would split the cell."""
    return code(text).replace("|", "\\|")


def mermaid_text(text: Any) -> str:
    out = escape_unsafe(str(text))
    for raw, safe in (('"', "#quot;"), ("<", "#lt;"), (">", "#gt;")):
        out = out.replace(raw, safe)
    return out


def load_problem_card(path: str) -> Dict[str, Any]:
    document = load_json(path, "the problem card")
    card = document.get("problem_card") if isinstance(document, dict) else None
    if not isinstance(card, dict) or not all(isinstance(card.get(k), str) for k in ("id", "ideal", "current", "gap")):
        raise InputError("the problem card must have problem_card with id, ideal, current, and gap")
    return card


def graph_nodes(document: Any) -> List[Dict[str, Any]]:
    nodes = document.get("requirements") if isinstance(document, dict) else None
    if not isinstance(nodes, list) or not all(
        isinstance(n, dict) and is_text(n.get("id")) and isinstance(n.get("children", []), list) for n in nodes
    ):
        raise InputError("every requirement needs an id and a children array; check the graph with its own checker first")
    return nodes


def load_open_findings(path: Optional[str]) -> List[Dict[str, Any]]:
    if path is None:
        return []
    document = load_json(path, "the challenge report")
    report = document.get("challenge_report") if isinstance(document, dict) else None
    findings = report.get("findings") if isinstance(report, dict) else None
    if not isinstance(findings, list):
        raise InputError("the challenge report must have challenge_report with a findings array")
    return [f for f in findings if isinstance(f, dict) and f.get("disposition") == "open"]


def render_card(card: Dict[str, Any], nodes: List[Dict[str, Any]], body: Dict[str, Any], gate: Dict[str, Any],
                findings: List[Dict[str, Any]], lang: str) -> str:
    L = LABELS[lang]
    decision = gate["decision"]
    lines = [f"# {L['title']}: {md(body.get('change_id', ''))} ({md(card['id'])})", "",
             f"**{L['decision']}: {MARKS[decision]} {decision}**", "", L["note"], "",
             f"## {L['problem']}", "",
             f"- **{L['current']}**: {md(card['current'])}",
             f"- **{L['ideal']}**: {md(card['ideal'])}",
             f"- **{L['gap']}**: {md(card['gap'])}", ""]
    risk = body.get("risk") if isinstance(body.get("risk"), dict) else {}
    approvals = [a for a in body.get("approvals", []) if isinstance(a, dict)] if isinstance(body.get("approvals"), list) else []
    approval_text = "; ".join(f"{md(a.get('by'))} ({md(a.get('decision'))}): {md(a.get('scope'))}" for a in approvals) or L["none"]
    lines += [f"## {L['change']}", "",
              f"- **{L['commit']}**: {code(body.get('reviewed_commit', ''))}",
              f"- **{L['implementer']}**: {md(body.get('implementer', ''))}",
              f"- **{L['risk']}**: {md(risk.get('class', 'unclassified'))} — {md(risk.get('rationale', ''))}",
              f"- **{L['approvals']}**: {approval_text}", ""]
    statuses = list(STATUSES)
    lines += [f"## {L['levels']}", "", f"| {L['level']} | " + " | ".join(statuses) + " |",
              "|---|" + "---|" * len(statuses)]
    for level in LEVELS:
        counts = gate["levels"].get(level, {})
        lines.append(f"| {level} | " + " | ".join(str(counts.get(st, 0)) for st in statuses) + " |")
    not_passed = [c for c in gate["checks"] if c["status"] not in ("passed", "not_applicable")]
    lines += ["", f"## {L['not_passed']}", ""]
    lines += [f"- {code(c['check_id'])} ({c['level']}, {md(c['requirement'])}): {c['status']}" for c in not_passed] or [f"- {L['none']}"]
    unresolved = [f"- {r['rule_id']} ({r['effect']}): {md(r['message'])}" for r in gate["reasons"]]
    unresolved += [f"- {md(f.get('id'))} ({md(f.get('kind'))} on {md(f.get('target'))}, {md(f.get('severity'))}): {md(f.get('statement'))}"
                   for f in findings]
    lines += ["", f"## {L['unresolved']}", ""] + (unresolved or [f"- {L['none']}"])
    decide = [L["risk_acceptance"]] if risk.get("class") == "high" else []
    decide.append(L["accept"] if decision == "pass" and not findings else L["return"])
    lines += ["", f"## {L['decide']}", ""] + [f"- {item}" for item in decide]
    lines += ["", f"## {L['requirements']}", ""] + render_requirements(nodes, gate["checks"], L)
    lines += ["", f"## {L['evidence']}", "",
              f"| {L['requirement']} | {L['check']} | {L['level']} | {L['status']} | {L['evidence']} |", "|---|---|---|---|---|"]
    for c in gate["checks"]:
        evidence = c["evidence"]
        if evidence is None:
            cell = "—"
        else:
            ref = str(evidence.get("ref", ""))
            kind = evidence.get("kind") if evidence.get("kind") in EVIDENCE_KINDS else "evidence"
            link = f"[{kind}]({ref})" if SAFE_URL.fullmatch(ref) else cell_code(ref)
            cell = f"{link} @ {cell_code(str(evidence.get('commit', ''))[:7])}"
        lines.append(f"| {md(c['requirement'])} | {cell_code(c['check_id'])} | {c['level']} | {c['status']} | {cell} |")
    return "\n".join(lines) + "\n"


def render_requirements(nodes: List[Dict[str, Any]], checks: List[Dict[str, Any]], L: Dict[str, str]) -> List[str]:
    """A Mermaid overview of the decomposition only, three levels deep, each
    requirement drawn once; deeper requirements are listed below it."""
    by_id: Dict[str, Dict[str, Any]] = {}
    for node in nodes:
        by_id.setdefault(node["id"], node)
    children_of = {nid: [c for c in node.get("children", []) if isinstance(c, str) and c in by_id] for nid, node in by_id.items()}
    referenced = {c for kids in children_of.values() for c in kids}
    depth: Dict[str, int] = {}
    queue = [nid for nid in by_id if nid not in referenced]
    for nid in queue:
        depth[nid] = 1
    index = 0
    while index < len(queue):
        nid = queue[index]
        index += 1
        for child in children_of[nid]:
            if child not in depth:
                depth[child] = depth[nid] + 1
                queue.append(child)
    own: Dict[str, List[str]] = {}
    for c in checks:
        own.setdefault(c["requirement"], []).append(c["status"])

    def own_state(nid: str) -> str:
        values = own.get(nid, [])
        if "failed" in values:
            return "fail"
        if values and "passed" in values and all(v in ("passed", "not_applicable") for v in values):
            return "pass"
        return "open"  # nothing passed, or something not run, blocked, or only not_applicable

    # A requirement's colour covers its own checks and everything below it.
    rank = {"pass": 0, "open": 1, "fail": 2}
    state: Dict[str, str] = {}
    for start in by_id:
        # Iterative post-order: every child is decided before its parent. A
        # node met again while it is still open is in a cycle and stays open.
        stack, visiting = [(start, False)], set()
        while stack:
            nid, children_done = stack.pop()
            if nid in state:
                continue
            if children_done:
                worst = own_state(nid)
                for child in children_of[nid]:
                    child_state = state.get(child, "open")
                    worst = child_state if rank[child_state] > rank[worst] else worst
                state[nid] = worst
                visiting.discard(nid)
            elif nid not in visiting:
                visiting.add(nid)
                stack.append((nid, True))
                stack.extend((child, False) for child in children_of[nid] if child not in state)
    drawn = [nid for nid in by_id if depth.get(nid, MAX_DEPTH + 1) <= MAX_DEPTH]
    key = {nid: f"n{i}" for i, nid in enumerate(drawn)}
    lines = ["```mermaid", "flowchart TD"]
    for nid in drawn:
        label = f"{nid} · {by_id[nid].get('decomposition', '')} · {state.get(nid, 'open')}"
        lines.append(f'  {key[nid]}["{mermaid_text(label)}"]:::{state.get(nid, "open")}')
    for nid in drawn:
        for child in children_of[nid]:
            if child in key:
                lines.append(f"  {key[nid]} --> {key[child]}")
    lines += ["  classDef pass fill:#e6f4ea,stroke:#1e7e34", "  classDef fail fill:#fdecea,stroke:#b02a37",
              "  classDef open fill:#fff4e5,stroke:#b36b00", "```", ""]
    lines += [f"- {code(nid)} ({md(by_id[nid].get('decomposition', ''))}): {md(by_id[nid].get('statement', ''))}" for nid in drawn]
    deeper = [nid for nid in by_id if nid not in key]
    if deeper:
        lines += ["", f"### {L['deeper']}", ""]
        lines += [f"- {code(nid)} ({md(by_id[nid].get('decomposition', ''))}): {md(by_id[nid].get('statement', ''))}" for nid in deeper]
    return lines


def run_card(problem: str, graph: str, manifest: str, report: Optional[str], lang: str) -> Tuple[str, str]:
    # Each file is read once, so the decision and what the card shows come
    # from the same content.
    card = load_problem_card(problem)
    document = load_json(graph, "the requirements graph")
    problem_id, criteria = graph_parts(document)
    body = load_manifest(manifest)
    if card["id"] != problem_id or body.get("problem_id") != problem_id:
        raise InputError(f"the problem card {show(card['id'])}, the graph ({show(problem_id)}), and the manifest ({show(body.get('problem_id'))}) must be for the same problem")
    if card.get("status") != "verified":
        raise InputError(f"the problem card is {show(card.get('status'))}, not verified; decompose and gate it first")
    gate = evaluate_gate(problem_id, criteria, body)
    findings = load_open_findings(report)
    if findings and gate["decision"] == "pass":
        # An unanswered objection keeps the change from passing, as in the
        # decomposition gate.
        gate["decision"] = "blocked"
    return gate["decision"], render_card(card, graph_nodes(document), body, gate, findings, lang)


# --- command line --------------------------------------------------------------


def error_result(target: Any, message: str) -> Dict[str, Any]:
    return {"output_version": OUTPUT_VERSION, "input_file": target, "graph": None, "status": "error",
            "rules_checked": [], "violations": [], "error": message}


def emit(result: Dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(result, indent=2))
        return
    if result["status"] == "error":
        print(f"error: {result['error']}", file=sys.stderr)
        return
    # The gate's reasons already include its manifest violations.
    for violation in result["violations"] if "decision" not in result else []:
        where = f" {escape_unsafe(violation['node_id'])}" if violation["node_id"] is not None else ""
        print(f"{violation['rule_id']}{where}: {violation['message']}")
    for reason in result.get("reasons", []):
        print(f"{reason['rule_id']} ({reason['effect']}): {reason['message']}")
    if "decision" in result:
        counts = "; ".join(f"{level} " + (", ".join(f"{k} {v}" for k, v in sorted(c.items())) or "none")
                           for level, c in result["levels"].items())
        print(f"Result: {result['decision']} ({counts}; consistency of records only)")
    else:
        print(f"Result: {result['status']} ({len(result['violations'])} violations; checked {' '.join(result['rules_checked'])})")


def requested_format(argv: Sequence[str]) -> str:
    for index, arg in enumerate(argv):
        value = argv[index + 1] if arg == "--format" and index + 1 < len(argv) else None
        if arg.startswith("--format="):
            value = arg.split("=", 1)[1]
        if value in FORMATS:
            return value
    return "text"


class _Parser(argparse.ArgumentParser):
    output_format = "text"

    def error(self, message: str) -> NoReturn:
        if self.output_format == "text":
            self.print_usage(sys.stderr)
        emit(error_result(None, f"invalid arguments: {message}"), self.output_format)
        sys.exit(EXIT_INPUT_ERROR)


def run(argv: Sequence[str], output_format: str) -> int:
    _Parser.output_format = output_format
    parser = _Parser(prog="assure.py", description="Check a verification manifest and decide assurance (read-only).")
    parser.add_argument("--format", choices=FORMATS, default="text")
    # Also accept --format after the subcommand; SUPPRESS keeps a value given
    # before it.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--format", choices=FORMATS, default=argparse.SUPPRESS)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("check", parents=[common]).add_argument("manifest")
    gate = commands.add_parser("gate", parents=[common])
    gate.add_argument("graph")
    gate.add_argument("manifest")
    collect = commands.add_parser("collect-junit", parents=[common])
    collect.add_argument("report")
    collect.add_argument("--graph", required=True)
    collect.add_argument("--commit", required=True)
    collect.add_argument("--ref", required=True)
    collect.add_argument("--kind", choices=("ci_job", "local_run"), default="ci_job")
    card = commands.add_parser("card", parents=[common])
    card.add_argument("--problem", required=True)
    card.add_argument("--graph", required=True)
    card.add_argument("--manifest", required=True)
    card.add_argument("--report")
    card.add_argument("--lang", choices=tuple(LABELS), default="en")
    args = parser.parse_args(argv)
    try:
        if args.command == "card":
            decision, text = run_card(args.problem, args.graph, args.manifest, args.report, args.lang)
            if args.format == "json":
                print(json.dumps({"output_version": OUTPUT_VERSION, "input_file": [args.problem, args.graph, args.manifest, args.report],
                                  "decision": decision, "markdown": text}, indent=2, ensure_ascii=False))
            else:
                sys.stdout.write(text)
            return EXIT_OK if decision == "pass" else EXIT_NOT_OK
        if args.command == "collect-junit":
            print(json.dumps(collect_junit(args.report, args.graph, args.commit, args.ref, args.kind), indent=2, ensure_ascii=False))
            return EXIT_OK
        if args.command == "check":
            violations = check_manifest(load_manifest(args.manifest))
            result = error_result(args.manifest, "")
            result.update(graph="verification_manifest", status="failed" if violations else "passed",
                          rules_checked=MANIFEST_RULES, violations=violations, error=None)
            emit(result, args.format)
            return EXIT_NOT_OK if violations else EXIT_OK
        gate_result = run_gate(args.graph, args.manifest)
    except InputError as exc:
        emit(error_result(getattr(args, "manifest", None) or getattr(args, "report", None), str(exc)), args.format)
        return EXIT_INPUT_ERROR
    result = error_result([args.graph, args.manifest], "")
    result.update(gate_result, status="passed" if gate_result["decision"] == "pass" else "failed", error=None)
    emit(result, args.format)
    return EXIT_OK if gate_result["decision"] == "pass" else EXIT_NOT_OK


def main(argv: Optional[Sequence[str]] = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    output_format = requested_format(arguments)
    try:
        return run(arguments, output_format)
    except Exception as exc:
        # A failure of the checker itself must not look like exit code 1.
        traceback.print_exc()
        emit(error_result(None, f"internal error: {type(exc).__name__}"), output_format)
        return EXIT_INPUT_ERROR


if __name__ == "__main__":
    sys.exit(main())
