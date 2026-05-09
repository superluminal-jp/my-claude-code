# Quickstart: OpenAI Codex Review Skill

## Prerequisites

1. **OpenAI API key** — export before use:
   ```bash
   export OPENAI_API_KEY=sk-...
   ```

2. **Codex CLI** — install once:
   ```bash
   npm install -g @openai/codex
   ```

3. **Git repository** — required for `git-changed` artifact mode (default).

## Basic Usage

After implementing a feature with Claude Code, run:

```
/review
```

This reviews all files changed since the last commit, applying both code quality and security lenses.

## Selecting Perspectives

Review only for security vulnerabilities:

```
/review --perspectives security
```

Review only for code quality:

```
/review --perspectives quality
```

## Selecting Artifacts

Review specific files:

```
/review --artifacts user-specified src/auth.ts src/utils/validation.ts
```

Review speckit spec/plan/tasks documents:

```
/review --artifacts speckit-docs
```

## Opt-In Automation (after each implementation)

To automatically run the review after every `/speckit-implement`, edit `.specify/extensions.yml`:

```yaml
after_implement:
  - extension: codex-review
    command: review
    enabled: true   # was false — change this to opt in
    optional: true
    ...
```

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `OPENAI_API_KEY is not set` | `export OPENAI_API_KEY=sk-...` in your shell |
| `` `codex` is not installed `` | `npm install -g @openai/codex` |
| `no artifacts found` in git-changed mode | Stage or commit files first, or use `--artifacts user-specified` |
| Codex times out on large artifact sets | Use `--artifacts user-specified` to pass a subset of files |
