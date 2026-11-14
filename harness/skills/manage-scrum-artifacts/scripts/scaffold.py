#!/usr/bin/env python3
"""Place a product's Scrum artifacts in a repository from the bundled templates.

Usage:
  scaffold.py init   --root ROOT [--product PATH]
  scaffold.py sprint --root ROOT [--product PATH] --start YYYY-MM-DD [--daily]

`init` places <product>/scrum/README.md, product-backlog.md, and
definition-of-done.md. `sprint` adds <product>/scrum/sprints/<NNN>-<start>/ with
the sprint templates; NNN is one more than the highest existing sprint number.

A file that already exists is never rewritten or removed: it is reported as
kept. Every request is validated before anything is written, so a refused
request (exit 2) leaves the folder as it was. The script writes only under
<product>/scrum/, which must be inside ROOT. It fills in no value: the Product
Goal, the Sprint Goal, the Definition of Done, and the order of the Product
Backlog are the Scrum Team's to write.

Standard library only; Python 3.9 or later. Exit 0 on success, 2 when the
request cannot be carried out.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from scrum_layout import (
    DAILY_SCRUM, PRODUCT_FILES, SPRINT_FILES, SPRINTS_DIR, UsageError,
    display, parse_date, parse_sprint_name, resolve_scrum_dir, sprint_folders,
)

TEMPLATES = Path(__file__).resolve().parent.parent / "templates"


def place(target: Path, template: Path, product: Path) -> str:
    """Write the template to target unless something is already there."""
    shown = display(target, product)
    if target.exists() or target.is_symlink():
        return f"kept {shown}"
    target.parent.mkdir(parents=True, exist_ok=True)
    # "x" fails instead of overwriting if the file appears in the meantime.
    with open(target, "xb") as handle:
        handle.write(template.read_bytes())
    return f"created {shown}"


def read_templates(names: dict[str, str]) -> dict[str, Path]:
    found = {}
    for placed, template in names.items():
        path = TEMPLATES / template
        if not path.is_file():
            raise UsageError(f"bundled template is missing: templates/{template}")
        found[placed] = path
    return found


def init(root_arg: str, product_arg: str) -> list[str]:
    _, product, scrum = resolve_scrum_dir(root_arg, product_arg)
    templates = read_templates(PRODUCT_FILES)
    return [place(scrum / placed, template, product) for placed, template in templates.items()]


def sprint(root_arg: str, product_arg: str, start_arg: str, daily: bool) -> list[str]:
    _, product, scrum = resolve_scrum_dir(root_arg, product_arg)
    if not scrum.is_dir():
        raise UsageError(f"{display(scrum, product)}/ does not exist; run init for this product first")
    start = parse_date(start_arg)
    if start is None:
        raise UsageError(f"--start is not a calendar date written as YYYY-MM-DD: {start_arg}")
    existing = [parsed for parsed in (parse_sprint_name(p.name) for p in sprint_folders(scrum)) if parsed]
    number = 1
    if existing:
        number = max(n for n, _ in existing) + 1
        latest = max(d for _, d in existing)
        if start <= latest:
            raise UsageError(f"--start {start_arg} is not after the latest sprint's start, {latest.isoformat()}")
    if number > 999:
        raise UsageError("the sprint number would exceed 999")
    names = {name: f"sprint/{name}" for name in SPRINT_FILES}
    if daily:
        names[DAILY_SCRUM] = f"sprint/{DAILY_SCRUM}"
    templates = read_templates(names)
    folder = scrum / SPRINTS_DIR / f"{number:03d}-{start.isoformat()}"
    return [place(folder / placed, template, product) for placed, template in templates.items()]


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="scaffold.py", description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("init", "sprint"):
        command = sub.add_parser(name)
        command.add_argument("--root", required=True, help="the repository root")
        command.add_argument("--product", default=".", help="the product folder, relative to the root (default: the root)")
        if name == "sprint":
            command.add_argument("--start", required=True, help="the sprint's start date, YYYY-MM-DD")
            command.add_argument("--daily", action="store_true", help="also place daily-scrum.md")
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            lines = init(args.root, args.product)
        else:
            lines = sprint(args.root, args.product, args.start, args.daily)
    except UsageError as error:
        print(f"scaffold: {error}", file=sys.stderr)
        return 2
    except OSError as error:
        print(f"scaffold: {error.strerror or error}: {error.filename}", file=sys.stderr)
        return 2
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
