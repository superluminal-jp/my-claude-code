#!/usr/bin/env python3
"""Check local links in Markdown files.

Scope: this is a link checker, not a full consistency validator. It checks
inline links, images, reference-style link definitions, and HTML href/src
attributes that point at local files, plus #fragments that point at Markdown
headings. Links inside fenced code blocks, inline code, and HTML comments are
ignored. External URLs are not fetched.

Severity:
  error   missing local target, or a relative link that escapes the project root
  warning root-relative link (/path) not found under any --site-root, or a
          #fragment with no matching heading/anchor (renderers differ in how
          they generate heading IDs). --strict turns warnings into errors.

With --changed, only problems in changed Markdown files, or problems caused by
changed/deleted/renamed targets, are reported, so pre-existing breakage elsewhere
does not block the current change.
"""
from __future__ import annotations

import sys

sys.dont_write_bytecode = True  # never leave __pycache__ in the Skill or project

import argparse
import json
import re
import unicodedata
from pathlib import Path
from typing import NamedTuple
from urllib.parse import unquote, urlparse

from common import ConfigError, GitError, changed_files, list_files, load_config

MARKDOWN_SUFFIXES = {".md", ".mdx", ".markdown"}

INLINE_LINK_RE = re.compile(
    r"!?\[(?:[^\[\]]|\[[^\]]*\])*\]"            # [text] or ![alt], one level of nested brackets
    r"\(\s*(<[^>\n]*>|[^()\s]*(?:\([^()\s]*\)[^()\s]*)*)"  # destination, balanced parens once
    r"(?:\s+(?:\"[^\"]*\"|'[^']*'|\([^)]*\)))?\s*\)"       # optional title
)
REF_DEF_RE = re.compile(r"^ {0,3}\[([^\]]+)\]:[ \t]*(<[^>\n]*>|\S+)", re.MULTILINE)
HTML_ATTR_RE = re.compile(r"<(?:a|img|source)\b[^>]*?\b(?:href|src)\s*=\s*[\"']([^\"']+)[\"']", re.IGNORECASE)
HTML_ID_RE = re.compile(r"<[a-z][^>]*?\b(?:id|name)\s*=\s*[\"']([^\"']+)[\"']", re.IGNORECASE)
ATX_RE = re.compile(r"^ {0,3}#{1,6}[ \t]+(.*?)[ \t]*#*[ \t]*$")
SETEXT_RE = re.compile(r"^ {0,3}(=+|-+)[ \t]*$")
FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
EXPLICIT_ID_RE = re.compile(r"\s*\{#([^}\s]+)[^}]*\}\s*$")


class Finding(NamedTuple):
    severity: str   # "error" | "warning"
    source: str     # project-relative file
    line: int
    target: str
    message: str
    target_path: str | None  # project-relative resolved target, if local


# --------------------------------------------------------------------------
# Markdown preprocessing
# --------------------------------------------------------------------------

def fence_mask(lines: list[str]) -> list[bool]:
    """True for lines inside (or delimiting) fenced code blocks."""
    mask = [False] * len(lines)
    fence: str | None = None
    for i, line in enumerate(lines):
        m = FENCE_RE.match(line)
        if fence is None:
            if m:
                fence = m.group(1)
                mask[i] = True
        else:
            mask[i] = True
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence) \
                    and not line.strip().lstrip(fence[0]).strip():
                fence = None
    return mask


def _blank(match: re.Match) -> str:
    return re.sub(r"[^\n]", " ", match.group(0))


def masked_text(text: str) -> tuple[str, list[str], list[bool]]:
    """Return text with code blocks, inline code, and HTML comments blanked.

    Offsets and line numbers are preserved.
    """
    lines = text.split("\n")
    in_fence = fence_mask(lines)
    out = []
    for line, fenced in zip(lines, in_fence):
        if fenced:
            out.append(" " * len(line))
        else:
            out.append(re.sub(r"(`+)(?!`).+?(?<!`)\1(?!`)", _blank, line))
    masked = "\n".join(out)
    masked = re.sub(r"<!--.*?-->", _blank, masked, flags=re.DOTALL)
    return masked, lines, in_fence


# --------------------------------------------------------------------------
# Anchors
# --------------------------------------------------------------------------

def slugify(heading: str) -> str:
    """Approximate GitHub's heading ID algorithm."""
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", heading)        # images
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)         # links -> text
    text = re.sub(r"<[^>]+>", "", text)                          # HTML tags
    text = text.replace("`", "").strip().lower()
    # GitHub keeps letters, combining marks, numbers, connector punctuation,
    # spaces, and hyphens (Python's \w would drop combining marks such as
    # Devanagari vowel signs).
    text = "".join(ch for ch in text
                   if ch in " -" or unicodedata.category(ch)[0] in "LMN" or unicodedata.category(ch) == "Pc")
    return text.replace(" ", "-")


def anchors_for(path: Path, cache: dict[Path, set[str]]) -> set[str]:
    if path in cache:
        return cache[path]
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        cache[path] = set()
        return cache[path]
    lines = text.split("\n")
    fenced = fence_mask(lines)
    anchors: set[str] = set()
    counts: dict[str, int] = {}

    def add_heading(raw: str) -> None:
        explicit = EXPLICIT_ID_RE.search(raw)
        if explicit:
            anchors.add(explicit.group(1))
            raw = raw[:explicit.start()]
        slug = slugify(raw)
        n = counts.get(slug, 0)
        counts[slug] = n + 1
        anchors.add(slug if n == 0 else f"{slug}-{n}")

    for i, line in enumerate(lines):
        if fenced[i]:
            continue
        m = ATX_RE.match(line)
        if m:
            add_heading(m.group(1))
        elif (i + 1 < len(lines) and not fenced[i + 1] and line.strip()
              and SETEXT_RE.match(lines[i + 1]) and not ATX_RE.match(line)
              and not line.lstrip().startswith(("-", "*", ">", "|"))):
            add_heading(line.strip())
        for hid in HTML_ID_RE.findall(line):
            anchors.add(hid)
    cache[path] = anchors
    return anchors


# --------------------------------------------------------------------------
# Link checking
# --------------------------------------------------------------------------

def normalize_target(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("<") and raw.endswith(">"):
        raw = raw[1:-1]
    return raw


def is_external(target: str) -> bool:
    if target.startswith("//"):
        return True
    scheme = urlparse(target).scheme
    # A single letter is a Windows drive letter, not a URL scheme.
    return bool(scheme) and len(scheme) > 1


def check_file(path: Path, root: Path, site_roots: list[Path],
               anchor_cache: dict[Path, set[str]]) -> list[Finding]:
    rel = path.relative_to(root).as_posix()
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return [Finding("error", rel, 1, "", "not valid UTF-8", None)]
    except OSError as exc:
        return [Finding("error", rel, 1, "", f"cannot read: {exc}", None)]

    masked, _, _ = masked_text(text)
    targets: list[tuple[int, str]] = []
    for regex in (INLINE_LINK_RE, REF_DEF_RE, HTML_ATTR_RE):
        for m in regex.finditer(masked):
            raw = m.group(m.lastindex or 1)
            targets.append((masked.count("\n", 0, m.start()) + 1, normalize_target(raw)))

    findings: list[Finding] = []
    root_resolved = root.resolve()
    for line, target in targets:
        if not target or is_external(target):
            continue
        path_part, _, fragment = target.partition("#")
        path_part = unquote(path_part.split("?", 1)[0])
        fragment = unquote(fragment)

        if not path_part:  # same-document fragment
            if fragment and fragment not in anchors_for(path, anchor_cache):
                findings.append(Finding("warning", rel, line, target, "no matching heading or anchor", rel))
            continue

        if path_part.startswith("/"):
            candidates = [(sr / path_part.lstrip("/")).resolve() for sr in site_roots]
            found = next((c for c in candidates if c.exists()), None)
            if found is None:
                findings.append(Finding("warning", rel, line, target,
                                        "root-relative link not found under any --site-root", None))
                continue
            candidate = found
        else:
            candidate = (path.parent / path_part).resolve()
            try:
                candidate.relative_to(root_resolved)
            except ValueError:
                findings.append(Finding("error", rel, line, target, "relative link escapes project root", None))
                continue
            if not candidate.exists():
                target_rel = candidate.relative_to(root_resolved).as_posix()
                findings.append(Finding("error", rel, line, target, "missing local target", target_rel))
                continue

        try:
            target_rel = candidate.relative_to(root_resolved).as_posix()
        except ValueError:
            target_rel = None
        if fragment and candidate.is_file() and candidate.suffix.lower() in MARKDOWN_SUFFIXES:
            if fragment not in anchors_for(candidate, anchor_cache):
                findings.append(Finding("warning", rel, line, target, "no matching heading or anchor", target_rel))
    return findings


def run_check(root: Path, config: dict, changes: list | None = None,
              site_root_args: list[str] | None = None) -> tuple[list[str], list[Finding]]:
    """Check all Markdown files; with ``changes``, keep only findings in changed
    files or caused by changed/deleted/renamed targets."""
    site_roots = [(root / s).resolve() for s in (site_root_args or [])] or [root]
    files = [f for f in list_files(root, config)[0] if Path(f).suffix.lower() in MARKDOWN_SUFFIXES]
    cache: dict[Path, set[str]] = {}
    findings: list[Finding] = []
    for rel in files:
        findings.extend(check_file(root / rel, root, site_roots, cache))
    if changes is not None:
        touched = {c.path for c in changes if c.status != "D"}
        gone = {c.path for c in changes if c.status == "D"} | {c.old_path for c in changes if c.old_path}
        findings = [f for f in findings
                    if f.source in touched or (f.target_path is not None and f.target_path in touched | gone)]
    return files, findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", default="", help="Project root (default: current directory)")
    parser.add_argument("--site-root", action="append", default=[],
                        help="Directory that root-relative links (/path) resolve against, relative to --root. "
                             "Repeatable. Default: the project root.")
    parser.add_argument("--changed", action="store_true",
                        help="Report only problems in changed files or caused by changed/deleted targets (needs Git)")
    parser.add_argument("--base", help="With --changed: compare with merge-base(BASE, HEAD)")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    parser.add_argument("--quiet", action="store_true", help="Print nothing when there are no findings")
    args = parser.parse_args()

    root = Path(args.root or ".").resolve()
    if not root.is_dir():
        print(f"error: not a directory: {root}", file=sys.stderr)
        return 2
    if args.base and not args.changed:
        print("error: --base requires --changed", file=sys.stderr)
        return 2
    try:
        config = load_config(root)
        changes = changed_files(root, args.base) if args.changed else None
    except ConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except GitError as exc:
        print(f"error: --changed needs Git: {exc}", file=sys.stderr)
        return 2

    files, findings = run_check(root, config, changes, args.site_root)

    if args.strict:
        findings = [f._replace(severity="error") for f in findings]
    errors = [f for f in findings if f.severity == "error"]
    warnings = [f for f in findings if f.severity == "warning"]

    if args.json:
        print(json.dumps({
            "root": str(root),
            "mode": "changed" if args.changed else "all",
            "markdown_files": len(files),
            "errors": [f._asdict() for f in errors],
            "warnings": [f._asdict() for f in warnings],
        }, indent=2, ensure_ascii=False))
    else:
        for f in errors + warnings:
            stream = sys.stderr if f.severity == "error" else sys.stdout
            print(f"{f.severity}: {f.source}:{f.line}: {f.message}: {f.target}", file=stream)
        if findings or not args.quiet:
            scope = "changed scope" if args.changed else "all files"
            print(f"Link check ({scope}): {len(files)} Markdown files, "
                  f"{len(errors)} errors, {len(warnings)} warnings.")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
