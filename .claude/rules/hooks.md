# Hook Configuration Rules

## Script conventions

- Location: `.claude/hooks/`; name by event (`pre-bash.sh`, `post-write.sh`, `session-start.sh`)
- Executable: `chmod +x .claude/hooks/*.sh`
- Reference with quoted `$CLAUDE_PROJECT_DIR`: `"$CLAUDE_PROJECT_DIR"/.claude/hooks/script.sh`

## Exit codes

| Code | Meaning | Behavior |
|---|---|---|
| 0 | Success | Action proceeds |
| 1 | Non-blocking | Logged; action proceeds |
| 2 | Blocking error | Action blocked; stderr shown to Claude |

Use **2** (not 1) to enforce policy.

## JSON response (when hook needs to decide)

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

## Events

| Event | Use for |
|---|---|
| `PreToolUse` | Block or audit tool calls before execution |
| `PostToolUse` | Run linters / formatters after file writes |
| `SessionStart` | Load environment, show project info |
| `Stop` | Cleanup or summary before Claude stops |
| `UserPromptSubmit` | Add context or block prompts before processing |
