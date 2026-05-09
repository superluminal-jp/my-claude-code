# Research: OpenAI Codex Review Skill

**Feature**: 007-codex-review-skill  
**Date**: 2026-05-10

## Decision Log

---

### 1. Codex CLI Invocation for Read-Only Review

**Decision**: Invoke `codex` with `--approval-policy suggest` (or the default suggest mode) and a prompt that explicitly instructs it to report findings only, without applying edits. The skill captures stdout.

**Rationale**: The `codex` CLI (`openai/codex` npm package) defaults to suggest mode, where it proposes changes but does not apply them without user approval. By running it non-interactively with a review-focused prompt and piping the output, we get a read-only advisory result. No `--full-auto` or `--dangerously-auto-approve-everything` flags are used.

**Invocation pattern**:
```
codex --quiet --approval-policy suggest \
  "Review the following files for [perspective]. Report findings only; do not edit files." \
  -- [file ...]
```

If `--quiet` and non-interactive invocation are not supported in the installed version, fall back to running `codex` on a prompt file via stdin redirection.

**Alternatives considered**:
- Direct OpenAI API call (`curl` or `openai` CLI): avoids the `codex` CLI entirely, but contradicts the spec requirement; deferred.
- `--full-auto` mode: applies edits automatically — rejected as it violates the read-only constraint.

---

### 2. Artifact Collection Modes

**Decision**: Three modes, default to `git-changed`.

| Mode | Command | Notes |
|------|---------|-------|
| `git-changed` (default) | `git diff --name-only HEAD` | Falls back to `git status --short` when HEAD doesn't exist (initial commit) |
| `user-specified` | Paths passed as arguments to `/review` | Glob expansion handled by shell before passing to skill |
| `speckit-docs` | Enumerate `specs/{FEATURE_DIR}/*.md` | Reads `feature.json` to resolve FEATURE_DIR |

When no artifacts are found in `git-changed` mode, the skill exits with an informative message rather than an error.

**Alternatives considered**:
- `git diff --staged` only: misses unstaged working-tree changes that Claude Code may have written — rejected.
- Always requiring user to specify files: reduces frictionless use — rejected for default mode.

---

### 3. Review Perspectives: Prompt Strategy

**Decision**: Use two fixed prompt templates embedded in the SKILL.md — one for code quality, one for security — combined into a single Codex invocation.

**Quality prompt focus**: correctness, naming, readability, dead code, error handling, maintainability.  
**Security prompt focus**: OWASP Top 10 classes (injection, auth, sensitive data, misconfiguration), hardcoded secrets, unsafe deserialization.

Both perspectives are applied by default. When the user passes `--perspectives quality` or `--perspectives security`, only the corresponding section is included.

**Rationale**: A single Codex invocation with a combined prompt is cheaper (one API call) and produces a coherent review report. Splitting into two sequential calls would double cost and latency with no measurable quality gain.

**Alternatives considered**:
- Separate prompt files in `prompts/` subdirectory: adds filesystem complexity for minimal benefit; rejected.
- LLM-generated dynamic prompt per invocation: unpredictable results; rejected.

---

### 4. Skill File Structure

**Decision**: Single `SKILL.md` in `.claude/skills/review/`. No auxiliary files needed.

**Rationale**: All project skills follow this pattern. The prompts are short enough to inline. No shell scripts are required because the skill instructs Claude Code to run shell commands directly (the existing project pattern for prerequisite checks).

**Deliverables**:
- `.claude/skills/review/SKILL.md` — complete skill definition

---

### 5. Hook Registration (opt-in `after_implement`)

**Decision**: Add an `after_implement` entry to `.specify/extensions.yml` with `enabled: false` and `optional: true`. Users opt in by setting `enabled: true`.

**Rationale**: Matches the Q3 decision (C) — on-demand by default, opt-in hook. The `enabled: false` default ensures the hook is documented but inactive until the user consciously enables it, avoiding surprise reviews on every implementation run.

**Hook entry**:
```yaml
after_implement:
  - extension: codex-review
    command: review
    enabled: false
    optional: true
    prompt: Run Codex review after implementation?
    description: Review implemented artifacts with OpenAI Codex for quality and security
    condition: null
```

---

### 6. Prerequisite Check Strategy

**Decision**: Check both prerequisites at skill entry before any artifact collection or Codex invocation.

- **API key**: `[[ -z "$OPENAI_API_KEY" ]]` — check env var presence. Does not validate the key value (avoids an unnecessary API call at startup).
- **Codex CLI**: `command -v codex` — standard shell PATH check.

If either check fails, output a message naming the missing prerequisite and the fix command, then exit without calling Codex.

**Alternatives considered**:
- Lazy check (fail when Codex is actually called): produces a less clear error from the Codex process itself — rejected.
- Validate API key with a test call: adds latency and consumes quota — rejected.
