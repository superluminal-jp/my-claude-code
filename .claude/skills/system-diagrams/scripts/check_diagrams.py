#!/usr/bin/env python3
"""Check system-architecture diagrams for the notation a first-time reader needs.

Reads, and never writes:
  - Markdown view pages: Mermaid blocks (flowchart, C4*, sequenceDiagram) and
    diagram images, plus the page around them (title, lead text, legend);
  - draw.io files: .drawio, .drawio.xml, and .drawio.svg (diagram data
    embedded in the SVG), compressed or not;
  - Structurizr DSL workspaces: .dsl;
  - a directory: every such file below it, plus the index page (README.md or
    index.md at its top) that must link every view page.

Usage:  python3 check_diagrams.py PATH... [--max-elements N]
Exit:   0 no errors (warnings may be printed), 1 at least one error,
        2 a path that does not exist, cannot be read, or has an unknown type.
Standard library only.
"""

from __future__ import annotations

import argparse
import base64
import binascii
import html
import os
import re
import sys
import urllib.parse
import xml.etree.ElementTree as ET
import zlib
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

# Not from any standard: the C4 model sets no element limit. A starting point
# for splitting a view; pass --max-elements to change it.
DEFAULT_MAX_ELEMENTS = 20


@dataclass(frozen=True)
class Finding:
    severity: str  # "E" error, "W" warning
    code: str
    path: str
    line: int  # 0 when the finding is about a whole directory or file
    message: str

    def render(self) -> str:
        where = f"{self.path}:{self.line}" if self.line else self.path
        return f"{self.severity} {self.code} {where} {self.message}"


class Report:
    def __init__(self, max_elements: int):
        self.max_elements = max_elements
        self.findings: list[Finding] = []
        # element id -> name -> first (path, line) where that name was used
        self.names: dict[str, dict[str, tuple[str, int]]] = {}

    def error(self, code, path, line, message):
        self.findings.append(Finding("E", code, str(path), line, message))

    def warn(self, code, path, line, message):
        self.findings.append(Finding("W", code, str(path), line, message))

    def name(self, ident, name, path, line):
        if ident and name:
            self.names.setdefault(ident, {}).setdefault(name, (str(path), line))

    def finish(self):
        for ident, names in sorted(self.names.items()):
            if len(names) > 1:
                path, line = min(names.values())
                listed = " / ".join(sorted(names))
                self.warn("X1", path, line,
                          f'"{ident}" has different names across views ({listed}); give one element one name')


# --------------------------------------------------------------------------- text helpers

# Only the HTML tags labels use, so that text such as "<scope>" stays text.
TAG_RE = re.compile(r"</?(?:a|b|br|div|em|font|hr|i|p|small|span|strong|sub|sup|u)\b[^<>]*>", re.IGNORECASE)
TYPE_RE = re.compile(r"\[[^\[\]]*\S[^\[\]]*\]")


def plain(text: str | None) -> str:
    """Visible text: entities decoded, HTML tags and surrounding quotes removed."""
    text = html.unescape(text or "")
    text = TAG_RE.sub(" ", text).replace("\xa0", " ").strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in "\"`":
        text = text[1:-1].strip()
    return text


# Words that name how something travels, not what or why. A label made only
# of these (and port numbers) tells a newcomer nothing about the relationship.
PROTOCOL_WORDS = {
    "amqp", "csv", "dns", "ftp", "graphql", "grpc", "http", "https", "imap", "jdbc", "json", "kafka",
    "ldap", "ldaps", "mqtt", "nfs", "oauth", "oauth2", "odbc", "oidc", "over", "port", "redis", "rest",
    "s3", "saml", "sftp", "smb", "smtp", "soap", "sql", "ssh", "tcp", "tls", "udp", "via", "websocket",
    "websockets", "ws", "wss", "xml", "ポート", "経由",
}


def protocol_only(label: str) -> bool:
    """True when a non-empty label names only a protocol, format, or port."""
    text = plain(label)
    if not text:
        return False
    rest = re.sub(r"\[[^\[\]]*\]", " ", text)
    words = [w for w in re.split(r"[\s/,+:;、・()（）-]+", rest) if w]
    return all(w.lower() in PROTOCOL_WORDS or w.isdigit() for w in words)


def first_line(label: str) -> str:
    """The element's name: the label up to its first line break."""
    label = html.unescape(label).strip().strip('"').strip()
    label = re.split(r"<br\s*/?>|\\n|\n", label, maxsplit=1)[0]
    return plain(label)


# --------------------------------------------------------------------------- Markdown

FENCE_RE = re.compile(r"^( {0,3})(`{3,}|~{3,})(.*)$")
H1_RE = re.compile(r"^#\s+\S")
HEADING_RE = re.compile(r"^#{1,6}\s+(.*?)\s*#*\s*$")
IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
LINK_MD_RE = re.compile(r"(?<!!)\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
LEGEND_RE = re.compile(r"(凡例|legend|\bkey\b)", re.IGNORECASE)


def parse_markdown(text: str):
    """Return (code blocks, lines outside code blocks).

    A block is (first content line number, info word, list of lines)."""
    blocks, outside = [], []
    fence, current = None, None
    for no, line in enumerate(text.splitlines(), 1):
        m = FENCE_RE.match(line)
        if fence:
            if m and m.group(2)[0] == fence[0] and len(m.group(2)) >= len(fence) and not m.group(3).strip():
                fence = None
            else:
                current.append(line)
            continue
        if m and not (m.group(2)[0] == "`" and "`" in m.group(3)):
            fence = m.group(2)
            info = m.group(3).strip().split()
            current = []
            blocks.append((no + 1, info[0].lower() if info else "", current))
            continue
        outside.append((no, line))
    return blocks, outside


def check_markdown(path: Path, text: str, report: Report) -> bool:
    """Check one page; return True when it holds a diagram (it is a view page)."""
    blocks, outside = parse_markdown(text)
    mermaid = [(start, body) for start, info, body in blocks if info == "mermaid"]
    images = [(no, m.group(1), m.group(2)) for no, line in outside for m in IMAGE_RE.finditer(line)]
    for no, alt, target in images:
        if not alt.strip():
            report.error("P4", path, no, f"image {target} has no alt text; say in it what the diagram shows")
    diagram_lines = sorted([start - 1 for start, _ in mermaid] + [no for no, _, _ in images])
    if not diagram_lines:
        return False
    first = diagram_lines[0]

    h1 = next((no for no, line in outside if H1_RE.match(line)), None)
    if h1 is None or h1 > first:
        report.error("P1", path, first, "no H1 title before the diagram; name the view type and its scope")
    start = h1 if h1 is not None and h1 < first else 0
    has_lead = any(
        start < no < first and line.strip() and not HEADING_RE.match(line) and not line.strip().startswith("<!--")
        for no, line in outside
    )
    if not has_lead:
        report.error("P2", path, first,
                     "no lead text between the title and the diagram; say in 1-3 sentences what the reader learns")
    headings = [m.group(1) for _, line in outside for m in [HEADING_RE.match(line)] if m]
    if not any(LEGEND_RE.search(h) for h in headings):
        report.error("P3", path, first, "no legend section (a heading with 凡例, Legend, or Key) explaining shapes, colours, and lines")
    if len(diagram_lines) > 1:
        report.warn("P5", path, diagram_lines[1], "more than one diagram on this page; give each view its own page")

    for start_line, body in mermaid:
        check_mermaid(path, start_line, body, report)
    return True


# --------------------------------------------------------------------------- Mermaid

C4_KINDS = {"C4Context", "C4Container", "C4Component", "C4Dynamic", "C4Deployment"}


def check_mermaid(path: Path, start: int, body: list[str], report: Report):
    lines = list(enumerate(body, start))
    i = 0
    while i < len(lines) and not lines[i][1].strip():
        i += 1
    if i < len(lines) and lines[i][1].strip() == "---":  # YAML front matter
        i += 1
        while i < len(lines) and lines[i][1].strip() != "---":
            i += 1
        i += 1
    content = [(no, t) for no, t in lines[i:] if t.strip() and not t.strip().startswith("%%")]
    if not content:
        report.warn("M9", path, start, "empty Mermaid block")
        return
    header_no, header = content[0]
    kind = header.split()[0]

    statements, has_title, has_descr, in_descr = [], False, False, False
    for no, t in content[1:]:
        s = t.strip()
        if in_descr:
            if s.endswith("}"):
                in_descr = False
            continue
        if re.match(r"accTitle\s*:\s*\S", s):
            has_title = True
            continue
        if re.match(r"accDescr\s*:\s*\S", s):
            has_descr = True
            continue
        if re.match(r"accDescr\s*\{", s):
            has_descr = True
            in_descr = not s.endswith("}")
            continue
        statements.append((no, s))
    if not has_title:
        report.error("M1", path, header_no, "no accTitle: give screen-reader users the diagram's title")
    if not has_descr:
        report.error("M2", path, header_no, "no accDescr: describe in words what the diagram shows")

    if kind in ("flowchart", "graph"):
        check_flowchart(path, statements, report)
    elif kind in C4_KINDS:
        check_c4(path, statements, report)
    elif kind == "sequenceDiagram":
        check_sequence(path, statements, report)
    elif kind.startswith("architecture"):
        report.error("M8", path, header_no,
                     "architecture diagrams cannot label their lines; draw the view as a flowchart instead")
    else:
        report.warn("M9", path, header_no, f"'{kind}' diagrams are checked only for accTitle and accDescr")


# Flowchart -------------------------------------------------------------------

Q, L = "\x00", "\x01"  # placeholders for quoted strings and |edge labels|
PLACEHOLDER_RE = re.compile(r"[\x00\x01](\d+)[\x00\x01]")
NODE_DEF_RE = re.compile(r"([A-Za-z_]\w*)[ \t]*(@\{|\(\(\(|\(\(|\(\[|\[\(|\[\[|\[/|\[\\|\{\{|\[|\(|\{|>)")
LINK_RE = re.compile(
    r"(?:<|(?<!\w)[xo])?(?:-{2,}|={2,}|-\.+-|~{3,})(?:>|[xo](?!\w))?"
    r"|-\.(?=\s)"  # opener of the dotted text form: A -. label .-> B
    r"|\.-+(?:>|[xo](?!\w))?"  # its closer
)
SKIP_KEYWORDS = {"classDef", "class", "style", "linkStyle", "click", "direction", "title", "end", "accTitle", "accDescr"}
TEXT_OPENERS = {"--", "==", "-."}


def check_flowchart(path, statements, report):
    defined: dict[str, tuple[str, int]] = {}
    used: dict[str, int] = {}
    boundaries: set[str] = set()

    for no, line in statements:
        quotes: list[str] = []
        masked = re.sub(r'"[^"]*"', lambda m: (quotes.append(m.group(0)), f"{Q}{len(quotes) - 1}{Q}")[1], line)

        def unmask(s, _quotes=quotes):
            return PLACEHOLDER_RE.sub(lambda m: _quotes[int(m.group(1))] if m.group(0)[0] == Q else "", s)

        for stmt in masked.split(";"):
            stmt = stmt.strip()
            if not stmt:
                continue
            word = stmt.split()[0]
            if word == "subgraph":
                m = re.match(r"subgraph\s+([A-Za-z_]\w*)", stmt)
                if m:
                    boundaries.add(m.group(1))
                continue
            if word in SKIP_KEYWORDS or word.split(":")[0] in SKIP_KEYWORDS:
                continue

            labels: list[str] = []
            stmt = re.sub(r"\|[^|]*\|", lambda m: (labels.append(unmask(m.group(0)[1:-1])), f" {L}{len(labels) - 1}{L} ")[1], stmt)
            defs, reduced = scan_node_defs(stmt)
            for ident, label in defs:
                label = unmask(label)
                if ident not in defined or TYPE_RE.search(defined[ident][0]) is None:
                    defined[ident] = (label, no)
                report.name(ident, first_line(label), path, no)
            reduced = re.sub(r":::\w+", " ", reduced)
            for ident in flowchart_edges(path, no, reduced, labels, report):
                used.setdefault(ident, no)

    for ident, (label, no) in defined.items():
        if not TYPE_RE.search(label):
            report.error("M4", path, no, f'"{first_line(label) or ident}" has no [Type] in its label, e.g. [Container: Python]')
    for ident, no in used.items():
        if ident not in defined and ident not in boundaries:
            report.error("M5", path, no, f'"{ident}" is drawn without a label giving its name and [Type]')
    elements = (set(defined) | set(used)) - boundaries
    if len(elements) > report.max_elements:
        report.warn("M6", path, statements[0][0] if statements else 0,
                    f"{len(elements)} elements (limit {report.max_elements}); split the view by boundary or by flow")


def scan_node_defs(s: str):
    """Find node definitions (id + shape + label); return them and the statement
    with each definition replaced by its bare id."""
    defs, out, i = [], [], 0
    while i < len(s):
        m = NODE_DEF_RE.match(s, i)
        if m and (i == 0 or not (s[i - 1].isalnum() or s[i - 1] in "_\x00\x01")):
            ident, opener = m.group(1), m.group(2)
            if opener == "@{":
                end = s.find("}", m.end())
                end = len(s) - 1 if end < 0 else end
                lm = re.search(r"label\s*:\s*(.+?)\s*(?:,|$)", s[m.end():end])
                label = lm.group(1) if lm else ""
            elif opener == ">":
                end = s.find("]", m.end())
                end = len(s) - 1 if end < 0 else end
                label = s[m.end():end]
            else:
                depth, k, end = 0, m.start(2), len(s) - 1
                while k < len(s):
                    if s[k] in "([{":
                        depth += 1
                    elif s[k] in ")]}":
                        depth -= 1
                        if depth == 0:
                            end = k
                            break
                    k += 1
                label = s[m.end(2):end].strip("()[]{}/\\ ")
            defs.append((ident, label))
            out.append(f" {ident} ")
            i = end + 1
            continue
        out.append(s[i])
        i += 1
    return defs, "".join(out)


def is_directed(token: str) -> bool:
    return token.startswith("<") or token.endswith(">") or bool(re.search(r"(^[xo][-=.])|([-=.][xo]$)", token))


def flowchart_edges(path, no, reduced, labels, report):
    """Report unlabelled or undirected links in one statement; return the ids it uses."""
    tokens = list(LINK_RE.finditer(reduced))
    if not tokens:
        return ids_in(reduced)
    pieces = [reduced[: tokens[0].start()]]
    for a, b in zip(tokens, tokens[1:]):
        pieces.append(reduced[a.end(): b.start()])
    pieces.append(reduced[tokens[-1].end():])
    label_pieces: set[int] = set()

    k = 0
    while k < len(tokens):
        tok = tokens[k].group(0)
        if tok.startswith("~"):  # invisible link: layout only
            k += 1
            continue
        # "--" and "==" are not links on their own, so text after them up to the
        # next link is that link's label: A -- label --> B
        if tok in TEXT_OPENERS and k + 1 < len(tokens) and pieces[k + 1].strip():
            label_pieces.add(k + 1)
            closer, labelled = tokens[k + 1].group(0), True
            k += 2
        else:
            closer = tok
            lm = re.match(r"\s*\x01(\d+)\x01", reduced[tokens[k].end():])
            labelled = bool(lm and plain(labels[int(lm.group(1))]))
            if labelled and protocol_only(labels[int(lm.group(1))]):
                report.warn("M10", path, no, "a line names only its protocol; say what flows and why, then [protocol]")
            k += 1
        if not labelled:
            report.error("M3", path, no, "a line has no label; write A -->|what flows and why [protocol]| B")
        if not is_directed(closer):
            report.warn("M7", path, no, "a line has no arrowhead; show which way the request or data goes")

    used = []
    for idx, piece in enumerate(pieces):
        if idx not in label_pieces:
            used.extend(ids_in(piece))
    return used


def ids_in(text: str) -> list[str]:
    text = PLACEHOLDER_RE.sub(" ", text).replace("&", " ")
    return re.findall(r"(?<![\w])[A-Za-z_]\w*", text)


# C4 -------------------------------------------------------------------------

C4_ELEMENT_RE = re.compile(
    r"^(Person|System|SystemDb|SystemQueue|Container|ContainerDb|ContainerQueue|Component|ComponentDb|ComponentQueue)(_Ext)?\s*\((.*)\)\s*$")
C4_REL_RE = re.compile(r"^(Rel|BiRel|Rel_[UDLR]|Rel_(?:Up|Down|Left|Right|Back|Neighbor))\s*\((.*)\)\s*$")


def split_args(s: str) -> list[str]:
    return [a.strip() for a in re.findall(r'(?:"[^"]*"|[^,])+', s)]


def check_c4(path, statements, report):
    count, first = 0, statements[0][0] if statements else 0
    for no, s in statements:
        m = C4_ELEMENT_RE.match(s)
        if m:
            count += 1
            args = split_args(m.group(3))
            if len(args) >= 2:
                report.name(args[0], plain(args[1]), path, no)
            continue
        m = C4_REL_RE.match(s)
        if m:
            args = split_args(m.group(2))
            if len(args) < 3 or not plain(args[2]):
                report.error("M3", path, no, "a relationship has no label; Rel(from, to, \"what and why\", \"protocol\")")
            elif protocol_only(args[2]):
                report.warn("M10", path, no, "a relationship names only its protocol; put the protocol in the fourth argument")
    if count > report.max_elements:
        report.warn("M6", path, first, f"{count} elements (limit {report.max_elements}); split the view by boundary or by flow")


# Sequence -------------------------------------------------------------------

PARTICIPANT_RE = re.compile(r"^(?:create\s+)?(participant|actor)\s+(\S+?)(?:\s+as\s+(.+))?$")
MESSAGE_RE = re.compile(r"^(\w+)\s*(<<-->>|<<->>|-->>|->>|--x|-x|--\)|-\)|-->|->)\s*[+-]?\s*(\w+)\s*(?::(.*))?$")


def check_sequence(path, statements, report):
    declared: dict[str, tuple[str, int]] = {}
    endpoints: dict[str, int] = {}
    for no, s in statements:
        m = PARTICIPANT_RE.match(s)
        if m:
            declared[m.group(2)] = (m.group(3) or m.group(2), no)
            continue
        m = MESSAGE_RE.match(s)
        if m:
            endpoints.setdefault(m.group(1), no)
            endpoints.setdefault(m.group(3), no)
            if not plain(m.group(4)):
                report.error("M3", path, no, "a message has no text; write A->>B: what is asked [protocol]")
            elif protocol_only(m.group(4)):
                report.warn("M10", path, no, "a message names only its protocol; say what is asked, then [protocol]")
    for ident, (label, no) in declared.items():
        report.name(ident, plain(TYPE_RE.sub(" ", label)), path, no)  # the name without its [Type]
        if not TYPE_RE.search(label):
            report.error("M4", path, no, f'participant "{label}" has no [Type], e.g. participant api as API [Container: Python]')
    for ident, no in endpoints.items():
        if ident not in declared:
            report.error("M4", path, no, f'"{ident}" is not declared; declare it with participant {ident} as Name [Type]')
    count = len(set(declared) | set(endpoints))
    if count > report.max_elements:
        report.warn("M6", path, statements[0][0], f"{count} participants (limit {report.max_elements}); split the flow")


# --------------------------------------------------------------------------- draw.io

def load_drawio_pages(path: Path, text: str):
    if path.name.lower().endswith(".svg"):
        content = ET.fromstring(text).get("content")
        if not content:
            raise ValueError("this SVG carries no draw.io diagram data (no content attribute)")
        text = content
    root = ET.fromstring(text)
    if root.tag == "mxGraphModel":
        return [("page 1", root)]
    if root.tag != "mxfile":
        raise ValueError(f"root element is <{root.tag}>, not <mxfile>")
    pages = []
    for n, diagram in enumerate(root.findall("diagram"), 1):
        name = diagram.get("name") or f"page {n}"
        model = diagram.find("mxGraphModel")
        if model is None:
            data = (diagram.text or "").strip()
            if not data:
                raise ValueError(f"page '{name}' is empty")
            raw = zlib.decompress(base64.b64decode(data), -15).decode("utf-8")
            model = ET.fromstring(urllib.parse.unquote(raw))
        pages.append((name, model))
    if not pages:
        raise ValueError("no <diagram> pages")
    return pages


def drawio_cells(model) -> list[dict]:
    root = model.find("root")
    cells = []
    for el in (root if root is not None else []):
        if el.tag == "mxCell":
            cells.append(dict(el.attrib))
        elif el.tag in ("object", "UserObject"):
            inner = el.find("mxCell")
            attrs = dict(inner.attrib) if inner is not None else {}
            attrs["id"] = el.get("id", "")
            attrs["value"] = el.get("label", "")
            cells.append(attrs)
    return cells


def check_drawio(path: Path, text: str, report: Report):
    try:
        pages = load_drawio_pages(path, text)
    except (ET.ParseError, ValueError, binascii.Error, zlib.error, UnicodeDecodeError) as exc:
        report.error("D1", path, 0, f"cannot read the draw.io diagram: {exc}")
        return
    for name, model in pages:
        cells = drawio_cells(model)
        by_id = {c.get("id"): c for c in cells}
        for ident, n in Counter(c.get("id") for c in cells).items():
            if n > 1:
                report.error("D2", path, 0, f"page '{name}': id '{ident}' is used {n} times")
        edges = {c.get("id") for c in cells if c.get("edge") == "1"}

        def under(cell, ancestor):
            seen = set()
            while cell is not None and cell.get("id") not in seen:
                seen.add(cell.get("id"))
                if cell.get("id") == ancestor:
                    return True
                cell = by_id.get(cell.get("parent"))
            return False

        for c in cells:
            if c.get("edge") != "1":
                continue
            for end in ("source", "target"):
                if c.get(end) not in by_id:
                    report.error("D3", path, 0, f"page '{name}': line '{c.get('id')}' has no {end} element; connect both ends")
            texts = [c.get("value")] + [x.get("value") for x in cells if x.get("parent") == c.get("id")]
            texts = [t for t in texts if plain(t)]
            if not texts:
                report.error("D4", path, 0, f"page '{name}': line '{c.get('id')}' has no label; say what flows and why")
            elif all(protocol_only(t) for t in texts):
                report.warn("D9", path, 0, f"page '{name}': line '{c.get('id')}' names only its protocol; say what flows and why")
        title = by_id.get("title")
        if title is None or not plain(title.get("value")):
            report.error("D5", path, 0, f"page '{name}': no cell with id 'title' naming the view type and scope")
        if "legend" not in by_id:
            report.error("D6", path, 0, f"page '{name}': no legend (a cell with id 'legend' holding the key)")

        count = 0
        for c in cells:
            if c.get("vertex") != "1" or c.get("id") in ("title",) or under(c, "legend") or c.get("parent") in edges:
                continue
            style = c.get("style") or ""
            container = style.startswith("group") or "swimlane" in style or "container=1" in style
            if not plain(c.get("value")):
                if not style.startswith("group"):
                    report.error("D7", path, 0, f"page '{name}': element '{c.get('id')}' has no text; give it a name and [Type]")
                continue
            if not container:
                count += 1
        if count > report.max_elements:
            report.warn("D8", path, 0, f"page '{name}': {count} elements (limit {report.max_elements}); split the view")


# --------------------------------------------------------------------------- Structurizr DSL

DSL_TOKEN_RE = re.compile(r'"(?:[^"\\]|\\.)*"|\{|\}|[^\s{}"]+')
ELEMENT_KINDS = {"person", "softwareSystem", "container", "component"}
# positional arguments a view header needs before it carries a description
VIEW_ARGS = {"systemLandscape": 2, "systemContext": 3, "container": 3, "component": 3, "dynamic": 3, "deployment": 4}


def unquote(token: str) -> str:
    return token[1:-1].strip() if len(token) >= 2 and token[0] == token[-1] == '"' else token.strip()


def check_dsl(path: Path, text: str, report: Report):
    text = re.sub(r"/\*.*?\*/", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S)
    seen: set[str] = set()
    stack: list[dict] = []
    for no, raw in enumerate(text.splitlines(), 1):
        s = raw.strip()
        if not s or s.startswith(("#", "//", "!")):
            continue
        tokens = DSL_TOKEN_RE.findall(s)
        stmt = []
        for t in tokens:
            if t in "{}":
                break
            stmt.append(t)
        kw_index = 2 if len(stmt) > 2 and stmt[1] == "=" else 0
        keyword = stmt[kw_index] if len(stmt) > kw_index else ""
        args = stmt[kw_index + 1:]
        context = [frame["keyword"] for frame in stack]
        if keyword in ("workspace", "model", "views"):
            seen.add(keyword)

        view = None
        if "views" in context and keyword in VIEW_ARGS and not any(f.get("view") for f in stack):
            view = {"line": no, "described": len(args) >= VIEW_ARGS[keyword]}
        elif "model" in context and keyword in ELEMENT_KINDS:
            if len(args) < 2 or not unquote(args[1]):
                report.warn("S3", path, no, f"{keyword} {args[0] if args else ''} has no description")
            if keyword in ("container", "component") and (len(args) < 3 or not unquote(args[2])):
                report.warn("S4", path, no, f"{keyword} {args[0] if args else ''} has no technology")
        if "->" in stmt:
            after = stmt[stmt.index("->") + 1:]
            if len(after) < 2 or not unquote(after[1]):
                report.error("S2", path, no, "relationship has no description; a -> b \"what and why\" \"protocol\"")
            elif protocol_only(unquote(after[1])):
                report.warn("S6", path, no, "relationship description names only a protocol; put it in the technology slot")
        if keyword in ("title", "description") and args and unquote(args[0]):
            for frame in reversed(stack):
                if frame.get("view"):
                    frame["view"]["described"] = True
                    break

        for t in tokens:
            if t == "{":
                stack.append({"keyword": keyword, "view": view})
                keyword, view = "", None
            elif t == "}":
                if stack:
                    finish_view(path, stack.pop().get("view"), report)
        if view is not None:  # header without a block
            finish_view(path, view, report)
    missing = [k for k in ("workspace", "model", "views") if k not in seen]
    if missing:
        report.error("S1", path, 0, f"no {', '.join(missing)} block; a workspace defines a model and the views drawn from it")


def finish_view(path, view, report):
    if view and not view["described"]:
        report.warn("S5", path, view["line"], "view has no description or title naming what it shows")


# --------------------------------------------------------------------------- files and directories

def file_kind(name: str):
    n = name.lower()
    if n.endswith(".md"):
        return "md"
    if n.endswith((".drawio", ".drawio.xml", ".drawio.svg")):
        return "drawio"
    if n.endswith(".dsl"):
        return "dsl"
    return None


def check_file(path: Path, report: Report) -> bool:
    kind = file_kind(path.name)
    if kind is None:
        raise ValueError(f"{path}: not a Markdown, draw.io, or Structurizr DSL file")
    text = path.read_text(encoding="utf-8")
    if kind == "md":
        return check_markdown(path, text, report)
    if kind == "drawio":
        check_drawio(path, text, report)
    else:
        check_dsl(path, text, report)
    return False


BACKUP_RE = re.compile(r"\.(original|orig)\.md$", re.IGNORECASE)


def local_links(page: Path) -> set[Path]:
    linked = set()
    for m in LINK_MD_RE.finditer(page.read_text(encoding="utf-8")):
        target = m.group(1)
        if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I) or target.startswith("#"):
            continue
        target = urllib.parse.unquote(target.split("#")[0].split("?")[0])
        linked.add((page.parent / target).resolve())
    return linked


def check_directory(root: Path, report: Report, index_name: str | None = None):
    """Check every file below root, then the index: --index if given, else
    README.md or index.md, else the one top-level page without a diagram that
    links to a view (for example the file the user asked to rework). Backups
    named *.original.md or *.orig.md are skipped."""
    pages, plain_pages = [], []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if not d.startswith(".") and d != "node_modules")
        for filename in sorted(filenames):
            if file_kind(filename) is None or BACKUP_RE.search(filename):
                continue
            path = Path(dirpath) / filename
            is_view = check_file(path, report)
            if is_view:
                pages.append(path)
            elif Path(dirpath) == root and file_kind(filename) == "md":
                plain_pages.append(path)
    if not pages:
        return
    if index_name:
        index = root / index_name
        if not index.is_file():
            report.error("I1", root, 0, f"the index {index_name} given with --index does not exist")
            return
    else:
        named = [p for p in plain_pages if p.name.lower() in ("readme.md", "index.md")]
        views = {p.resolve() for p in pages}
        linking = [p for p in plain_pages if local_links(p) & views]
        candidates = named or linking
        if len(candidates) != 1:
            found = ", ".join(p.name for p in candidates) or "none"
            report.error("I1", root, 0, "no single index page listing the views in reading order "
                         f"(README.md, index.md, or one page linking to the views; found: {found}); "
                         "name it with --index")
            return
        index = candidates[0]
    linked = local_links(index)
    for page in pages:
        if page.resolve() != index.resolve() and page.resolve() not in linked:
            report.error("I2", page, 0, f"not linked from {index.name}; list every view there")


def check_paths(paths, max_elements: int = DEFAULT_MAX_ELEMENTS, index: str | None = None) -> list[Finding]:
    report = Report(max_elements)
    for p in paths:
        path = Path(p)
        if path.is_dir():
            check_directory(path, report, index)
        elif path.is_file():
            check_file(path, report)
        else:
            raise FileNotFoundError(f"{p}: no such file or directory")
    report.finish()
    return sorted(report.findings, key=lambda f: (f.path, f.line, f.code))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Check system-architecture diagrams for title, legend, types, labels, and accessible text.")
    parser.add_argument("paths", nargs="+", help="view pages, draw.io files, .dsl workspaces, or directories")
    parser.add_argument("--max-elements", type=int, default=DEFAULT_MAX_ELEMENTS,
                        help=f"warn when one view has more elements than this (default {DEFAULT_MAX_ELEMENTS})")
    parser.add_argument("--index", default=None,
                        help="file name of the index page inside each directory given (default: README.md, "
                             "index.md, or the one top-level page without a diagram that links to the views)")
    args = parser.parse_args(argv)
    try:
        findings = check_paths(args.paths, args.max_elements, args.index)
    except (OSError, ValueError, UnicodeDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    for f in findings:
        print(f.render())
    errors = sum(f.severity == "E" for f in findings)
    if findings:
        print(f"{errors} error(s), {len(findings) - errors} warning(s)")
    else:
        print("ok")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
