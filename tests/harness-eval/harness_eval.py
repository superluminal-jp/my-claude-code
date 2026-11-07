#!/usr/bin/env python3
"""Check, build, run, and compare the whole-harness behavior baseline.

The harness is what install.sh puts in ~/.claude: .claude/CLAUDE.md, the
rules, and the skills. This script measures it as a whole with
`claude plugin eval`:

  check    the capability map (docs/harness/capability-map.json) and the
           scenario suite (tests/harness-eval/scenarios.json) against the
           working tree; no model call.
  render   write docs/harness/capability-map.md from the map and the suite.
  run      build the harness as one plugin from two git commits (the harness
           and the suite, each from git, never from the working tree) in a
           temporary directory, validate it, and run the suite. --dry-run
           stops before the first model call.
  compare  per-case score differences between two results.

Standard library only. See docs/harness-eval.md (spec 066).
"""

from __future__ import annotations

import argparse
import io
import json
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

MAP_PATH = "docs/harness/capability-map.json"
MAP_MD_PATH = "docs/harness/capability-map.md"
SUITE_PATH = "tests/harness-eval/scenarios.json"
FIXTURE_DIR = "tests/harness-eval/fixtures"
SUITE_PATHS = ("docs/harness", "tests/harness-eval")
RESULTS_DIR = "tests/harness-eval/results"

# Claude Code caps a hook's plain stdout at 10,000 characters and replaces a
# longer one with a file path and a 2,000-character preview (hooks reference).
HOOK_OUTPUT_CAP = 10_000
PLUGIN_NAME = "harness"
KINDS = ("expectation", "observation", "probe")
DEFAULT_TOOLS = ["Read", "Glob", "Grep", "Skill", "AskUserQuestion", "TodoWrite"]
DEFAULT_MAX_TURNS = 12
DEFAULT_TIMEOUT = 600
JAPANESE = re.compile(r"[぀-ヿ㐀-鿿＀-￯]")
SKILL_NAME = re.compile(r"^[a-z0-9][a-z0-9-]*$")
CASE_ID = re.compile(r"^[a-z0-9][a-z0-9-]*$")
# Every fixture starts with this line, so a fixture started anywhere but an
# empty directory (the eval's fresh workspace) stops before writing a file.
FIXTURE_GUARD = '[ -z "$(ls -A .)" ] || { echo "fixture: run me in an empty directory" >&2; exit 1; }'
# claude plugin eval runs a scaffold script as the user, outside the agent's
# OS sandbox. A fixture is therefore data (fixtures/<name>.json), and the
# script is generated from it by render_scaffold(). As a second line of
# defense the generated script must also use only these commands, outside
# heredoc bodies.
FIXTURE_COMMANDS = {"set", "cat", "printf", "mkdir", "git", "chmod"}
FIXTURE_GIT = {"init", "checkout", "add", "commit"}
HEREDOC = re.compile(r"<<-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1")
FIXTURE_KEYS = {"schema_version", "description", "files", "commit", "after_commit"}
PATH_PART = re.compile(r"^[A-Za-z0-9._-]+$")
# A path part that would let git run code or change what git runs, compared
# in lower case because the default macOS file system ignores letter case.
FORBIDDEN_PARTS = {".", "..", ".git", ".gitattributes", ".gitmodules"}
GIT_SAFE = "-c core.hooksPath=/dev/null"
GIT_IDENTITY = GIT_SAFE + " -c user.email=eval@example.invalid -c user.name=eval"
# Tools a scenario may list; anything else is granted only by eval_command.
READ_ONLY_TOOLS = {"Read", "Glob", "Grep", "NotebookRead", "Skill", "AskUserQuestion", "TodoWrite"}


class BuildError(Exception):
    """The harness or suite cannot be built into a plugin for evaluation."""


@dataclass
class Built:
    plugin_dir: Path
    harness_commit: str
    suite_commit: str
    case_count: int
    harness_ref: str
    suite_ref: str
    # Where the suite, written for its own commit, no longer matches the
    # harness commit (a component or a quoted phrase it lacks). Recorded, not fatal.
    drift: list[str] = field(default_factory=list)
    probe_cases: list[str] = field(default_factory=list)
    case_ids: list[str] = field(default_factory=list)


# --------------------------------------------------------------------- helpers


def skill_pattern(name: str) -> str:
    """Regex over a Skill tool input's JSON that matches `name`, bare or namespaced."""
    if not SKILL_NAME.match(name):
        raise ValueError(f"not a skill name: {name!r}")
    return r'"skill"\s*:\s*"(?:[\w-]+:)?' + name + '"'


def squash(text: str) -> str:
    return " ".join(text.split())


def read_text(root: Path, rel: str) -> str | None:
    path = root / rel
    return path.read_text(encoding="utf-8") if path.is_file() else None


def harness_components(root: Path, files: list[str] | None = None) -> dict[str, str]:
    """Map component id to path for the harness under `root`."""
    if files is None:
        base = root / ".claude"
        files = [p.relative_to(root).as_posix() for p in base.rglob("*") if p.is_file()] if base.is_dir() else []
    found: dict[str, str] = {}
    for rel in files:
        parts = rel.split("/")
        if rel == ".claude/CLAUDE.md":
            found["apex"] = rel
        elif len(parts) >= 3 and parts[1] == "rules" and rel.endswith(".md"):
            found["rule:" + "/".join(parts[2:])[:-3]] = rel
        elif len(parts) == 4 and parts[1] == "skills" and parts[3] == "SKILL.md":
            found["skill:" + parts[2]] = rel
    return found


def declared_children(skill_text: str) -> list[str]:
    """Names listed as - `name` in a SKILL.md's ## Child skills section, outside fences."""
    names, in_section, fence = [], False, None
    for line in skill_text.splitlines():
        stripped = line.strip()
        marker = re.match(r"^(`{3,}|~{3,})", stripped)
        if fence:
            if marker and marker.group(1)[0] == fence[0] and len(marker.group(1)) >= len(fence):
                fence = None
            continue
        if marker:
            fence = marker.group(1)
            continue
        if line.startswith("## "):
            in_section = stripped == "## Child skills"
            continue
        m = re.match(r"^- `([a-z0-9][a-z0-9-]*)`\s*$", stripped)
        if in_section and m:
            names.append(m.group(1))
    return names


def parse_frontmatter(text: str) -> dict:
    """Read frontmatter this script wrote: one `key: <JSON value>` per line."""
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("no frontmatter")
    out = {}
    for line in lines[1:]:
        if line == "---":
            return out
        key, _, value = line.partition(": ")
        out[key] = json.loads(value)
    raise ValueError("unterminated frontmatter")


def frontmatter(fields: dict) -> str:
    # A JSON value is also a valid YAML flow value, so each line is valid YAML.
    body = "".join(f"{k}: {json.dumps(v, ensure_ascii=True)}\n" for k, v in fields.items())
    return "---\n" + body + "---\n"


# ----------------------------------------------------------------------- check


def fixture_data_violations(data) -> list[str]:
    """Why fixture data could write outside its workspace or make git run code."""
    if not isinstance(data, dict):
        return ["fixture data must be an object"]
    out = [f"unknown key {k!r}" for k in sorted(set(data) - FIXTURE_KEYS)]
    if data.get("schema_version") != 1:
        out.append("schema_version must be 1")
    if not isinstance(data.get("commit", False), bool):
        out.append("commit must be true or false")
    if not data.get("files"):
        out.append("files must name at least one file")
    for key in ("files", "after_commit"):
        files = data.get(key, {})
        if not isinstance(files, dict):
            out.append(f"{key} must map paths to contents")
            continue
        for path, content in files.items():
            parts = path.split("/") if isinstance(path, str) else []
            if not parts or any(not PATH_PART.match(part) or part.lower() in FORBIDDEN_PARTS for part in parts):
                out.append(f"{key}: unsafe path {path!r}")
            if not isinstance(content, str) or not content.endswith("\n"):
                out.append(f"{key}: {path!r} must be text that ends with a newline")
    return out


def _write_files(files: dict) -> list[str]:
    lines = []
    for path in sorted(files):
        content = files[path]
        parent = path.rpartition("/")[0]
        if parent:
            lines.append(f"mkdir -p -- '{parent}'")
        body = content[:-1].split("\n")
        delimiter, n = "FIXTURE_EOF", 0
        while delimiter in body:
            n += 1
            delimiter = f"FIXTURE_EOF_{n}"
        lines += [f"cat > '{path}' <<'{delimiter}'", *body, delimiter]
    return lines


def render_scaffold(data: dict) -> str:
    """The scaffold script for valid fixture data. Paths are validated, every
    heredoc is quoted, and git never runs a hook."""
    lines = ["#!/usr/bin/env bash",
             "# Generated by tests/harness-eval/harness_eval.py from fixture data; do not edit.",
             "set -euo pipefail", FIXTURE_GUARD]
    lines += _write_files(data["files"])
    if data.get("commit"):
        lines += [f"git {GIT_SAFE} -c init.templateDir= init -q", f"git {GIT_SAFE} checkout -q -b main",
                  f"git {GIT_IDENTITY} add -A",
                  f"git {GIT_IDENTITY} -c commit.gpgsign=false commit -qm initial"]
    lines += _write_files(data.get("after_commit", {}))
    return "\n".join(lines) + "\n"


def fixture_violations(text: str) -> list[str]:
    """Why a fixture script could do more than write files into its workspace."""
    out: list[str] = []
    terminator = None
    seen_command = False
    for n, raw in enumerate(text.splitlines(), start=1):
        if terminator is not None:
            if raw == terminator:
                terminator = None
            continue
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line == FIXTURE_GUARD:
            if seen_command:
                out.append(f"line {n}: the empty-directory guard must be the first command after set")
            seen_command = True
            continue
        words = line.split()
        if words[0] == "set":
            continue
        if not seen_command:
            out.append(f"line {n}: the first command after set must be the empty-directory guard")
        seen_command = True
        if words[0] not in FIXTURE_COMMANDS:
            out.append(f"line {n}: {words[0]} is not an allowed fixture command")
        code = HEREDOC.sub("", line)
        stripped = re.sub(r"'[^']*'", "''", code)
        if re.search(r"\$\(|`|\||;|&", stripped):
            out.append(f"line {n}: command substitution, pipes, ; and & are not allowed")
        for target in re.findall(r">>?\s*(\S+)", stripped):
            if target.startswith(("/", "~")) or ".." in target.split("/"):
                out.append(f"line {n}: writes outside the workspace: {target}")
        if words[0] == "git":
            rest = words[1:]
            while rest and rest[0] in ("-c", "-q"):
                rest = rest[2:] if rest[0] == "-c" else rest[1:]
            if not rest or rest[0] not in FIXTURE_GIT:
                out.append(f"line {n}: git {rest[0] if rest else ''} is not an allowed git subcommand")
        m = HEREDOC.search(line)
        if m:
            terminator = m.group(2)
    if terminator is not None:
        out.append(f"heredoc {terminator} is never closed")
    if not seen_command:
        out.append("no empty-directory guard")
    return out


def _check_basis(where: str, basis, harness: Path, allowed: set[str] | None, out: list[str]) -> None:
    items = basis if isinstance(basis, list) else [basis]
    if not items or any(not isinstance(b, dict) for b in items):
        out.append(f"{where}: needs a basis with file and quote")
        return
    for b in items:
        file, quote = b.get("file"), b.get("quote")
        if not isinstance(file, str) or not isinstance(quote, str) or not quote.strip():
            out.append(f"{where}: basis needs a file and a non-empty quote")
            continue
        if allowed is not None and file not in allowed:
            out.append(f"{where}: basis file {file} is not an owner of its stages, a cited source of them, or the apex")
            continue
        text = read_text(harness, file)
        if text is None:
            out.append(f"{where}: basis file {file} does not exist")
        elif squash(quote) not in squash(text):
            out.append(f"{where}: quote not found in {file}: {quote!r}")


def _check_examples(where: str, pattern: str, flags: str, examples, out: list[str]) -> None:
    try:
        rx = re.compile(pattern, re.IGNORECASE if "i" in (flags or "") else 0)
    except re.error as exc:
        out.append(f"{where}: invalid pattern: {exc}")
        return
    if not isinstance(examples, dict) or not examples.get("match") or not examples.get("no_match"):
        out.append(f"{where}: needs examples with at least one match and one no_match")
        return
    for ex in examples["match"]:
        if not rx.search(ex):
            out.append(f"{where}: pattern does not match its example {ex!r}")
    for ex in examples["no_match"]:
        if rx.search(ex):
            out.append(f"{where}: pattern matches its no_match example {ex!r}")


def check_map(cmap: dict, harness: Path, files: list[str] | None, out: list[str]) -> dict:
    actual = harness_components(harness, files)
    comps = {c.get("id"): c for c in cmap.get("components", []) if isinstance(c, dict)}
    for cid, path in sorted(actual.items()):
        if cid not in comps:
            out.append(f"component {cid} ({path}) is missing from the map")
        elif comps[cid].get("path") != path:
            out.append(f"component {cid}: path should be {path}")
    for cid, comp in sorted(comps.items()):
        if cid not in actual:
            out.append(f"map names {cid} but {comp.get('path')} does not exist")
    for cid, comp in sorted(comps.items()):
        if not str(cid).startswith("skill:") or cid not in actual:
            continue
        declared = sorted("skill:" + n for n in declared_children(read_text(harness, actual[cid]) or ""))
        if sorted(comp.get("children", [])) != declared:
            out.append(f"component {cid}: children must be {declared}, as its ## Child skills section declares")

    for cid, comp in sorted(comps.items()):
        if "in_eval" in comp and (comp["in_eval"] is not False or not str(comp.get("reason", "")).strip()):
            out.append(f"component {cid}: in_eval false needs a reason (and only false may be given)")
    owned = set()
    stages = {}
    for st in cmap.get("stages", []):
        sid = st.get("id")
        if sid in stages:
            out.append(f"stage {sid} is defined twice")
        stages[sid] = st
        owners = st.get("owners", [])
        gap = st.get("gap") is True
        if bool(owners) == gap:
            out.append(f"stage {sid}: give either owners or gap: true, not both or neither")
        for o in owners:
            if o not in comps:
                out.append(f"stage {sid}: owner {o} is not a map component")
            owned.add(o)
        if "unobservable" in st and not (isinstance(st["unobservable"], str) and st["unobservable"].strip()):
            out.append(f"stage {sid}: unobservable needs a reason")
        _check_basis(f"stage {sid}", st.get("basis", []), harness, None, out)
    for cid in sorted(set(comps) - owned):
        out.append(f"component {cid} owns no stage")
    if not any(st.get("requires_unused_skill_grader") for st in stages.values()):
        out.append("no stage sets requires_unused_skill_grader, so over-application is never checked")

    for g in cmap.get("boundary_groups", []):
        gid, members = g.get("id"), g.get("members", [])
        if len(members) < 2 or any(m not in comps or not m.startswith("skill:") for m in members):
            out.append(f"boundary group {gid}: needs two or more skill components of the map")
        _check_basis(f"boundary group {gid}", g.get("basis", []), harness, None, out)

    settings_text = read_text(harness, ".claude/settings.json")
    classified = cmap.get("settings", {})
    if settings_text is not None:
        for key in json.loads(settings_text):
            entry = classified.get(key)
            if not isinstance(entry, dict) or not isinstance(entry.get("in_eval"), bool) \
                    or not str(entry.get("reason", "")).strip():
                out.append(f"settings.json key {key!r} is not classified as in or out of the eval with a reason")
    return {"components": comps, "stages": stages, "actual": actual}


def scenario_graders_by_skill(sc: dict, expect: str) -> set[str]:
    return {"skill:" + g["skill"] for g in sc.get("graders", [])
            if g.get("type") == "skill" and g.get("expect") == expect and isinstance(g.get("skill"), str)}


def check_suite(suite: dict, cmap: dict, info: dict, harness: Path, suite_root: Path, out: list[str]) -> None:
    comps, stages, actual = info["components"], info["stages"], info["actual"]
    skills = sorted(c[len("skill:"):] for c in actual if c.startswith("skill:"))
    always_on = {p for c, p in actual.items() if c == "apex" or c.startswith("rule:")}
    apex_path = actual.get("apex")
    scenarios = suite.get("scenarios", [])
    seen = set()
    for sc in scenarios:
        sid = sc.get("id")
        where = f"scenario {sid}"
        if not isinstance(sid, str) or not CASE_ID.match(sid) or sid in seen:
            out.append(f"{where}: id must be unique kebab-case")
        seen.add(sid)
        kind = sc.get("kind")
        if kind not in KINDS:
            out.append(f"{where}: kind must be one of {KINDS}")
        sc_stages = sc.get("stages", [])
        for st in sc_stages:
            if st not in stages:
                out.append(f"{where}: names stage {st}, which is not in the map")
        if kind != "probe" and not sc_stages:
            out.append(f"{where}: names no stage")
        tools = sc.get("allowed_tools", DEFAULT_TOOLS)
        if not isinstance(tools, list) or any(tool not in READ_ONLY_TOOLS for tool in tools):
            extra = sorted(set(tools) - READ_ONLY_TOOLS) if isinstance(tools, list) else tools
            out.append(f"{where}: allowed_tools may list only read-only tools; not {extra}")
        if not JAPANESE.search(sc.get("prompt", "")):
            out.append(f"{where}: the prompt must be written in Japanese")
        if kind == "probe":
            allowed = always_on
        else:
            allowed = {apex_path} if apex_path else set()
            for st in sc_stages:
                stage = stages.get(st, {})
                allowed |= {comps[o].get("path") for o in stage.get("owners", []) if o in comps}
                allowed |= {b.get("file") for b in stage.get("basis", []) if isinstance(b, dict)}
            # A boundary group's basis records why its members exclude one
            # another, so it may justify asserting a member unused.
            expected = scenario_graders_by_skill(sc, "used")
            for g in cmap.get("boundary_groups", []):
                if expected & set(g.get("members", [])):
                    allowed |= {b.get("file") for b in g.get("basis", []) if isinstance(b, dict)}
        graders = sc.get("graders", [])
        if not graders:
            out.append(f"{where}: needs at least one grader")
        gids = set()
        for g in graders:
            gid = g.get("id")
            gwhere = f"{where} grader {gid}"
            if not isinstance(gid, str) or not CASE_ID.match(gid) or gid in gids:
                out.append(f"{gwhere}: id must be unique kebab-case within the scenario")
            gids.add(gid)
            _check_basis(gwhere, g.get("basis"), harness, allowed, out)
            gtype = g.get("type")
            if gtype == "skill":
                name = g.get("skill")
                if name not in skills:
                    out.append(f"{gwhere}: {name!r} is not a skill of the harness")
                    continue
                if g.get("expect") == "used" and comps.get("skill:" + name, {}).get("in_eval") is False:
                    out.append(f"{gwhere}: skill {name} is left out of the eval, so it can never be used there")
                if g.get("expect") not in ("used", "unused"):
                    out.append(f"{gwhere}: expect must be used or unused")
                rx = re.compile(skill_pattern(name))
                if not (rx.search(json.dumps({"skill": name}, separators=(",", ":")))
                        and rx.search(json.dumps({"skill": f"{PLUGIN_NAME}:{name}"}))):
                    out.append(f"{gwhere}: pattern misses the skill's own name")
                for other in skills:
                    if other != name and rx.search(json.dumps({"skill": f"{PLUGIN_NAME}:{other}"})):
                        out.append(f"{gwhere}: pattern also matches {other}")
            elif gtype == "tool":
                if not isinstance(g.get("tool"), str) or not isinstance(g.get("input_match"), str):
                    out.append(f"{gwhere}: needs tool and input_match")
                    continue
                _check_examples(gwhere, g["input_match"], "", g.get("examples"), out)
            elif gtype == "tool_order":
                for side in ("before", "after"):
                    s = g.get(side)
                    if not isinstance(s, dict) or not isinstance(s.get("tool"), str) \
                            or not isinstance(s.get("input_match"), str):
                        out.append(f"{gwhere}: {side} needs tool and input_match")
                        continue
                    _check_examples(f"{gwhere} {side}", s["input_match"], "", s.get("examples"), out)
            elif gtype == "regex":
                if not isinstance(g.get("pattern"), str):
                    out.append(f"{gwhere}: needs a pattern")
                    continue
                _check_examples(gwhere, g["pattern"], g.get("flags", ""), g.get("examples"), out)
            else:
                out.append(f"{gwhere}: type must be skill, tool, tool_order, or regex")
        fixture = sc.get("fixture")
        if fixture is not None:
            text = read_text(suite_root, f"{FIXTURE_DIR}/{fixture}.json")
            if text is None:
                out.append(f"{where}: fixture {fixture} does not exist as {FIXTURE_DIR}/{fixture}.json")
            else:
                try:
                    data = json.loads(text)
                except ValueError as exc:
                    out.append(f"{where}: fixture {fixture} is not JSON: {exc}")
                    continue
                problems = fixture_data_violations(data)
                if not problems:
                    problems = fixture_violations(render_scaffold(data))
                for v in problems:
                    out.append(f"{where}: fixture {fixture}: {v}")

    probed = {g.get("basis", {}).get("file") for s in scenarios if s.get("kind") == "probe"
              for g in s.get("graders", []) if g.get("type") == "regex" and isinstance(g.get("basis"), dict)}
    for path in sorted(always_on - probed):
        out.append(f"the probe does not check that {path} reached the model")

    expectation = [s for s in scenarios if s.get("kind") == "expectation"]
    observation = [s for s in scenarios if s.get("kind") == "observation"]
    for sid, st in stages.items():
        if "unobservable" in st:
            continue
        pool, label = (observation, "observation") if st.get("gap") else (expectation, "expectation")
        if not any(sid in s.get("stages", []) for s in pool):
            out.append(f"stage {sid} has no {label} scenario")
        if st.get("requires_unused_skill_grader") and not any(
                sid in s.get("stages", []) and scenario_graders_by_skill(s, "unused") for s in expectation):
            out.append(f"stage {sid} needs an expectation scenario that asserts a skill is not used")

    children = {cid: set(c.get("children", [])) for cid, c in comps.items()}
    for sc in expectation:
        expected = scenario_graders_by_skill(sc, "used")
        unused = scenario_graders_by_skill(sc, "unused")
        exempt = set().union(*(children.get(e, set()) for e in expected)) if expected else set()
        for g in cmap.get("boundary_groups", []):
            members = set(g.get("members", []))
            for m in sorted(expected & members):
                for o in sorted(members - {m} - exempt - expected):
                    if o not in unused:
                        out.append(f"scenario {sc.get('id')} expects {m} of {g.get('id')} "
                                   f"and must also assert {o} unused")
    compound = [s for s in expectation if len(s.get("stages", [])) >= 2]
    if len(compound) < 3:
        out.append(f"only {len(compound)} compound expectation scenarios; need at least 3")


def check(harness: Path, suite_root: Path, files: list[str] | None = None, check_render: bool = False) -> list[str]:
    """Every violation of the map and suite rules; an empty list means none."""
    out: list[str] = []
    try:
        cmap = json.loads((suite_root / MAP_PATH).read_text(encoding="utf-8"))
        suite = json.loads((suite_root / SUITE_PATH).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return [f"cannot read the map or the suite: {exc}"]
    info = check_map(cmap, harness, files, out)
    check_suite(suite, cmap, info, harness, suite_root, out)
    if check_render:
        current = read_text(suite_root, MAP_MD_PATH)
        if current != render_map(cmap, suite):
            out.append(f"{MAP_MD_PATH} is stale; run: python3 tests/harness-eval/harness_eval.py render")
    return out


# ---------------------------------------------------------------------- render

BRANCH_LABEL = {"define": "定義", "execute": "実行", "handoff": "引き渡し"}


def render_map(cmap: dict, suite: dict) -> str:
    scenarios = suite.get("scenarios", [])

    def covering(sid: str) -> str:
        names = [s["id"] for s in scenarios if sid in s.get("stages", [])]
        return ", ".join(f"`{n}`" for n in names) if names else "—"

    lines = [
        "# harness の受け持ちの対応表",
        "",
        f"この文書は `{MAP_PATH}` と `{SUITE_PATH}` から `tests/harness-eval/harness_eval.py render` が生成する。"
        "手で編集しない。正本は JSON で、`harness_eval.py check` が実在の部品・引用・シナリオとの整合を検査する。",
        "",
        "## 段階と担い手",
        "",
        "| 段階 | 枝 | 内容 | 担い手 | シナリオ |",
        "|---|---|---|---|---|",
    ]
    for st in cmap.get("stages", []):
        if st.get("gap"):
            owners = "**担い手なし**"
        else:
            owners = ", ".join(f"`{o}`" for o in st.get("owners", []))
        note = f"（観測しない: {st['unobservable']}）" if "unobservable" in st else ""
        lines.append(f"| `{st['id']}` | {BRANCH_LABEL.get(st.get('branch'), st.get('branch'))} | "
                     f"{st.get('title', '')}{note} | {owners} | {covering(st['id'])} |")
    lines += ["", "## 境界グループ", "",
              "同じグループのスキルは互いの description で除外し合う。グループのスキルを期待するシナリオは、"
              "他のメンバー（期待するスキルが宣言した子を除く）が使われないことも判定する。", ""]
    for g in cmap.get("boundary_groups", []):
        lines.append(f"- `{g['id']}`: " + ", ".join(f"`{m}`" for m in g.get("members", [])))
    left_out = [c for c in cmap.get("components", []) if c.get("in_eval") is False]
    if left_out:
        lines += ["", "## 評価に含めないスキル", "", "| スキル | 理由 |", "|---|---|"]
        lines += [f"| `{c['id']}` | {c.get('reason', '')} |" for c in left_out]
    lines += ["", "## settings.json の扱い", "", "| 項目 | 評価に含めるか | 理由 |", "|---|---|---|"]
    for key, entry in cmap.get("settings", {}).items():
        lines.append(f"| `{key}` | {'含める' if entry.get('in_eval') else '含めない'} | {entry.get('reason', '')} |")
    counts = {k: sum(1 for s in scenarios if s.get("kind") == k) for k in KINDS}
    lines += ["", "## シナリオの数", "",
              f"期待 {counts['expectation']} 件、観測 {counts['observation']} 件、到達確認 {counts['probe']} 件。", ""]
    return "\n".join(lines)


# ----------------------------------------------------------------------- build


def ensure_outside(path: Path, repo: Path) -> None:
    """Refuse a build directory outside the temp dir, or inside the repository or ~/.claude."""
    p = path.resolve()
    tmp = Path(tempfile.gettempdir()).resolve()
    for forbidden in (repo.resolve(), (Path.home() / ".claude").resolve()):
        if p == forbidden or forbidden in p.parents:
            raise BuildError(f"build directory {p} is inside {forbidden}")
    if p != tmp and tmp not in p.parents:
        raise BuildError(f"build directory {p} is not under the temporary directory {tmp}")


def git_out(repo: Path, *args: str) -> bytes:
    res = subprocess.run(["git", "-C", str(repo), *args], capture_output=True)
    if res.returncode != 0:
        raise BuildError(f"git {' '.join(args)} failed: {res.stderr.decode(errors='replace').strip()}")
    return res.stdout


def resolve(repo: Path, ref: str) -> str:
    return git_out(repo, "rev-parse", "--verify", f"{ref}^{{commit}}").decode().strip()


def extract(repo: Path, sha: str, paths: tuple[str, ...], dest: Path) -> None:
    data = git_out(repo, "archive", "--format=tar", sha, "--", *paths)
    dest.mkdir(parents=True, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(data)) as tar:
        if hasattr(tarfile, "data_filter"):
            tar.extractall(dest, filter="data")
        else:  # Python < 3.12: refuse anything that would land outside dest
            root = dest.resolve()
            for member in tar.getmembers():
                target = (dest / member.name).resolve()
                if root not in target.parents and target != root or member.issym() or member.islnk():
                    raise BuildError(f"unsafe archive member {member.name}")
            tar.extractall(dest)


def always_on(harness: Path) -> list[tuple[str, str]]:
    """(relative path, text) of the apex and the rules, apex first."""
    files = [".claude/CLAUDE.md"] + sorted(
        p.relative_to(harness).as_posix() for p in (harness / ".claude/rules").rglob("*.md"))
    return [(rel, (harness / rel).read_text(encoding="utf-8")) for rel in files if (harness / rel).is_file()]


def render_grader(g: dict) -> dict:
    if g["type"] == "skill":
        fields = {"type": "tool_used", "tool": "Skill", "input_match": skill_pattern(g["skill"])}
        fields.update({"min": 1} if g["expect"] == "used" else {"min": 0, "max": 0})
        return fields
    if g["type"] == "tool":
        fields = {"type": "tool_used", "tool": g["tool"], "input_match": g["input_match"]}
        for key in ("min", "max"):
            if key in g:
                fields[key] = g[key]
        return fields
    if g["type"] == "tool_order":
        return {"type": "tool_order",
                "before": {"tool": g["before"]["tool"], "input_match": g["before"]["input_match"]},
                "after": {"tool": g["after"]["tool"], "input_match": g["after"]["input_match"]}}
    fields = {"type": "regex", "pattern": g["pattern"]}
    if g.get("flags"):
        fields["flags"] = g["flags"]
    target = g.get("target")
    if isinstance(target, dict) and "file" in target:
        fields["target"] = {"source": "file", "path": target["file"]}
    elif target in ("last_message", "trace"):
        fields["target"] = target
    if g.get("match"):
        fields["match"] = g["match"]
    return fields


def build(repo: Path, harness_ref: str, suite_ref: str, out_dir: Path) -> Built:
    """Assemble the harness at `harness_ref` and the suite at `suite_ref` into one plugin."""
    ensure_outside(out_dir, repo)
    harness_sha, suite_sha = resolve(repo, harness_ref), resolve(repo, suite_ref)
    src_h, src_s = out_dir / "src-harness", out_dir / "src-suite"
    extract(repo, harness_sha, (".claude",), src_h)
    extract(repo, suite_sha, SUITE_PATHS + (".claude",), src_s)
    # The suite must hold against the harness it was written for, its own commit.
    violations = check(src_s, src_s)
    if violations:
        raise BuildError("the map or the suite has violations at the suite commit:\n  " + "\n  ".join(violations))
    # Every component at the harness commit must be in the map, or whether it
    # may enter the eval (in_eval) is unknown; fail safe rather than include it.
    cmap = json.loads((src_s / MAP_PATH).read_text(encoding="utf-8"))
    mapped = {c.get("id") for c in cmap.get("components", []) if isinstance(c, dict)}
    unmapped = sorted(set(harness_components(src_h)) - mapped)
    if unmapped:
        raise BuildError(f"the harness commit has components the suite's map does not name: {', '.join(unmapped)}; "
                         "whether they may enter the eval is unknown, so use a suite commit whose map names them")
    # Anything else the harness commit lacks (a component the suite maps, a
    # quoted phrase) is what a before-and-after comparison measures.
    drift = check(src_h, src_s)

    # The plugin's only hooks are the generated ones, which --trust-plugin trusts.
    for found in (src_h / ".claude/skills").rglob("*"):
        declares = found.name == "hooks.json" or (
            found.name == "plugin.json" and "hooks" in json.loads(found.read_text(encoding="utf-8") or "{}"))
        if found.name == "SKILL.md":
            lines = found.read_text(encoding="utf-8").splitlines()
            if lines and lines[0] == "---":
                end = next((i for i, line in enumerate(lines[1:], 1) if line == "---"), len(lines))
                declares = any(re.match(r"^hooks\s*:", line) for line in lines[1:end])
        if declares:
            raise BuildError(f"{found.relative_to(src_h)} declares hooks; the eval would run them as trusted")
    left_out = {c["id"][len("skill:"):] for c in cmap.get("components", [])
                if c.get("id", "").startswith("skill:") and c.get("in_eval") is False}
    plugin = out_dir / PLUGIN_NAME
    (plugin / ".claude-plugin").mkdir(parents=True)
    (plugin / ".claude-plugin/plugin.json").write_text(json.dumps({
        "name": PLUGIN_NAME,
        "description": f"Whole-harness behavior baseline: .claude/ at {harness_sha[:12]}, suite at {suite_sha[:12]}.",
    }, indent=2) + "\n", encoding="utf-8")
    # A skill's own evals/ is test material, not instructions, and its
    # hand-written scaffold scripts would run as the user under --scaffold.
    skills_root = src_h / ".claude/skills"

    def ignore(d: str, names: list[str]) -> list[str]:
        if Path(d) == skills_root:
            return [n for n in names if n in left_out]
        if Path(d).parent == skills_root:
            return [n for n in names if n == "evals"]
        return []

    shutil.copytree(skills_root, plugin / "skills", ignore=ignore)
    stray = sorted(p.relative_to(plugin).as_posix() for p in (plugin / "skills").rglob("case.yaml"))
    if stray:
        raise BuildError(f"eval cases outside the generated evals/ would also run: {', '.join(stray)}")

    (plugin / "context").mkdir()
    hooks = []
    for i, (rel, text) in enumerate(always_on(src_h), start=1):
        if any(re.match(r"^@\S", line) for line in text.splitlines()):
            raise BuildError(f"{rel} imports another file with @; injecting its text would not expand it")
        if rel.startswith(".claude/rules/") and re.match(r"^---\n(?:.*\n)*?paths\s*:", text):
            raise BuildError(f"{rel} is path-scoped; it would not load in every session")
        name = f"{i:02d}-" + rel[len(".claude/"):].replace("/", "-")
        chunk = (f"Contents of ~/{rel} (user's private global instructions for all projects):\n\n{text}")
        if len(chunk) >= HOOK_OUTPUT_CAP:
            raise BuildError(f"{rel} is {len(chunk)} characters with its header; a hook can inject fewer than {HOOK_OUTPUT_CAP}")
        (plugin / "context" / name).write_text(chunk, encoding="utf-8")
        hooks.append({"type": "command", "command": "cat", "args": ["${CLAUDE_PLUGIN_ROOT}/context/" + name],
                      "timeout": 10})
    (plugin / "hooks").mkdir()
    (plugin / "hooks/hooks.json").write_text(json.dumps(
        {"description": "Inject the always-on apex and rules, one file per hook.",
         "hooks": {"SessionStart": [{"matcher": "startup|clear|compact", "hooks": hooks}]}},
        indent=2) + "\n", encoding="utf-8")

    suite = json.loads((src_s / SUITE_PATH).read_text(encoding="utf-8"))
    evals = plugin / "evals"
    for sc in suite["scenarios"]:
        case = evals / sc["id"]
        (case / "graders").mkdir(parents=True)
        case_yaml = f'schema_version: "1.1"\nname: {json.dumps(sc["id"])}\n'
        if sc.get("fixture"):
            data = json.loads((src_s / FIXTURE_DIR / f"{sc['fixture']}.json").read_text(encoding="utf-8"))
            (case / "fixture.sh").write_text(render_scaffold(data), encoding="utf-8")
            case_yaml += 'context:\n  scaffold_script: "fixture.sh"\n'
        (case / "case.yaml").write_text(case_yaml, encoding="utf-8")
        (case / "prompt.md").write_text(frontmatter({
            "description": sc.get("description", ""),
            "tags": [sc["kind"], *sc.get("stages", [])],
            "max_turns": sc.get("max_turns", DEFAULT_MAX_TURNS),
            "timeout_seconds": sc.get("timeout_seconds", DEFAULT_TIMEOUT),
            "allowed_tools": sc.get("allowed_tools", DEFAULT_TOOLS),
        }) + "\n" + sc["prompt"].rstrip() + "\n", encoding="utf-8")
        for g in sc["graders"]:
            (case / "graders" / f"{g['id']}.md").write_text(frontmatter(render_grader(g)), encoding="utf-8")
    count = sum(1 for p in evals.iterdir() if p.is_dir())
    return Built(plugin, harness_sha, suite_sha, count, harness_ref, suite_ref, drift=drift,
                 probe_cases=[sc["id"] for sc in suite["scenarios"] if sc.get("kind") == "probe"],
                 case_ids=[sc["id"] for sc in suite["scenarios"]])


# ------------------------------------------------------------------------- run


def eval_command(plugin_dir: Path, model: str, runs: int, max_cost_usd: float, output_dir: Path) -> list[str]:
    # Only Bash is granted, and it runs in the eval's OS sandbox: writes stay in
    # the run's workspace and no network domain is granted. No WebFetch, no
    # real MCP servers, no publishing of the report.
    return ["claude", "plugin", "eval", str(plugin_dir),
            "--model", model, "--runs", str(runs), "--ablation", "none", "--threshold", "0",
            "--max-cost-usd", format(max_cost_usd, "g"), "--no-publish", "--trust-plugin", "--scaffold",
            "--allow-tools", "Bash", "--output-dir", str(output_dir)]


def run_metadata(b: Built, model: str, runs: int, max_cost_usd: float, command: list[str],
                 claude_version: str) -> dict:
    return {"harness_ref": b.harness_ref, "harness_commit": b.harness_commit,
            "suite_ref": b.suite_ref, "suite_commit": b.suite_commit,
            "model": model, "runs": runs, "max_cost_usd": max_cost_usd,
            "case_count": b.case_count, "case_ids": b.case_ids, "probe_cases": b.probe_cases,
            "harness_drift": b.drift, "claude_version": claude_version, "command": command}


def result_dir_name(b: Built, stamp: str) -> str:
    return f"{stamp}_h-{b.harness_commit[:12]}_s-{b.suite_commit[:12]}"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def cmd_run(args) -> int:
    if args.max_cost_usd is None or args.max_cost_usd <= 0:
        print("error: --max-cost-usd must be given and greater than 0; every run is a billed model call",
              file=sys.stderr)
        return 2
    repo = Path(args.repo) if args.repo else repo_root()
    work = Path(tempfile.mkdtemp(prefix="harness-eval-"))
    try:
        b = build(repo, args.harness_ref, args.suite_ref, work)
    except BuildError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    for line in b.drift:
        print(f"note: the harness commit differs from the suite's: {line}", file=sys.stderr)
    model = args.model
    if model is None:
        settings = json.loads((work / "src-harness/.claude/settings.json").read_text(encoding="utf-8"))
        model = settings.get("model")
        if not model:
            print("error: the harness sets no model; pass --model", file=sys.stderr)
            return 2
    validate = subprocess.run(["claude", "plugin", "validate", str(b.plugin_dir)], capture_output=True, text=True)
    out_dir = work / "results"
    command = eval_command(b.plugin_dir, model, args.runs, args.max_cost_usd, out_dir)
    version = subprocess.run(["claude", "--version"], capture_output=True, text=True).stdout.strip()
    summary = run_metadata(b, model, args.runs, args.max_cost_usd, command, version)
    summary["validate_exit_code"] = validate.returncode
    summary["validate_output"] = (validate.stdout + validate.stderr).strip()
    if validate.returncode != 0:
        print(validate.stdout + validate.stderr, file=sys.stderr)
        print(json.dumps(summary, indent=2))
        return 1
    if args.dry_run:
        summary["build_dir"] = str(work)
        summary["dry_run"] = True
        print(json.dumps(summary, indent=2))
        return 0
    summary["started_at"] = datetime.now(timezone.utc).isoformat()
    res = subprocess.run(command)
    summary["finished_at"] = datetime.now(timezone.utc).isoformat()
    summary["eval_exit_code"] = res.returncode
    if res.returncode == 2:
        summary["note"] = "the cost ceiling stopped the run; the result is partial"
        print("warning: the cost ceiling stopped the run; the result is partial", file=sys.stderr)
    # The eval must have run exactly the suite's cases: none of its own, none lost.
    cases_ok = False
    try:
        result = load_result(out_dir)
    except (OSError, ValueError) as exc:
        summary["result_error"] = str(exc)
        print(f"error: {exc}", file=sys.stderr)
    else:
        found = {c.get("name") for c in result.get("cases", [])}
        summary["cases_missing"] = sorted(set(b.case_ids) - found)
        summary["cases_unexpected"] = sorted(str(n) for n in found - set(b.case_ids))
        cases_ok = not summary["cases_unexpected"] and (result.get("partial") or not summary["cases_missing"])
        if not cases_ok:
            print(f"error: the eval's cases differ from the suite's: missing {summary['cases_missing']}, "
                  f"unexpected {summary['cases_unexpected']}", file=sys.stderr)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dest = Path(args.results_dir) if args.results_dir else repo / RESULTS_DIR
    dest = dest / result_dir_name(b, stamp)
    if out_dir.is_dir():
        shutil.copytree(out_dir, dest)
    else:
        dest.mkdir(parents=True)
    (dest / "metadata.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"results: {dest}")
    if not args.keep_build:
        shutil.rmtree(work, ignore_errors=True)
    if res.returncode not in (0, 2):
        return res.returncode
    return 0 if cases_ok else 1


# --------------------------------------------------------------------- compare


def _scores(result: dict) -> dict[str, float | None]:
    return {c["name"]: (c.get("aggregates") or {}).get("score") for c in result.get("cases", [])}


def compare(before: dict, after: dict, threshold: float) -> dict:
    a, b = _scores(before), _scores(after)
    rows = []
    for name in sorted(set(a) & set(b)):
        if a[name] is None or b[name] is None:
            rows.append({"case": name, "before": a[name], "after": b[name], "delta": None, "flag": True})
            continue
        delta = round(b[name] - a[name], 4)
        rows.append({"case": name, "before": a[name], "after": b[name], "delta": delta,
                     "flag": abs(delta) >= threshold - 1e-9})
    return {"both": rows, "only_before": sorted(set(a) - set(b)), "only_after": sorted(set(b) - set(a))}


def load_result(path: Path) -> dict:
    """The aggregate result in `path`: the shallowest one, and only if it is the only one at its depth."""
    if path.is_dir():
        found = list(path.rglob("aggregate-result.json"))
        if not found:
            raise FileNotFoundError(f"no aggregate-result.json under {path}")
        depth = min(len(p.relative_to(path).parts) for p in found)
        top = sorted(p for p in found if len(p.relative_to(path).parts) == depth)
        if len(top) > 1:
            raise ValueError(f"several aggregate-result.json under {path} at the same depth: "
                             + ", ".join(p.relative_to(path).as_posix() for p in top))
        path = top[0]
    return json.loads(path.read_text(encoding="utf-8"))


def compare_dirs(before: Path, after: Path, threshold: float) -> dict:
    """compare(), plus every reason the two results may not be comparable."""
    a, b = load_result(before), load_result(after)
    res = compare(a, b, threshold)
    problems = []
    metas = []
    for label, path in (("before", before), ("after", after)):
        meta = path / "metadata.json" if path.is_dir() else path.parent / "metadata.json"
        metas.append(json.loads(meta.read_text(encoding="utf-8")) if meta.is_file() else None)
        if metas[-1] is None:
            problems.append(f"{label}: no metadata.json, so the suite and the model cannot be confirmed")
    for label, result in (("before", a), ("after", b)):
        if result.get("partial"):
            problems.append(f"{label}: the result is partial ({result.get('partialReason', 'no reason given')})")
    if all(metas):
        for key, name in (("suite_commit", "suite"), ("model", "model"),
                          ("claude_version", "claude_version"), ("runs", "runs")):
            if key not in metas[0] or key not in metas[1]:
                problems.append(f"{key} is missing from a metadata.json, so the {name} cannot be confirmed")
            elif metas[0][key] != metas[1][key]:
                problems.append(f"the {name} differs: {metas[0][key]} vs {metas[1][key]}")
    # A result whose probe did not pass may have measured Claude without the
    # always-on files, and a run that found other cases measured another suite.
    for label, meta, result in zip(("before", "after"), metas, (a, b)):
        if meta is None:
            continue
        if not isinstance(meta.get("probe_cases"), list):
            problems.append(f"{label}: probe_cases is missing from metadata.json, so the probe cannot be confirmed")
        elif not meta["probe_cases"]:
            problems.append(f"{label}: the suite has no probe, so nothing shows the always-on files reached the model")
        else:
            scores = _scores(result)
            for case in meta["probe_cases"]:
                score = scores.get(case)
                if not isinstance(score, (int, float)) or score < 1 - 1e-9:
                    problems.append(f"{label}: the probe {case} did not pass in every run (score {score}), "
                                    "so the always-on files may not have reached the model")
        if meta.get("cases_unexpected"):
            problems.append(f"{label}: the eval ran cases outside the suite: {meta['cases_unexpected']}")
        if meta.get("cases_missing") and not result.get("partial"):
            problems.append(f"{label}: the eval did not run these suite cases: {meta['cases_missing']}")
    res["problems"] = problems
    return res


def cmd_compare(args) -> int:
    try:
        res = compare_dirs(Path(args.before), Path(args.after), args.threshold)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    for problem in res["problems"]:
        print(f"PROBLEM {problem}")
    print(f"case\tbefore\tafter\tdelta\tflag (|delta| >= {args.threshold}; a screening mark, not a significance test)")
    for r in res["both"]:
        print(f"{r['case']}\t{r['before']}\t{r['after']}\t{r['delta']}\t{'*' if r['flag'] else ''}")
    for label in ("only_before", "only_after"):
        for name in res[label]:
            print(f"{name}\t({label.replace('_', ' ')})")
    return 1 if res["problems"] and not args.allow_mismatch else 0


# ------------------------------------------------------------------------ main


def working_tree_files(repo: Path) -> list[str]:
    out = subprocess.run(["git", "-C", str(repo), "ls-files", "--cached", "--others", "--exclude-standard",
                          "--", ".claude"], capture_output=True, text=True, check=True).stdout
    return [line for line in out.splitlines() if (repo / line).is_file()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check", help="check the map and the suite against the working tree")
    sub.add_parser("render", help=f"write {MAP_MD_PATH}")
    run = sub.add_parser("run", help="build from git and run the suite with claude plugin eval")
    run.add_argument("--harness-ref", default="HEAD")
    run.add_argument("--suite-ref", default="HEAD")
    run.add_argument("--model", help="default: the harness settings.json model")
    run.add_argument("--runs", type=int, default=3)
    run.add_argument("--max-cost-usd", type=float)
    run.add_argument("--results-dir", help=f"default: {RESULTS_DIR}/")
    run.add_argument("--dry-run", action="store_true", help="build and validate, print the command, call no model")
    run.add_argument("--keep-build", action="store_true")
    run.add_argument("--repo", help=argparse.SUPPRESS)
    cmp_ = sub.add_parser("compare", help="per-case score differences between two results")
    cmp_.add_argument("before")
    cmp_.add_argument("after")
    cmp_.add_argument("--threshold", type=float, default=0.34)
    cmp_.add_argument("--allow-mismatch", action="store_true",
                      help="exit 0 even when the suites, models, or completeness differ")
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code or 0)
    if args.cmd == "run":
        return cmd_run(args)
    if args.cmd == "compare":
        return cmd_compare(args)
    repo = repo_root()
    if args.cmd == "render":
        cmap = json.loads((repo / MAP_PATH).read_text(encoding="utf-8"))
        suite = json.loads((repo / SUITE_PATH).read_text(encoding="utf-8"))
        (repo / MAP_MD_PATH).write_text(render_map(cmap, suite), encoding="utf-8")
        print(f"wrote {MAP_MD_PATH}")
        return 0
    violations = check(repo, repo, working_tree_files(repo), check_render=True)
    for v in violations:
        print(f"FAIL {v}")
    print(f"Result: {'passed' if not violations else 'failed'} ({len(violations)} violations)")
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
