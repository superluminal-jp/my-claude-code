---
description: A new public module is added where nothing documents the package; one document is created, with no decision record and no changelog.
max_turns: 30
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, TaskCreate, TaskUpdate, TaskList]
---

Add a new public module pkg/purge.py that exposes purge(directory, days), which deletes the files in the directory that are older than the given number of days.
