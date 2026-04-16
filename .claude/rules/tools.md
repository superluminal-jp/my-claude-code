---
name: Tool Use Rules
description: Tool selection and parallel execution best practices
type: rules
---

# Tool Use Rules

## Prefer Dedicated Tools Over Bash

| Task                 | Use           | Avoid               |
|----------------------|---------------|---------------------|
| Read a file          | Read          | `cat`, `head`, `tail` |
| Search file contents | Grep          | `grep`, `rg`        |
| Find files           | Glob          | `find`, `ls`        |
| Edit a file          | Edit          | `sed`, `awk`        |
| Create a file        | Write         | `echo >`, `cat <<EOF` |

Reserve Bash for system commands that require shell execution.

## Parallel Tool Calls

Run independent calls in a single message block:
- Reading multiple files with no dependencies between them
- Searching different parts of the codebase
- Running independent validation checks

Sequential calls only when output B depends on output A.

## Agent Tool Usage

Use specialized agents only when:
- The task spans the entire codebase and requires multi-step exploration
- You need to protect the main context window from large results
- The user explicitly requests a subagent

Do not spawn agents for tasks you can complete with direct tools (Glob, Grep, Read).

## Read Before Edit

Always read a file before modifying it. Edit will fail if the old_string is not present—
use Read first to confirm the exact text to replace.

## CLAUDE.md Imports

Reference other files in CLAUDE.md using `@path/to/file` syntax to keep individual
files focused and under 200 lines.
