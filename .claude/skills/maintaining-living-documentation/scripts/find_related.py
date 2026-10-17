#!/usr/bin/env python3
"""List the documents next to changed files, as candidates for a documentation update.

Read-only. Requires Git. For every changed file that is not documentation, the
documents in the same directory (proximity P1) are candidates, unless they
changed too. Without --base, compares the worktree (staged, unstaged, and
untracked files) with HEAD. With --base REF, compares the worktree with
merge-base(REF, HEAD). --root may be a subdirectory of a repository; only
changes under it are reported.

The JSON output follows contract C1: {"changed": [...], "candidates":
[{"source", "path", "kind", "proximity", "reason"}], "truncated": 0}.
"""
from __future__ import annotations

import sys

sys.dont_write_bytecode = True  # never leave __pycache__ in the Skill or project

import argparse
import json
from collections import defaultdict
from pathlib import Path, PurePosixPath

from common import (
    DOC_SUFFIXES, Change, ConfigError, GitError, changed_files, classify, excluded, is_changelog,
    list_files, load_config,
)


def directory_of(path: str) -> str:
    parent = PurePosixPath(path).parent.as_posix()
    return "" if parent == "." else parent


def is_candidate_document(path: str, config: dict) -> bool:
    """A Markdown-like document that is neither change history nor a decision record."""
    if PurePosixPath(path).suffix.lower() not in DOC_SUFFIXES:
        return False
    return not is_changelog(path) and "decision" not in classify(path, config)


def find_candidates(root: Path, config: dict, changes: list[Change]) -> dict:
    """Return the C1 report for ``changes`` (a list of changes under ``root``)."""
    changes = [c for c in changes if not excluded(c.path, config)]
    changed = {c.path for c in changes}
    sources = sorted(c.path for c in changes if "documentation" not in classify(c.path, config))

    documents_by_dir: dict[str, list[str]] = defaultdict(list)
    if sources:
        files, _ = list_files(root, config)
        for path in files:
            if path not in changed and is_candidate_document(path, config):
                documents_by_dir[directory_of(path)].append(path)

    candidates = [
        {
            "source": source,
            "path": document,
            "kind": "sibling",
            "proximity": "P1",
            "reason": f"document in the same directory as the changed file {source}; it was not changed",
        }
        for source in sources
        for document in documents_by_dir.get(directory_of(source), [])
    ]
    candidates.sort(key=lambda c: (c["path"], c["source"]))
    return {"changed": sorted(changed), "candidates": candidates, "truncated": 0}


def render_text(report: dict) -> str:
    lines = [f"changed files: {len(report['changed'])}"]
    if not report["candidates"]:
        lines.append("no related documents found.")
        return "\n".join(lines)
    sources_by_path: dict[str, list[str]] = defaultdict(list)
    for candidate in report["candidates"]:
        sources_by_path[candidate["path"]].append(candidate["source"])
    lines.append("related documents (P1):")
    for path in sorted(sources_by_path):
        lines.append(f"  {path}  <- {', '.join(sources_by_path[path])}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", default="", help="Project root (default: current directory)")
    parser.add_argument("--base", help="Compare the worktree with merge-base(BASE, HEAD), e.g. origin/main")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    root = Path(args.root or ".").resolve()
    if not root.is_dir():
        print(f"error: not a directory: {root}", file=sys.stderr)
        return 2
    try:
        config = load_config(root)
        changes = changed_files(root, args.base)
    except ConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except GitError as exc:
        print(f"error: {exc}. find_related.py needs Git; without it, look for documents next to "
              f"the changed files yourself (inspect_project.py lists the project's documentation).",
              file=sys.stderr)
        return 2

    report = find_candidates(root, config, changes)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(render_text(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
