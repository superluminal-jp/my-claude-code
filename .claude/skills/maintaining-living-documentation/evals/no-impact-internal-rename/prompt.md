---
description: A behavior-preserving rename; documentation must stay untouched and the report must say there is no impact.
max_turns: 30
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, TaskCreate, TaskUpdate, TaskList]
---

In app.py, rename the local variable `t` in timeout_seconds() to `value`. Keep the behavior the same.
