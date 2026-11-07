"""The script that produced probe-trace-summary.txt (run with python3 -I).

It reads the trace.jsonl that claude plugin eval kept (--keep-temp) for the
probe-always-on re-run and prints the SessionStart hook events, the
assistant's text verbatim, and the name of every tool the assistant called.
"""
import json
from pathlib import Path

p = Path("/private/tmp/e-ft7CaG/out/trace.jsonl")
events = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
print("source: trace.jsonl of the probe-always-on re-run (kept with --keep-temp)")
for e in events:
    if e.get("type") == "system" and e.get("subtype") in ("hook_started", "hook_response"):
        print(f"system {e['subtype']}: {e.get('hook_name')} exit_code={e.get('exit_code')}")
for e in events:
    if e.get("type") == "assistant":
        for c in e.get("message", {}).get("content", []):
            if c.get("type") == "text":
                print("assistant text:\n" + c["text"])
            if c.get("type") == "tool_use":
                print("assistant tool_use:", c.get("name"))
