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
file exists is check_links.py's concern. Only relative links count: links in code blocks,
inline code, and HTML comments, site-absolute links (/path), fragment-only links, external
links, and links that leave the repository do not. A README that still holds the unfilled
marker TODO(unfilled) outside code and comments gets a warning with the number of markers,
which leaves the exit code unchanged.

Without a declaration nothing is checked: candidate patterns are listed instead, from
package.json workspaces, pyproject.toml [tool.uv.workspace] members (Python 3.11 or later,
which has tomllib; earlier versions note that the file was not read), and folders named
"features".

With --hook it runs as a Claude Code PreToolUse hook and reads the hook input from stdin.
For a Bash command that runs `git commit`, it finds the project: the nearest folder holding
.living-documentation.json, from the directory the commit runs in (the input's "cwd", moved
by a `cd` before the commit or by git's -C) up to its Git worktree root. When that
configuration declares a tree, it prints the tree errors (at most 20, and the count of the
rest), or the configuration error, as additionalContext for Claude, each cut to one line of
at most 200 characters. It never returns a permission decision, so the commit is neither
approved nor blocked. Anything else prints nothing: unreadable input, a directory that does
not exist as written (one given by a variable or a substitution is not expanded), and a
configuration without a "tree" key, even an invalid one. It always exits 0.

Exit codes: 0 no error, 1 one or more errors, 2 invalid configuration or arguments.
"""
from __future__ import annotations

import sys

sys.dont_write_bytecode = True  # never leave __pycache__ in the Skill or project

import argparse
import json
import posixpath
import re
import shlex
from pathlib import Path
from urllib.parse import unquote

from check_links import HTML_ATTR_RE, INLINE_LINK_RE, REF_DEF_RE, is_external, masked_text, normalize_target
from common import (
    CONFIG_NAME, README_NAME, ConfigError, TreeNode, directories_of, git_toplevel, list_files, load_config,
    segment_match, tree_nodes,
)

UNFILLED_MARKER = "TODO(unfilled)"
HOOK_LIMIT = 20  # errors listed in the hook's context; the rest are counted
HOOK_LINE_LIMIT = 200  # characters of repository text in one line of the hook's context
ASSIGNMENT_RE = re.compile(r"^[A-Za-z_]\w*=")
SHELL_OPERATOR_CHARS = set(";&|()")

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


def simple_commands(command: str) -> list[list[str]] | None:
    """The words of each simple command in a shell command line, or None when it cannot be split.

    Quotes are respected, so a commit message holding `;` or `(` stays one word. A here-document
    body is dropped: the command that reads it comes before `<<`.
    """
    lexer = shlex.shlex(command.split("<<", 1)[0].replace("\n", " ; "), posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    try:
        tokens = list(lexer)
    except ValueError:
        return None
    commands: list[list[str]] = [[]]
    for token in tokens:
        if set(token) <= SHELL_OPERATOR_CHARS:
            commands.append([])
        else:
            commands[-1].append(token)
    return [words for words in commands if words]


def moved(directory: Path | None, target: str) -> Path | None:
    """The directory after `cd target` or `git -C target`, taken as written.

    A path given by a variable or a substitution is not expanded; it names no existing
    folder, so no configuration is found there and the hook stays silent.
    """
    return None if directory is None else (directory / Path(target).expanduser()).resolve()


def commit_directory(command: str, cwd: Path) -> tuple[bool, Path | None]:
    """Whether the command runs `git commit`, and the directory it runs in (None if unknown).

    A `cd` before the commit and git's `-C` options move the directory; `-c` and other
    global options are skipped.
    """
    commands = simple_commands(command)
    if commands is None:
        return False, None
    directory: Path | None = cwd
    for words in commands:
        while words and ASSIGNMENT_RE.match(words[0]):
            words = words[1:]
        if not words:
            continue
        if words[0] == "cd":
            directory = moved(directory, words[1] if len(words) > 1 else "~")
            continue
        if words[0] != "git":
            continue
        place, index = directory, 1
        while index < len(words) and words[index].startswith("-"):
            if words[index] in ("-C", "-c") and index + 1 < len(words):
                if words[index] == "-C":
                    place = moved(place, words[index + 1])
                index += 2
            else:
                index += 1
        if index < len(words) and words[index] == "commit":
            return True, place
    return False, None


def configured_root(directory: Path) -> Path | None:
    """The nearest folder holding .living-documentation.json, from directory up to its Git worktree root."""
    top = git_toplevel(directory) if directory.is_dir() else None
    for folder in (directory, *directory.parents):
        if (folder / CONFIG_NAME).is_file():
            return folder
        if top is None or folder == top:
            return None
    return None


def plain(text: str) -> str:
    """Repository text as one line of at most HOOK_LINE_LIMIT characters."""
    flat = "".join(c if c.isprintable() else " " for c in text)
    return flat if len(flat) <= HOOK_LINE_LIMIT else flat[:HOOK_LINE_LIMIT - 3] + "..."


def hook(raw: str) -> str:
    """The PreToolUse hook output for a Bash `git commit`, or "" when there is nothing to say.

    It only adds context for Claude: it never returns a permission decision, so the
    commit goes through the normal permission flow whatever the tree holds.
    """
    try:
        payload = json.loads(raw)
        command = payload["tool_input"]["command"]
        cwd = payload.get("cwd") or ""
    except (ValueError, TypeError, KeyError, AttributeError):
        return ""
    if payload.get("tool_name") != "Bash" or not isinstance(command, str) or not isinstance(cwd, str):
        return ""
    found, directory = commit_directory(command, Path(cwd).resolve())
    root = configured_root(directory) if found and directory else None
    if root is None:
        return ""
    # Only a declared tree is this hook's concern: any other content, valid or not, stays silent.
    try:
        declared = json.loads((root / CONFIG_NAME).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError):
        return ""
    if not isinstance(declared, dict) or "tree" not in declared:
        return ""
    where = plain(str(root))
    try:
        config = load_config(root)
        errors = check(root, tree_nodes(root, config, list_files(root, config)[0]))[0]
    except ConfigError as exc:
        text = (f"sync-docs could not check the documentation tree of {where} before this commit: "
                f"{plain(str(exc))}. This hook does not block the commit.")
    else:
        if not errors:
            return ""
        lines = [f"- {plain(error['message'])}" for error in errors[:HOOK_LIMIT]]
        if len(errors) > HOOK_LIMIT:
            lines.append(f"(and {len(errors) - HOOK_LIMIT} more; run check_tree.py for the full list)")
        text = "\n".join([f"sync-docs: the documentation tree of {where} has {len(errors)} error(s) (check_tree.py). "
                          "This hook does not block the commit, which may already be made. If this change caused "
                          "an error, fix it in a follow-up commit; otherwise tell the person it was already there:",
                          *lines])
    return json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": text}})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", default="", help="Project root (default: current directory)")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    parser.add_argument("--hook", action="store_true", help="Run as a Claude Code PreToolUse hook (input on stdin)")
    args = parser.parse_args()
    if args.hook:
        # A hook must never stop the commit or the session: any failure means no output and exit 0.
        try:
            output = hook(sys.stdin.read())
        except Exception:  # noqa: BLE001
            output = ""
        if output:
            print(output)
        return 0

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
