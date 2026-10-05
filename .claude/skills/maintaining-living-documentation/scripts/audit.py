#!/usr/bin/env python3
"""Summarize changed files and their possible documentation impact.

Read-only. Requires Git. Without --base, compares the worktree (staged,
unstaged, and untracked files) with HEAD. With --base REF, compares the
worktree with merge-base(REF, HEAD), so committed and uncommitted changes on
the branch are both included. --root may be a subdirectory of a repository;
only changes under it are reported.
"""
from __future__ import annotations

import sys

sys.dont_write_bytecode = True  # never leave __pycache__ in the Skill or project

import argparse
import json
from collections import defaultdict
from pathlib import Path

from common import (
    ConfigError, GitError, changed_files, classify, comparison_rev, excluded, file_at,
    is_changelog, list_files, load_config, record_status, substance_changed,
)

IMPACT_HINTS = {
    "implementation": "Check behavior, interfaces, architecture, operations, and user-facing documentation for material change.",
    "specification": "Check generated/reference documentation and implementations that claim conformance to the changed specifications.",
    "decision": "Check architecture/requirements documentation and whether the decision supersedes earlier rationale.",
    "documentation": "Check links, generated outputs, citations, and consistency with authoritative implementation/specifications.",
    "evidence": "Check whether changed tests/benchmarks/validation alter documented claims or acceptance evidence.",
    "generated": "Confirm generated artifacts were regenerated from authoritative sources and belong in version control here.",
    "infrastructure": "Check deployment, operations, CI, and environment documentation (runbooks, topology, prerequisites).",
    "configuration": "Check configuration reference, defaults, installation/build instructions, and dependency documentation.",
}
USER_VISIBLE = {"implementation", "specification", "configuration", "infrastructure"}


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
        print(f"error: {exc}. audit.py needs Git; use inspect_project.py and "
              f"check_links.py for projects without Git.", file=sys.stderr)
        return 2

    changes = [c for c in changes if not excluded(c.path, config)]
    by_category: dict[str, list[str]] = defaultdict(list)
    aggregate: set[str] = set()
    for change in changes:
        for cat in classify(change.path, config):
            aggregate.add(cat)
            by_category[cat].append(change.path)

    impacts = [IMPACT_HINTS[c] for c in IMPACT_HINTS if c in aggregate]
    removed = [c for c in changes if c.status == "D" or c.status == "R"]
    if removed:
        impacts.append("Files were deleted or renamed: update references to the old paths "
                       "(check_links.py --changed reports broken links to them).")

    accepted_edits: list[str] = []
    rev = comparison_rev(root, args.base)
    for change in changes:
        if rev is None or change.status not in ("M", "D", "R") or "decision" not in classify(change.path, config):
            continue
        old = file_at(root, rev, change.old_path or change.path)
        if old is None or record_status(old) != "accepted":
            continue
        if change.status == "D":
            accepted_edits.append(f"{change.path} (deleted)")
            continue
        try:
            new = (root / change.path).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if substance_changed(old, new):
            accepted_edits.append(change.path)
    if accepted_edits:
        impacts.append("Accepted decision records changed beyond status and supersession links or were deleted: "
                       + ", ".join(accepted_edits) + ". Accepted records are immutable: restore them, keep "
                       "superseded or deprecated ones, and record a new decision that supersedes them, unless "
                       "the edit only fixes a typo.")

    changelog_changed = any(is_changelog(c.path) for c in changes)
    project_changelogs = [] if changelog_changed else [f for f in list_files(root, config)[0] if is_changelog(f)]
    if aggregate & USER_VISIBLE and not changelog_changed and project_changelogs:
        impacts.append("The project keeps change history (" + ", ".join(project_changelogs[:3]) +
                       ") but it was not updated: add an entry if the change is user-visible, "
                       "breaking, or a deprecation.")
    if aggregate & USER_VISIBLE and "documentation" not in aggregate:
        impacts.append("No documentation file changed. Either update affected documentation or "
                       "record why the change has no documentation impact.")

    result = {
        "root": str(root),
        "base": args.base,
        "changes": [
            {"path": c.path, "status": c.status, **({"old_path": c.old_path} if c.old_path else {})}
            for c in changes
        ],
        "categories": {k: v for k, v in sorted(by_category.items())},
        "documentation_changed": "documentation" in aggregate,
        "accepted_records_modified": accepted_edits,
        "changelog_changed": changelog_changed,
        "possible_impacts": impacts,
        "note": "Impact hints are conservative heuristics, not proof that documentation changes are required or sufficient.",
    }

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    if not changes:
        print("No changed files found.")
        return 0
    print(f"changed files: {len(changes)}" + (f" (since merge-base with {args.base})" if args.base else ""))
    for category, files in sorted(by_category.items()):
        print(f"\n{category} ({len(files)}):")
        for f in files[:20]:
            print(f"  - {f}")
        if len(files) > 20:
            print(f"  ... {len(files) - 20} more")
    if removed:
        print("\ndeleted/renamed:")
        for c in removed[:20]:
            print(f"  - {c.old_path or c.path}" + (f" -> {c.path}" if c.old_path else " (deleted)"))
    print("\npossible documentation impact:")
    for item in impacts:
        print(f"  - {item}")
    print(f"\n{result['note']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
