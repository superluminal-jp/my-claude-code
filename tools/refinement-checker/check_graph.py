#!/usr/bin/env python3
"""Read-only structural checker for requirement and skill graphs.

Contract: specs/059-refinement-graph-checker/ (spec.md, contracts/cli.md,
data-model.md). A passing result means only that a declaration satisfies the
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
SCHEMA_VERSION = 1
MAX_INPUT_BYTES = 5 * 1024 * 1024

EXIT_PASSED = 0
EXIT_VIOLATIONS = 1
EXIT_INPUT_ERROR = 2

DECOMPOSITIONS = ("AND", "OR", "LEAF")
LEVELS = ("L1", "L2", "L3")
PERMISSIONS = ("read_only", "workspace_write", "external_effect")
ROLES = ("orchestrator", "worker", "auditor", "checker")
READ_ONLY_ROLES = ("auditor", "checker")

TOP_LEVEL_FIELDS = frozenset({"schema_version", "requirements", "skills"})
REQUIREMENT_FIELDS = frozenset(
    {"id", "statement", "decomposition", "children", "acceptance", "assumptions", "counterexamples", "selection"}
)
ACCEPTANCE_FIELDS = frozenset({"id", "description", "level"})
SKILL_FIELDS = frozenset({"id", "children", "permission", "role"})

RULES_CHECKED: Dict[str, List[str]] = {
    "requirements": ["S-00", "S-01", "S-02", "S-03", "S-04", "S-05", "S-06", "S-07", "S-08", "S-11"],
    "skills": ["S-00", "S-01", "S-02", "S-03", "S-08", "S-09"],
    "skills-dir": ["S-02", "S-03", "S-08", "S-10"],
}

# How spec 058 FR-001 declares a child, read exactly as declared_children in
# tests/run-config-pyramid.sh does (spec FR-004, research R6).
_CHILD_SECTION = re.compile(r"^## Child skills\s*$")
_CHILD_DECLARATION = re.compile(r"^- `([A-Za-z0-9_-]+)`")

# Characters that could forge or hide lines in the human-readable output
# (spec FR-013, CWE-117): controls, format characters such as bidirectional
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
    # A node whose id repeats an earlier one is still checked (review finding 2).
    duplicate: bool = False
    # False when ``children`` was not an array of strings; rules that count
    # children are then skipped instead of reporting a follow-on error.
    children_valid: bool = True


class Report:
    """Collects violations and returns them in a fixed order (research R4)."""

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
    # and line separators as they are (spec FR-013).
    return "".join(f"\\u{ord(c):04x}" if unicodedata.category(c) in _UNSAFE_CATEGORIES else c for c in text)


def is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and value.strip() != ""


def is_string_list(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


# --- reading input -----------------------------------------------------------


def read_text(path: Path, what: str) -> str:
    # O_NONBLOCK keeps a FIFO from blocking the open; fstat on the opened file
    # then rejects anything that is not a regular file, and the read is bounded
    # even when the reported size is wrong (review finding 3).
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
    # could hide part of a declaration (research R2).
    obj: Dict[str, Any] = {}
    for key, value in pairs:
        if key in obj:
            raise InputError(f"duplicate key {show(key)} in a JSON object")
        obj[key] = value
    return obj


def parse_declaration(text: str) -> Tuple[str, List[Any]]:
    """Validates the top level (spec FR-001) and returns (graph kind, nodes)."""
    try:
        document = json.loads(text, object_pairs_hook=_reject_duplicate_keys)
    except json.JSONDecodeError as exc:
        raise InputError(f"invalid JSON at line {exc.lineno} column {exc.colno}: {exc.msg}") from None
    except RecursionError:
        raise InputError("JSON nesting is too deep to read") from None
    if not isinstance(document, dict):
        raise InputError("the top level must be a JSON object")
    version = document.get("schema_version")
    if type(version) is not int or version != SCHEMA_VERSION:
        raise InputError(f"schema_version must be the integer {SCHEMA_VERSION} (got {show(version)})")
    undefined = sorted(set(document) - TOP_LEVEL_FIELDS)
    if undefined:
        raise InputError(f"undefined top-level field {show(undefined[0])}")
    kinds = [kind for kind in ("requirements", "skills") if kind in document]
    if len(kinds) != 1:
        raise InputError("the top level must have exactly one of requirements or skills")
    kind = kinds[0]
    if not isinstance(document[kind], list):
        raise InputError(f"{kind} must be an array")
    return kind, document[kind]


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
        # they still count as referenced (review finding 2).
        targets = edges.setdefault(node.node_id, [])
        targets.extend(child for child in seen if child in defined and child not in targets)
    return edges


def find_cycles(order: List[str], edges: Dict[str, List[str]]) -> List[List[str]]:
    """Iterative depth-first search (research R3). Each cycle starts at its
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
        # auditor or checker can reach must be read-only too (spec D6).
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


# --- compatibility mode (spec 058) --------------------------------------------


def declared_children(text: str) -> List[str]:
    """The names a SKILL.md declares in its "## Child skills" section."""
    names: List[str] = []
    in_code = in_section = False
    for line in text.split("\n"):
        if line.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
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
            # A self-declaration is already a cycle (S-03); spec 058 reports it
            # only once as well. Like spec 058, a child counts as a parent when
            # it declares anything, even a skill that does not exist.
            if child != node.node_id and declared[child]:
                report.add(
                    "S-10",
                    node.position,
                    node.node_id,
                    f"declares {show(child)}, which declares children of its own (spec 058 allows one level)",
                )
    return "skills-dir", report.violations()


# --- command line --------------------------------------------------------------


def check_file(path: Path) -> Tuple[str, List[Violation]]:
    kind, raw_nodes = parse_declaration(read_text(path, "the declaration file"))
    if kind == "skills":
        return kind, check_skills(raw_nodes)
    return kind, check_requirements(raw_nodes)


def escape_unsafe(text: str) -> str:
    """Escapes a raw id for the text output: a backslash is doubled, so an
    escape sequence in the output always stands for one character (spec FR-013)."""
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
        print(f"{violation['rule_id']}{where}: {violation['message']}")
    count = len(result["violations"])
    noun = "violation" if count == 1 else "violations"
    rules = " ".join(result["rules_checked"])
    print(f"Result: {result['status']} ({result['graph']}; {count} {noun}; checked {rules}; structural rules only)")


FORMATS = ("text", "json")


def error_result(target: Optional[str], message: str) -> Dict[str, Any]:
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
    still be reported in the requested format (review finding 4)."""
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
    parser.add_argument("--format", choices=FORMATS, default="text", help="output format (default: text)")
    args = parser.parse_args(argv)
    target = args.file if args.file is not None else args.skills_dir
    try:
        if (args.file is None) == (args.skills_dir is None):
            raise InputError("give exactly one of FILE or --skills-dir DIR")
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
