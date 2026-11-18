#!/usr/bin/env python3
"""ADR-0029: every skill and agent of the harness has one place in the phase tree.

The tree has three levels below the harness: the AI-DLC phase the element's
main output supports (Ideation, Inception, Construction, Operation, or
Cross-phase when it is tied to none), the branch of harness/CLAUDE.md it
supports (define, execute, handoff), and the element. Each element declares
its place in its own frontmatter:

  metadata:
    phase: construction
    branch: execute
    stage: E-implement   # only when its stages span several branches

Rules, each reported with the element it concerns:

  DECL     every harness/skills/*/SKILL.md and harness/agents/*.md declares
           phase and branch exactly once, with values from
           assert_skill_contract.PHASES and BRANCHES
  MAP      docs/harness/capability-map.json names the element as a component
           and gives it at least one stage
  BRANCH   when the element's stages carry one branch, branch is that branch
  STAGE    when they carry several, stage is one of its stages and branch is
           that stage's branch; a stage that is given is always one of them
  TAG      the description ends with " [<Phase> / <branch>]"
  README   README.md and README.ja.md hold, between <!-- role-tree:start -->
           and <!-- role-tree:end -->, the table this script generates
  PURPOSE  every purpose cell of those tables is one sentence (the
           description's first, without the tag)
  TREE     in the diagram block of that page, every node but the root is the
           head of exactly one edge, and every edge joins declared nodes
  DIAGRAM  docs/harness/skill-map/03-role-tree.md holds, between
           <!-- role-tree-diagram:start --> and <!-- role-tree-diagram:end -->,
           the Mermaid block this script generates

Usage (from the repository root, or with --root):
  assert_role_tree.py              check every rule
  assert_role_tree.py --print      print the tree as text
  assert_role_tree.py --names      print the element names, one per line
  assert_role_tree.py --table en|ja  print the README table
  assert_role_tree.py --mermaid    print the diagram block
  assert_role_tree.py --self-test  check the repository, then check that a
                                   copy with one rule broken is refused, for
                                   every rule
Exit 0 when every rule holds, 1 when one fails, 2 when a file cannot be read.
Standard library only; reads files and writes only under $TMPDIR (self-test).
"""
from __future__ import annotations

import json
import re
import shutil
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

sys.path.insert(0, str(Path(__file__).resolve().parent))
from assert_skill_contract import BRANCHES, PHASES  # noqa: E402

PHASE_ORDER = ("ideation", "inception", "construction", "operation", "cross-phase")
PHASE_LABEL = {
    "ideation": "Ideation", "inception": "Inception", "construction": "Construction",
    "operation": "Operation", "cross-phase": "Cross-phase",
}
PHASE_GLOSS = {
    "ideation": "意図と範囲を確かめる",
    "inception": "要件と設計を定める",
    "construction": "作り、試す",
    "operation": "配備し、運用する",
    "cross-phase": "どのフェーズにも重ねて使う",
}
BRANCH_ORDER = ("define", "execute", "handoff")
BRANCH_GLOSS = {"define": "1 正しい作業を定める", "execute": "2 統制の下で実行する", "handoff": "3 引き渡す"}
KIND_LABEL = {"en": {"skill": "skill", "agent": "agent"}, "ja": {"skill": "スキル", "agent": "エージェント"}}
TABLE_HEADER = {"en": ("Phase", "Branch", "Name", "Kind", "Purpose"), "ja": ("フェーズ", "枝", "名前", "種類", "目的")}
READMES = {"README.md": "en", "README.ja.md": "ja"}
DIAGRAM_PAGE = "docs/harness/skill-map/03-role-tree.md"
CAPABILITY_MAP = "docs/harness/capability-map.json"
README_MARK = ("<!-- role-tree:start -->", "<!-- role-tree:end -->")
DIAGRAM_MARK = ("<!-- role-tree-diagram:start -->", "<!-- role-tree-diagram:end -->")
# A sentence ends at 。 or at a period followed by whitespace; "draw.io" does not.
SENTENCE_BREAK = re.compile(r"。(?=\S)|\.(?=\s+\S)")
TOP = re.compile(r"^([A-Za-z0-9_-]+):\s*(.*)$")
NESTED = re.compile(r"^  ([A-Za-z0-9_-]+):\s*(.*)$")


class Unreadable(Exception):
    pass


@dataclass
class Element:
    name: str
    kind: str  # "skill" or "agent"
    path: str
    description: str = ""
    metadata: dict[str, str] = field(default_factory=dict)
    duplicates: list[str] = field(default_factory=list)

    @property
    def component(self) -> str:
        return f"skill:{self.name}" if self.kind == "skill" else f"agent:{self.name}.md"

    @property
    def placed(self) -> bool:
        return self.metadata.get("phase") in PHASES and self.metadata.get("branch") in BRANCHES


def unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def read(root: Path, rel: str) -> str:
    try:
        return (root / rel).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise Unreadable(f"{rel}: {exc}") from exc


def parse(root: Path, rel: str, name: str, kind: str) -> Element:
    element = Element(name, kind, rel)
    match = re.match(r"^---\n(.*?)\n---\n", read(root, rel), re.S)
    if not match:
        return element
    seen_top: set[str] = set()
    in_metadata = False
    for line in match.group(1).split("\n"):
        nested, top = NESTED.match(line), TOP.match(line)
        if in_metadata and nested:
            key = nested.group(1)
            if key in element.metadata:
                element.duplicates.append(f"metadata.{key}")
            element.metadata[key] = unquote(nested.group(2))
        elif top:
            key = top.group(1)
            if key in seen_top:
                element.duplicates.append(key)
            seen_top.add(key)
            in_metadata = key == "metadata" and not top.group(2)
            if key == "description":
                element.description = unquote(top.group(2))
    return element


def elements(root: Path) -> list[Element]:
    found = [
        parse(root, f"harness/skills/{d.name}/SKILL.md", d.name, "skill")
        for d in sorted((root / "harness/skills").iterdir())
        if (d / "SKILL.md").is_file()
    ]
    found += [
        parse(root, f"harness/agents/{p.name}", p.stem, "agent")
        for p in sorted((root / "harness/agents").glob("*.md"))
    ]
    return sorted(found, key=lambda e: e.name)


def tag(element: Element) -> str:
    return f" [{PHASE_LABEL[element.metadata['phase']]} / {element.metadata['branch']}]"


def purpose(element: Element) -> str:
    text = element.description
    if element.placed and text.endswith(tag(element)):
        text = text[: -len(tag(element))]
    match = re.match(r"^(.*?(?:。|\.(?=\s|$)))", text)
    return (match.group(1) if match else text).replace("|", "\\|")


def grouped(items: list[Element]) -> list[tuple[str, str, list[Element]]]:
    groups = []
    for role in PHASE_ORDER:
        for branch in BRANCH_ORDER:
            members = [e for e in items if e.placed and e.metadata["phase"] == role and e.metadata["branch"] == branch]
            if members:
                groups.append((role, branch, members))
    return groups


def text_tree(items: list[Element]) -> str:
    lines = ["harness"]
    groups = grouped(items)
    roles = [r for r in PHASE_ORDER if any(g[0] == r for g in groups)]
    unplaced = [e for e in items if not e.placed]
    for ri, role in enumerate(roles):
        last_role = ri == len(roles) - 1 and not unplaced
        lines.append(("└── " if last_role else "├── ") + PHASE_LABEL[role])
        pad = "    " if last_role else "│   "
        branches = [g for g in groups if g[0] == role]
        for bi, (_, branch, members) in enumerate(branches):
            last_branch = bi == len(branches) - 1
            lines.append(pad + ("└── " if last_branch else "├── ") + branch)
            pad2 = pad + ("    " if last_branch else "│   ")
            for mi, member in enumerate(members):
                lines.append(pad2 + ("└── " if mi == len(members) - 1 else "├── ") + f"{member.name} ({member.kind})")
    if unplaced:
        lines.append("└── (unplaced)")
        for mi, member in enumerate(unplaced):
            lines.append("    " + ("└── " if mi == len(unplaced) - 1 else "├── ") + f"{member.name} ({member.kind})")
    return "\n".join(lines) + "\n"


def table(items: list[Element], lang: str) -> str:
    header = TABLE_HEADER[lang]
    rows = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    for role, branch, members in grouped(items):
        for member in members:
            rows.append(f"| {PHASE_LABEL[role]} | {branch} | `{member.name}` | {KIND_LABEL[lang][member.kind]} | {purpose(member)} |")
    return "\n".join(rows) + "\n"


def ident(name: str) -> str:
    return name.replace("-", "_")


def mermaid(items: list[Element]) -> str:
    out = [
        "```mermaid",
        "flowchart LR",
        "  accTitle: コンポーネント図: フェーズの木",
        "  accDescr: harness のスキルとエージェントを、AI-DLC のフェーズ、作業の枝、要素の3段の木に置いた図。"
        "どの要素も親は1つで、各要素の前付けの metadata.phase と metadata.branch から生成している。",
        '  harness["ハーネス<br/>[このシステム: harness/skills/ と harness/agents/]"]:::system',
    ]
    edges = []
    groups = grouped(items)
    for role in PHASE_ORDER:
        if not any(g[0] == role for g in groups):
            continue
        rid = f"role_{ident(role)}"
        out.append(f'  {rid}["{PHASE_LABEL[role]}<br/>[フェーズ: {PHASE_GLOSS[role]}]"]:::container')
        edges.append(f'  harness -->|"含む"| {rid}')
        for _, branch, members in (g for g in groups if g[0] == role):
            bid = f"{ident(role)}_{branch}"
            out.append(f'  {bid}["{branch}<br/>[枝: {BRANCH_GLOSS[branch]}]"]:::component')
            edges.append(f'  {rid} -->|"含む"| {bid}')
            for member in members:
                out.append(f'  {ident(member.name)}["{member.name}<br/>[{KIND_LABEL["ja"][member.kind]}]"]:::component')
                edges.append(f'  {bid} -->|"含む"| {ident(member.name)}')
    out += edges
    out += [
        "  classDef system fill:#DCE9F7,stroke:#1F4E79,stroke-width:2px,color:#0B1F33",
        "  classDef container fill:#E8F1FB,stroke:#1F4E79,color:#0B1F33",
        "  classDef component fill:#F3F8FD,stroke:#1F4E79,color:#0B1F33",
        "```",
    ]
    return "\n".join(out) + "\n"


def tree_violations(block: str) -> list[str]:
    """Read the diagram block as a graph: one root, and one parent for every other node."""
    nodes = re.findall(r"^  ([A-Za-z_][A-Za-z0-9_]*)\[", block, re.M)
    edges = re.findall(r"^  ([A-Za-z_][A-Za-z0-9_]*) -->\|\"[^\"]*\"\| ([A-Za-z_][A-Za-z0-9_]*)$", block, re.M)
    out = [f"edge {a} --> {b} joins a node that is not declared" for a, b in edges if a not in nodes or b not in nodes]
    heads = [b for _, b in edges]
    roots = [n for n in nodes if n not in heads]
    if len(roots) != 1:
        out.append(f"the diagram has {len(roots)} roots {roots}, not one")
    out += [f"{n} has {heads.count(n)} parents" for n in nodes if heads.count(n) > 1]
    return out


def between(text: str, marks: tuple[str, str]) -> str | None:
    start, end = text.find(marks[0]), text.find(marks[1])
    if start < 0 or end < start:
        return None
    return text[start + len(marks[0]):end].strip("\n") + "\n"


def check(root: Path) -> list[tuple[str, str, str]]:
    """Every violation as (rule, element or file, message)."""
    items = elements(root)
    out: list[tuple[str, str, str]] = []
    try:
        cmap = json.loads(read(root, CAPABILITY_MAP))
    except json.JSONDecodeError as exc:
        raise Unreadable(f"{CAPABILITY_MAP}: {exc}") from exc
    components = {c["id"] for c in cmap.get("components", [])}
    stages = cmap.get("stages", [])
    for e in items:
        for dup in e.duplicates:
            out.append(("DECL", e.name, f"{e.path}: {dup} is given more than once"))
        if e.metadata.get("phase") not in PHASES:
            out.append(("DECL", e.name, f"{e.path}: metadata.phase {e.metadata.get('phase')!r} is not one of {sorted(PHASES)}"))
        if e.metadata.get("branch") not in BRANCHES:
            out.append(("DECL", e.name, f"{e.path}: metadata.branch {e.metadata.get('branch')!r} is not one of {sorted(BRANCHES)}"))
        if e.component not in components:
            out.append(("MAP", e.name, f"{CAPABILITY_MAP} has no component {e.component}"))
        own = {s["id"]: s["branch"] for s in stages if e.component in s.get("owners", [])}
        if not own:
            out.append(("MAP", e.name, f"{CAPABILITY_MAP} gives {e.component} no stage"))
        branch, stage = e.metadata.get("branch"), e.metadata.get("stage")
        if stage is not None and stage not in own:
            out.append(("STAGE", e.name, f"metadata.stage {stage!r} is not one of its stages {sorted(own)}"))
        elif stage is not None and own[stage] != branch:
            out.append(("STAGE", e.name, f"metadata.stage {stage} is on branch {own[stage]}, not {branch}"))
        if len(set(own.values())) == 1 and branch != next(iter(own.values())):
            out.append(("BRANCH", e.name, f"its stages {sorted(own)} are all on branch {next(iter(own.values()))}, not {branch}"))
        if len(set(own.values())) > 1 and stage is None:
            out.append(("STAGE", e.name, f"its stages {sorted(own)} span branches {sorted(set(own.values()))}; metadata.stage must name one"))
        if not e.placed or not e.description.endswith(tag(e)):
            want = tag(e) if e.placed else " [<Phase> / <branch>]"
            out.append(("TAG", e.name, f"{e.path}: the description does not end with {want.strip()!r}"))
    for rel, lang in READMES.items():
        block = between(read(root, rel), README_MARK)
        if block is None:
            out.append(("README", rel, f"no {README_MARK[0]} ... {README_MARK[1]} block"))
        elif block != table(items, lang):
            out.append(("README", rel, "the phase table differs from the declarations; regenerate it with --table " + lang))
        for row in re.findall(r"^\| [^|]+ \| [^|]+ \| `([^`]+)` \| [^|]+ \| (.*) \|$", block or "", re.M):
            name, cell = row
            if SENTENCE_BREAK.search(cell.rstrip("。.")):
                out.append(("PURPOSE", rel, f"the purpose of {name} is more than one sentence: {cell[:60]!r}..."))
    block = between(read(root, DIAGRAM_PAGE), DIAGRAM_MARK) if (root / DIAGRAM_PAGE).is_file() else None
    if block is None:
        out.append(("DIAGRAM", DIAGRAM_PAGE, f"no {DIAGRAM_MARK[0]} ... {DIAGRAM_MARK[1]} block"))
    elif block != mermaid(items):
        out.append(("DIAGRAM", DIAGRAM_PAGE, "the tree diagram differs from the declarations; regenerate it with --mermaid"))
    if block is not None:
        out += [("TREE", DIAGRAM_PAGE, message) for message in tree_violations(block)]
    return out


# --- self-test: one rule broken per copy -------------------------------------------------

def replace_in(rel: str, old: str, new: str) -> Callable[[Path], None]:
    def apply(root: Path) -> None:
        path = root / rel
        text = path.read_text(encoding="utf-8")
        if old not in text:
            raise AssertionError(f"self-test cannot apply: {old!r} not in {rel}")
        path.write_text(text.replace(old, new, 1), encoding="utf-8")
    return apply


def drop_metadata(rel: str) -> Callable[[Path], None]:
    def apply(root: Path) -> None:
        path = root / rel
        text = re.sub(r"\nmetadata:\n(  [^\n]*\n)+", "\n", path.read_text(encoding="utf-8"), count=1)
        path.write_text(text, encoding="utf-8")
    return apply


def drop_component(component: str) -> Callable[[Path], None]:
    def apply(root: Path) -> None:
        path = root / CAPABILITY_MAP
        cmap = json.loads(path.read_text(encoding="utf-8"))
        cmap["components"] = [c for c in cmap["components"] if c["id"] != component]
        path.write_text(json.dumps(cmap, ensure_ascii=False, indent=2), encoding="utf-8")
    return apply


def add_agent(root: Path) -> None:
    (root / "harness/agents/extra-agent.md").write_text(
        "---\nname: extra-agent\ndescription: A new agent without a place.\n---\n\nBody.\n", encoding="utf-8")


def first_table_row(lang: str) -> Callable[[Path], None]:
    def apply(root: Path) -> None:
        rel = next(r for r, l in READMES.items() if l == lang)
        path = root / rel
        text = path.read_text(encoding="utf-8")
        start = text.index(README_MARK[0])
        row = re.search(r"^\| Ideation \| [^|]+ \| `[^`]+` \| [^|]+ \| ", text[start:], re.M)
        if not row:
            raise AssertionError(f"self-test cannot apply: no Ideation row in {rel}")
        at = start + row.end()
        path.write_text(text[:at] + "Rewritten by hand. " + text[at:], encoding="utf-8")
    return apply


def two_sentences(lang: str) -> Callable[[Path], None]:
    def apply(root: Path) -> None:
        rel = next(r for r, l in READMES.items() if l == lang)
        path = root / rel
        text = path.read_text(encoding="utf-8")
        start = text.index(README_MARK[0])
        row = re.search(r"^\| Construction \| [^|]+ \| `[^`]+` \| [^|]+ \| ", text[start:], re.M)
        if not row:
            raise AssertionError(f"self-test cannot apply: no Construction row in {rel}")
        at = start + row.end()
        path.write_text(text[:at] + "一文目を足した。" + text[at:], encoding="utf-8")
    return apply


MUTATIONS: list[tuple[str, str, Callable[[Path], None]]] = [
    ("an agent definition without metadata", "DECL", drop_metadata("harness/agents/check-runner.md")),
    ("a skill whose phase is not defined", "DECL", replace_in("harness/skills/implement-change/SKILL.md", "  phase: construction", "  phase: testing")),
    ("a single-branch element on another branch", "BRANCH", replace_in("harness/skills/define-problem/SKILL.md", "  branch: define", "  branch: execute")),
    ("an element missing from the capability map", "MAP", drop_component("skill:clarify-intent")),
    ("phase given twice", "DECL", replace_in("harness/skills/sync-docs/SKILL.md", "  phase: cross-phase\n", "  phase: cross-phase\n  phase: cross-phase\n")),
    ("a new agent definition without a place", "DECL", add_agent),
    ("a multi-branch element without stage", "STAGE", replace_in("harness/skills/implement-change/SKILL.md", "  stage: E-implement\n", "")),
    ("a stage on another branch than the declared one", "STAGE", replace_in("harness/agents/read-only-reviewer.md", "  stage: H-verify", "  stage: E-delegate")),
    ("a description without its tag", "TAG", replace_in("harness/skills/sync-docs/SKILL.md", " [Cross-phase / handoff]\n", "\n")),
    ("a tag naming another phase", "TAG", replace_in("harness/skills/structure-document/SKILL.md", " [Cross-phase / handoff]\n", " [Ideation / handoff]\n")),
    ("a README table row edited by hand", "README", first_table_row("en")),
    ("a README.ja table row edited by hand", "README", first_table_row("ja")),
    ("a README.ja purpose cell of two sentences", "PURPOSE", two_sentences("ja")),
    ("a node with a second parent in the tree diagram", "TREE",
     replace_in(DIAGRAM_PAGE, '  construction_execute -->|"含む"| implement_change\n',
                '  construction_execute -->|"含む"| implement_change\n  cross_phase_handoff -->|"含む"| implement_change\n')),
    ("a tree diagram edited by hand", "DIAGRAM", replace_in(DIAGRAM_PAGE, '-->|"含む"| define_problem', '-->|"含む"| define_problems')),
]


def copy_inputs(root: Path, dest: Path) -> None:
    rels = [f"harness/skills/{d.name}/SKILL.md" for d in (root / "harness/skills").iterdir() if (d / "SKILL.md").is_file()]
    rels += [f"harness/agents/{p.name}" for p in (root / "harness/agents").glob("*.md")]
    rels += [CAPABILITY_MAP, DIAGRAM_PAGE, *READMES]
    for rel in rels:
        (dest / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / rel, dest / rel)


def self_test(root: Path) -> int:
    failures = check(root)
    if failures:
        for rule, where, message in failures:
            print(f"FAIL {rule} {where}: {message}", file=sys.stderr)
        print("role-tree self-test: the repository itself fails, so no copy was tried", file=sys.stderr)
        return 1
    missed = 0
    for label, rule, mutate in MUTATIONS:
        with tempfile.TemporaryDirectory(prefix="role-tree-") as tmp:
            copy_root = Path(tmp)
            copy_inputs(root, copy_root)
            mutate(copy_root)
            rules = {r for r, _, _ in check(copy_root)}
        refused = rule in rules
        missed += not refused
        print(f"{'refused' if refused else 'MISSED '} {rule:8s} {label}")
    print(f"role-tree self-test: {len(MUTATIONS) - missed} of {len(MUTATIONS)} broken copies refused")
    return 1 if missed else 0


def main(argv: list[str]) -> int:
    args = argv[1:]
    root = Path.cwd()
    if "--root" in args:
        i = args.index("--root")
        root = Path(args[i + 1])
        del args[i:i + 2]
    try:
        if args == ["--print"]:
            sys.stdout.write(text_tree(elements(root)))
            return 0
        if args == ["--names"]:
            sys.stdout.write("".join(f"{e.name}\n" for e in elements(root)))
            return 0
        if len(args) == 2 and args[0] == "--table" and args[1] in TABLE_HEADER:
            sys.stdout.write(table(elements(root), args[1]))
            return 0
        if args == ["--mermaid"]:
            sys.stdout.write(mermaid(elements(root)))
            return 0
        if args == ["--self-test"]:
            return self_test(root)
        if args:
            print(__doc__, file=sys.stderr)
            return 2
        failures = check(root)
    except (Unreadable, OSError) as exc:
        print(f"role-tree: cannot read {exc}", file=sys.stderr)
        return 2
    for rule, where, message in failures:
        print(f"FAIL {rule} {where}: {message}", file=sys.stderr)
    count = len(elements(root))
    print(f"phase-tree: {count} elements, {len(failures)} violations")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
