#!/usr/bin/env python3
"""spec 070 R1a: the read-only reviewer, and the other subagent definitions.

R1a: `harness/agents/read-only-reviewer.md` declares exactly the fields
name, description, tools, model, effort, omitClaudeMd, and metadata (the
map of its place in the phase tree, with no key but phase, branch, and stage,
whose values tests/assert_role_tree.py checks; ADR-0029), with tools exactly
Read, Grep, and Glob, model sonnet, effort xhigh, and omitClaudeMd true, and
its body tells the reviewer to answer `NOT REVIEWED: <path>: <reason>` when a
file it was given cannot be read.

R1b (the challenger and assurance review procedures name the definition) was
dropped with the skills that held those procedures (ADR-0029).

The other subagent definitions fix the model, effort, and tools of the work
they are for, so that delegation does not depend on a model named at each
call: `check-runner` and `file-searcher` run on haiku without CLAUDE.md, and
`file-searcher` cannot run commands; `task-worker` runs on sonnet at xhigh.
`scrum-master-agent`, which holds the Scrum Master accountability that
apply-scrum-guide keeps apart from the Developer working in the main
conversation, runs on sonnet at xhigh without CLAUDE.md and can only read and
search, and that skill's SKILL.md names it.

The script checks the repository's files, then checks that every one of a set
of single changes to them (another tool, another model, a missing field, ...)
is refused, so that the check
is shown able to fail on each rule.

Usage: assert_reviewer_agent.py REPO_ROOT. Exit 0 when the repository's files
pass and every changed copy is refused, 1 otherwise.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List, Tuple

AGENT = "harness/agents/read-only-reviewer.md"
# name -> the frontmatter values each of the other definitions must fix.
OTHER_AGENTS = {
    "check-runner": {"model": "haiku", "effort": "low", "tools": "Bash, Read, Grep, Glob", "omitClaudeMd": "true"},
    "file-searcher": {"model": "haiku", "effort": "medium", "tools": "Read, Grep, Glob", "omitClaudeMd": "true"},
    "task-worker": {"model": "sonnet", "effort": "xhigh"},
    "scrum-master-agent": {"model": "sonnet", "effort": "xhigh", "tools": "Read, Grep, Glob", "omitClaudeMd": "true"},
}
# name -> the procedure files that start that subagent and so must name it.
STARTED_BY = {
    "scrum-master-agent": ("harness/skills/apply-scrum-guide/SKILL.md",),
}
FIELDS = {"name", "description", "tools", "model", "effort", "omitClaudeMd", "metadata"}
EXPECTED = {"name": "read-only-reviewer", "model": "sonnet", "effort": "xhigh", "omitClaudeMd": "true"}
TOOLS = {"Read", "Grep", "Glob"}
# The keys of the metadata map: the element's place in the phase tree (ADR-0029).
METADATA_KEYS = {"phase", "branch", "stage"}
NOT_REVIEWED = "NOT REVIEWED: <path>: <reason>"


def split_frontmatter(text: str) -> Tuple[List[str], str]:
    """The lines between the opening and closing '---', and the body after them."""
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return [], text
    for i, line in enumerate(lines[1:], 1):
        if line == "---":
            return lines[1:i], "\n".join(lines[i + 1:])
    return [], text


def agent_violations(text: str) -> List[str]:
    head, body = split_frontmatter(text)
    if not head:
        return ["the definition has no frontmatter between '---' lines"]
    fields: Dict[str, str] = {}
    out = []
    in_metadata = False
    for line in head:
        if in_metadata and line.startswith("  "):
            # An entry of the metadata map: one indented 'key: value' line.
            nested_key, nested_sep, nested_value = line[2:].partition(":")
            if not nested_sep or not nested_key or nested_key != nested_key.strip() or not nested_value.strip():
                out.append(f"metadata entry is not '  key: value': {line!r}")
            elif nested_key not in METADATA_KEYS:
                out.append(f"metadata key {nested_key!r} is not one of {sorted(METADATA_KEYS)}")
            continue
        key, sep, value = line.partition(":")
        if not sep or not key.strip() or key != key.strip():
            out.append(f"frontmatter line is not 'key: value': {line!r}")
            continue
        if key in fields:
            out.append(f"field {key} is given twice")
        fields[key] = value.strip()
        in_metadata = key == "metadata" and not value.strip()
    if set(fields) != FIELDS:
        out.append(f"fields must be exactly {sorted(FIELDS)}, not {sorted(fields)}")
    for key, want in EXPECTED.items():
        if key in fields and fields[key] != want:
            out.append(f"{key} must be {want}, not {fields[key]!r}")
    if "tools" in fields:
        tools = {t.strip() for t in fields["tools"].strip("[]").split(",") if t.strip()}
        if tools != TOOLS:
            out.append(f"tools must be exactly {sorted(TOOLS)}, not {sorted(tools)}")
    if not fields.get("description"):
        out.append("description must not be empty")
    if NOT_REVIEWED not in body:
        out.append(f"the body does not give the answer {NOT_REVIEWED!r} for a file that cannot be read")
    return out


def other_agent_violations(root: Path) -> List[str]:
    out = []
    for name, expected in OTHER_AGENTS.items():
        path = root / "harness" / "agents" / f"{name}.md"
        if not path.is_file():
            out.append(f"harness/agents/{name}.md is missing")
            continue
        head, body = split_frontmatter(path.read_text(encoding="utf-8"))
        fields = {key: value.strip() for key, _, value in (line.partition(":") for line in head)}
        if fields.get("name") != name:
            out.append(f"{name}: name must be {name}, not {fields.get('name')!r}")
        if not fields.get("description"):
            out.append(f"{name}: description must not be empty")
        for key, want in expected.items():
            if fields.get(key) != want:
                out.append(f"{name}: {key} must be {want!r}, not {fields.get(key)!r}")
        if not body.strip():
            out.append(f"{name}: the definition has no body")
    return out


def started_by_violations(texts: Dict[str, str], name: str) -> List[str]:
    return [f"{rel} does not name the subagent {name} it starts" for rel, text in texts.items() if name not in text]


def started_by_texts(root: Path) -> Dict[str, Dict[str, str]]:
    return {name: {rel: (root / rel).read_text(encoding="utf-8") for rel in files} for name, files in STARTED_BY.items()}


def changed_agents(text: str) -> List[Tuple[str, str]]:
    def swap(old: str, new: str) -> str:
        if old not in text:
            raise SystemExit(f"cannot build the changed copy: {old!r} is not in {AGENT}")
        return text.replace(old, new, 1)

    return [
        ("another name", swap("name: read-only-reviewer", "name: reader")),
        ("Bash among the tools", swap("tools: Read, Grep, Glob", "tools: Read, Grep, Glob, Bash")),
        ("Glob missing from the tools", swap("tools: Read, Grep, Glob", "tools: Read, Grep")),
        ("another model", swap("model: sonnet", "model: opus")),
        ("another effort", swap("effort: xhigh", "effort: high")),
        ("CLAUDE.md loaded", swap("omitClaudeMd: true", "omitClaudeMd: false")),
        ("a missing field", swap("effort: xhigh\n", "")),
        ("an extra field", swap("omitClaudeMd: true\n", "omitClaudeMd: true\npermissionMode: plan\n")),
        ("a metadata entry outside the map", swap("metadata:\n", "")),
        ("an unknown metadata key", swap("  branch: handoff\n", "  branch: handoff\n  owner: someone\n")),
        ("no NOT REVIEWED answer", swap(NOT_REVIEWED, "a short note")),
    ]


def main(root: Path) -> int:
    agent_text = (root / AGENT).read_text(encoding="utf-8")
    started = started_by_texts(root)
    failures = []
    started_violations = [v for other, files in started.items() for v in started_by_violations(files, other)]
    for v in agent_violations(agent_text) + other_agent_violations(root) + started_violations:
        failures.append(f"repository: {v}")
    if failures:
        # The changed copies are built from a passing definition; there is none.
        for f in failures:
            print(f"FAIL {f}", file=sys.stderr)
        return 1
    for label, changed in changed_agents(agent_text):
        if not agent_violations(changed):
            failures.append(f"a definition with {label} is not refused")
    for other, files in started.items():
        rel = next(iter(files))
        if not started_by_violations(dict(files, **{rel: files[rel].replace(other, "a subagent")}), other):
            failures.append(f"a {rel} that does not name {other} is not refused")
    for f in failures:
        print(f"FAIL {f}", file=sys.stderr)
    if failures:
        return 1
    print(f"ok: {AGENT} and the other definitions hold, and {len(changed_agents(agent_text)) + len(started)} changed copies are refused")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__.strip().splitlines()[-2], file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(main(Path(sys.argv[1])))
