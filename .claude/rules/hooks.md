---
name: Hook Configuration Rules
description: How hooks should be configured and maintained in this project
type: rules
---

# Hook Configuration Rules

## Hook Script Conventions

- Store hook scripts in `.claude/hooks/`
- Name scripts by event: `pre-bash.sh`, `post-write.sh`, `session-start.sh`
- Make scripts executable: `chmod +x .claude/hooks/*.sh`
- Reference with quoted `$CLAUDE_PROJECT_DIR`: `"$CLAUDE_PROJECT_DIR"/.claude/hooks/script.sh`

## Exit Code Semantics

| Code | Meaning          | Behavior                          |
|------|------------------|-----------------------------------|
| 0    | Success          | Action proceeds                   |
| 2    | Blocking error   | Action blocked; stderr shown to Claude |
| 1    | Non-blocking     | Logged; action proceeds           |

Use exit code **2** to enforce policy, not exit code 1.

## JSON Output Format

When a hook needs to communicate back:
```json
{
  "continue": true,
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow|deny|ask",
    "permissionDecisionReason": "Reason string"
  }
}
```

## Hook Event Reference

| Event              | Use for                                           |
|--------------------|---------------------------------------------------|
| `PreToolUse`       | Block or audit tool calls before execution        |
| `PostToolUse`      | Run linters, formatters after file writes         |
| `SessionStart`     | Load environment, display project info            |
| `Stop`             | Run cleanup or summary before Claude stops        |
| `UserPromptSubmit` | Add context or block prompts before processing    |
