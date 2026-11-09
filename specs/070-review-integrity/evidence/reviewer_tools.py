"""Summarize the read-only reviewer subagents of past sessions (spec 070, G1).

Reads Claude Code subagent transcripts (``<session>/subagents/agent-*.jsonl``)
and their ``.meta.json`` under the project directory given as the first
argument. A transcript counts as a reviewer when its first user message starts
with the challenger prompt ("You are a skeptical, read-only reviewer") or an
assurance reviewer prompt ("You are an independent, read-only reviewer").

For each reviewer it prints the subagent type, the model and effort recorded
in the meta file, the tool calls it made, how many Bash commands ran Python or
a git command whose output was piped into Python, whether the transcript has
an ``instructions`` attachment (the user's and project's CLAUDE.md, rules, and
memory index), and which deferred tools were offered to it. At the end it
counts, over all reviewers' Bash commands, the programs the commands started
(each segment between ``&&``, ``||``, ``;``, ``|`` and newlines, by its first
word after ``cd`` and variable assignments; ``git`` with its subcommand), and
the commands that match a pattern of a state-changing operation. Read-only:
it opens files and prints; it writes nothing.
"""
import collections
import json
import pathlib
import re
import shlex
import sys

OPENINGS = ("You are a skeptical, read-only reviewer", "You are an independent, read-only reviewer")
RUNS_PYTHON = re.compile(r"(^|[\s;&|(])python3?\b")
OFFERED_OF_INTEREST = ("WebFetch", "WebSearch", "EnterWorktree", "SendMessage", "TaskStop")
SEGMENT_SPLIT = re.compile(r"&&|\|\||;|\||\n")
ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
# Operations that change files or git state. A redirection counts unless it
# goes to /dev/null or duplicates a descriptor (2>&1).
STATE_CHANGING = re.compile(
    r"(^|[\s;&|(])(rm|mv|cp|mkdir|touch|tee|chmod|ln)\s"
    r"|sed\s+-i|git\s+(checkout|switch|reset|stash|commit|add|worktree|apply|restore|clean|push)\b"
    r"|(?<![0-9&<>])>>?(?!&|\s*/dev/null|=)")
HEREDOC_BODY = re.compile(r"<<-?\s*'?(\w+)'?\n.*?\n\1(\n|$)", re.S)


def programs(command):
    """First word of each segment, skipping cd and variable assignments."""
    found = []
    for segment in SEGMENT_SPLIT.split(HEREDOC_BODY.sub("<<HEREDOC\n", command)):
        try:
            words = shlex.split(segment, comments=True)
        except ValueError:
            words = segment.split()
        while words and ASSIGNMENT.match(words[0]):
            words = words[1:]
        if not words or words[0] == "cd":
            continue
        name = pathlib.PurePath(words[0]).name
        if name == "git" and len(words) > 1:
            sub = next((w for w in words[1:] if not w.startswith("-")), "")
            name = f"git {sub}"
        found.append(name)
    return found


def first_user_text(lines):
    for d in lines:
        msg = d.get("message") or {}
        if d.get("type") == "user" and isinstance(msg.get("content"), str):
            return msg["content"]
    return ""


def main(project_dir):
    rows = []
    totals = collections.Counter()
    started = collections.Counter()
    changing = []
    for path in sorted(pathlib.Path(project_dir).glob("*/subagents/agent-*.jsonl")):
        lines = []
        for raw in path.read_text(errors="replace").splitlines():
            try:
                lines.append(json.loads(raw))
            except json.JSONDecodeError:
                continue
        first = first_user_text(lines)
        if not first.startswith(OPENINGS):
            continue
        meta_path = path.with_name(path.stem + ".meta.json")
        meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
        tools = collections.Counter()
        python_runs = 0
        instructions = []
        offered = set()
        mcp_offered = 0
        for d in lines:
            att = d.get("attachment")
            if isinstance(att, dict):
                if att.get("type") == "instructions":
                    instructions = [f.get("path", "") for f in att.get("files", [])]
                if att.get("type") == "deferred_tools_delta":
                    names = att.get("addedNames") or []
                    offered.update(n for n in names if n in OFFERED_OF_INTEREST)
                    mcp_offered += sum(1 for n in names if n.startswith("mcp__"))
            content = (d.get("message") or {}).get("content")
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "tool_use":
                        name = block.get("name")
                        tools[name] += 1
                        if name == "Bash":
                            command = block.get("input", {}).get("command", "")
                            if RUNS_PYTHON.search(command):
                                python_runs += 1
                            started.update(programs(command))
                            if STATE_CHANGING.search(HEREDOC_BODY.sub("<<HEREDOC\n", command)):
                                changing.append((path.stem[-8:], command[:150].replace("\n", " ")))
        role = "challenger" if first.startswith(OPENINGS[0]) else "assurance"
        rows.append((path.parent.parent.name[:8], path.stem[-8:], role, meta.get("agentType"),
                     meta.get("model"), meta.get("effort"), meta.get("finished"), dict(tools),
                     python_runs, len(instructions), sorted(offered), mcp_offered))
        totals["reviewers"] += 1
        totals["bash"] += tools.get("Bash", 0)
        totals["python_runs"] += python_runs
        totals["webfetch"] += tools.get("WebFetch", 0)
        totals["with_instructions"] += 1 if instructions else 0
        totals[f"type:{meta.get('agentType')}"] += 1
        totals[f"finished:{meta.get('finished')}"] += 1
    print("session  agent    role        type     model   effort finished | tool calls | bash running python | "
          "instruction files | deferred tools offered (of interest) | mcp tools offered")
    for r in rows:
        print(f"{r[0]} {r[1]} {r[2]:<11} {r[3]!s:<8} {r[4]!s:<7} {r[5]!s:<6} {r[6]!s:<8} | {r[7]} | {r[8]} | "
              f"{r[9]} | {r[10]} | {r[11]}")
    print()
    print("totals:", dict(sorted(totals.items())))
    print()
    print("programs started by the reviewers' Bash commands (segment count):")
    for name, count in started.most_common():
        print(f"  {count:4d}  {name}")
    print()
    print(f"Bash commands matching a state-changing pattern: {len(changing)}")
    for agent, command in changing:
        print(f"  {agent}: {command}")


if __name__ == "__main__":
    main(sys.argv[1])
