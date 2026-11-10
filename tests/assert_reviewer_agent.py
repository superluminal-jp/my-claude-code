#!/usr/bin/env python3
"""spec 070 R1a and R1b: the read-only reviewer the two review procedures start.

R1a: `harness/agents/read-only-reviewer.md` declares exactly the fields
name, description, tools, model, effort, and omitClaudeMd, with tools exactly
Read, Grep, and Glob, model sonnet, effort xhigh, and omitClaudeMd true, and
its body tells the reviewer to answer `NOT REVIEWED: <path>: <reason>` when a
file it was given cannot be read.

R1b: the challenger procedure (specify-requirements's SKILL.md and
references/challenge.md) and the assurance review procedure
(verify-change's SKILL.md and references/assurance-review.md) name the
definition's `name`, and no longer describe the reviewer only as "a new
subagent that can only read and search".

The other subagent definitions fix the model, effort, and tools of the work
they are for, so that delegation does not depend on a model named at each
call: `check-runner` and `file-searcher` run on haiku without CLAUDE.md, and
`file-searcher` cannot run commands; `task-worker` runs on sonnet at xhigh.

The script checks the repository's files, then checks that every one of a set
of single changes to them (another tool, another model, a missing field, a
procedure that does not name the reviewer, ...) is refused, so that the check
is shown able to fail on each rule.

Usage: assert_reviewer_agent.py REPO_ROOT. Exit 0 when the repository's files
pass and every changed copy is refused, 1 otherwise.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List, Tuple

AGENT = "harness/agents/read-only-reviewer.md"
PROCEDURES = (
    "harness/skills/specify-requirements/SKILL.md",
    "harness/skills/specify-requirements/references/challenge.md",
    "harness/skills/verify-change/SKILL.md",
    "harness/skills/verify-change/references/assurance-review.md",
)
# name -> the frontmatter values each of the other definitions must fix.
OTHER_AGENTS = {
    "check-runner": {"model": "haiku", "effort": "low", "tools": "Bash, Read, Grep, Glob", "omitClaudeMd": "true"},
    "file-searcher": {"model": "haiku", "effort": "medium", "tools": "Read, Grep, Glob", "omitClaudeMd": "true"},
    "task-worker": {"model": "sonnet", "effort": "xhigh"},
}
OLD_PHRASES = (
    "a new subagent that can only read and search",
    "a new subagent whose tools can only read and search",
)
FIELDS = {"name", "description", "tools", "model", "effort", "omitClaudeMd"}
EXPECTED = {"name": "read-only-reviewer", "model": "sonnet", "effort": "xhigh", "omitClaudeMd": "true"}
TOOLS = {"Read", "Grep", "Glob"}
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
    for line in head:
        key, sep, value = line.partition(":")
        if not sep or not key.strip() or key != key.strip():
            out.append(f"frontmatter line is not 'key: value': {line!r}")
            continue
        if key in fields:
            out.append(f"field {key} is given twice")
        fields[key] = value.strip()
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


def procedure_violations(texts: Dict[str, str], name: str) -> List[str]:
    out = []
    for rel, text in texts.items():
        if name not in text:
            out.append(f"{rel} does not name the reviewer {name}")
        for phrase in OLD_PHRASES:
            if phrase in text:
                out.append(f"{rel} still describes the reviewer as {phrase!r}")
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


def agent_name(text: str) -> str:
    head, _ = split_frontmatter(text)
    for line in head:
        key, _, value = line.partition(":")
        if key == "name":
            return value.strip()
    return ""


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
        ("no NOT REVIEWED answer", swap(NOT_REVIEWED, "a short note")),
    ]


def main(root: Path) -> int:
    agent_text = (root / AGENT).read_text(encoding="utf-8")
    texts = {rel: (root / rel).read_text(encoding="utf-8") for rel in PROCEDURES}
    name = agent_name(agent_text)
    failures = []
    for v in agent_violations(agent_text) + procedure_violations(texts, name) + other_agent_violations(root):
        failures.append(f"repository: {v}")
    if failures:
        # The changed copies are built from a passing definition; there is none.
        for f in failures:
            print(f"FAIL {f}", file=sys.stderr)
        return 1
    for label, changed in changed_agents(agent_text):
        if not agent_violations(changed):
            failures.append(f"a definition with {label} is not refused")
    first = PROCEDURES[0]
    unnamed = dict(texts, **{first: texts[first].replace(name, "a reviewer")})
    if not procedure_violations(unnamed, name):
        failures.append(f"a {first} that does not name {name} is not refused")
    old = dict(texts, **{first: texts[first] + "\n" + OLD_PHRASES[0] + "\n"})
    if not procedure_violations(old, name):
        failures.append(f"a {first} with the old description is not refused")
    for f in failures:
        print(f"FAIL {f}", file=sys.stderr)
    if failures:
        return 1
    print(f"ok: {AGENT} and the {len(PROCEDURES)} procedure files hold, and {len(changed_agents(agent_text)) + 2} changed copies are refused")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__.strip().splitlines()[-2], file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(main(Path(sys.argv[1])))
