#!/usr/bin/env python3
"""Claude Code hook that enforces the living-documentation workflow.

Registered by hooks/hooks.json when this folder loads as a plugin.

  SessionStart  stop_gate.py --session-start
                Records a fingerprint of the worktree, so files that were
                already modified before the session do not trigger the gate,
                and adds the mandatory rule (hooks/rule.md) to Claude's
                context unless the project or user already installed it as
                .claude/rules/living-documentation.md. It runs again after
                compaction to restore the rule.
  UserPromptSubmit  stop_gate.py --turn-start
                Records the worktree fingerprint when a turn begins, so the Stop
                gate only judges changes made during that turn, not edits made
                between turns by the user or other tools.
  Stop          stop_gate.py
                When the worktree changed during the session, checks that
                1. no broken local links are introduced (check_links --changed), and
                2. if behavior-, interface-, configuration-, infrastructure-, or
                   decision-related files changed, Claude's final message
                   contains the completion report headed "Documentation impact".
                A failed check blocks the stop and tells Claude what is
                missing and asks Claude not to repeat its earlier answer. The
                same worktree state is blocked at most LIVING_DOCS_GATE_MAX_BLOCKS
                times (default 2) and never on a re-entry caused by the gate's own
                block (stop_hook_active); then the stop is allowed and the user
                sees a warning. Claude Code also caps consecutive Stop blocks.

Mode, first match wins: LIVING_DOCS_GATE environment variable, then
"enforcement" in .living-documentation.json, then "block".
  block  block as described above
  warn   never block; show the user a warning
  off    do nothing (no rule injection either)

The hook never writes project files and keeps its state in the system temp
directory. It exits 0 silently outside Git worktrees, when Git is missing, and
on internal errors (fail open); CI remains the hard gate.
"""
from __future__ import annotations

import sys

sys.dont_write_bytecode = True  # never leave __pycache__ in the Skill or project

import hashlib
import json
import os
import re
import tempfile
import unicodedata
from pathlib import Path

from common import (
    SKILL_ROOT, ConfigError, changed_files, classify, excluded, git_toplevel, load_config, run_git,
)

REPORT_MARKER = re.compile(r"documentation\s+impact", re.IGNORECASE)
REPORT_REQUIRED_FOR = {"implementation", "specification", "configuration", "infrastructure", "decision"}
RULE_TEMPLATE = SKILL_ROOT / "hooks" / "rule.md"
RULE_NAME = "living-documentation.md"
MODES = ("block", "warn", "off")
RELATED_LIMIT = 10  # documents listed in one problem; the rest are summarized as "+N more"

# Reasons that say nothing, in normalized form (see normalize_reason). A report that gives one of these as
# its reason for "no documentation impact" is treated as having no reason.
BOILERPLATE_REASONS = frozenset({
    "n/a", "na", "none", "nil", "no", "nothing", "no impact", "no change", "no changes", "no change needed",
    "not applicable", "no documentation impact", "なし", "無し", "該当なし", "変更なし", "影響なし", "特になし",
})

# Report lines. Horizontal whitespace only, so a match never runs into the next line.
_LINE_START = r"^[ \t>*_`#•\-]*"
_NONE_RE = re.compile(
    _LINE_START + r"documentation[ \t]+impact[ \t*_`]*[:：]?[ \t*_`]*none\b[ \t*_`]*"
    r"(?:(?:[—–:：]|-+)[ \t]*(?P<reason>.*))?$", re.IGNORECASE | re.MULTILINE)
_UPDATED_RE = re.compile(_LINE_START + r"updated[ \t*_`]*[:：][ \t]*(?P<content>.*)$", re.IGNORECASE | re.MULTILINE)
_NO_CHANGE_RE = re.compile(_LINE_START + r"no[ \t]+change[ \t]+needed[ \t*_`]*[:：][ \t]*(?P<content>.*)$",
                           re.IGNORECASE | re.MULTILINE)
_REASON_SPLIT = re.compile(r"\s[—–-]\s|[—–]")  # "<area> — <reason>"; a hyphen inside a path does not split
_PLACEHOLDER = re.compile(r"<[^<>]*>")  # unfilled template text such as <reason>
_MARKDOWN_NOISE = re.compile(r"[*_`]")


# --------------------------------------------------------------------------
# State
# --------------------------------------------------------------------------

def state_dir() -> Path:
    return Path(tempfile.gettempdir()) / "living-documentation-gate"


def state_path(root: Path, session_id: str) -> Path:
    key = hashlib.sha256(f"{root}\0{session_id}".encode()).hexdigest()[:32]
    return state_dir() / f"{key}.json"


def load_state(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def save_state(path: Path, state: dict) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(f".{os.getpid()}.tmp")
        tmp.write_text(json.dumps(state), encoding="utf-8")
        tmp.replace(path)
    except OSError:
        pass


def fingerprint(root: Path) -> str | None:
    """Identify the current set of uncommitted changes (paths, sizes, mtimes)."""
    proc = run_git(root, "--no-optional-locks", "status", "--porcelain=v1", "-z", "--untracked-files=all", ".")
    if proc is None or proc.returncode != 0:
        return None
    digest = hashlib.sha256()
    for entry in sorted(e for e in proc.stdout.split("\0") if e):
        digest.update(entry.encode("utf-8", "surrogateescape"))
        path = root / entry[3:] if len(entry) > 3 else None
        try:
            if path is not None and path.is_file():
                st = path.stat()
                digest.update(f"\0{st.st_size}\0{st.st_mtime_ns}".encode())
        except OSError:
            pass
        digest.update(b"\n")
    head = run_git(root, "rev-parse", "-q", "--verify", "HEAD")
    digest.update((head.stdout.strip() if head is not None else "").encode())
    return digest.hexdigest()


# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

def gate_mode(root: Path) -> str:
    env = os.environ.get("LIVING_DOCS_GATE", "").strip().lower()
    if env in MODES:
        return env
    try:
        return load_config(root).get("enforcement", "block")
    except ConfigError:
        return "block"  # evaluate() reports the configuration error


def rule_installed(root: Path) -> bool:
    return (root / ".claude" / "rules" / RULE_NAME).exists() or \
        (Path.home() / ".claude" / "rules" / RULE_NAME).exists()


# --------------------------------------------------------------------------
# Evaluation
# --------------------------------------------------------------------------

def evaluate(root: Path, last_message: str | None) -> list[str]:
    """Return a list of problems; empty when the change satisfies the gate."""
    try:
        config = load_config(root)
    except ConfigError as exc:
        return [f"{exc}"]
    changes = [c for c in changed_files(root) if not excluded(c.path, config)]
    if not changes:
        return []

    problems: list[str] = []
    import check_links  # local import keeps SessionStart fast

    _, findings = check_links.run_check(root, config, changes)
    errors = [f for f in findings if f.severity == "error"]
    if errors:
        listed = "; ".join(f"{f.source}:{f.line} -> {f.target} ({f.message})" for f in errors[:10])
        more = f" (+{len(errors) - 10} more)" if len(errors) > 10 else ""
        problems.append(f"Broken local links in the changed scope: {listed}{more}. Fix them or the references.")

    categories = set()
    for change in changes:
        categories |= classify(change.path, config)
    needs_report = sorted(categories & REPORT_REQUIRED_FOR)
    if needs_report and last_message is not None and not REPORT_MARKER.search(last_message):
        problems.append(
            "Changed files include " + ", ".join(needs_report) + " artifacts, but the final message has no "
            "completion report. Use the maintaining-living-documentation skill: update affected "
            "documentation (and change history if the project keeps it), run its checks, then end with the "
            "report headed 'Documentation impact' (or 'Documentation impact: none — <reason>')."
        )
    if last_message is not None:
        problems += report_quality_problems(last_message, needs_report, "documentation" in categories)
    related = unaddressed_related(root, config, changes, last_message)
    if related:
        problems.append(related)
    return problems


def _is_noise(char: str) -> bool:
    return char.isspace() or unicodedata.category(char)[0] in "PSZ"


def normalize_reason(text: str) -> str:
    """Fold width and case, drop template placeholders and markdown marks, trim punctuation and spaces."""
    text = _MARKDOWN_NOISE.sub("", _PLACEHOLDER.sub("", unicodedata.normalize("NFKC", text).casefold()))
    start, end = 0, len(text)
    while start < end and _is_noise(text[start]):
        start += 1
    while end > start and _is_noise(text[end - 1]):
        end -= 1
    return text[start:end]


def is_boilerplate(text: str) -> bool:
    """True when the reason is empty, only punctuation, an unfilled template, or a stock phrase."""
    reason = normalize_reason(text)
    return not any(char.isalnum() for char in reason) or reason in BOILERPLATE_REASONS


def none_declarations(message: str) -> list[str]:
    """Reasons given in 'Documentation impact: none — <reason>' lines, in order ('' when there is none)."""
    return [(match.group("reason") or "").strip() for match in _NONE_RE.finditer(message)]


def report_lines(message: str) -> tuple[list[str], list[str]]:
    """Contents of 'Updated:' lines that say something, and reasons of 'No change needed:' lines."""
    updated = []
    for match in _UPDATED_RE.finditer(message):
        content = match.group("content").strip()
        if any(char.isalnum() for char in _PLACEHOLDER.sub("", content)):
            updated.append(content)
    no_change = []
    for match in _NO_CHANGE_RE.finditer(message):
        parts = _REASON_SPLIT.split(match.group("content").strip(), maxsplit=1)
        no_change.append(parts[-1].strip())
    return updated, no_change


def report_quality_problems(message: str, needs_report: list[str], docs_changed: bool) -> list[str]:
    """Problems with the content of the completion report (contract C2)."""
    nones = none_declarations(message)
    if any(is_boilerplate(reason) for reason in nones):
        return ["The final message says 'Documentation impact: none' without a specific reason. State why the "
                "change needs no documentation update: 'Documentation impact: none — <what stays unchanged "
                "and why>'."]
    if needs_report and not docs_changed and not nones and REPORT_MARKER.search(message):
        updated, no_change = report_lines(message)
        if not updated and all(is_boilerplate(reason) for reason in no_change):
            return ["Changed files include " + ", ".join(needs_report) + " artifacts and no documentation file "
                    "changed, but the report has no 'Updated: <file> — <what changed>' line, no 'No change "
                    "needed: <area> — <specific reason>' line, and no 'Documentation impact: none — <reason>' "
                    "line. Add one."]
    return []


RELATED_LABELS = {
    "sibling": "next to changed {source}",
    "mention": "mentions changed {source}",
    "changelog": "change history; user-visible change {source}",
}


def unaddressed_related(root: Path, config: dict, changes: list, last_message: str | None) -> str | None:
    """Describe related documents (next to, naming, or recording changed files) that were neither changed nor named.

    A candidate is addressed when it changed (find_candidates already leaves such documents out)
    or when its project-relative path appears in the final message (contract C2). Advisory
    comment records (P0) point at the changed file itself and are never enforced.
    """
    if last_message is None:
        return None
    import find_related  # local import keeps SessionStart fast

    report = find_related.find_candidates(root, config, changes)
    labels_by_path: dict[str, list[str]] = {}
    for candidate in report["candidates"]:
        if candidate["kind"] == "comment" or candidate["path"] in last_message:
            continue
        label = RELATED_LABELS[candidate["kind"]].format(source=candidate["source"])
        labels_by_path.setdefault(candidate["path"], []).append(label)
    if not labels_by_path:
        return None
    paths = sorted(labels_by_path)
    listed = "; ".join(f"{path} ({', '.join(labels_by_path[path])})" for path in paths[:RELATED_LIMIT])
    more = f" (+{len(paths) - RELATED_LIMIT} more)" if len(paths) > RELATED_LIMIT else ""
    omitted = (f" (+{report['truncated']} more not listed: raise related.max_candidates)"
               if report["truncated"] else "")
    return ("Documents related to changed files were neither updated nor named in the final message: "
            f"{listed}{more}{omitted}. Update each one, or name its path in your final message with the "
            "reason it needs no change.")


# --------------------------------------------------------------------------
# Entry points
# --------------------------------------------------------------------------

def emit(obj: dict) -> None:
    print(json.dumps(obj, ensure_ascii=False))


def project_root(payload: dict) -> Path | None:
    candidate = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd()
    return git_toplevel(Path(candidate).resolve())


def on_session_start(payload: dict) -> int:
    root = project_root(payload)
    session_id = payload.get("session_id")
    if root is None:
        return 0
    if session_id:
        path = state_path(root, session_id)
        state = load_state(path)
        if "baseline" not in state:  # resume, clear, and compact keep the original baseline
            state["baseline"] = fingerprint(root)
            save_state(path, state)
    if gate_mode(root) != "off" and not rule_installed(root):
        location = (f"\nThe maintaining-living-documentation skill is installed at {SKILL_ROOT}; "
                    f"its scripts are in {SKILL_ROOT / 'scripts'}.\n")
        emit({"hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": RULE_TEMPLATE.read_text(encoding="utf-8") + location,
        }})
    return 0


def on_turn_start(payload: dict) -> int:
    root = project_root(payload)
    session_id = payload.get("session_id")
    if root is None or not session_id:
        return 0
    path = state_path(root, session_id)
    state = load_state(path)
    state["turn_start"] = fingerprint(root)
    save_state(path, state)
    return 0


def on_stop(payload: dict) -> int:
    if payload.get("stop_reason") not in (None, "end_turn"):
        return 0
    root = project_root(payload)
    if root is None:
        return 0
    mode = gate_mode(root)
    if mode == "off":
        return 0
    session_id = payload.get("session_id") or "unknown-session"

    path = state_path(root, session_id)
    state = load_state(path)
    current = fingerprint(root)
    if current is None or current in (state.get("baseline"), state.get("last_ok"), state.get("turn_start")):
        return 0  # nothing changed during this turn (turn_start is absent until the first prompt)

    problems = evaluate(root, payload.get("last_assistant_message"))
    if not problems:
        state["last_ok"] = current
        state.pop("blocks", None)
        save_state(path, state)
        return 0

    try:
        max_blocks = max(0, int(os.environ.get("LIVING_DOCS_GATE_MAX_BLOCKS", "2")))
    except ValueError:
        max_blocks = 2
    blocks = state.get("blocks", {})
    count = blocks.get(current, 0)
    summary = "Living documentation gate: " + " ".join(problems)
    # A re-entry after our own block (stop_hook_active) must not block again: a second round only
    # makes Claude restate its earlier output.
    reentry = bool(payload.get("stop_hook_active"))

    if mode == "block" and count < max_blocks and not reentry:
        blocks[current] = count + 1
        state["blocks"] = blocks
        save_state(path, state)
        emit({"decision": "block", "reason": summary + " Do not repeat or restate your previous answer; "
                                                      "reply with only the missing correction or report."})
        return 0

    # Warn mode, or the block budget for this worktree state is spent.
    state["last_ok"] = current  # do not repeat the warning for the same state
    save_state(path, state)
    emit({"systemMessage": summary + " (not blocking: review before committing)"})
    return 0


def main() -> int:
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except ValueError:
        payload = {}
    try:
        args = sys.argv[1:]
        if "--session-start" in args:
            return on_session_start(payload)
        return on_turn_start(payload) if "--turn-start" in args else on_stop(payload)
    except Exception as exc:  # noqa: BLE001 - fail open; CI is the hard gate
        print(f"living-documentation gate skipped: {exc}", file=sys.stderr)
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
