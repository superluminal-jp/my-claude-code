#!/usr/bin/env python3
"""Check every skill package under a directory against the skill contract.

Usage: assert_skill_contract.py [SKILLS_DIR]   (default: harness/skills)

The contract is what makes a skill one unit that loads cheaply and runs
inside the Claude Code Bash sandbox:

  C-01  name: equals the directory, lowercase words joined by hyphens, <= 64
  C-02  description: one line, 1..1024 characters (Agent Skills
        specification), states an exclusion boundary, has no XML tags
  C-03  frontmatter keys: only the allowed ones; no when_to_use, no model
        (a model switch drops the prompt cache)
  C-04  metadata: kind, permission, sandbox have defined values; a skill that
        needs the network names its hosts
  C-05  body: <= 500 lines, <= 20000 characters, no prose block over 150
        words or 1200 characters
  C-06  sections: "Done when"; "Bundled files" when files are bundled; every
        top-level reference is named in SKILL.md with its load condition
  C-07  sandbox: no bare mktemp, no /tmp literal, no instruction to write
        outside the repository unless it names $TMPDIR; osascript only in a
        skill declared to run outside the sandbox; network commands only in
        a skill declared to need it
  C-08  names: no retired skill name; no other skill's name unless this
        skill is an orchestrator that declares it as a child
  C-09  paths: no install-root path, no placeholder such as <skill-dir>, no
        reference to this repository's specs/ or archive/
  C-10  links: package-relative Markdown links resolve
  C-11  parents: an orchestrator declares at least two existing children,
        none of them an orchestrator; no other kind declares children

Standard library only. Reads files and writes nothing. Exit 0 when every
check passes, 1 when any fails, 2 when the directory cannot be read.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ALLOWED_KEYS = {
    "name", "description", "license", "compatibility", "metadata",
    "allowed-tools", "disable-model-invocation", "user-invocable", "paths",
    "argument-hint", "effort", "context", "agent",
}
KINDS = {"worker", "overlay", "integration", "orchestrator"}
PERMISSIONS = {"read_only", "workspace_write", "external_effect"}
SANDBOX = {"inside", "network", "outside"}
RETIRED = (
    "apple-notes", "apple-reminders", "aws-research", "clarifier", "coder",
    "digital-agency-frontend", "digital-agency-slides", "git-workflow",
    "maintaining-living-documentation", "problem-definition",
    "product-strategy", "pyramid-structure", "requirements-decomposition",
    "scrum-master", "secure-logging", "system-diagrams", "verified-delivery",
)
EXCLUSION = re.compile(r"(Do not use|Not for|使わない|対象外)")
NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
TEXT_SUFFIXES = {".md", ".py", ".js", ".sh", ".swift", ".json", ".html", ".css", ".txt", ".yaml", ".yml"}
# Verbatim third-party archives and test data are not this skill's own text.
VENDORED_PARTS = {"dads-docs", "fixtures", "__pycache__", "node_modules"}
NETWORK_COMMANDS = re.compile(
    r"(^|[\s;&|(])(curl|wget|npm|npx|pip|pip3|uv|git clone)\s|playwright install"
)


def word_boundary(name: str) -> re.Pattern[str]:
    # \w is Unicode-aware, so a name inside a Japanese heading anchor such as
    # #誰がscrum-masterになれるか is not taken for the skill's name.
    return re.compile(r"(?<![\w/-])" + re.escape(name) + r"(?![\w-])")


def without_code(text: str) -> str:
    """Drop fenced blocks and inline code, where a link-shaped string is an example."""
    text = re.sub(r"^[ \t]*(```|~~~).*?^[ \t]*\1[ \t]*$", "", text, flags=re.S | re.M)
    return re.sub(r"`[^`\n]*`", "", text)


class Skill:
    def __init__(self, directory: Path) -> None:
        self.dir = directory
        self.dirname = directory.name
        self.text = (directory / "SKILL.md").read_text(encoding="utf-8")
        self.front: dict[str, str] = {}
        self.metadata: dict[str, str] = {}
        self.front_error = ""
        self.body = self.text
        match = re.match(r"^---\n(.*?)\n---\n", self.text, re.S)
        if not match:
            self.front_error = "no frontmatter block"
            return
        self.body = self.text[match.end():]
        in_metadata = False
        for line in match.group(1).split("\n"):
            if not line.strip():
                continue
            nested = re.match(r"^  ([A-Za-z0-9_-]+):\s*(.*)$", line)
            top = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
            if in_metadata and nested:
                self.metadata[nested.group(1)] = unquote(nested.group(2))
            elif top:
                in_metadata = top.group(1) == "metadata" and not top.group(2)
                self.front[top.group(1)] = unquote(top.group(2))
            else:
                self.front_error = f"frontmatter line is not 'key: value' on one line: {line!r}"

    def own_text_files(self, include_tests: bool = False):
        for path in sorted(self.dir.rglob("*")):
            if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
                continue
            parts = set(path.relative_to(self.dir).parts)
            if parts & VENDORED_PARTS:
                continue
            if not include_tests and "tests" in parts:
                continue
            yield path


def unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def prose_blocks(body: str):
    """Yield (line number, text) for each prose block outside tables and code."""
    block: list[str] = []
    start = 0
    fenced = False
    for number, line in enumerate(body.split("\n"), 1):
        if line.lstrip().startswith(("```", "~~~")):
            fenced = not fenced
            if block:
                yield start, " ".join(block)
                block = []
            continue
        is_table = line.lstrip().startswith("|")
        is_item_start = bool(re.match(r"^\s*([-*]|\d+\.)\s", line))
        if fenced or is_table or not line.strip() or is_item_start:
            if block:
                yield start, " ".join(block)
                block = []
            if fenced or is_table or not line.strip():
                continue
        if not block:
            start = number
        block.append(line.strip())
    if block:
        yield start, " ".join(block)


def child_names(body: str) -> list[str]:
    section = re.search(r"^## Child skills\s*\n(.*?)(?=^## |\Z)", body, re.S | re.M)
    if not section:
        return []
    return re.findall(r"^- `([^`]+)`\s*$", section.group(1), re.M)


def check_skill(skill: Skill, all_names: set[str], kinds: dict[str, str]) -> list[str]:
    failures: list[str] = []

    def fail(rule: str, message: str) -> None:
        failures.append(f"{rule} {skill.dirname}: {message}")

    if skill.front_error:
        fail("C-03", skill.front_error)

    name = skill.front.get("name", "")
    if name != skill.dirname:
        fail("C-01", f"name {name!r} is not the directory name")
    if not NAME.match(skill.dirname) or len(skill.dirname) > 64:
        fail("C-01", "name must be lowercase words joined by single hyphens, at most 64 characters")
    if re.search(r"anthropic|claude", skill.dirname):
        fail("C-01", "name contains a reserved word")

    description = skill.front.get("description", "")
    if not 1 <= len(description) <= 1024:
        fail("C-02", f"description is {len(description)} characters; the limit is 1..1024")
    if not EXCLUSION.search(description):
        fail("C-02", "description states no exclusion boundary (Do not use / Not for / 使わない / 対象外)")
    if re.search(r"<[A-Za-z/][^>]*>", description):
        fail("C-02", "description contains an XML tag")

    for key in skill.front:
        if key not in ALLOWED_KEYS:
            fail("C-03", f"frontmatter key {key!r} is not allowed")

    kind = skill.metadata.get("kind", "")
    sandbox = skill.metadata.get("sandbox", "")
    if kind not in KINDS:
        fail("C-04", f"metadata.kind {kind!r} is not one of {sorted(KINDS)}")
    if skill.metadata.get("permission", "") not in PERMISSIONS:
        fail("C-04", f"metadata.permission is not one of {sorted(PERMISSIONS)}")
    if sandbox not in SANDBOX:
        fail("C-04", f"metadata.sandbox {sandbox!r} is not one of {sorted(SANDBOX)}")
    if sandbox == "network" and not skill.metadata.get("network-hosts"):
        fail("C-04", "metadata.sandbox is network but metadata.network-hosts names no host")

    body_lines = skill.body.count("\n") + 1
    if body_lines > 500:
        fail("C-05", f"body has {body_lines} lines; the limit is 500")
    if len(skill.body) > 20000:
        fail("C-05", f"body has {len(skill.body)} characters; the limit is 20000")
    for line, text in prose_blocks(skill.body):
        words = len(text.split())
        if words > 150 or len(text) > 1200:
            fail("C-05", f"SKILL.md body line {line}: one block of {words} words, {len(text)} characters")

    if not re.search(r"^## (Done when|完了の確認)\s*$", skill.body, re.M):
        fail("C-06", "no '## Done when' section")
    bundled = [d for d in ("references", "scripts", "assets", "examples") if (skill.dir / d).is_dir()]
    if bundled and not re.search(r"^## (Bundled files|同梱ファイル)\s*$", skill.body, re.M):
        fail("C-06", f"bundles {', '.join(bundled)} but has no '## Bundled files' section")
    references = skill.dir / "references"
    if references.is_dir():
        for path in sorted(references.glob("*.md")):
            if f"references/{path.name}" not in skill.body:
                fail("C-06", f"references/{path.name} is not named in SKILL.md")

    others = sorted(all_names - {skill.dirname})
    declared = set(child_names(skill.body)) if kind == "orchestrator" else set()
    for path in skill.own_text_files():
        relative = path.relative_to(skill.dir).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        in_scripts = relative.startswith("scripts/")
        for number, line in enumerate(text.split("\n"), 1):
            where = f"{relative}:{number}"
            if "mktemp" in line and "TMPDIR" not in line:
                fail("C-07", f"{where}: mktemp without a $TMPDIR template fails in the sandbox")
            if re.search(r"(?<![A-Za-z0-9_$}{.:-])/tmp/", line):
                fail("C-07", f"{where}: /tmp literal; use $TMPDIR")
            if path.suffix == ".md" and "outside the repository" in line and "TMPDIR" not in line:
                fail("C-07", f"{where}: asks for a write outside the repository without naming $TMPDIR")
            if sandbox != "outside" and re.search(r"\bosascript\b", line):
                fail("C-07", f"{where}: osascript cannot run inside the sandbox")
            if in_scripts and sandbox != "network" and NETWORK_COMMANDS.search(line) and not line.lstrip().startswith("#"):
                fail("C-07", f"{where}: network command in a skill not declared sandbox: network")
        if path.suffix == ".md" or in_scripts:
            for retired in RETIRED:
                if word_boundary(retired).search(text):
                    fail("C-08", f"{relative}: names the retired skill {retired!r}")
        if path.suffix == ".md":
            for other in others:
                if other in declared:
                    continue
                if word_boundary(other).search(text):
                    fail("C-08", f"{relative}: names the skill {other!r}")
            for pattern, message in (
                (r"\.claude/skills/|~/\.claude/", "install-root path"),
                (r"<skill-dir>|<base>|<this skill", "placeholder for the skill directory; use ${CLAUDE_SKILL_DIR}"),
                (r"(?<![A-Za-z0-9_./-])(specs/[0-9]{3}|archive/)", "reference to this repository's specs/ or archive/"),
            ):
                if re.search(pattern, text):
                    fail("C-09", f"{relative}: {message}")
            for target in re.findall(r"\]\(([^)\s]+)\)", without_code(text)):
                if re.match(r"^([a-z][a-z0-9+.-]*:|#|<)", target):
                    continue
                target_path = (path.parent / target.split("#", 1)[0]).resolve()
                if not target_path.exists():
                    fail("C-10", f"{relative}: link target {target!r} does not exist")

    children = child_names(skill.body)
    if kind == "orchestrator":
        if len(children) < 2:
            fail("C-11", "an orchestrator declares at least two children under '## Child skills'")
        for child in children:
            if child not in all_names:
                fail("C-11", f"declared child {child!r} is not a skill")
            elif kinds.get(child) == "orchestrator":
                fail("C-11", f"declared child {child!r} is itself an orchestrator")
    elif children:
        fail("C-11", "only an orchestrator may have a '## Child skills' section")
    return failures


def main(argv: list[str]) -> int:
    root = Path(argv[1] if len(argv) > 1 else "harness/skills")
    if not root.is_dir():
        print(f"skill-contract: {root} is not a directory", file=sys.stderr)
        return 2
    skills = [Skill(d) for d in sorted(root.iterdir()) if (d / "SKILL.md").is_file()]
    if not skills:
        print(f"skill-contract: no skill found under {root}", file=sys.stderr)
        return 2
    names = {s.dirname for s in skills}
    kinds = {s.dirname: s.metadata.get("kind", "") for s in skills}
    failures: list[str] = []
    for skill in skills:
        failures.extend(check_skill(skill, names, kinds))
    for skill in skills:
        print(
            f"{skill.dirname:28s} kind={skill.metadata.get('kind', '-'):12s} "
            f"sandbox={skill.metadata.get('sandbox', '-'):8s} "
            f"description={len(skill.front.get('description', '')):4d} "
            f"body={len(skill.body.split()):5d} words"
        )
    for failure in failures:
        print(f"FAIL {failure}", file=sys.stderr)
    print(f"skill-contract: {len(skills)} skills, {len(failures)} failures")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
