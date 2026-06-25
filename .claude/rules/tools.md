# Tool Use Rules

Purpose: pick the right tool, and the right amount of delegation and memory, so work is correct and context-efficient. Applies to every task.

## Prefer dedicated tools over Bash

| Task | Use | Avoid |
|---|---|---|
| Read file | Read | `cat`, `head`, `tail` |
| Search text | Grep | `grep`, `rg` |
| Find files | Glob | `find`, `ls` |
| Edit file | Edit | `sed`, `awk` |
| Create file | Write | `echo >`, `cat <<EOF` |

Reserve Bash for commands that require shell execution.

## Parallel calls (default — batch independently)

**Default to parallel** whenever operations do not depend on each other's output. Parallelism is the normal mode, not an optimization of last resort.

### Batch in one message

| Pattern | Examples |
|---|---|
| Multi-file reads | Skills, configs, or modules needed for the same task |
| Disjoint searches | Grep/Glob across different paths or patterns |
| Independent checks | `git status` + `git diff` + `git log`; lint + test discovery |
| MCP prep | Read tool schemas, then call multiple MCP tools |
| Mixed reads | Read + Grep + Glob when paths are already known |

### Stay sequential only when

- B needs A's output (search → read the hit; parse → act on result)
- Edit depends on Read for exact `old_string`
- Shell command B uses exit code or stdout of command A

**Anti-pattern**: serializing obviously independent calls — adds latency with no benefit.

## Read before Edit

Read the file first; Edit fails unless `old_string` matches exactly.

## Subagents (use actively — delegate exploration)

Subagents are a **first-class delegation layer**. Consider them **before** loading dozens of files or grep dumps into the main conversation.

### Delegate when

| Trigger | Example |
|---|---|
| Broad fan-out exploration | "How does auth work across this codebase?" |
| Unknown scope | Need to find patterns across many directories |
| Context protection | Conclusion needed, not 50 file contents |
| Multiple independent tracks | API layer + DB layer + infra in parallel |
| Explicit user request | "Use subagents" / "explore in parallel" |
| Non-trivial investigation | Debugging spanning modules; architecture survey |

Prefer `explore` for codebase search; `shell` for git/CI commands; `generalPurpose` for multi-step research.

### Use direct tools instead when

- Single known file path
- Narrow Grep with known pattern and small expected hits
- Edit in ≤3 files with known locations
- Anything finishable in a few direct tool calls

**Anti-pattern**: subagent for a single-file read or known-scope edit — delegation overhead exceeds savings.

### Parallel subagents

When multiple research areas are **independent**, launch subagents in **one message** (not one after another). Examples:

- Explore frontend + backend concurrently
- Run bugbot + security-review on the same diff in parallel (when user requests review)
- User says "in parallel" — always batch launches

Return the subagent **conclusion** to the user; omit raw file dumps unless requested.

## Memory (use actively — `autoMemoryEnabled: true`)

Claude Memory is a **first-class persistence layer**. Use it proactively every session — not only when the user says "remember this."

### Read (start of task)

Consult Memory **before** exploring the repo when the task may depend on:

- User preferences (language, style, tools, commit/PR habits)
- Prior decisions and their rationale
- Project conventions not obvious from `CLAUDE.md` or code
- Locations of key files or workflows discovered in past sessions

If Memory is empty or stale for this project, say nothing — proceed and seed it as facts emerge.

### Write (during and after work)

**Persist without being asked** when you learn something durable, cross-session, and costly to rederive:

| Trigger | Example |
|---|---|
| User states a preference | "日本語で返して", "PRは小さく" |
| Decision made with rationale | "SQLite over Postgres for local dev because …" |
| User corrects your behavior | "Always run tests before commit" |
| Non-obvious convention found | "Auth middleware lives in `src/lib/auth.ts`" |
| Resolved ambiguity worth reusing | Default branch naming, deploy target, test runner |
| Task boundary | Significant work complete — capture decisions before context rolls off |

Keep entries concise (one fact per memory). Do not announce every write unless the user would care.

### Do not store

- Transient state (current branch, in-progress step, this-turn plan)
- Secrets, credentials, tokens, PII
- Anything reconstructable in seconds from the repo or `CLAUDE.md`
- Business domain terms/rules/structure → use repo docs below instead

### Complement — domain knowledge docs

For **what the product is** (team-visible, version-controlled), prefer:

- `docs/ubiquitous-language.md` — terms and rules (`ubiquitous-language` skill, always-on)
- `docs/models/` — structure (`domain-model` skill, always-on)

Use Claude Memory for **how the agent should work on this project**; use domain docs for **what the system means**. See `skill-routing.md` § Domain knowledge memory.

## CLAUDE.md imports

Use `@path/to/file` to keep files focused and under ~200 lines.
