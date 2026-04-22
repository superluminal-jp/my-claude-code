# Tool Use Rules

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

## Subagents

Spawn only for: codebase-wide multi-step exploration, context-window protection from large results, or explicit user request. Otherwise use Glob/Grep/Read directly.

## CLAUDE.md imports

Use `@path/to/file` to keep files focused and under ~200 lines.
