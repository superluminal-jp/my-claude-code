#!/usr/bin/env python3
"""Check the declared documentation tree, or propose a declaration when there is none.

Read-only. Standard library only; no network; no project file is written.

With a "tree" declaration in .living-documentation.json, every node (the repository root,
each product, each feature folder) needs a README.md that links to the README of each child
node and, below the root, back to the README of its parent. Each break is one error:
  missing-readme       the node's folder has no README.md
  missing-child-link   the node's README does not link to a child node
  missing-parent-link  the node's README does not link to its parent node
A link counts by its target path, written as the README or as its folder; whether the target
file exists is check_links.py's concern. Links in code blocks, inline code, and HTML comments
do not count. A README that still holds the unfilled marker TODO(unfilled) gets a warning,
which leaves the exit code unchanged.

Without a declaration nothing is checked: candidate patterns are listed instead.

Exit codes: 0 no error, 1 one or more errors, 2 invalid configuration or arguments.
"""
from __future__ import annotations

import sys

sys.dont_write_bytecode = True  # never leave __pycache__ in the Skill or project

import argparse
import json
import posixpath
from pathlib import Path
from urllib.parse import unquote

from check_links import HTML_ATTR_RE, INLINE_LINK_RE, REF_DEF_RE, is_external, masked_text, normalize_target
from common import (
    CONFIG_NAME, README_NAME, ConfigError, TreeNode, directories_of, list_files, load_config, segment_match,
    tree_nodes,
)

UNFILLED_MARKER = "TODO(unfilled)"

try:
    import tomllib
except ImportError:  # Python < 3.11: pyproject.toml workspaces are reported as unread
    tomllib = None


def workspace_patterns(root: Path, files: list[str], notes: list[str]) -> list[str]:
    """Product candidates: package.json workspaces and pyproject.toml [tool.uv.workspace] members."""
    patterns: list[str] = []
    if "package.json" in files:
        try:
            workspaces = json.loads((root / "package.json").read_text(encoding="utf-8")).get("workspaces", [])
        except (OSError, UnicodeDecodeError, ValueError, AttributeError) as exc:
            notes.append(f"package.json could not be read ({exc}); its workspaces were not used")
            workspaces = []
        if isinstance(workspaces, dict):
            workspaces = workspaces.get("packages", [])
        patterns += [w for w in workspaces if isinstance(w, str)]
    if "pyproject.toml" in files:
        if tomllib is None:
            notes.append("pyproject.toml was not read: tomllib needs Python 3.11 or later")
        else:
            try:
                data = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
                members = data.get("tool", {}).get("uv", {}).get("workspace", {}).get("members", [])
            except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError, AttributeError) as exc:
                notes.append(f"pyproject.toml could not be read ({exc}); its workspace members were not used")
                members = []
            patterns += [m for m in members if isinstance(m, str)]
    cleaned = [p.removeprefix("./").rstrip("/") for p in patterns if not p.startswith("!")]
    return list(dict.fromkeys(p for p in cleaned if p))


def propose(root: Path, files: list[str]) -> tuple[dict, list[str]]:
    """Candidate patterns per kind, and notes on sources that could not be read.

    Feature candidates are the children of every folder named "features"; inside a
    product candidate, the product part of the path is replaced by its pattern.
    """
    notes: list[str] = []
    products = workspace_patterns(root, files, notes)
    features: list[str] = []
    directories = directories_of(files)
    for directory in sorted(directories):
        parts = directory.split("/")
        if parts[-1] != "features" or not any(d.startswith(directory + "/") for d in directories):
            continue
        pattern = directory
        for product in products:
            depth = len(product.split("/"))
            if len(parts) > depth and segment_match("/".join(parts[:depth]), product):
                pattern = "/".join([product] + parts[depth:])
                break
        features.append(pattern + "/*")
    return {"products": products, "features": list(dict.fromkeys(features))}, notes


def readme_of(node: TreeNode) -> str:
    return f"{node.path}/{README_NAME}" if node.path else README_NAME


def display(path: str) -> str:
    return path or "."


def linked_directories(readme_dir: str, text: str) -> set[str]:
    """Project-relative folders whose README this text links to (a README or its folder)."""
    masked, _, _ = masked_text(text)
    linked: set[str] = set()
    for regex in (INLINE_LINK_RE, REF_DEF_RE, HTML_ATTR_RE):
        for match in regex.finditer(masked):
            target = normalize_target(match.group(match.lastindex or 1))
            if not target or is_external(target) or target.startswith(("/", "#")):
                continue
            path_part = unquote(target.split("#", 1)[0].split("?", 1)[0])
            resolved = posixpath.normpath(posixpath.join(readme_dir or ".", path_part))
            if resolved == ".." or resolved.startswith("../"):
                continue
            if posixpath.basename(resolved) == README_NAME:
                resolved = posixpath.dirname(resolved)
            linked.add("" if resolved in (".", "") else resolved)
    return linked


def unfilled_count(text: str) -> int:
    return masked_text(text)[0].count(UNFILLED_MARKER)


def check(root: Path, nodes: list[TreeNode]) -> tuple[list[dict], list[dict]]:
    children: dict[str, list[str]] = {node.path: [] for node in nodes}
    for node in nodes:
        if node.parent is not None:
            children[node.parent].append(node.path)
    errors: list[dict] = []
    warnings: list[dict] = []
    for node in nodes:
        readme = readme_of(node)
        try:
            text = (root / readme).read_text(encoding="utf-8")
        except FileNotFoundError:
            errors.append({"node": node.path, "kind": "missing-readme", "readme": readme, "target": None,
                           "message": f"{display(node.path)}: no {README_NAME} in this {node.kind} folder"})
            continue
        except (OSError, UnicodeDecodeError) as exc:
            errors.append({"node": node.path, "kind": "missing-readme", "readme": readme, "target": None,
                           "message": f"{readme}: cannot be read as UTF-8 text ({exc})"})
            continue
        linked = linked_directories(node.path, text)
        for child in children[node.path]:
            if child not in linked:
                errors.append({"node": node.path, "kind": "missing-child-link", "readme": readme, "target": child,
                               "message": f"{readme}: no link to the child node {child}"})
        if node.parent is not None and node.parent not in linked:
            errors.append({"node": node.path, "kind": "missing-parent-link", "readme": readme,
                           "target": node.parent,
                           "message": f"{readme}: no link to the parent node {display(node.parent)}"})
        count = unfilled_count(text)
        if count:
            warnings.append({"readme": readme, "count": count,
                             "message": f"{readme}: {count} unfilled item(s) marked {UNFILLED_MARKER}"})
    return errors, warnings


def render_text(report: dict) -> str:
    if not report["declared"]:
        lines = [f"no tree declared in {CONFIG_NAME}; nothing was checked."]
        lines += [f"note: {note}" for note in report["notes"]]
        candidates = {kind: patterns for kind, patterns in report["candidates"].items() if patterns}
        if candidates:
            lines.append(f"candidate declaration (confirm it, then add it to {CONFIG_NAME}):")
            lines.append(json.dumps({"tree": candidates}, indent=2))
        else:
            lines.append("no candidates found: declare tree.products and tree.features by hand if the project has them.")
        return "\n".join(lines)
    lines = [f"error: {e['message']}" for e in report["errors"]]
    lines += [f"warning: {w['message']}" for w in report["warnings"]]
    lines.append(f"tree: {len(report['nodes'])} node(s), {len(report['errors'])} error(s), "
                 f"{len(report['warnings'])} warning(s)")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", default="", help="Project root (default: current directory)")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    root = Path(args.root or ".").resolve()
    if not root.is_dir():
        print(f"error: not a directory: {root}", file=sys.stderr)
        return 2
    try:
        config = load_config(root)
        files = list_files(root, config)[0]
        nodes = tree_nodes(root, config, files) if "tree" in config else None
    except ConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if nodes is None:
        candidates, notes = propose(root, files)
        report = {"declared": False, "nodes": [], "errors": [], "warnings": [], "candidates": candidates,
                  "notes": notes}
    else:
        errors, warnings = check(root, nodes)
        report = {"declared": True, "nodes": [node._asdict() for node in nodes], "errors": errors,
                  "warnings": warnings}
    print(json.dumps(report, indent=2, ensure_ascii=False) if args.json else render_text(report))
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
