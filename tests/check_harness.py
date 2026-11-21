#!/usr/bin/env python3
"""Check the files under harness/ against the format Claude Code reads.

Usage: python3 tests/check_harness.py [harness-directory]
Exits 0 when every check passes, 1 otherwise. Standard library only.

The limits come from the Claude Code and Agent Skills documentation:
- CLAUDE.md: target under 200 lines.
- Rules: `paths` is the only front matter field Claude Code reads.
- Skills: name of lowercase letters, digits, and hyphens, at most 64
  characters, without "anthropic" or "claude"; description at most 1,024
  characters, without XML tags; body under 500 lines; a reference file over
  100 lines has a table of contents.
- Subagents: `name` and `description` are required.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

CLAUDE_MD_MAX_LINES = 200
ALWAYS_LOADED_RULE_MAX_LINES = 60
SKILL_NAME_MAX = 64
SKILL_DESCRIPTION_MAX = 1024
SKILL_BODY_MAX_LINES = 500
REFERENCE_TOC_THRESHOLD = 100

# Front matter fields Claude Code reads. `metadata`, `license`, and
# `compatibility` are accepted by the Agent Skills format but ignored by
# Claude Code, so this repository does not use them.
SKILL_FIELDS = {
    "name", "description", "when_to_use", "argument-hint", "arguments",
    "disable-model-invocation", "user-invocable", "allowed-tools",
    "disallowed-tools", "model", "effort", "context", "agent", "background",
    "hooks", "paths", "shell",
}
AGENT_FIELDS = {
    "name", "description", "tools", "disallowedTools", "model", "effort",
    "permissionMode", "maxTurns", "autoCompactWindow", "skills", "mcpServers",
    "hooks", "memory", "background", "omitClaudeMd", "isolation", "color",
    "initialPrompt",
}
RULE_FIELDS = {"paths"}

# Files copied unchanged from an official source; their contents are not ours
# to restructure, so the reference checks skip them.
VENDORED = ("references/dads-docs/",)

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
TAG_RE = re.compile(r"<[^>]+>")
LINK_RE = re.compile(r"`((?:references|assets|scripts)/[^`\s]+)`")


def split_front_matter(text: str) -> tuple[dict[str, str] | None, str]:
    """Return (top-level front matter fields, body).

    Reads only top-level `key: value` lines, which is all these files use;
    nested lines are kept as part of the preceding key's value.
    """
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return None, text
    fields: dict[str, str] = {}
    key = None
    for line in text[4:end].splitlines():
        match = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$", line)
        if match:
            key = match.group(1)
            fields[key] = match.group(2).strip()
        elif key is not None and line.strip():
            fields[key] += "\n" + line.strip()
    return fields, text[end + 5:]


def unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def check_claude_md(root: Path, errors: list[str]) -> None:
    path = root / "CLAUDE.md"
    if not path.is_file():
        errors.append("CLAUDE.md: missing")
        return
    lines = path.read_text(encoding="utf-8").splitlines()
    if len(lines) > CLAUDE_MD_MAX_LINES:
        errors.append(f"CLAUDE.md: {len(lines)} lines, over {CLAUDE_MD_MAX_LINES}")


def check_rules(root: Path, errors: list[str]) -> None:
    rules = sorted((root / "rules").rglob("*.md"))
    if not rules:
        errors.append("rules/: no rule files")
    for path in rules:
        rel = path.relative_to(root)
        text = path.read_text(encoding="utf-8")
        fields, body = split_front_matter(text)
        if text.startswith("---") and fields is None:
            errors.append(f"{rel}: front matter is not closed")
            continue
        fields = fields or {}
        unknown = set(fields) - RULE_FIELDS
        if unknown:
            errors.append(f"{rel}: front matter fields Claude Code ignores: {sorted(unknown)}")
        if "paths" in fields and fields["paths"] in ("", "[]", '""', "''"):
            errors.append(f"{rel}: `paths` is empty")
        if not body.strip():
            errors.append(f"{rel}: empty body")
        if "paths" not in fields:
            count = len(body.splitlines())
            if count > ALWAYS_LOADED_RULE_MAX_LINES:
                errors.append(
                    f"{rel}: {count} lines load in every session; "
                    f"keep it under {ALWAYS_LOADED_RULE_MAX_LINES} or scope it with `paths`"
                )


def check_skills(root: Path, errors: list[str]) -> None:
    skills_dir = root / "skills"
    skill_dirs = sorted(p for p in skills_dir.iterdir() if p.is_dir() and not p.name.startswith(".")) if skills_dir.is_dir() else []
    if not skill_dirs:
        errors.append("skills/: no skills")
    for skill in skill_dirs:
        rel = skill.relative_to(root)
        skill_md = skill / "SKILL.md"
        if not skill_md.is_file():
            errors.append(f"{rel}: no SKILL.md")
            continue
        fields, body = split_front_matter(skill_md.read_text(encoding="utf-8"))
        if fields is None:
            errors.append(f"{rel}/SKILL.md: no front matter")
            continue
        unknown = set(fields) - SKILL_FIELDS
        if unknown:
            errors.append(f"{rel}/SKILL.md: front matter fields Claude Code ignores: {sorted(unknown)}")

        name = unquote(fields.get("name", ""))
        if name != skill.name:
            errors.append(f"{rel}/SKILL.md: name {name!r} differs from directory {skill.name!r}")
        if not NAME_RE.match(name) or len(name) > SKILL_NAME_MAX:
            errors.append(f"{rel}/SKILL.md: name must be lowercase letters, digits, hyphens, at most {SKILL_NAME_MAX}")
        if "anthropic" in name or "claude" in name:
            errors.append(f"{rel}/SKILL.md: name contains a reserved word")

        description = unquote(fields.get("description", ""))
        if not description:
            errors.append(f"{rel}/SKILL.md: no description")
        if len(description) > SKILL_DESCRIPTION_MAX:
            errors.append(f"{rel}/SKILL.md: description is {len(description)} characters, over {SKILL_DESCRIPTION_MAX}")
        if TAG_RE.search(description):
            errors.append(f"{rel}/SKILL.md: description contains an XML tag")
        if "Use when" not in description and "Use for" not in description:
            errors.append(f"{rel}/SKILL.md: description does not say when to use the skill")

        body_lines = len(body.splitlines())
        if body_lines >= SKILL_BODY_MAX_LINES:
            errors.append(f"{rel}/SKILL.md: body is {body_lines} lines, not under {SKILL_BODY_MAX_LINES}")

        for target in sorted(set(LINK_RE.findall(body))):
            if not (skill / target.rstrip("/")).exists():
                errors.append(f"{rel}/SKILL.md: points to {target}, which does not exist")

        for ref in sorted((skill / "references").glob("*.md")) if (skill / "references").is_dir() else []:
            ref_rel = ref.relative_to(root).as_posix()
            if any(marker in ref_rel for marker in VENDORED):
                continue
            ref_text = ref.read_text(encoding="utf-8")
            if f"references/{ref.name}" not in body:
                errors.append(f"{ref_rel}: not mentioned in SKILL.md, so it would never be read")
            if len(ref_text.splitlines()) > REFERENCE_TOC_THRESHOLD and not re.search(
                r"^## (Contents|Table of contents)\s*$", ref_text, re.MULTILINE
            ):
                errors.append(f"{ref_rel}: over {REFERENCE_TOC_THRESHOLD} lines without a contents section")


def check_agents(root: Path, errors: list[str]) -> None:
    agents = sorted((root / "agents").glob("*.md"))
    if not agents:
        errors.append("agents/: no agent files")
    for path in agents:
        rel = path.relative_to(root)
        fields, body = split_front_matter(path.read_text(encoding="utf-8"))
        if fields is None:
            errors.append(f"{rel}: no front matter")
            continue
        unknown = set(fields) - AGENT_FIELDS
        if unknown:
            errors.append(f"{rel}: front matter fields Claude Code ignores: {sorted(unknown)}")
        name = unquote(fields.get("name", ""))
        if name != path.stem:
            errors.append(f"{rel}: name {name!r} differs from file name {path.stem!r}")
        if ":" in name:
            errors.append(f"{rel}: name contains a colon")
        if not unquote(fields.get("description", "")):
            errors.append(f"{rel}: no description")
        if not body.strip():
            errors.append(f"{rel}: empty body, so the agent has no system prompt")


def main() -> int:
    default_root = Path(__file__).resolve().parent.parent / "harness"
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else default_root
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 1
    errors: list[str] = []
    check_claude_md(root, errors)
    check_rules(root, errors)
    check_skills(root, errors)
    check_agents(root, errors)
    for error in errors:
        print(f"FAIL {error}")
    if errors:
        print(f"{len(errors)} problem(s) in {root}")
        return 1
    print(f"OK {root}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
