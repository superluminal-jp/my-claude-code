"""Where a product's Scrum artifacts live in a repository, shared by the two scripts.

The Scrum Guide prescribes no folder or file layout, so every name here is this
skill's own convention (references/conventions.md). Standard library only.
"""
from __future__ import annotations

import datetime
import re
from pathlib import Path

SCRUM_DIR = "scrum"
SPRINTS_DIR = "sprints"
PRODUCT_BACKLOG = "product-backlog.md"
DEFINITION_OF_DONE = "definition-of-done.md"
SPRINT_BACKLOG = "sprint-backlog.md"
DAILY_SCRUM = "daily-scrum.md"

# Placed file -> bundled template, relative to templates/.
PRODUCT_FILES = {
    "README.md": "scrum-readme.md",
    PRODUCT_BACKLOG: PRODUCT_BACKLOG,
    DEFINITION_OF_DONE: DEFINITION_OF_DONE,
}
SPRINT_FILES = (
    SPRINT_BACKLOG,
    "increment.md",
    "sprint-planning.md",
    "sprint-review.md",
    "sprint-retrospective.md",
)

SPRINT_NAME = re.compile(r"^(\d{3})-(\d{4}-\d{2}-\d{2})$")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class UsageError(Exception):
    """The request cannot be carried out as given; the caller exits with 2."""


def parse_date(text: str) -> datetime.date | None:
    """A real calendar date written exactly as YYYY-MM-DD, or None."""
    if not ISO_DATE.match(text):
        return None
    try:
        return datetime.date.fromisoformat(text)
    except ValueError:
        return None


def parse_sprint_name(name: str) -> tuple[int, datetime.date] | None:
    match = SPRINT_NAME.match(name)
    if not match:
        return None
    start = parse_date(match.group(2))
    if start is None:
        return None
    return int(match.group(1)), start


def resolve_scrum_dir(root_arg: str, product_arg: str) -> tuple[Path, Path, Path]:
    """Return (root, product, scrum) as resolved paths, all inside the root.

    The product comes from a person or a model, so it is checked before any
    file is touched: it must be a relative path to an existing folder that,
    with symbolic links followed, is still inside the root. The same holds for
    the product's scrum folder when it already exists.
    """
    root = Path(root_arg).resolve()
    if not root.is_dir():
        raise UsageError(f"--root is not a folder: {root_arg}")
    if Path(product_arg).is_absolute():
        raise UsageError("--product must be a path relative to --root")
    product = (root / product_arg).resolve()
    if product != root and root not in product.parents:
        raise UsageError(f"--product leaves the root: {product_arg}")
    if not product.is_dir():
        raise UsageError(f"--product is not an existing folder: {product_arg}")
    scrum = product / SCRUM_DIR
    resolved = scrum.resolve()
    if scrum.is_symlink() or resolved != scrum:
        if root not in resolved.parents:
            raise UsageError(f"{display(scrum, root)} is a link that leaves the root")
    if scrum.exists() and not scrum.is_dir():
        raise UsageError(f"{display(scrum, root)} is not a folder")
    return root, product, scrum


def display(path: Path, base: Path) -> str:
    """The path as written in messages: relative to the product, with forward slashes."""
    try:
        return path.relative_to(base).as_posix()
    except ValueError:
        return path.as_posix()


def sprint_folders(scrum: Path) -> list[Path]:
    """The folders directly under scrum/sprints/, sorted by name; files there are ignored."""
    sprints = scrum / SPRINTS_DIR
    if not sprints.is_dir():
        return []
    return sorted((p for p in sprints.iterdir() if p.is_dir()), key=lambda p: p.name)
