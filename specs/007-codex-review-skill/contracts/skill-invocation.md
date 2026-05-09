# Contract: review Skill Invocation

**Type**: Claude Code slash command  
**Command**: `/review`  
**Feature**: 007-codex-review-skill

## Invocation Signature

```
/review [--artifacts <mode>] [--perspectives <perspective>[,<perspective>]] [<file> ...]
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--artifacts` | `git-changed` \| `user-specified` \| `speckit-docs` | `git-changed` | Artifact collection mode. `user-specified` requires `<file>` arguments. |
| `--perspectives` | Comma-separated list of `quality`, `security` | `quality,security` | Review lenses to apply. |
| `<file> ...` | File path(s) or glob(s) | — | Required when `--artifacts user-specified`; ignored otherwise. |

## Examples

```bash
# Default: review git-changed files for quality and security
/review

# Review only for security
/review --perspectives security

# Review specific files for quality
/review --artifacts user-specified --perspectives quality src/auth.ts src/middleware.ts

# Review speckit documents for both perspectives
/review --artifacts speckit-docs
```

## Exit Conditions

| Status | Trigger | Output |
|--------|---------|--------|
| `success` | Codex returns output | Codex review result displayed in conversation |
| `no-artifacts` | No files resolved for the selected mode | Informative message: which mode, why empty |
| `prereq-failed` | API key or CLI missing | Named prerequisite + install/export instructions |
| `codex-error` | Codex exits non-zero | Actionable error message (no raw stack trace) |

## Hook Registration (opt-in)

To enable automatic review after `/speckit-implement`, set `enabled: true` in `.specify/extensions.yml`:

```yaml
after_implement:
  - extension: codex-review
    command: review
    enabled: true   # change from false to opt-in
    optional: true
    prompt: Run Codex review after implementation?
    description: Review implemented artifacts with OpenAI Codex for quality and security
    condition: null
```

When triggered as a hook, the skill runs with the `git-changed` artifact mode and both perspectives applied (no arguments passed by the hook runner).
