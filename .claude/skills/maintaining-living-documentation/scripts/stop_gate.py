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
  Stop          stop_gate.py
                When the worktree changed during the session, checks that
                1. no broken local links are introduced (check_links --changed), and
                2. if behavior-, interface-, configuration-, infrastructure-, or
                   decision-related files changed, Claude's final message
                   contains the completion report headed "Documentation impact".
                A failed check blocks the stop and tells Claude what is
                missing. The same worktree state is blocked at most
                LIVING_DOCS_GATE_MAX_BLOCKS times (default 2); after that the
                stop is allowed and the user sees a warning. Claude Code also
                caps consecutive Stop blocks on its own.

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
from pathlib import Path

from common import (
    SKILL_ROOT, ConfigError, changed_files, classify, excluded, git_toplevel, load_config, run_git,
)

REPORT_MARKER = re.compile(r"documentation\s+impact", re.IGNORECASE)
REPORT_REQUIRED_FOR = {"implementation", "specification", "configuration", "infrastructure", "decision"}
RULE_TEMPLATE = SKILL_ROOT / "hooks" / "rule.md"
RULE_NAME = "living-documentation.md"
MODES = ("block", "warn", "off")


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
    return problems


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
    if current is None or current in (state.get("baseline"), state.get("last_ok")):
        return 0

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

    if mode == "block" and count < max_blocks:
        blocks[current] = count + 1
        state["blocks"] = blocks
        save_state(path, state)
        emit({"decision": "block", "reason": summary})
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
        return on_session_start(payload) if "--session-start" in sys.argv[1:] else on_stop(payload)
    except Exception as exc:  # noqa: BLE001 - fail open; CI is the hard gate
        print(f"living-documentation gate skipped: {exc}", file=sys.stderr)
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
