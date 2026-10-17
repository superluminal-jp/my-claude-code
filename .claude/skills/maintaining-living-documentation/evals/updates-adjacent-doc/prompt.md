---
description: A new option is added to a tool whose README sits next to it; the README must follow.
max_turns: 30
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, TaskCreate, TaskUpdate, TaskList]
---

In tools/convert.py, add a `--quiet` flag that suppresses the progress messages.
