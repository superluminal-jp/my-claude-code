import json, sys, re, os
rounds = sys.argv[1:]
for spec in rounds:
    label, path = spec.split("=", 1)
    calls, results = {}, {}
    usage_in = usage_out = cache_read = cache_create = 0
    turns = 0
    with open(os.path.realpath(path), encoding="utf-8") as f:
        for line in f:
            try:
                d = json.loads(line)
            except ValueError:
                continue
            msg = d.get("message") or {}
            if d.get("type") == "assistant":
                u = msg.get("usage") or {}
                if u:
                    turns += 1
                    usage_in += u.get("input_tokens", 0); usage_out += u.get("output_tokens", 0)
                    cache_read += u.get("cache_read_input_tokens", 0); cache_create += u.get("cache_creation_input_tokens", 0)
                for c in msg.get("content") or []:
                    if isinstance(c, dict) and c.get("type") == "tool_use":
                        inp = c.get("input") or {}
                        calls[c["id"]] = (c.get("name"), inp.get("command") or inp.get("file_path") or inp.get("pattern") or json.dumps(inp)[:80])
            if d.get("type") == "user":
                for c in msg.get("content") or [] if isinstance(msg.get("content"), list) else []:
                    if isinstance(c, dict) and c.get("type") == "tool_result":
                        content = c.get("content")
                        text = content if isinstance(content, str) else "".join(x.get("text", "") for x in content or [] if isinstance(x, dict))
                        results[c["tool_use_id"]] = len(text.encode("utf-8"))
    rec = re.compile(r"specs/068-skill-procedure-gaps")
    kinds = {"records": 0, "diff/other": 0}
    big = []
    for cid, (name, what) in calls.items():
        size = results.get(cid, 0)
        key = "records" if rec.search(str(what)) and "git" not in str(what).split()[:3] else "diff/other"
        if "git" in str(what) and "diff" in str(what):
            key = "diff/other"
        kinds[key] += size
        big.append((size, name, str(what)[:110]))
    big.sort(reverse=True)
    total = sum(results.values())
    print(f"== round {label}: {len(calls)} tool calls, {turns} assistant turns; tool results {total//1024} KB "
          f"(record-dir reads {kinds['records']//1024} KB, git diff and other {kinds['diff/other']//1024} KB); "
          f"input {usage_in}, cache read {cache_read}, cache create {cache_create}, output {usage_out}")
    for size, name, what in big[:4]:
        print(f"   {size//1024:5d} KB  {name}: {what}")
