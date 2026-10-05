# Quickstart: Validate the refreshed prompts

Prerequisite: both root files edited per [tasks.md](./tasks.md). Contract: [portable-prompt-contract.md](./contracts/portable-prompt-contract.md).

1. **Lengths (PP-01)** — extract each fenced block and compare with its budget and stated count:
   ```bash
   python3 - <<'PY'
   import re,sys
   for f in ("chatgpt-system-prompt.md","claude-ai-system-prompt.md"):
       t=open(f,encoding="utf-8").read()
       for i,b in enumerate(re.findall(r"```\n(.*?)\n```",t,re.S)):
           print(f,i,len(b))
   PY
   ```
   Expected: ChatGPT blocks ≤ 1,500 each; Claude block ≤ ~4,000; counts equal those written in the files.
2. **Forbidden content (PP-04, PP-07)** — grep the fenced blocks for `\.claude|rules/|skills/|/speckit|GPT|Claude (Opus|Sonnet|Fable)|MUST|NEVER|CRITICAL|ALWAYS`; expected: no match.
3. **Facts (PP-02, PP-03)** — open each URL under "Verified facts"; confirm field labels, path, limits against the page.
4. **Coverage (PP-05, PP-06)** — tick each source rule in R6 as conveyed or listed under "Not ported".
5. **Documentation** — run `.claude/skills/maintaining-living-documentation/scripts/check_links.py --changed`; expected: pass.
