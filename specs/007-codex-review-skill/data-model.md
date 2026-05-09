# Data Model: OpenAI Codex Review Skill

**Feature**: 007-codex-review-skill  
**Date**: 2026-05-10

## Entities

### ArtifactMode

Enum controlling which files are collected for review.

| Value | Description | Resolution |
|-------|-------------|------------|
| `git-changed` | Files changed since last commit (default) | `git diff --name-only HEAD` |
| `user-specified` | Explicit paths/globs passed as arguments | Skill arguments, shell-expanded |
| `speckit-docs` | Speckit markdown documents for the current feature | Resolved from `.specify/feature.json` → `specs/{FEATURE_DIR}/*.md` |

**Default**: `git-changed`  
**Constraint**: At least one file must resolve; if empty, skill exits with informative message.

---

### ReviewPerspective

Enum selecting which review lenses to apply.

| Value | Prompt Focus |
|-------|-------------|
| `quality` | Correctness, naming, readability, dead code, error handling, maintainability |
| `security` | OWASP Top 10 classes, hardcoded secrets, unsafe patterns |

**Default**: both (`quality` + `security`)  
**Constraint**: At least one perspective must be selected.

---

### PrerequisiteCheck

Guard evaluated before any artifact collection or Codex invocation.

| Check | Method | Failure message |
|-------|--------|----------------|
| `OPENAI_API_KEY` set | `[[ -z "$OPENAI_API_KEY" ]]` | "OPENAI_API_KEY is not set. Export it with: export OPENAI_API_KEY=sk-..." |
| `codex` CLI installed | `command -v codex` | "`codex` is not installed. Install with: npm install -g @openai/codex" |

**Constraint**: Both must pass before proceeding. Failures are independent — report all that fail.

---

### ReviewResult

Output produced by a single skill invocation.

| Field | Description |
|-------|-------------|
| `artifacts_reviewed` | List of file paths passed to Codex |
| `perspectives_applied` | List of perspectives used |
| `codex_output` | Raw structured text from Codex stdout |
| `status` | `success` \| `no-artifacts` \| `prereq-failed` \| `codex-error` |

**Constraint**: `codex_output` is displayed verbatim in the Claude Code conversation. The skill does not post-process or summarize Codex output — the raw result is the deliverable.

---

## State Transitions

```
INVOKED
  └─► PrerequisiteCheck
        ├─ FAIL → output error message → EXIT (prereq-failed)
        └─ PASS
             └─► ArtifactCollection (mode = ArtifactMode)
                   ├─ EMPTY → output "no artifacts found" → EXIT (no-artifacts)
                   └─ NON-EMPTY
                        └─► CodexInvocation (perspectives = ReviewPerspective[])
                              ├─ ERROR → output actionable error → EXIT (codex-error)
                              └─ SUCCESS → display ReviewResult.codex_output → EXIT (success)
```
