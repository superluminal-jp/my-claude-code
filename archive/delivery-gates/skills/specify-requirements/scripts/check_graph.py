#!/usr/bin/env python3
"""Read-only structural checker for requirement and skill graphs.

Formats and rules: references/checker.md in this skill. A passing result means only that a declaration satisfies the
structural rules listed in ``rules_checked``; it is not a security verdict
and does not show that children are sufficient for their parent.

The checker reads its input and nothing else: it writes no file, opens no
network connection, starts no process, and never executes input content.

Exit codes: 0 no violation, 1 rule violations, 2 input that cannot be
interpreted (or a failure of the checker itself).
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
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, NoReturn, Optional, Sequence, Tuple

OUTPUT_VERSION = 1
SCHEMA_VERSIONS = (1, 2)  # 2 adds problem_id to requirements graphs
MAX_INPUT_BYTES = 5 * 1024 * 1024

EXIT_PASSED = 0
EXIT_VIOLATIONS = 1
EXIT_INPUT_ERROR = 2

DECOMPOSITIONS = ("AND", "OR", "LEAF")
LEVELS = ("L1", "L2", "L3")
PERMISSIONS = ("read_only", "workspace_write", "external_effect")
ROLES = ("orchestrator", "worker", "auditor", "checker")
READ_ONLY_ROLES = ("auditor", "checker")

TOP_LEVEL_FIELDS = frozenset({"schema_version", "problem_id", "requirements", "skills", "problem_card", "challenge_report"})
DECLARATION_KINDS = ("requirements", "skills", "problem_card", "challenge_report")
REQUIREMENT_FIELDS = frozenset(
    {"id", "statement", "decomposition", "children", "acceptance", "assumptions", "counterexamples", "selection", "origin"}
)
ACCEPTANCE_FIELDS = frozenset({"id", "description", "level", "stage"})
# When a criterion can be verified: before the change is deployed (the
# default when stage is absent) or only after it.
STAGES = ("pre_deploy", "post_deploy")
# A requirement a person directed rather than one derived from the problem:
# who directed it and where that can be read.
ORIGIN_FIELDS = frozenset({"kind", "by", "ref"})
ORIGIN_KINDS = ("instruction",)
SKILL_FIELDS = frozenset({"id", "children", "permission", "role"})
PROBLEM_TEXT_FIELDS = ("id", "ideal", "current", "gap", "significance")
PROBLEM_LIST_FIELDS = ("hypotheses", "proposed_solutions", "out_of_scope")
PROBLEM_FIELDS = frozenset(PROBLEM_TEXT_FIELDS + PROBLEM_LIST_FIELDS + ("status", "status_rationale", "evidence", "counter_evidence"))
EVIDENCE_FIELDS = frozenset({"source", "observation"})
STATUSES = ("verified", "unverified", "refuted")
REPORT_FIELDS = frozenset({"problem_id", "reviewer", "context_given", "findings"})
FINDING_FIELDS = frozenset({"id", "kind", "target", "severity", "statement", "disposition", "resolution"})
FINDING_KINDS = (
    "false_positive", "alternative_cause", "solution_as_problem", "mixed_statement",
    "counterexample", "missing_child", "or_overlap", "missing_evidence", "other",
)
SEVERITIES = ("high", "medium", "low")
DISPOSITIONS = ("open", "accepted", "rejected")

RULES_CHECKED: Dict[str, List[str]] = {
    "requirements": ["S-00", "S-01", "S-02", "S-03", "S-04", "S-05", "S-06", "S-07", "S-08", "S-11", "S-12"],
    "skills": ["S-00", "S-01", "S-02", "S-03", "S-08", "S-09"],
    "skills-dir": ["S-02", "S-03", "S-08", "S-10"],
    "problem_card": ["C-00", "C-01", "C-02", "C-03"],
    "challenge_report": ["R-00", "R-01", "R-02"],
    "gate": ["G-01", "G-02", "G-03", "G-04"],
}

# How a "## Child skills" section declares a child: one "- `name`" line per
# child, outside code blocks, until the next level-two heading.
_CHILD_SECTION = re.compile(r"^## Child skills\s*$")
_CHILD_DECLARATION = re.compile(r"^- `([A-Za-z0-9_-]+)`")
# A fenced code block as CommonMark defines it: up to three spaces, then a run
# of at least three backticks or tildes; the rest of the line follows.
_FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")

# Characters that could forge or hide lines in the human-readable output
# (CWE-117): controls, format characters such as bidirectional
# overrides, and line or paragraph separators.
_UNSAFE_CATEGORIES = frozenset({"Cc", "Cf", "Zl", "Zp"})


class InputError(Exception):
    """The input cannot be interpreted; the checker exits with code 2."""


@dataclass(frozen=True)
class Violation:
    rule_id: str
    node_id: Optional[str]
    message: str


@dataclass
class Node:
    position: int
    node_id: str
    raw: Dict[str, Any]
    children: List[str] = field(default_factory=list)
    # A node whose id repeats an earlier one is still checked, and its children
    # still count as referenced.
    duplicate: bool = False
    # False when ``children`` was not an array of strings; rules that count
    # children are then skipped instead of reporting a follow-on error.
    children_valid: bool = True


class Report:
    """Collects violations and returns them in a fixed order: by rule, then node, then detection."""

    def __init__(self) -> None:
        self._items: List[Tuple[str, int, int, Optional[str], str]] = []

    def add(self, rule_id: str, position: int, node_id: Optional[str], message: str) -> None:
        # Within one rule and node, the detection order follows the declaration.
        self._items.append((rule_id, position, len(self._items), node_id, message))

    def violations(self) -> List[Violation]:
        ordered = sorted(self._items, key=lambda item: item[:3])
        return [Violation(rule_id, node_id, message) for rule_id, _, _, node_id, message in ordered]


def show(value: Any) -> str:
    """A short JSON rendering of a value for messages."""
    text = json.dumps(value, ensure_ascii=False)
    text = text if len(text) <= 60 else text[:57] + "..."
    # JSON escapes C0 controls but leaves DEL, C1 controls, format characters,
    # and line separators as they are.
    return "".join(f"\\u{ord(c):04x}" if unicodedata.category(c) in _UNSAFE_CATEGORIES else c for c in text)


def is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and value.strip() != ""


def is_string_list(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


# --- reading input -----------------------------------------------------------


def read_text(path: Path, what: str) -> str:
    # O_NONBLOCK keeps a FIFO from blocking the open; fstat on the opened file
    # then rejects anything that is not a regular file, and the read is bounded
    # even when the reported size is wrong.
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
    # JSON does not forbid repeated keys and Python keeps the last value, which
    # could hide part of a declaration.
    obj: Dict[str, Any] = {}
    for key, value in pairs:
        if key in obj:
            raise InputError(f"duplicate key {show(key)} in a JSON object")
        obj[key] = value
    return obj


def parse_declaration(text: str) -> Tuple[str, Any, Optional[str]]:
    """Validates the top level and returns
    (kind, body, problem_id). The body is a node array for a graph and an
    object for a problem card or challenge report."""
    try:
        document = json.loads(text, object_pairs_hook=_reject_duplicate_keys)
    except json.JSONDecodeError as exc:
        raise InputError(f"invalid JSON at line {exc.lineno} column {exc.colno}: {exc.msg}") from None
    except RecursionError:
        raise InputError("JSON nesting is too deep to read") from None
    except ValueError:
        # Python refuses to convert an integer with too many digits.
        raise InputError("a number in the input is too long to read") from None
    if not isinstance(document, dict):
        raise InputError("the top level must be a JSON object")
    version = document.get("schema_version")
    if type(version) is not int or version not in SCHEMA_VERSIONS:
        raise InputError(f"schema_version must be the integer 1 or 2 (got {show(version)})")
    undefined = sorted(set(document) - TOP_LEVEL_FIELDS)
    if undefined:
        raise InputError(f"undefined top-level field {show(undefined[0])}")
    kinds = [kind for kind in DECLARATION_KINDS if kind in document]
    if len(kinds) != 1:
        raise InputError("the top level must have exactly one of " + ", ".join(DECLARATION_KINDS))
    kind = kinds[0]
    graph = kind in ("requirements", "skills")
    if not isinstance(document[kind], list if graph else dict):
        raise InputError(f"{kind} must be {'an array' if graph else 'an object'}")
    problem_id = document.get("problem_id")
    if version == 2:
        if kind != "requirements":
            raise InputError("schema_version 2 is defined only for requirements graphs")
        if not is_nonempty_string(problem_id):
            raise InputError("a version 2 requirements graph needs a non-empty problem_id")
    elif "problem_id" in document:
        raise InputError("problem_id needs schema_version 2")
    return kind, document[kind], problem_id


# --- rules shared by both graph kinds ----------------------------------------


def parse_nodes(raw_nodes: Sequence[Any], allowed_fields: frozenset, report: Report) -> List[Node]:
    """Applies S-00 (shape) and S-01 (ids); returns the nodes that have a usable id."""
    nodes: List[Node] = []
    first_position: Dict[str, int] = {}
    for position, raw in enumerate(raw_nodes):
        label = f"node #{position + 1}"
        if not isinstance(raw, dict):
            report.add("S-00", position, None, f"{label} is not a JSON object")
            continue
        node_id = raw.get("id")
        if node_id is not None and not isinstance(node_id, str):
            report.add("S-00", position, None, f"{label} has an id that is not a string")
            continue
        if not is_nonempty_string(node_id):
            report.add("S-01", position, None, f"{label} has no id")
            continue
        for key in sorted(set(raw) - allowed_fields):
            report.add("S-00", position, node_id, f"undefined field {show(key)}")
        duplicate = node_id in first_position
        if duplicate:
            report.add("S-01", position, node_id, f"id is already used by node #{first_position[node_id] + 1}")
        else:
            first_position[node_id] = position
        children = raw.get("children", [])
        children_valid = is_string_list(children)
        if not children_valid:
            report.add("S-00", position, node_id, "children must be an array of strings")
            children = []
        nodes.append(Node(position, node_id, raw, children, duplicate, children_valid))
    return nodes


def check_references(
    nodes: List[Node], report: Report, undefined: str = "child {child} is not defined"
) -> Dict[str, List[str]]:
    """Applies S-02 and returns the edges between defined nodes."""
    defined = {node.node_id for node in nodes}
    edges: Dict[str, List[str]] = {}
    for node in nodes:
        seen: List[str] = []
        for child in node.children:
            if child in seen:
                report.add("S-02", node.position, node.node_id, f"lists child {show(child)} more than once")
                continue
            seen.append(child)
            if child not in defined:
                report.add("S-02", node.position, node.node_id, undefined.format(child=show(child)))
        node.children = seen
        # A repeated id contributes its children to the same graph node, so
        # they still count as referenced.
        targets = edges.setdefault(node.node_id, [])
        targets.extend(child for child in seen if child in defined and child not in targets)
    return edges


def find_cycles(order: List[str], edges: Dict[str, List[str]]) -> List[List[str]]:
    """Iterative depth-first search. Each cycle starts at its
    earliest-declared node, and each is reported once."""
    position = {node_id: index for index, node_id in enumerate(order)}
    state = dict.fromkeys(order, 0)  # 0 unvisited, 1 on the current path, 2 finished
    cycles: List[List[str]] = []
    seen = set()
    for start in order:
        if state[start]:
            continue
        state[start] = 1
        path = [start]
        path_index = {start: 0}
        stack = [iter(edges[start])]
        while stack:
            child = next(stack[-1], None)
            if child is None:
                stack.pop()
                finished = path.pop()
                del path_index[finished]
                state[finished] = 2
            elif state[child] == 0:
                state[child] = 1
                path_index[child] = len(path)
                path.append(child)
                stack.append(iter(edges[child]))
            elif state[child] == 1:
                cycle = path[path_index[child]:]
                first = min(range(len(cycle)), key=lambda i: position[cycle[i]])
                cycle = cycle[first:] + cycle[:first]
                if tuple(cycle) not in seen:
                    seen.add(tuple(cycle))
                    cycles.append(cycle)
    return cycles


def check_cycles(nodes: List[Node], edges: Dict[str, List[str]], report: Report) -> None:
    """Applies S-03. S-08 needs no check: a shared child is legal."""
    position: Dict[str, int] = {}
    for node in nodes:
        position.setdefault(node.node_id, node.position)
    for cycle in find_cycles(list(position), edges):
        path = " -> ".join(escape_unsafe(node_id) for node_id in cycle + [cycle[0]])
        report.add("S-03", position[cycle[0]], cycle[0], f"cycle: {path}")


# --- requirement graphs --------------------------------------------------------


def check_requirement_fields(node: Node, report: Report) -> Optional[str]:
    """Applies S-00 to the requirement fields and S-04; returns the decomposition if valid."""
    raw, where = node.raw, (node.position, node.node_id)
    if not is_nonempty_string(raw.get("statement")):
        report.add("S-00", *where, "statement must be a non-empty string")
    for name in ("assumptions", "counterexamples"):
        if name in raw and not is_string_list(raw[name]):
            report.add("S-00", *where, f"{name} must be an array of strings")
    if "origin" in raw:
        origin = raw["origin"]
        if (not isinstance(origin, dict) or set(origin) != ORIGIN_FIELDS or origin.get("kind") not in ORIGIN_KINDS
                or not is_nonempty_string(origin.get("by")) or not is_nonempty_string(origin.get("ref"))):
            report.add("S-00", *where, 'origin must be {"kind": "instruction", "by": <who directed it>, "ref": <where>}, '
                                       "with non-empty by and ref and no other field")
    decomposition = raw.get("decomposition")
    if decomposition not in DECOMPOSITIONS:
        got = "none" if "decomposition" not in raw else show(decomposition)
        report.add("S-04", *where, f"decomposition must be AND, OR, or LEAF (got {got})")
        return None
    if not node.children_valid:
        return decomposition
    count = len(node.children)
    if decomposition == "LEAF" and count:
        report.add("S-04", *where, f"a LEAF has no children (got {count})")
    elif decomposition != "LEAF" and count < 2:
        report.add("S-04", *where, f"an {decomposition} needs at least 2 children (got {count})")
    return decomposition


def check_selection(node: Node, decomposition: Optional[str], report: Report) -> None:
    """Applies S-05."""
    raw, where = node.raw, (node.position, node.node_id)
    if not node.children_valid:
        return
    if "selection" in raw:
        selection = raw["selection"]
        if not isinstance(selection, dict) or not all(isinstance(v, str) for v in selection.values()):
            report.add("S-00", *where, "selection must map child ids to condition strings")
            return
        if decomposition != "OR":
            if decomposition is not None:
                report.add("S-05", *where, "only an OR node has a selection")
            return
    elif decomposition != "OR":
        return
    else:
        selection = {}
    for child in node.children:
        if not is_nonempty_string(selection.get(child)):
            report.add("S-05", *where, f"no selection condition for child {show(child)}")
    for key in selection:
        if key not in node.children:
            report.add("S-05", *where, f"selection names {show(key)}, which is not a child")


def check_acceptance(node: Node, owners: Dict[str, str], report: Report) -> None:
    """Applies S-06 and S-07; ``owners`` maps acceptance ids already seen to their node."""
    raw, where = node.raw, (node.position, node.node_id)
    if "acceptance" not in raw:
        report.add("S-06", *where, "has no acceptance criterion")
        return
    entries = raw["acceptance"]
    if not isinstance(entries, list):
        report.add("S-00", *where, "acceptance must be an array")
        return
    if not entries:
        report.add("S-06", *where, "has no acceptance criterion")
        return
    for index, entry in enumerate(entries):
        label = f"acceptance #{index + 1}"
        if not isinstance(entry, dict):
            report.add("S-00", *where, f"{label} is not a JSON object")
            continue
        for key in sorted(set(entry) - ACCEPTANCE_FIELDS):
            report.add("S-00", *where, f"{label} has an undefined field {show(key)}")
        if not is_nonempty_string(entry.get("description")):
            report.add("S-00", *where, f"{label} description must be a non-empty string")
        criterion_id = entry.get("id")
        if not is_nonempty_string(criterion_id):
            report.add("S-07", *where, f"{label} has no id")
        elif criterion_id in owners:
            report.add("S-07", *where, f"acceptance id {show(criterion_id)} is already used by {show(owners[criterion_id])}")
        else:
            owners[criterion_id] = node.node_id
        if entry.get("level") not in LEVELS:
            report.add("S-07", *where, f"{label} level must be L1, L2, or L3 (got {show(entry.get('level'))})")
        if "stage" in entry and entry["stage"] not in STAGES:
            report.add("S-07", *where, f"{label} stage must be pre_deploy or post_deploy (got {show(entry['stage'])})")


def check_parent_level(node: Node, decomposition: Optional[str], report: Report) -> None:
    """Applies S-12: a parent's own acceptance cannot be only leaf checks. A
    node with no criteria is reported by S-06 alone."""
    entries = node.raw.get("acceptance")
    if decomposition not in ("AND", "OR") or not isinstance(entries, list) or not entries:
        return
    if not any(isinstance(entry, dict) and entry.get("level") in ("L2", "L3") for entry in entries):
        report.add("S-12", node.position, node.node_id,
                   f"an {decomposition} needs an L2 or L3 acceptance criterion of its own, not only L1")


def check_roots(raw_nodes: Sequence[Any], nodes: List[Node], edges: Dict[str, List[str]], report: Report) -> None:
    """Applies S-11. With no root at all the graph has a cycle, which S-03 reports."""
    if not raw_nodes:
        report.add("S-11", -1, None, "the requirements graph declares no node")
        return
    if not all(node.children_valid for node in nodes):
        return  # the edges are unknown; S-00 already fails the graph
    children = {child for targets in edges.values() for child in targets}
    roots = [node_id for node_id in edges if node_id not in children]
    if len(roots) >= 2:
        names = ", ".join(show(root) for root in roots)
        report.add("S-11", -1, None, f"the graph has {len(roots)} roots ({names}); a requirements graph has one")


def check_requirements(raw_nodes: Sequence[Any]) -> List[Violation]:
    report = Report()
    nodes = parse_nodes(raw_nodes, REQUIREMENT_FIELDS, report)
    edges = check_references(nodes, report)
    check_cycles(nodes, edges, report)
    owners: Dict[str, str] = {}
    for node in nodes:
        decomposition = check_requirement_fields(node, report)
        check_selection(node, decomposition, report)
        check_acceptance(node, owners, report)
        check_parent_level(node, decomposition, report)
    check_roots(raw_nodes, nodes, edges, report)
    return report.violations()


# --- skill graphs --------------------------------------------------------------


def check_skill_fields(node: Node, report: Report) -> Tuple[Optional[str], Optional[str]]:
    """Applies the value part of S-09; returns (permission, role), each None when invalid."""
    where = (node.position, node.node_id)
    values: Dict[str, Optional[str]] = {}
    for name, allowed in (("permission", PERMISSIONS), ("role", ROLES)):
        value = node.raw.get(name)
        if value in allowed:
            values[name] = value
        else:
            got = "none" if name not in node.raw else show(value)
            report.add("S-09", *where, f"{name} must be one of {', '.join(allowed)} (got {got})")
            values[name] = None
    return values["permission"], values["role"]


def check_skills(raw_nodes: Sequence[Any]) -> List[Violation]:
    report = Report()
    nodes = parse_nodes(raw_nodes, SKILL_FIELDS, report)
    edges = check_references(nodes, report)
    check_cycles(nodes, edges, report)
    declared = [(node, check_skill_fields(node, report)) for node in nodes]
    permission: Dict[str, Optional[str]] = {}
    for node, values in declared:
        permission.setdefault(node.node_id, values[0])
    for node, (_, role) in declared:
        if role not in READ_ONLY_ROLES:
            continue
        where = (node.position, node.node_id)
        own = permission[node.node_id] if not node.duplicate else None
        if own is not None and own != "read_only":
            report.add("S-09", *where, f"an {role} must be read_only (declared {own})")
        # Applying a child produces the child's effects, so everything an
        # auditor or checker can reach must be read-only too.
        visited = {node.node_id}
        queue = deque(edges[node.node_id])
        while queue:
            child = queue.popleft()
            if child in visited:
                continue
            visited.add(child)
            reached = permission[child]
            if reached is not None and reached != "read_only":
                report.add("S-09", *where, f"the {role} reaches {show(child)}, which is {reached}, through its children")
            queue.extend(edges[child])
    return report.violations()


# --- compatibility mode: ## Child skills declarations ---------------------------


def declared_children(text: str) -> List[str]:
    """The names a SKILL.md declares in its "## Child skills" section."""
    names: List[str] = []
    in_section = False
    fence: Optional[Tuple[str, int]] = None  # (character, length) of the open fence
    for line in text.split("\n"):
        line = line[:-1] if line.endswith("\r") else line
        match = _FENCE.match(line)
        if fence is not None:
            # Only a run of the same character, at least as long, with nothing
            # but spaces or tabs after it, closes the block.
            if match and match.group(1)[0] == fence[0] and len(match.group(1)) >= fence[1] \
                    and re.fullmatch(r"[ \t]*", match.group(2)):
                fence = None
            continue
        # A backtick fence's info string cannot contain a backtick.
        if match and not (match.group(1)[0] == "`" and "`" in match.group(2)):
            fence = (match.group(1)[0], len(match.group(1)))
            continue
        if line.startswith("## "):
            in_section = bool(_CHILD_SECTION.match(line))
            continue
        match = _CHILD_DECLARATION.match(line) if in_section else None
        if match:
            names.append(match.group(1))
    return names


def check_skills_dir(directory: Path) -> Tuple[str, List[Violation]]:
    if not directory.is_dir():
        raise InputError(f"{escape_unsafe(str(directory))} is not a readable directory")
    try:
        skills = sorted(
            (entry for entry in directory.iterdir() if entry.is_dir() and (entry / "SKILL.md").is_file()),
            key=lambda entry: entry.name,
        )
    except OSError as exc:
        raise InputError(f"cannot read {escape_unsafe(str(directory))}: {exc.strerror or exc}") from None
    report = Report()
    nodes = [
        Node(position, entry.name, {}, declared_children(read_text(entry / "SKILL.md", f"{escape_unsafe(entry.name)}/SKILL.md")))
        for position, entry in enumerate(skills)
    ]
    edges = check_references(nodes, report, "declares {child}, which has no SKILL.md in the skills directory")
    check_cycles(nodes, edges, report)
    declared = {node.node_id: node.children for node in nodes}
    for node in nodes:
        for child in edges[node.node_id]:
            # A self-declaration is already a cycle (S-03) and is reported only
            # there. A child counts as a parent when it declares anything, even
            # a skill that does not exist.
            if child != node.node_id and declared[child]:
                report.add(
                    "S-10",
                    node.position,
                    node.node_id,
                    f"declares {show(child)}, which declares children of its own (only one level is allowed)",
                )
    return "skills-dir", report.violations()


# --- problem cards and challenge reports ---------------------------------------


def _evidence(card: Dict[str, Any], name: str, where: Tuple[int, Optional[str]], report: Report) -> int:
    """Applies C-00 to an evidence list; returns the number of well-formed entries."""
    if name not in card:
        if name == "evidence":
            report.add("C-00", *where, "evidence is missing (use [] when there is none)")
        return 0
    entries = card[name]
    if not isinstance(entries, list):
        report.add("C-00", *where, f"{name} must be an array")
        return 0
    good = 0
    for index, entry in enumerate(entries):
        if (
            isinstance(entry, dict)
            and set(entry) == EVIDENCE_FIELDS
            and all(is_nonempty_string(entry[key]) for key in EVIDENCE_FIELDS)
        ):
            good += 1
        else:
            report.add("C-00", *where, f"{name} #{index + 1} must have exactly a non-empty source and observation")
    return good


def check_problem_card(card: Dict[str, Any]) -> List[Violation]:
    report = Report()
    where = (0, card.get("id") if is_nonempty_string(card.get("id")) else None)
    for key in sorted(set(card) - PROBLEM_FIELDS):
        report.add("C-00", *where, f"undefined field {show(key)}")
    for name in PROBLEM_TEXT_FIELDS:
        if not is_nonempty_string(card.get(name)):
            report.add("C-00", *where, f"{name} must be a non-empty string")
    for name in PROBLEM_LIST_FIELDS:
        if name in card and not is_string_list(card[name]):
            report.add("C-00", *where, f"{name} must be an array of strings")
    if "status_rationale" in card and not isinstance(card["status_rationale"], str):
        report.add("C-00", *where, "status_rationale must be a string")
    evidence = _evidence(card, "evidence", where, report)
    counter = _evidence(card, "counter_evidence", where, report)
    status = card.get("status")
    if "status" not in card:
        report.add("C-00", *where, "status is missing")
    elif status not in STATUSES:
        report.add("C-03", *where, f"status must be verified, unverified, or refuted (got {show(status)})")
    if status == "verified" and not evidence:
        report.add("C-01", *where, "a verified problem needs at least one evidence entry")
    if counter and not is_nonempty_string(card.get("status_rationale")):
        report.add("C-02", *where, "counter_evidence needs a status_rationale that explains the status")
    if status == "refuted" and not counter:
        report.add("C-02", *where, "a refuted problem needs at least one counter_evidence entry")
    return report.violations()


def check_challenge_report(body: Dict[str, Any], targets: Optional[set] = None) -> List[Violation]:
    """Applies R-00 to R-02, and R-03 when ``targets`` (the ids a finding may name) is given."""
    report = Report()
    where = (-1, None)
    for key in sorted(set(body) - REPORT_FIELDS):
        report.add("R-00", *where, f"undefined field {show(key)}")
    for name in ("problem_id", "reviewer"):
        if not is_nonempty_string(body.get(name)):
            report.add("R-00", *where, f"{name} must be a non-empty string")
    if not is_string_list(body.get("context_given")):
        report.add("R-00", *where, "context_given must be an array of strings")
    findings = body.get("findings")
    if not isinstance(findings, list):
        report.add("R-00", *where, "findings must be an array")
        return report.violations()
    seen = set()
    for position, finding in enumerate(findings):
        label = f"finding #{position + 1}"
        if not isinstance(finding, dict):
            report.add("R-00", position, None, f"{label} is not a JSON object")
            continue
        finding_id = finding.get("id")
        at = (position, finding_id if is_nonempty_string(finding_id) else None)
        for key in sorted(set(finding) - FINDING_FIELDS):
            report.add("R-00", *at, f"undefined field {show(key)}")
        if not isinstance(finding_id, str):
            report.add("R-00", *at, f"{label} needs an id")
        elif not finding_id.strip():
            report.add("R-01", *at, f"{label} has an empty id")
        elif finding_id in seen:
            report.add("R-01", *at, "id is already used by another finding")
        else:
            seen.add(finding_id)
        for name, allowed in (("kind", FINDING_KINDS), ("severity", SEVERITIES), ("disposition", DISPOSITIONS)):
            if name not in finding:
                report.add("R-00", *at, f"{name} is missing")
            elif finding[name] not in allowed:
                report.add("R-01", *at, f"{name} must be one of {', '.join(allowed)} (got {show(finding[name])})")
        for name in ("target", "statement"):
            if not is_nonempty_string(finding.get(name)):
                report.add("R-00", *at, f"{name} must be a non-empty string")
        if "resolution" in finding and not isinstance(finding["resolution"], str):
            report.add("R-00", *at, "resolution must be a string")
        elif finding.get("disposition") in ("accepted", "rejected") and not is_nonempty_string(finding.get("resolution")):
            report.add("R-02", *at, f"a {finding['disposition']} finding needs a resolution")
        target = finding.get("target")
        if targets is not None and is_nonempty_string(target) and target not in targets:
            report.add("R-03", *at, f"target {show(target)} is neither the problem nor a requirement")
    return report.violations()


def load_for_gate(path: Path, kind: str, what: str) -> Tuple[Any, Optional[str]]:
    found, body, problem_id = parse_declaration(read_text(path, what))
    if found != kind:
        raise InputError(f"{what} must be a {kind} declaration (got {found})")
    return body, problem_id


def run_gate(paths: Sequence[str]) -> Dict[str, Any]:
    """Decides whether a problem may proceed to implementation (rules G-01 to G-04)."""
    if len(paths) not in (2, 3):
        raise InputError("--gate takes CARD GRAPH [REPORT]")
    card, _ = load_for_gate(Path(paths[0]), "problem_card", "the problem card")
    graph, problem_id = load_for_gate(Path(paths[1]), "requirements", "the requirements graph")
    challenge = load_for_gate(Path(paths[2]), "challenge_report", "the challenge report")[0] if len(paths) == 3 else None
    reasons: List[Tuple[str, str]] = []
    card_id = card.get("id")
    card_violations = check_problem_card(card)
    if card_violations:
        reasons.append(("G-01", f"the problem card has {len(card_violations)} violation(s)"))
    elif card.get("status") != "verified":
        reasons.append(("G-01", f"the problem is {card.get('status')}, not verified"))
    graph_violations = check_requirements(graph)
    if graph_violations:
        reasons.append(("G-02", f"the requirements graph has {len(graph_violations)} violation(s)"))
    if problem_id is None:
        reasons.append(("G-02", "the requirements graph is not linked to a problem (schema_version 2 with problem_id)"))
    elif problem_id != card_id:
        reasons.append(("G-02", f"the requirements graph belongs to problem {show(problem_id)}, not {show(card_id)}"))
    report_violations: List[Violation] = []
    if challenge is not None:
        # Only ids that are strings can be targets; other ids are already
        # reported by the card and graph rules.
        targets = {card_id} if is_nonempty_string(card_id) else set()
        targets |= {node["id"] for node in graph if isinstance(node, dict) and is_nonempty_string(node.get("id"))}
        report_violations = check_challenge_report(challenge, targets)
        if report_violations:
            reasons.append(("G-03", f"the challenge report has {len(report_violations)} violation(s)"))
        if challenge.get("problem_id") != card_id:
            reasons.append(("G-03", f"the challenge report is for problem {show(challenge.get('problem_id'))}, not {show(card_id)}"))
        findings = challenge.get("findings") if isinstance(challenge.get("findings"), list) else []
        for finding in findings:
            if isinstance(finding, dict) and finding.get("disposition") == "open":
                reasons.append(("G-04", f"finding {show(finding.get('id'))} ({show(finding.get('kind'))} on {show(finding.get('target'))}) is still open"))
    decision = "blocked" if reasons else "ready"
    rules = RULES_CHECKED["problem_card"] + RULES_CHECKED["requirements"]
    if challenge is not None:
        rules += RULES_CHECKED["challenge_report"] + ["R-03"]
    labelled = (
        [("card", v) for v in card_violations]
        + [("graph", v) for v in graph_violations]
        + [("report", v) for v in report_violations]
    )
    return {
        "graph": "gate",
        "decision": decision,
        "challenge": "recorded" if challenge is not None else "not_run",
        "reasons": [{"rule_id": rule_id, "message": message} for rule_id, message in reasons],
        "rules_checked": rules + RULES_CHECKED["gate"],
        "violations": [
            {"rule_id": v.rule_id, "input": source, "node_id": v.node_id, "message": v.message} for source, v in labelled
        ],
    }


# --- command line --------------------------------------------------------------


def check_file(path: Path) -> Tuple[str, List[Violation]]:
    kind, body, _ = parse_declaration(read_text(path, "the declaration file"))
    checks = {
        "requirements": check_requirements,
        "skills": check_skills,
        "problem_card": check_problem_card,
        "challenge_report": check_challenge_report,
    }
    return kind, checks[kind](body)


def escape_unsafe(text: str) -> str:
    """Escapes a raw id for the text output: a backslash is doubled, so an
    escape sequence in the output always stands for one character."""
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


def emit(result: Dict[str, Any], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(result, indent=2))
        return
    if result["status"] == "error":
        print(f"error: {result['error']}", file=sys.stderr)
        return
    for violation in result["violations"]:
        # Messages carry ids only through show() or escape_unsafe(); the raw
        # node id is escaped here.
        where = f" {escape_unsafe(violation['node_id'])}" if violation["node_id"] is not None else ""
        source = f" [{violation['input']}]" if "input" in violation else ""
        print(f"{violation['rule_id']}{source}{where}: {violation['message']}")
    for reason in result.get("reasons", []):
        print(f"{reason['rule_id']}: {reason['message']}")
    count = len(result["violations"])
    noun = "violation" if count == 1 else "violations"
    rules = " ".join(result["rules_checked"])
    if "decision" in result:
        print(f"Result: {result['decision']} (gate; challenge {result['challenge']}; {count} {noun}; checked {rules}; structural rules only)")
        return
    print(f"Result: {result['status']} ({result['graph']}; {count} {noun}; checked {rules}; structural rules only)")


FORMATS = ("text", "json")


def error_result(target: Any, message: str) -> Dict[str, Any]:
    return {
        "output_version": OUTPUT_VERSION,
        "input_file": target,
        "graph": None,
        "status": "error",
        "rules_checked": [],
        "violations": [],
        "error": message,
    }


def requested_format(argv: Sequence[str]) -> str:
    """The --format value, read before argparse so that an argument error can
    still be reported in the requested format."""
    for index, arg in enumerate(argv):
        value = argv[index + 1] if arg == "--format" and index + 1 < len(argv) else None
        if arg.startswith("--format="):
            value = arg.split("=", 1)[1]
        if value in FORMATS:
            return value
    return "text"


class _Parser(argparse.ArgumentParser):
    def __init__(self, output_format: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.output_format = output_format

    def error(self, message: str) -> NoReturn:
        if self.output_format == "text":
            self.print_usage(sys.stderr)
        emit(error_result(None, f"invalid arguments: {message}"), self.output_format)
        sys.exit(EXIT_INPUT_ERROR)


def run(argv: Sequence[str], output_format: str) -> int:
    parser = _Parser(
        output_format,
        prog="check_graph.py",
        description="Check the structure of a requirement or skill graph declaration (read-only).",
    )
    parser.add_argument("file", nargs="?", help="declaration file (JSON)")
    parser.add_argument("--skills-dir", metavar="DIR", help="compatibility mode: read ## Child skills from DIR/*/SKILL.md")
    parser.add_argument("--gate", nargs="+", metavar="FILE", help="decide readiness: CARD GRAPH [REPORT]")
    parser.add_argument("--format", choices=FORMATS, default="text", help="output format (default: text)")
    args = parser.parse_args(argv)
    target = args.file if args.file is not None else args.skills_dir
    if args.gate is not None:
        target = list(args.gate)
    try:
        if sum(mode is not None for mode in (args.file, args.skills_dir, args.gate)) != 1:
            raise InputError("give exactly one of FILE, --skills-dir DIR, or --gate CARD GRAPH [REPORT]")
        if args.gate is not None:
            gate = run_gate(args.gate)
            result = error_result(target, "")
            result.update(gate, status="passed" if gate["decision"] == "ready" else "failed", error=None)
            emit(result, args.format)
            return EXIT_PASSED if gate["decision"] == "ready" else EXIT_VIOLATIONS
        if args.skills_dir is not None:
            kind, violations = check_skills_dir(Path(args.skills_dir))
        else:
            kind, violations = check_file(Path(args.file))
    except InputError as exc:
        emit(error_result(target, str(exc)), args.format)
        return EXIT_INPUT_ERROR
    result = error_result(target, "")
    result.update(
        graph=kind,
        status="failed" if violations else "passed",
        rules_checked=RULES_CHECKED[kind],
        violations=[{"rule_id": v.rule_id, "node_id": v.node_id, "message": v.message} for v in violations],
        error=None,
    )
    emit(result, args.format)
    return EXIT_VIOLATIONS if violations else EXIT_PASSED


def main(argv: Optional[Sequence[str]] = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    output_format = requested_format(arguments)
    try:
        return run(arguments, output_format)
    except Exception as exc:
        # A failure of the checker itself must not look like exit code 1
        # (violations): show the traceback and report it as an error.
        traceback.print_exc()
        emit(error_result(None, f"internal error: {type(exc).__name__}"), output_format)
        return EXIT_INPUT_ERROR


if __name__ == "__main__":
    sys.exit(main())
