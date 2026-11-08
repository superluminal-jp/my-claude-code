#!/usr/bin/env python3
"""R0-A2: summarizes what each assurance reviewer subagent read and used, from
its Claude Code transcript (a JSONL file of the subagent's turns).

For each round it prints the tool calls, the assistant turns, the bytes of
tool results, and the summed usage of the turns (input, cache read, cache
creation, output), then every tool call that names the record directory,
classified:
  contents  read a file of the record directory in the repository
  names     listed record-directory paths (ls, or git ls-tree, --stat,
            --name-only, --name-status, log), reading no file's contents
  bundle    read the record directory's copy inside a review bundle
Only "contents" calls count against R0-A2. A person can check every
classification against the printed command.

Usage: transcript_usage.py --records DIR LABEL=TRANSCRIPT... Reads only.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from typing import Dict, List, Tuple

NAME_ONLY = re.compile(r"\bgit\b[^|;&]*\b(ls-tree|--stat|--name-only|--name-status|log)\b")
# git log with -p or --patch, and git show, print file contents.
PATCH = re.compile(r"\bgit\b[^|;&]*(\s-p\b|--patch\b|\bshow\b)")


def classify(what: str, records: str) -> str:
    if re.search(r"/bundle-[^/\s]*/", what):
        return "bundle"
    # "| cat" only turns off git's pager; it reads nothing of its own.
    reading = re.search(r"\b(cat|head|tail|sed|less|grep|python3?|open)\b", re.sub(r"\|\s*cat\b", "", what))
    if (NAME_ONLY.search(what) or re.search(r"(^|[;&|]\s*)ls\b", what)) and not reading and not PATCH.search(what):
        return "names"
    return "contents"


def summarize(path: str, records: str) -> Tuple[Dict[str, int], List[Tuple[str, str, str, int]]]:
    calls: Dict[str, Tuple[str, str]] = {}
    results: Dict[str, int] = {}
    usage = {"tool_calls": 0, "turns": 0, "result_bytes": 0, "input": 0, "cache_read": 0, "cache_create": 0, "output": 0}
    with open(os.path.realpath(path), encoding="utf-8") as handle:
        for line in handle:
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            message = entry.get("message") or {}
            if entry.get("type") == "assistant":
                turn = message.get("usage") or {}
                if turn:
                    usage["turns"] += 1
                    usage["input"] += turn.get("input_tokens", 0)
                    usage["cache_read"] += turn.get("cache_read_input_tokens", 0)
                    usage["cache_create"] += turn.get("cache_creation_input_tokens", 0)
                    usage["output"] += turn.get("output_tokens", 0)
                for part in message.get("content") or []:
                    if isinstance(part, dict) and part.get("type") == "tool_use":
                        given = part.get("input") or {}
                        # Every argument that can name a path: a Grep or Glob call names its
                        # directory in "path" and may name it in "pattern" or "glob".
                        what = " ".join(str(given[k]) for k in ("command", "file_path", "path", "pattern", "glob") if given.get(k)) or json.dumps(given)
                        calls[part["id"]] = (part.get("name", ""), str(what))
            if entry.get("type") == "user" and isinstance(message.get("content"), list):
                for part in message["content"]:
                    if isinstance(part, dict) and part.get("type") == "tool_result":
                        body = part.get("content")
                        text = body if isinstance(body, str) else "".join(x.get("text", "") for x in body or [] if isinstance(x, dict))
                        results[part["tool_use_id"]] = len(text.encode("utf-8"))
    usage["tool_calls"] = len(calls)
    usage["result_bytes"] = sum(results.values())
    named = [(classify(what, records), name, what, results.get(cid, 0)) for cid, (name, what) in calls.items()
             if records in what and name != "SubagentHandback"]
    return usage, named


def main() -> int:
    parser = argparse.ArgumentParser(prog="transcript_usage.py")
    parser.add_argument("--records", required=True, help="the record directory, as the reviewer would name it")
    parser.add_argument("rounds", nargs="+", help="LABEL=TRANSCRIPT")
    args = parser.parse_args()
    for spec in args.rounds:
        label, path = spec.split("=", 1)
        usage, named = summarize(path, args.records)
        contents = sum(1 for kind, *_ in named if kind == "contents")
        print(f"== round {label}: {usage['tool_calls']} tool calls, {usage['turns']} turns, tool results {usage['result_bytes'] // 1024} KB; "
              f"input {usage['input']}, cache read {usage['cache_read']}, cache create {usage['cache_create']}, output {usage['output']}; "
              f"record-directory contents read: {contents}")
        for kind, name, what, size in named:
            print(f"   {kind:8s} {size:7d} B  {name}: {what[:150]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
