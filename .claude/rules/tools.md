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

## Parallel calls

Batch independent calls in one message (multi-file reads, disjoint searches, independent checks). Sequential only when B depends on A's output.

## Read before Edit

Read the file first; Edit fails unless `old_string` matches exactly.

## Subagents (delegate deliberately)

Delegate to a subagent only when one of these holds; otherwise use Glob/Grep/Read directly:

- **Broad fan-out search** across many files or directories where you need only the conclusion, not the file dumps.
- **Context protection**: the work yields large intermediate output that would crowd the main context.
- **Explicit user request** to use an agent.

Anti-pattern: never spawn a subagent for a single-file read, a known-scope edit, or anything finishable in a few direct tool calls — the delegation overhead costs more than it saves.

## Memory (persist only durable facts)

Memory is enabled (`autoMemoryEnabled` in `settings.json`). Use it deliberately:

- **Write** when a fact is durable, cross-session, and costly to rederive: project conventions, decisions and their rationale, locations of key files, stable user preferences.
- **Read** at task start when the task plausibly depends on such facts.

Anti-pattern: do not store transient state (current branch, in-progress step), secrets or credentials, or anything reconstructable in seconds from the repo. Memory is a cache for hard-won context, not a scratchpad.

## CLAUDE.md imports

Use `@path/to/file` to keep files focused and under ~200 lines.
