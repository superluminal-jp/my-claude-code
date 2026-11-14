#!/usr/bin/env python3
"""Check the shape of a product's Scrum artifacts in a repository.

Usage: check_artifacts.py --root ROOT [--product PATH] [--format text|json]

Errors (exit 1), one per finding:
  SA-01  scrum/product-backlog.md is missing
  SA-02  scrum/definition-of-done.md is missing
  SA-03  a second product-backlog.md or definition-of-done.md exists under scrum/
  SA-04  a folder under scrum/sprints/ is not named <NNN>-<YYYY-MM-DD>
  SA-05  two sprint folders have the same number
  SA-06  a sprint folder has no sprint-backlog.md
  SA-07  a sprint's start date is not after the start of the sprint numbered before it

Warnings (exit code unchanged): a commitment the Scrum Team has not written yet.
  SW-01  Product Goal          in scrum/product-backlog.md
  SW-02  Definition of Done    in scrum/definition-of-done.md
  SW-03  Sprint Goal           in each sprint's sprint-backlog.md

The script reads files and writes nothing. It checks shape only: it cannot
tell whether the order of the Product Backlog serves the Product Goal or
whether an Increment meets the Definition of Done.

Standard library only; Python 3.9 or later. Exit 0 with no error, 1 with one
or more errors, 2 when the product cannot be checked.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

from scrum_layout import (
    DEFINITION_OF_DONE, PRODUCT_BACKLOG, SPRINT_BACKLOG, SPRINTS_DIR, UsageError,
    display, parse_sprint_name, resolve_scrum_dir, sprint_folders,
)

MAX_BYTES = 5 * 1024 * 1024


def commitment_is_written(path: Path, field: str) -> bool:
    """True when the `- **<field>**：` line has a value, on it or indented under it."""
    try:
        if path.stat().st_size > MAX_BYTES:
            return True  # too large to read; not this check's finding
        lines = path.read_text(encoding="utf-8", errors="replace").split("\n")
    except OSError:
        return False
    pattern = re.compile(r"^\s*[-*]\s*\*\*" + re.escape(field) + r"\*\*\s*[：:]\s*(.*)$")
    for index, line in enumerate(lines):
        match = pattern.match(line)
        if not match:
            continue
        if match.group(1).strip():
            return True
        for following in lines[index + 1:]:
            if not following.strip():
                continue
            # A value continued on the next lines is indented under the field.
            return following[:1] in (" ", "\t")
        return False
    return False


def check(product: Path, scrum: Path) -> tuple[list[dict], list[dict]]:
    errors: list[dict] = []
    warnings: list[dict] = []

    def add(target: list[dict], rule: str, path: Path, message: str) -> None:
        target.append({"rule": rule, "path": display(path, product), "message": message})

    backlog = scrum / PRODUCT_BACKLOG
    done = scrum / DEFINITION_OF_DONE
    if not backlog.is_file():
        add(errors, "SA-01", backlog, "the Product Backlog is missing")
    if not done.is_file():
        add(errors, "SA-02", done, "the Definition of Done is missing")

    singles = {PRODUCT_BACKLOG: "Product Backlog", DEFINITION_OF_DONE: "Definition of Done"}
    for folder, _, files in sorted(os.walk(scrum)):
        if Path(folder) == scrum:
            continue
        for name in sorted(files):
            if name in singles:
                add(errors, "SA-03", Path(folder) / name,
                    f"a product has one {singles[name]}, kept in scrum/{name}; this is a second one")

    numbered: list[tuple[int, object, Path]] = []
    seen: dict[int, Path] = {}
    for folder in sprint_folders(scrum):
        parsed = parse_sprint_name(folder.name)
        if parsed is None:
            add(errors, "SA-04", folder, "a sprint folder is named <NNN>-<YYYY-MM-DD>, a three-digit number and a real start date")
            continue
        number, start = parsed
        if number in seen:
            add(errors, "SA-05", folder, f"sprint number {number:03d} is already used by {seen[number].name}")
        else:
            seen[number] = folder
            numbered.append((number, start, folder))
        if not (folder / SPRINT_BACKLOG).is_file():
            add(errors, "SA-06", folder / SPRINT_BACKLOG, "the sprint has no Sprint Backlog")

    numbered.sort(key=lambda item: item[0])
    for (_, earlier, earlier_folder), (_, later, folder) in zip(numbered, numbered[1:]):
        if later <= earlier:
            add(errors, "SA-07", folder, f"its start date is not after the start of {earlier_folder.name}")

    if backlog.is_file() and not commitment_is_written(backlog, "Product Goal"):
        add(warnings, "SW-01", backlog, "the Product Goal is not written yet; the Product Owner writes it")
    if done.is_file() and not commitment_is_written(done, "Definition of Done"):
        add(warnings, "SW-02", done, "the Definition of Done is not written yet; the Scrum Team writes it")
    for _, _, folder in numbered:
        sprint_backlog = folder / SPRINT_BACKLOG
        if sprint_backlog.is_file() and not commitment_is_written(sprint_backlog, "Sprint Goal"):
            add(warnings, "SW-03", sprint_backlog, "the Sprint Goal is not written yet; the Scrum Team writes it in Sprint Planning")
    return errors, warnings


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="check_artifacts.py", description=__doc__.split("\n\n")[0])
    parser.add_argument("--root", required=True, help="the repository root")
    parser.add_argument("--product", default=".", help="the product folder, relative to the root (default: the root)")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)
    try:
        root, product, scrum = resolve_scrum_dir(args.root, args.product)
        if not scrum.is_dir():
            raise UsageError(f"{display(scrum, product)}/ does not exist in this product")
        errors, warnings = check(product, scrum)
    except UsageError as error:
        print(f"check_artifacts: {error}", file=sys.stderr)
        return 2
    except OSError as error:
        print(f"check_artifacts: {error.strerror or error}: {error.filename}", file=sys.stderr)
        return 2
    shown = display(product, root) if product != root else "."
    if args.format == "json":
        print(json.dumps({"product": shown, "errors": errors, "warnings": warnings}, ensure_ascii=False, indent=2))
    else:
        for label, items in (("ERROR", errors), ("WARN", warnings)):
            for item in items:
                print(f"{label} {item['rule']} {item['path']}: {item['message']}")
        print(f"Result: {len(errors)} errors, {len(warnings)} warnings (product {shown}; shape only)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
