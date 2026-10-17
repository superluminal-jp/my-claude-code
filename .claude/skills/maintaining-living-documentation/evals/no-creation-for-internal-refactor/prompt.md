---
description: A private helper is renamed; no document is created or edited and the report says there is no impact.
max_turns: 30
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, TaskCreate, TaskUpdate, TaskList]
---

In pkg/text.py, rename the private helper `_norm` to `_normalize`. Keep the behavior the same.
