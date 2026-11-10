#!/usr/bin/env python3
"""List the documents a change may leave out of date, as candidates for a documentation update.

Read-only. Requires Git. Without --base, compares the worktree (staged, unstaged, and
untracked files) with HEAD. With --base REF, compares the worktree with merge-base(REF, HEAD).
--root may be a subdirectory of a repository; only changes under it are reported.

Candidates, closest first (contract C1; documents that changed too are never candidates):
  P0 comment    the changed implementation file itself (advisory: keep its comments in step)
  P1 sibling    a document in the same directory as a changed file
  P2 mention    a document that names a changed file by path, or by name when the name is long enough
  P3 changelog  the project's change history, when a user-visible change left it untouched
related.max_candidates keeps the closest documents and counts the rest in "truncated";
related.min_name_length sets the shortest file name that counts as a mention.

The JSON output is {"changed": [...], "candidates": [{"source", "path", "kind", "proximity",
"reason"}], "truncated": N}.
"""
from __future__ import annotations

import sys

sys.dont_write_bytecode = True  # never leave __pycache__ in the Skill or project

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path, PurePosixPath

from common import (
    CHANGELOG_DIRS, CHANGELOG_STEMS, DOC_SUFFIXES, Change, ConfigError, GitError, changed_files, classify, excluded,
    is_changelog, list_files, load_config,
)

DEFAULT_MAX_CANDIDATES = 10
DEFAULT_MIN_NAME_LENGTH = 6
MAX_DOCUMENT_BYTES = 1024 * 1024  # larger documents are not searched for mentions
USER_VISIBLE = {"implementation", "specification", "configuration", "infrastructure"}
PROXIMITY_RANK = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}


def directory_of(path: str) -> str:
    parent = PurePosixPath(path).parent.as_posix()
    return "" if parent == "." else parent


def is_candidate_document(path: str, config: dict) -> bool:
    """A Markdown-like document that is neither change history nor a decision record."""
    if PurePosixPath(path).suffix.lower() not in DOC_SUFFIXES:
        return False
    return not is_changelog(path) and "decision" not in classify(path, config)


def read_document(root: Path, path: str) -> str | None:
    """Text of a document, or None when it is too large or cannot be read as UTF-8."""
    try:
        full = root / path
        if full.stat().st_size > MAX_DOCUMENT_BYTES:
            return None
        return full.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def mention_patterns(source: str, min_name_length: int) -> list[tuple[str, re.Pattern]]:
    """The whole path, and the file name when it is long enough, as whole-word patterns."""
    name = PurePosixPath(source).name
    tokens = [source] + ([name] if len(name) >= min_name_length and name != source else [])
    return [(token, re.compile(r"(?<![\w.-])" + re.escape(token) + r"(?![\w-])")) for token in tokens]


def find_candidates(root: Path, config: dict, changes: list[Change]) -> dict:
    """Return the C1 report for ``changes`` (a list of changes under ``root``)."""
    settings = config.get("related", {})
    max_candidates = settings.get("max_candidates", DEFAULT_MAX_CANDIDATES)
    min_name_length = settings.get("min_name_length", DEFAULT_MIN_NAME_LENGTH)

    changes = [c for c in changes if not excluded(c.path, config)]
    changed = {c.path for c in changes}
    categories = {c.path: classify(c.path, config) for c in changes}
    sources = sorted(path for path, cats in categories.items() if "documentation" not in cats)

    records: dict[tuple[str, str], dict] = {}

    def add(source: str, path: str, kind: str, proximity: str, reason: str) -> None:
        current = records.get((path, source))
        if current is None or PROXIMITY_RANK[proximity] < PROXIMITY_RANK[current["proximity"]]:
            records[(path, source)] = {"source": source, "path": path, "kind": kind,
                                       "proximity": proximity, "reason": reason}

    if sources:
        files, _ = list_files(root, config)
        documents = [f for f in files if f not in changed and is_candidate_document(f, config)]

        documents_by_dir: dict[str, list[str]] = defaultdict(list)
        for document in documents:
            documents_by_dir[directory_of(document)].append(document)
        for source in sources:
            for document in documents_by_dir.get(directory_of(source), []):
                add(source, document, "sibling", "P1",
                    f"document in the same directory as the changed file {source}; it was not changed")

        patterns = {source: mention_patterns(source, min_name_length) for source in sources}
        for document in documents:
            text = read_document(root, document)
            if text is None:
                continue
            for source in sources:
                if (document, source) in records:
                    continue
                for token, pattern in patterns[source]:
                    if pattern.search(text):
                        add(source, document, "mention", "P2",
                            f"mentions {token}, which changed; this document was not changed")
                        break

        user_visible = [s for s in sources if categories[s] & USER_VISIBLE]
        # Only the project's own history counts: a changelog inside a vendored subtree describes that code.
        changelogs = [f for f in files if "/" not in f and f.lower().split(".", 1)[0] in CHANGELOG_STEMS]
        history_changed = any(is_changelog(path) and ("/" not in path or path.split("/")[0].lower() in CHANGELOG_DIRS)
                              for path in changed)
        if user_visible and changelogs and not history_changed:
            for changelog in changelogs:
                add(user_visible[0], changelog, "changelog", "P3",
                    f"the project keeps change history; {len(user_visible)} user-visible change(s), "
                    f"starting with {user_visible[0]}")

        for source in sources:
            if categories[source] == {"implementation"}:
                add(source, source, "comment", "P0",
                    "comments in the changed file itself; keep them in step with the code (advisory)")

    ordered = sorted(records.values(), key=lambda r: (PROXIMITY_RANK[r["proximity"]], r["path"], r["source"]))
    kept_paths: list[str] = []
    dropped_paths: set[str] = set()
    candidates = []
    for record in ordered:
        if record["kind"] != "comment":  # advisory comment records do not count toward the cap
            if record["path"] not in kept_paths:
                if len(kept_paths) >= max_candidates:
                    dropped_paths.add(record["path"])
                    continue
                kept_paths.append(record["path"])
        candidates.append(record)
    return {"changed": sorted(changed), "candidates": candidates, "truncated": len(dropped_paths)}


def render_text(report: dict) -> str:
    lines = [f"changed files: {len(report['changed'])}"]
    documents = [c for c in report["candidates"] if c["kind"] != "comment"]
    comments = [c for c in report["candidates"] if c["kind"] == "comment"]
    if not documents:
        lines.append("no related documents found.")
    else:
        detail: dict[str, list[dict]] = defaultdict(list)
        for candidate in documents:
            detail[candidate["path"]].append(candidate)
        lines.append("related documents (closest first):")
        for path in sorted(detail, key=lambda p: (PROXIMITY_RANK[detail[p][0]["proximity"]], p)):
            first = detail[path][0]
            lines.append(f"  {path}  [{first['proximity']} {first['kind']}]  <- "
                         + ", ".join(c["source"] for c in detail[path]))
    if report["truncated"]:
        lines.append(f"({report['truncated']} more not listed: raise related.max_candidates)")
    if comments:
        lines.append("comments to keep in step (advisory): " + ", ".join(c["path"] for c in comments))
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
