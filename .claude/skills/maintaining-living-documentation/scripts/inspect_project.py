#!/usr/bin/env python3
"""Inventory a project's artifact classes without assuming a repository layout.

Read-only. Uses Git's file list (honoring .gitignore) inside a worktree and a
filesystem walk otherwise.
"""
from __future__ import annotations

import sys

sys.dont_write_bytecode = True  # never leave __pycache__ in the Skill or project

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

from common import CONFIG_NAME, ConfigError, classify, git_toplevel, is_changelog, list_files, load_config


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default="", help="Project root (default: current directory)")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    root = Path(args.root or ".").resolve()
    if not root.is_dir():
        print(f"error: not a directory: {root}", file=sys.stderr)
        return 2
    try:
        config = load_config(root)
    except ConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    files, source = list_files(root, config)
    counts: Counter[str] = Counter()
    examples: dict[str, list[str]] = defaultdict(list)
    top_dirs: Counter[str] = Counter()
    changelogs: list[str] = []

    for relative in files:
        if "/" in relative:
            top_dirs[relative.split("/", 1)[0]] += 1
        if is_changelog(relative):
            changelogs.append(relative)
        for category in classify(relative, config):
            counts[category] += 1
            if len(examples[category]) < 8:
                examples[category].append(relative)

    toplevel = git_toplevel(root)
    result = {
        "root": str(root),
        "git_worktree": str(toplevel) if toplevel else None,
        "file_source": source,
        "configuration": str(root / CONFIG_NAME) if (root / CONFIG_NAME).exists() else None,
        "files_scanned": len(files),
        "categories": dict(sorted(counts.items())),
        "examples": dict(sorted(examples.items())),
        "changelogs": changelogs[:20],
        "top_directories": [name for name, _ in top_dirs.most_common(15)],
        "note": "Classification is heuristic. Correct it with *_globs in " + CONFIG_NAME + ".",
    }

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    print(f"root: {result['root']}")
    print(f"git worktree: {result['git_worktree'] or 'none'} (files from {source})")
    if result["configuration"]:
        print(f"configuration: {result['configuration']}")
    print(f"files scanned: {len(files)}")
    print("\nartifact classes:")
    for category, count in sorted(counts.items()):
        print(f"  {category}: {count}")
        for example in examples[category][:5]:
            print(f"    - {example}")
    if changelogs:
        print("\nchange history files:")
        for item in changelogs[:10]:
            print(f"  - {item}")
    if top_dirs:
        print("\ntop-level directories:")
        for name, count in top_dirs.most_common(15):
            print(f"  {name}/ ({count} files)")
    print(f"\n{result['note']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
