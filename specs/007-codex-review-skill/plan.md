# Implementation Plan: OpenAI Codex Review Skill

**Branch**: `007-codex-review-skill` | **Date**: 2026-05-10 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `specs/007-codex-review-skill/spec.md`

## Summary

Add a `/review` skill to Claude Code that runs OpenAI Codex over user-selected artifacts and reports quality and security findings. The skill checks for `OPENAI_API_KEY` and the `codex` CLI at startup and exits with actionable messages when either is missing. Artifacts are selectable per invocation (git-changed files by default, user-specified paths, or speckit documents). Both code quality and security perspectives are applied by default; each is selectable individually. The skill is on-demand by default and supports opt-in registration as an `after_implement` hook.

## Technical Context

**Language/Version**: Markdown (SKILL.md) — no compiled runtime; shell commands issued by Claude Code  
**Primary Dependencies**: `codex` CLI (`@openai/codex`, npm), `OPENAI_API_KEY` env var, `git` (for `git-changed` mode)  
**Storage**: Stateless — reads filesystem and git; writes nothing  
**Testing**: Manual invocation against a test fixture; shell command validation  
**Target Platform**: Claude Code CLI on macOS/Linux (bash required)  
**Project Type**: Claude Code skill (markdown SKILL.md)  
**Performance Goals**: Prerequisite check < 1 s; full review delivered < 60 s (Codex response bound)  
**Constraints**: Read-only — skill never modifies files; bash available; internet access required for Codex API call

## Constitution Check

Constitution file contains placeholder content only — no project-specific gates are defined. No violations to evaluate.

## Project Structure

### Documentation (this feature)

```text
specs/007-codex-review-skill/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── skill-invocation.md   # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit-tasks)
```

### Source Code (repository root)

```text
.claude/skills/review/
└── SKILL.md             # Skill definition (sole deliverable)

.specify/
└── extensions.yml       # Modified: add after_implement hook entry (enabled: false)
```

**Structure Decision**: Single-file skill following the project's existing pattern (`coder/SKILL.md`, `ubiquitous-language/SKILL.md`, etc.). No auxiliary scripts or prompt files are needed — prompts are inlined in SKILL.md.

## Complexity Tracking

No constitution violations. No complexity justification required.

---

## Implementation Notes

### SKILL.md structure

The skill file must contain:

1. **YAML frontmatter** — `name`, `description`, `argument-hint`, `user-invocable: true`
2. **Prerequisite Check section** — shell commands to verify `OPENAI_API_KEY` and `codex`
3. **Argument Parsing section** — resolve `--artifacts`, `--perspectives`, and `<file>` args with defaults
4. **Artifact Collection section** — one branch per `ArtifactMode`; empty-set guard
5. **Codex Invocation section** — combined quality+security prompt with per-perspective sections; captures stdout
6. **Output section** — display `ReviewResult` in conversation; handle non-zero exit

### extensions.yml change

Append the following to the `after_implement` list in `.specify/extensions.yml`:

```yaml
  - extension: codex-review
    command: review
    enabled: false
    optional: true
    prompt: Run Codex review after implementation?
    description: Review implemented artifacts with OpenAI Codex for quality and security
    condition: null
```

The `enabled: false` default ensures existing workflows are unaffected until the user opts in.
