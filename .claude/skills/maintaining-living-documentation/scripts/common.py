#!/usr/bin/env python3
"""Shared helpers for the living-documentation scripts.

Standard library only. Nothing here writes to the target project.
"""
from __future__ import annotations

import fnmatch
import json
import os
import re
import subprocess
from pathlib import Path, PurePosixPath
from typing import Iterable, NamedTuple

SKILL_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = SKILL_ROOT / "schemas" / "config.schema.json"
CONFIG_NAME = ".living-documentation.json"

# Directory names skipped wherever they occur (VCS metadata, dependency
# trees, virtual environments, caches).
ALWAYS_EXCLUDED_DIRS = {
    ".git", ".hg", ".svn", "node_modules", ".venv", "venv", "__pycache__",
    ".tox", ".nox", ".mypy_cache", ".pytest_cache", ".ruff_cache",
    ".gradle", ".terraform", ".next", ".nuxt",
}
# Directory names skipped only at the project root, because nested
# directories with these names are often real source code.
TOP_LEVEL_EXCLUDED_DIRS = {"dist", "build", "target", "vendor", "out", "site", "_build"}

CATEGORIES = (
    "implementation", "documentation", "specification", "decision",
    "evidence", "generated", "infrastructure", "configuration",
)


class ConfigError(ValueError):
    pass


class GitError(RuntimeError):
    pass


class Change(NamedTuple):
    path: str            # project-relative POSIX path (new path for renames)
    status: str          # A, M, D, R, C, T, U
    old_path: str | None  # previous path for renames/copies


# --------------------------------------------------------------------------
# Glob matching
# --------------------------------------------------------------------------

def glob_match(relative: str, pattern: str) -> bool:
    """fnmatch-based matching where '*' also crosses '/'.

    A leading '**/' additionally matches at the top level, so
    '**/node_modules/**' matches both 'node_modules/x' and 'a/node_modules/x'.
    """
    pattern = pattern.removeprefix("./")
    if fnmatch.fnmatchcase(relative, pattern):
        return True
    if pattern.startswith("**/") and fnmatch.fnmatchcase(relative, pattern[3:]):
        return True
    return False


def match_any(relative: str, patterns: Iterable[str]) -> bool:
    return any(glob_match(relative, p) for p in patterns)


# --------------------------------------------------------------------------
# Configuration (validated against the bundled JSON Schema)
# --------------------------------------------------------------------------

def _schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _check_type(value, spec: dict) -> bool:
    expected = spec.get("type")
    if "enum" in spec and value not in spec["enum"]:
        return False
    if expected == "string":
        return isinstance(value, str)
    if expected == "array":
        if not isinstance(value, list):
            return False
        item_spec = spec.get("items", {})
        return all(_check_type(v, item_spec) for v in value) if item_spec else True
    return True


def load_config(root: Path) -> dict:
    """Load and validate the optional project configuration.

    Accepted keys and their types come from schemas/config.schema.json, so the
    schema is the single source of truth.
    """
    path = root / CONFIG_NAME
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigError(f"invalid {CONFIG_NAME}: {exc}") from exc
    if not isinstance(data, dict):
        raise ConfigError(f"invalid {CONFIG_NAME}: top level must be an object")
    properties = _schema()["properties"]
    unknown = set(data) - set(properties)
    if unknown:
        raise ConfigError(
            f"invalid {CONFIG_NAME}: unknown keys: {', '.join(sorted(unknown))} "
            f"(accepted: {', '.join(sorted(properties))})"
        )
    for key, value in data.items():
        if not _check_type(value, properties[key]):
            spec = properties[key]
            expected = " or ".join(repr(v) for v in spec["enum"]) if "enum" in spec else spec.get("type")
            raise ConfigError(f"invalid {CONFIG_NAME}: {key} must be {expected}"
                              + (" of strings" if spec.get("type") == "array" else ""))
    return data


# --------------------------------------------------------------------------
# Exclusion and file listing
# --------------------------------------------------------------------------

def excluded(relative: str, config: dict, is_dir: bool = False) -> bool:
    relative = relative.removeprefix("./").rstrip("/")
    parts = relative.split("/")
    dir_parts = parts if is_dir else parts[:-1]
    if any(part in ALWAYS_EXCLUDED_DIRS for part in dir_parts):
        return True
    if dir_parts and dir_parts[0] in TOP_LEVEL_EXCLUDED_DIRS:
        return True
    patterns = config.get("exclude_globs", [])
    if not patterns:
        return False
    candidates = [relative, relative + "/"] if is_dir else [relative]
    for i in range(1, len(dir_parts) + (0 if is_dir else 1)):
        prefix = "/".join(parts[:i])
        candidates += [prefix, prefix + "/"]
    return any(glob_match(c, p) for c in candidates for p in patterns)


def run_git(root: Path, *args: str) -> subprocess.CompletedProcess | None:
    """Run a read-only git command. Returns None when git is not installed."""
    try:
        return subprocess.run(
            ["git", *args], cwd=root, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
    except (FileNotFoundError, PermissionError):
        return None


def git_toplevel(root: Path) -> Path | None:
    """Return the enclosing Git worktree root, or None (no git / not a repo)."""
    proc = run_git(root, "rev-parse", "--show-toplevel")
    if proc is None or proc.returncode != 0:
        return None
    return Path(proc.stdout.strip()).resolve()


def list_files(root: Path, config: dict) -> tuple[list[str], str]:
    """List project files as project-relative POSIX paths.

    Inside a Git worktree, tracked and untracked-but-not-ignored files are used
    so that .gitignore is honored. Otherwise the directory tree is walked.
    Returns (paths, source) where source is "git" or "filesystem".
    """
    root = root.resolve()
    if git_toplevel(root) is not None:
        proc = run_git(root, "ls-files", "-z", "--cached", "--others", "--exclude-standard")
        if proc is not None and proc.returncode == 0:
            seen: set[str] = set()
            files: list[str] = []
            for rel in proc.stdout.split("\0"):
                if not rel or rel in seen:
                    continue
                seen.add(rel)
                if not (root / rel).is_file():  # deleted in the worktree
                    continue
                if not excluded(rel, config):
                    files.append(rel)
            return sorted(files), "git"

    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        current = Path(dirpath)
        rel_dir = current.relative_to(root).as_posix()
        rel_dir = "" if rel_dir == "." else rel_dir + "/"
        dirnames[:] = sorted(d for d in dirnames if not excluded(rel_dir + d, config, is_dir=True))
        for name in sorted(filenames):
            rel = rel_dir + name
            if not excluded(rel, config):
                files.append(rel)
    return files, "filesystem"


# --------------------------------------------------------------------------
# Change detection
# --------------------------------------------------------------------------

def _parse_name_status(output: str) -> list[Change]:
    tokens = output.split("\0")
    changes: list[Change] = []
    i = 0
    while i < len(tokens):
        status = tokens[i]
        if not status:
            i += 1
            continue
        code = status[0]
        if code in ("R", "C"):
            old, new = tokens[i + 1], tokens[i + 2]
            changes.append(Change(new, code, old))
            i += 3
        else:
            changes.append(Change(tokens[i + 1], code, None))
            i += 2
    return changes


def comparison_rev(root: Path, base: str | None = None) -> str | None:
    """The commit the worktree is compared with: HEAD, merge-base(BASE, HEAD), or None if unborn."""
    if base:
        mb = run_git(root, "merge-base", base, "HEAD")
        if mb is None or mb.returncode != 0:
            raise GitError(f"cannot find merge base of {base!r} and HEAD: "
                           f"{(mb.stderr.strip() if mb else '') or 'unknown revision'}")
        return mb.stdout.strip()
    head = run_git(root, "rev-parse", "--verify", "-q", "HEAD")
    return "HEAD" if head is not None and head.returncode == 0 else None


def file_at(root: Path, rev: str, relative: str) -> str | None:
    """Content of a root-relative path at a commit, or None."""
    proc = run_git(root, "show", f"{rev}:./{relative}")
    return proc.stdout if proc is not None and proc.returncode == 0 else None


def changed_files(root: Path, base: str | None = None) -> list[Change]:
    """Changes in the worktree relative to HEAD (or to merge-base(BASE, HEAD)).

    Includes staged, unstaged, and untracked (not ignored) files. Paths are
    relative to ``root``, and only changes under ``root`` are reported, so
    ``root`` may be a subdirectory of a monorepo.
    """
    if git_toplevel(root) is None:
        if run_git(root, "--version") is None:
            raise GitError("git is not installed")
        raise GitError(f"not inside a Git worktree: {root}")

    diff_opts = ["diff", "--name-status", "-z", "-M", "--relative"]
    rev = comparison_rev(root, base)
    if rev is not None:
        proc = run_git(root, *diff_opts, rev)
    else:  # unborn branch: everything staged is new
        proc = run_git(root, *diff_opts, "--cached")
    if proc is None or proc.returncode != 0:
        raise GitError((proc.stderr.strip() if proc else "") or "git diff failed")

    by_path: dict[str, Change] = {c.path: c for c in _parse_name_status(proc.stdout)}
    untracked = run_git(root, "ls-files", "-z", "--others", "--exclude-standard")
    if untracked is not None and untracked.returncode == 0:
        for rel in untracked.stdout.split("\0"):
            if rel and rel not in by_path:
                by_path[rel] = Change(rel, "A", None)
    return sorted(by_path.values(), key=lambda c: c.path)


# --------------------------------------------------------------------------
# Classification
# --------------------------------------------------------------------------

DOC_SUFFIXES = {".md", ".mdx", ".markdown", ".rst", ".adoc", ".asciidoc"}
DOC_DIRS = {"docs", "doc", "documentation", "handbook", "manual", "guides", "wiki"}
DOC_STEMS = {
    "readme", "changelog", "changes", "history", "news", "release_notes",
    "release-notes", "releasenotes", "contributing", "authors", "notice",
    "license", "licence", "copying", "security", "code_of_conduct", "citation",
}
CHANGELOG_STEMS = {"changelog", "changes", "history", "news", "release_notes", "release-notes", "releasenotes"}
CHANGELOG_DIRS = {"changelog.d", "changes", ".changeset", "newsfragments", "releasenotes"}

DECISION_DIRS = {"adr", "adrs", "decisions", "decision-records", "decision_records", "architecture-decisions"}
DECISION_NAME_RE = re.compile(r"^adr[-_ ]?\d")

SPEC_DIRS = {"specs", "specification", "specifications", "schema", "schemas", "openapi", "asyncapi", "proto", "protos"}
SPEC_SUFFIXES = {".proto", ".avsc", ".graphql", ".gql", ".thrift", ".xsd", ".wsdl", ".smithy"}
SPEC_STEMS = {"openapi", "asyncapi", "swagger"}

EVIDENCE_DIRS = {"test", "tests", "testing", "__tests__", "spec", "e2e", "benchmark", "benchmarks", "bench", "validation"}
EVIDENCE_NAME_RE = re.compile(
    r"(^test_.*\.py$)|(_test\.(py|go|rs|exs?)$)|(\.(test|spec)\.[cm]?[jt]sx?$)|(_spec\.rb$)"
    r"|(\.feature$)"
)
# Case-sensitive: FooTest.java / FooTests.cs, but not latest.java.
EVIDENCE_CLASS_RE = re.compile(r"[a-z0-9]Tests?\.(java|kt|cs)$")

GENERATED_DIRS = {"generated", "gen", "__generated__", "_generated"}
GENERATED_NAME_RE = re.compile(r"(_pb2(_grpc)?\.py$)|(\.pb\.go$)|(\.g\.dart$)|(\.generated\.\w+$)|(\.min\.(js|css)$)")

INFRA_NAMES = {
    "dockerfile", "containerfile", "docker-compose.yml", "docker-compose.yaml",
    "compose.yml", "compose.yaml", "jenkinsfile", ".gitlab-ci.yml", "procfile",
    "vagrantfile", "azure-pipelines.yml", "bitbucket-pipelines.yml", ".travis.yml",
    "cloudbuild.yaml", "skaffold.yaml", "chart.yaml",
}
INFRA_SUFFIXES = {".tf", ".tfvars", ".hcl", ".bicep", ".nomad"}
INFRA_DIRS = {".circleci", ".buildkite", "terraform", "infra", "infrastructure",
              "deploy", "deployment", "deployments", "k8s", "kubernetes", "helm",
              "charts", "ansible"}

CONFIG_NAMES = {
    "pyproject.toml", "setup.cfg", "setup.py", "pipfile", "pipfile.lock",
    "poetry.lock", "uv.lock", "package.json", "package-lock.json", "yarn.lock",
    "pnpm-lock.yaml", "go.mod", "go.sum", "cargo.toml", "cargo.lock", "pom.xml",
    "build.gradle", "build.gradle.kts", "settings.gradle", "settings.gradle.kts",
    "gemfile", "gemfile.lock", "composer.json", "composer.lock", "makefile",
    "cmakelists.txt", ".env.example", ".editorconfig", "tox.ini", "noxfile.py",
    ".pre-commit-config.yaml", "mkdocs.yml", "mkdocs.yaml", "docusaurus.config.js",
    "docusaurus.config.ts", "conf.py",
}
CONFIG_NAME_RE = re.compile(r"(^requirements.*\.(txt|in)$)|(^tsconfig.*\.json$)|(^\.env\.[\w.-]+\.example$)")
CONFIG_SUFFIXES = {".ini", ".cfg", ".conf", ".toml", ".properties"}
CONFIG_DIRS = {"config", "configs", "conf", "settings", ".config"}


RECORD_STATUS_RES = (
    re.compile(r"^\s*(?:[-*]\s*)?status\s*:\s*[\"']?([A-Za-z]+)", re.IGNORECASE | re.MULTILINE),
    re.compile(r"^#+\s*status\s*\n+\s*([A-Za-z]+)", re.IGNORECASE | re.MULTILINE),
)
# Lines whose change does not alter a record's substance: lifecycle metadata and supersession links.
RECORD_METADATA_RE = re.compile(r"^\s*(?:[-*]\s*)?(status|date|superseded[ -]by|supersedes)\b|supersed",
                                re.IGNORECASE)


def record_status(text: str) -> str | None:
    """Lower-case status of a decision record (front matter, bullet, or Status section)."""
    for regex in RECORD_STATUS_RES:
        m = regex.search(text)
        if m:
            return m.group(1).lower()
    return None


def substance_changed(old: str, new: str) -> bool:
    """True if a record changed beyond whitespace, status, dates, and added links.

    Removed or rewritten lines count as substance unless they are lifecycle
    metadata. Added lines are allowed when they are metadata, headings, or
    links (for example a "More Information" section pointing at the record
    that supersedes this one).
    """
    import difflib
    a = [line.strip() for line in old.splitlines() if line.strip()]
    b = [line.strip() for line in new.splitlines() if line.strip()]
    for line in difflib.unified_diff(a, b, lineterm="", n=0):
        if line.startswith(("---", "+++", "@@")):
            continue
        sign, body = line[0], line[1:]
        if RECORD_METADATA_RE.search(body):
            continue
        if sign == "+" and (body.startswith("#") or "](" in body or "://" in body):
            continue
        return True
    return False


def is_changelog(relative: str) -> bool:
    p = PurePosixPath(relative.lower())
    stem = p.name.split(".", 1)[0]
    return stem in CHANGELOG_STEMS or any(part in CHANGELOG_DIRS for part in p.parts[:-1])


def classify(relative: str, config: dict) -> set[str]:
    """Classify a project-relative path into artifact categories.

    If any project-configured *_globs pattern matches, the configured
    categories replace the built-in heuristics for that file, so projects can
    correct false positives.
    """
    custom = {c for c in CATEGORIES if match_any(relative, config.get(f"{c}_globs", []))}
    if custom:
        return custom

    p = PurePosixPath(relative.lower())
    name, suffix = p.name, p.suffix
    stem = name.split(".", 1)[0]
    dirs = set(p.parts[:-1])
    posix = p.as_posix()
    cats: set[str] = set()

    if suffix in DOC_SUFFIXES or (stem in DOC_STEMS and suffix in {"", ".txt"}):
        cats.add("documentation")
    if dirs & DOC_DIRS and suffix in DOC_SUFFIXES | {".txt", ".png", ".svg", ".drawio", ".puml", ".mmd"}:
        cats.add("documentation")

    if dirs & DECISION_DIRS or DECISION_NAME_RE.match(name):
        cats.add("decision")

    if (dirs & SPEC_DIRS or suffix in SPEC_SUFFIXES or name.endswith(".schema.json")
            or (stem in SPEC_STEMS and suffix in {".yaml", ".yml", ".json"})):
        cats.add("specification")

    if dirs & EVIDENCE_DIRS or EVIDENCE_NAME_RE.search(name) or EVIDENCE_CLASS_RE.search(PurePosixPath(relative).name):
        cats.add("evidence")

    if dirs & GENERATED_DIRS or GENERATED_NAME_RE.search(name):
        cats.add("generated")

    if (name in INFRA_NAMES or name.startswith("dockerfile.") or suffix in INFRA_SUFFIXES
            or dirs & INFRA_DIRS or posix.startswith(".github/workflows/")
            or "/.github/workflows/" in posix):
        cats.add("infrastructure")

    if (name in CONFIG_NAMES or CONFIG_NAME_RE.search(name) or suffix in CONFIG_SUFFIXES
            or (dirs & CONFIG_DIRS and suffix in {".yaml", ".yml", ".json", ".toml", ".ini", ".env"})):
        cats.add("configuration")

    if not cats:
        cats.add("implementation")
    return cats
