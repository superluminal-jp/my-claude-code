---
description: A change reverses an accepted decision. The record must be proposed, not created, and the accepted record must stay untouched.
max_turns: 30
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, TaskCreate, TaskUpdate, TaskList]
---

Switch store.py from the JSON file to SQLite (standard library sqlite3), keeping the same load and save functions.
