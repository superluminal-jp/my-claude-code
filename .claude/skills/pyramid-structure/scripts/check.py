#!/usr/bin/env python3
"""Mechanical Minto-pyramid checks (stdlib only).

Usage:
  check.py md FILE.md|- [--template H1,H2] [--offtree H1,H2] [--pair M:R]... [--max-group N]
  check.py tree FILE.json|-
Output: one finding per line "<E|W|I> <rule> <loc> <msg>", then "ok" or "E=n W=n I=n".
Exit: 0 no errors, 1 errors found, 2 unreadable input.
"""

from __future__ import annotations

import argparse
import itertools
import json
import re
import sys
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------- findings


@dataclass(frozen=True)
class Finding:
    sev: str  # E error | W warning | I info
    rule: str
    loc: str
    msg: str

    def __str__(self) -> str:
        return f"{self.sev} {self.rule} {self.loc} {self.msg}"


# Topic labels: headings/claims that name a topic instead of stating a claim.
LABELS = frozenset(
    {
        "introduction",
        "background",
        "purpose",
        "objective",
        "objectives",
        "method",
        "methods",
        "materials and methods",
        "methodology",
        "results",
        "findings",
        "discussion",
        "conclusion",
        "conclusions",
        "summary",
        "overview",
        "analysis",
        "issues",
        "problems",
        "challenges",
        "reasons",
        "risks",
        "recommendations",
        "proposal",
        "next steps",
        "details",
        "notes",
        "はじめに",
        "背景",
        "目的",
        "方法",
        "手法",
        "材料と方法",
        "結果",
        "考察",
        "結論",
        "まとめ",
        "概要",
        "分析",
        "課題",
        "問題点",
        "理由",
        "リスク",
        "提案",
        "今後の課題",
        "詳細",
        "序論",
        "本論",
        "おわりに",
    }
)
# Conventional non-claim sections: not labels, not counted as group members.
OFFTREE = frozenset(
    {
        "sources",
        "出典",
        "abstract",
        "references",
        "bibliography",
        "appendix",
        "appendices",
        "acknowledgments",
        "acknowledgements",
        "supplementary material",
        "要旨",
        "抄録",
        "参考文献",
        "引用文献",
        "付録",
        "謝辞",
        "補足資料",
    }
)
_NUM_PREFIX = re.compile(r"^(?:\d+(?:\.\d+)*\.?|[IVX]+\.|第\s*\d+\s*[章節])\s*")


def norm(title: str) -> str:
    """Strip outline numbering and casefold, for label lookup."""
    return _NUM_PREFIX.sub("", title.strip()).strip().casefold()


# ---------------------------------------------------------------- markdown


@dataclass
class Item:
    """A list item; nested items are its children."""

    text: str
    line: int
    indent: int
    children: list[Item] = field(default_factory=list)


@dataclass
class Section:
    level: int
    title: str
    line: int
    body: int = 0  # non-blank content lines before the next heading
    children: list[Section] = field(default_factory=list)
    lists: list[list[Item]] = field(default_factory=list)  # contiguous top-level lists in the body
    pseudo: list[tuple[int, str]] = field(default_factory=list)  # (line, text) of bold-only lines used as headings


@dataclass
class Doc:
    root: Section  # level 0; holds content before the first heading
    sections: list[Section]  # headings in document order
    opening: str  # kind of the first content block: para, list, table, code or none
    opening_line: int


_HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
_FENCE = re.compile(r"^\s*(```|~~~)")
_LIST = re.compile(r"^(\s*)(?:[-*+]|\d+[.)])\s+(.*)$")


def parse_md(text: str) -> Doc:
    """Parse ATX headings and list items into trees; skip YAML front matter and fenced code."""
    lines = text.splitlines()
    start = 0
    if lines and lines[0].strip() == "---":
        for j in range(1, len(lines)):
            if lines[j].strip() in ("---", "..."):
                start = j + 1
                break
    root = Section(0, "", 0)
    stack = [root]
    flat: list[Section] = []
    fence, opening, opening_line = "", "none", 0
    group: list[Item] | None = None
    istack: list[Item] = []
    in_comment = False  # inside an HTML comment that spans lines
    for i, raw in enumerate(lines[start:], start + 1):
        if in_comment:
            in_comment = "-->" not in raw
            continue
        m_fence = _FENCE.match(raw)
        if m_fence or fence:
            if m_fence and not fence:
                fence = m_fence.group(1)
                if opening == "none":
                    opening, opening_line = "code", i
                if not raw[:1].isspace():
                    group, istack = None, []
            elif m_fence and m_fence.group(1) == fence:
                fence = ""
            stack[-1].body += 1
            continue
        stripped = raw.lstrip()
        if stripped.startswith("<!--"):
            # Comments are not content; plain string search, since this only skips them and sanitizes nothing.
            in_comment = "-->" not in stripped[4:]
            continue
        m = _HEADING.match(raw)
        if m:
            sec = Section(len(m.group(1)), m.group(2), i)
            while stack[-1].level >= sec.level:
                stack.pop()
            stack[-1].children.append(sec)
            stack.append(sec)
            flat.append(sec)
            group, istack = None, []
            continue
        if not raw.strip():
            continue
        m_list = _LIST.match(raw)
        if opening == "none":
            opening = "list" if m_list else "table" if raw.lstrip().startswith("|") else "para"
            opening_line = i
        stack[-1].body += 1
        if m_list:
            item = Item(m_list.group(2).strip(), i, len(m_list.group(1).expandtabs(4)))
            if group is None:
                group, istack = [], []
                stack[-1].lists.append(group)
            while istack and istack[-1].indent > item.indent:
                istack.pop()
            if istack and istack[-1].indent == item.indent:
                istack.pop()
            (istack[-1].children if istack else group).append(item)
            istack.append(item)
        elif not raw[:1].isspace():
            group, istack = None, []  # an unindented paragraph or table ends the list
            m_bold = _BOLD_ONLY.match(raw)
            if m_bold:
                stack[-1].pseudo.append((i, m_bold.group(2).rstrip(":：").strip()))
    return Doc(root, flat, opening, opening_line)


_BOLD_LEAD = re.compile(r"^(\*\*|__)(.+?)\1")
_BOLD_ONLY = re.compile(r"^(\*\*|__)(.+?)\1[:：]?\s*$")


def _lead(text: str) -> str:
    """The part of a list item that would carry its claim: bold lead, text before a colon, or the whole."""
    m = _BOLD_LEAD.match(text)
    if m:
        return m.group(2).rstrip(":：").strip()
    head = re.split(r"[:：]", text, maxsplit=1)[0]
    return head.strip()


def _walk(items: Iterable[Item]) -> Iterable[Item]:
    for it in items:
        yield it
        yield from _walk(it.children)


def _ids(flat: Iterable[Section], prefix: str) -> dict[int, int]:
    pat = re.compile(rf"(?<![A-Za-z0-9]){re.escape(prefix)}(\d+)(?![0-9])")
    found: dict[int, int] = {}
    for s in flat:
        for k in pat.findall(s.title):
            found.setdefault(int(k), s.line)
    return found


def check_md(
    text: str,
    *,
    template: frozenset[str] = frozenset(),
    pairs: Sequence[tuple[str, str]] = (),
    max_group: int = 0,
    offtree: frozenset[str] = frozenset(),
) -> list[Finding]:
    """Surface checks on Markdown headings and lists (rules S1-S8), sorted by line.

    template: fixed genre headings (not labels). offtree: extra non-claim headings.
    """
    doc = parse_md(text)
    flat = doc.sections
    tmpl = {t.strip().casefold() for t in template}
    off = OFFTREE | {t.strip().casefold() for t in offtree}
    out: list[Finding] = []
    prev = 0
    for s in flat:
        loc, name = f"L{s.line}", s.title[:40]
        n = sum(1 for c in s.children if norm(c.title) not in off)
        if prev and s.level > prev + 1:
            out.append(Finding("E", "S1", loc, f"'{name}' skips level h{prev}->h{s.level}"))
        prev = s.level
        if n == 1:
            out.append(Finding("W", "S2", loc, f"'{name}' has 1 claim subsection; merge or add siblings"))
        if s.children and not s.body:
            out.append(Finding("W", "S3", loc, f"'{name}' has no lead text; heading must then state the summary claim"))
        if not s.children and not s.body:
            out.append(Finding("E", "S4", loc, f"'{name}' is empty"))
        key = norm(s.title)
        if key in LABELS and key not in tmpl and key not in off:
            out.append(Finding("W", "S5", loc, f"'{name}' is a topic label; make it a claim or pass --template"))
        if max_group and n > max_group:
            out.append(Finding("W", "S6", loc, f"'{name}' groups {n} items > {max_group}"))
    for a, b in pairs:
        ida, idb = _ids(flat, a), _ids(flat, b)
        for k in sorted(ida.keys() - idb.keys()):
            out.append(Finding("E", "S7", f"L{ida[k]}", f"{a}{k} has no {b}{k}"))
        for k in sorted(idb.keys() - ida.keys()):
            out.append(Finding("E", "S7", f"L{idb[k]}", f"{b}{k} has no {a}{k}"))
    off_levels: list[int] = []  # levels of open off-tree headings; their bodies hold no claims
    for s in [doc.root, *flat]:
        while off_levels and off_levels[-1] >= s.level:
            off_levels.pop()
        if s.level and norm(s.title) in off:
            off_levels.append(s.level)
        if off_levels:
            continue
        for group in s.lists:
            _check_list(group, max_group, off | tmpl, out)
        for line, text in s.pseudo:
            if norm(text) in LABELS and norm(text) not in tmpl:
                out.append(Finding("W", "S5", f"L{line}", f"'{text[:40]}' is a topic label; state the claim instead"))
    if doc.opening in ("list", "table", "code"):
        out.append(
            Finding(
                "W", "S8", f"L{doc.opening_line}", f"opens with a {doc.opening}; state the answer in a sentence first"
            )
        )
    return sorted(out, key=lambda f: int(f.loc[1:]) if f.loc[1:].isdigit() else 0)


def _check_list(group: list[Item], max_group: int, exempt: set[str] | frozenset[str], out: list[Finding]) -> None:
    """List-tree checks; exempt holds template and off-tree labels that may lead an item."""
    if len(group) == 1:
        out.append(Finding("W", "S2", f"L{group[0].line}", "list has 1 item; fold it into the text or add siblings"))
    if max_group and len(group) > max_group:
        out.append(Finding("W", "S6", f"L{group[0].line}", f"list groups {len(group)} items > {max_group}"))
    for it in _walk(group):
        loc, name = f"L{it.line}", it.text[:40]
        if len(it.children) == 1:
            out.append(Finding("W", "S2", loc, f"'{name}' has 1 sub-point; merge or add siblings"))
        if max_group and len(it.children) > max_group:
            out.append(Finding("W", "S6", loc, f"'{name}' groups {len(it.children)} sub-points > {max_group}"))
        key = norm(_lead(it.text))
        if key in LABELS and key not in exempt:
            out.append(Finding("W", "S5", loc, f"'{name}' leads with a topic label; lead with the claim"))


# ---------------------------------------------------------------- propositional logic


class FormulaError(ValueError):
    """Raised for malformed formulas or too many atoms."""


@dataclass(frozen=True)
class Var:
    name: str


@dataclass(frozen=True)
class Not:
    x: Expr


@dataclass(frozen=True)
class Bin:
    op: str  # & | -> <->
    a: Expr
    b: Expr


Expr = Var | Not | Bin

_TOKEN = re.compile(r"\s*(<->|->|[!&|()]|[A-Za-z_][A-Za-z0-9_]*)")
MAX_ATOMS = 12


def _tokenize(src: str) -> list[str]:
    toks: list[str] = []
    pos = 0
    while pos < len(src):
        if src[pos:].strip() == "":
            break
        m = _TOKEN.match(src, pos)
        if not m:
            raise FormulaError(f"bad char at {pos} in '{src}'")
        toks.append(m.group(1))
        pos = m.end()
    return toks


class _Parser:
    """iff := imp ('<->' imp)* ; imp := or ('->' imp)? ; or := and ('|' and)* ;
    and := un ('&' un)* ; un := '!' un | '(' iff ')' | atom"""

    def __init__(self, src: str) -> None:
        self.src = src
        self.toks = _tokenize(src)
        self.i = 0

    def peek(self) -> str | None:
        return self.toks[self.i] if self.i < len(self.toks) else None

    def take(self) -> str:
        tok = self.peek()
        if tok is None:
            raise FormulaError(f"unexpected end in '{self.src}'")
        self.i += 1
        return tok

    def parse(self) -> Expr:
        e = self.iff()
        if self.peek() is not None:
            raise FormulaError(f"unexpected '{self.peek()}' in '{self.src}'")
        return e

    def iff(self) -> Expr:
        e = self.imp()
        while self.peek() == "<->":
            self.take()
            e = Bin("<->", e, self.imp())
        return e

    def imp(self) -> Expr:
        e = self.disj()
        if self.peek() == "->":
            self.take()
            return Bin("->", e, self.imp())
        return e

    def disj(self) -> Expr:
        e = self.conj()
        while self.peek() == "|":
            self.take()
            e = Bin("|", e, self.conj())
        return e

    def conj(self) -> Expr:
        e = self.unary()
        while self.peek() == "&":
            self.take()
            e = Bin("&", e, self.unary())
        return e

    def unary(self) -> Expr:
        tok = self.take()
        if tok == "!":
            return Not(self.unary())
        if tok == "(":
            e = self.iff()
            if self.take() != ")":
                raise FormulaError(f"missing ')' in '{self.src}'")
            return e
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", tok):
            return Var(tok)
        raise FormulaError(f"unexpected '{tok}' in '{self.src}'")


def parse_formula(src: str) -> Expr:
    return _Parser(src).parse()


def _atoms(e: Expr) -> set[str]:
    match e:
        case Var(name):
            return {name}
        case Not(x):
            return _atoms(x)
        case Bin(_, a, b):
            return _atoms(a) | _atoms(b)
    raise AssertionError(e)


def _eval(e: Expr, env: dict[str, bool]) -> bool:
    match e:
        case Var(name):
            return env[name]
        case Not(x):
            return not _eval(x, env)
        case Bin("&", a, b):
            return _eval(a, env) and _eval(b, env)
        case Bin("|", a, b):
            return _eval(a, env) or _eval(b, env)
        case Bin("->", a, b):
            return (not _eval(a, env)) or _eval(b, env)
        case Bin("<->", a, b):
            return _eval(a, env) == _eval(b, env)
    raise AssertionError(e)


def entails(premises: Sequence[str], conclusion: str) -> dict[str, bool] | None:
    """Truth-table entailment. Returns None if valid, else a countermodel."""
    ps = [parse_formula(p) for p in premises]
    c = parse_formula(conclusion)
    names = sorted(set().union(*(_atoms(p) for p in ps), _atoms(c)))
    if len(names) > MAX_ATOMS:
        raise FormulaError(f"{len(names)} atoms > {MAX_ATOMS}")
    for vals in itertools.product((False, True), repeat=len(names)):
        env = dict(zip(names, vals, strict=True))
        if all(_eval(p, env) for p in ps) and not _eval(c, env):
            return env
    return None


# ---------------------------------------------------------------- claim tree

KINDS = frozenset({"claim", "context", "history", "record", "significance"})
ORDERS = frozenset({"deductive", "chronological", "structural", "comparative"})
_KEYS: dict[str, type | tuple[type, ...]] = {
    "id": str,
    "parent": (str, type(None)),
    "kind": str,
    "text": str,
    "order": str,
    "reason": str,
    "therefore": bool,
    "prop": str,
    "universe": list,
    "scope": list,
}
_REQUIRED = ("id", "parent", "kind", "text")
Node = dict[str, object]


def _schema(data: object, out: list[Finding]) -> list[Node]:
    if not isinstance(data, dict) or not isinstance(data.get("nodes"), list):
        out.append(Finding("E", "T1", "-", 'top level must be {"nodes": [...]}'))
        return []
    nodes: list[Node] = []
    seen: set[str] = set()
    for i, n in enumerate(data["nodes"]):
        loc = f"#{i}"
        if not isinstance(n, dict):
            out.append(Finding("E", "T1", loc, "node must be an object"))
            continue
        for k in _REQUIRED:
            if k not in n:
                out.append(Finding("E", "T1", loc, f"missing '{k}'"))
        for k, v in n.items():
            if k not in _KEYS:
                out.append(Finding("E", "T1", loc, f"unknown key '{k}'"))
            elif not isinstance(v, _KEYS[k]):
                out.append(Finding("E", "T1", loc, f"'{k}' has wrong type"))
        if n.get("kind") not in KINDS:
            out.append(Finding("E", "T1", loc, f"kind must be one of {sorted(KINDS)}"))
        if "order" in n and n["order"] not in ORDERS:
            out.append(Finding("E", "T1", loc, f"order must be one of {sorted(ORDERS)}"))
        for k in ("universe", "scope"):
            v = n.get(k)
            if isinstance(v, list) and not all(isinstance(x, str) for x in v):
                out.append(Finding("E", "T1", loc, f"'{k}' must be a list of strings"))
        nid = n.get("id")
        if isinstance(nid, str):
            if nid in seen:
                out.append(Finding("E", "T1", loc, f"duplicate id '{nid}'"))
            seen.add(nid)
        nodes.append(n)
    return nodes


def _sentences(text: str) -> int:
    return len([s for s in re.split(r"[。．！？!?]+|\.(?:\s|$)", text) if s.strip()])


def _strs(v: object) -> list[str]:
    return [x for x in v if isinstance(x, str)] if isinstance(v, list) else []


def check_tree(data: object) -> list[Finding]:
    """Logic checks on a claim-tree JSON (rules T1-T12)."""
    out: list[Finding] = []
    nodes = _schema(data, out)
    if out:
        return out
    by_id = {str(n["id"]): n for n in nodes}
    kids: dict[str, list[Node]] = {i: [] for i in by_id}
    roots = [n for n in nodes if n["parent"] is None]
    for n in nodes:
        p = n["parent"]
        if isinstance(p, str):
            if p in by_id:
                kids[p].append(n)
            else:
                out.append(Finding("E", "T2", str(n["id"]), f"parent '{p}' not found"))
    if len(roots) != 1:
        out.append(Finding("E", "T2", "-", f"{len(roots)} roots; need exactly 1"))
    elif roots[0]["kind"] != "claim":
        out.append(Finding("E", "T2", str(roots[0]["id"]), "root must be a claim"))
    cycles: set[frozenset[str]] = set()
    for n in nodes:
        path: list[str] = []
        cur: Node | None = n
        while cur is not None and isinstance(cur["parent"], str):
            cid = str(cur["id"])
            if cid in path:
                cycles.add(frozenset(path[path.index(cid) :]))
                break
            path.append(cid)
            cur = by_id.get(cur["parent"])
    for cyc in sorted(cycles, key=sorted):
        out.append(Finding("E", "T2", ",".join(sorted(cyc)), "cycle"))
    if out:
        return out

    root_id = str(roots[0]["id"])
    for n in nodes:
        nid, kind = str(n["id"]), n["kind"]
        if kind != "claim":
            if kids[nid]:
                out.append(Finding("E", "T10", nid, f"{kind} must be a leaf"))
            if kind in ("significance", "history") and n["parent"] != root_id:
                where = "apex" if kind == "significance" else "intro/appendix"
                out.append(Finding("W", "T10", nid, f"{kind} belongs at {where}, not under '{n['parent']}'"))
            if kind == "context" and _sentences(str(n["text"])) > 2:
                out.append(Finding("W", "T9", nid, "context > 2 sentences"))
            continue

        if norm(str(n["text"])) in LABELS:
            out.append(Finding("E", "T12", nid, f"'{n['text']}' is a topic label, not a claim"))
        claims = [c for c in kids[nid] if c["kind"] == "claim"]
        order = n.get("order")
        if len(claims) == 1:
            out.append(Finding("W", "T3", nid, "1 child claim; merge or add siblings"))
        if len(claims) >= 2 and order is None:
            out.append(Finding("E", "T4", nid, f"group of {len(claims)} lacks 'order'"))
        if order == "deductive":
            if len(claims) > 4:
                out.append(Finding("E", "T5", nid, f"deductive group has {len(claims)} points > 4"))
            tf = sum(1 for c in claims if c.get("therefore") is True)
            if tf > 2:
                out.append(Finding("E", "T6", nid, f"{tf} 'therefore' points > 2"))
            if nid == root_id and not n.get("reason"):
                out.append(
                    Finding("W", "T7", nid, "deductive key line; add 'reason' (reader would reject / cannot follow)")
                )
            _validity(nid, claims, out)
        universe = _strs(n.get("universe"))
        if universe:
            _mece(nid, universe, claims, out)
    return out


def _validity(nid: str, claims: list[Node], out: list[Finding]) -> None:
    if len(claims) < 2:
        return
    props = [c.get("prop") for c in claims]
    missing = [str(c["id"]) for c, p in zip(claims, props, strict=True) if not p]
    if missing:
        out.append(Finding("I", "T8", nid, f"validity unchecked; no 'prop' on {','.join(missing)}"))
        return
    try:
        cm = entails([str(p) for p in props[:-1]], str(props[-1]))
    except FormulaError as e:
        out.append(Finding("E", "T8", nid, f"bad formula: {e}"))
        return
    if cm is not None:
        model = ",".join(f"{k}={int(v)}" for k, v in cm.items())
        out.append(
            Finding("E", "T8", nid, f"'{claims[-1]['id']}' not entailed by preceding points; countermodel {model}")
        )


def _mece(nid: str, universe: list[str], claims: list[Node], out: list[Finding]) -> None:
    scopes = {str(c["id"]): set(_strs(c.get("scope"))) for c in claims}
    if not all(scopes.values()):
        out.append(Finding("I", "T11", nid, "MECE unchecked; 'scope' missing on some children"))
        return
    uni = set(universe)
    unknown = set().union(*scopes.values()) - uni
    if unknown:
        out.append(Finding("E", "T11", nid, f"scope outside universe: {sorted(unknown)}"))
    for (a, sa), (b, sb) in itertools.combinations(scopes.items(), 2):
        if sa & sb:
            out.append(Finding("E", "T11", nid, f"overlap {a}/{b}: {sorted(sa & sb)}"))
    uncovered = uni - set().union(*scopes.values())
    if uncovered:
        out.append(Finding("E", "T11", nid, f"uncovered: {sorted(uncovered)}"))


# ---------------------------------------------------------------- cli


def _pair(s: str) -> tuple[str, str]:
    m = re.fullmatch(r"([A-Za-z]+):([A-Za-z]+)", s)
    if not m:
        raise argparse.ArgumentTypeError("use PREFIX:PREFIX, e.g. M:R")
    return m.group(1), m.group(2)


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="mode", required=True)
    md = sub.add_parser("md", help="surface checks on Markdown headings and lists")
    md.add_argument("file", help="Markdown file, or - for stdin")
    md.add_argument("--template", default="", help="comma list of fixed genre headings, e.g. Methods,Results")
    md.add_argument(
        "--pair", type=_pair, action="append", default=[], help="numbered sections that must correspond, e.g. M:R"
    )
    md.add_argument("--max-group", type=int, default=0, help="warn when a section has more subsections (0=off)")
    md.add_argument("--offtree", default="", help="comma list of extra non-claim headings, e.g. Checklist")
    tr = sub.add_parser("tree", help="logic checks on claim-tree JSON")
    tr.add_argument("file", help="claim-tree JSON file, or - for stdin")
    args = ap.parse_args(argv)

    try:
        text = sys.stdin.read() if args.file == "-" else Path(args.file).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        print(f"cannot read {args.file}: {e.__class__.__name__}", file=sys.stderr)
        return 2
    if args.mode == "md":

        def csv(s: str) -> frozenset[str]:
            return frozenset(t for t in s.split(",") if t.strip())

        found = check_md(
            text,
            template=csv(args.template),
            pairs=args.pair,
            max_group=args.max_group,
            offtree=csv(args.offtree),
        )
    else:
        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            found = [Finding("E", "T1", f"L{e.lineno}", "invalid JSON")]
        else:
            found = check_tree(data)
    for f in found:
        print(f)
    counts = {s: sum(1 for f in found if f.sev == s) for s in "EWI"}
    print("ok" if not found else " ".join(f"{s}={n}" for s, n in counts.items()))
    return 1 if counts["E"] else 0


if __name__ == "__main__":
    sys.exit(main())
