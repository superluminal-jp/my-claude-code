# Implementation Plan: Clarify Skill Pre-Trigger on Speckit Specify

**Branch**: `008-clarify-pretrigger-specify` | **Date**: 2026-05-26 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `specs/008-clarify-pretrigger-specify/spec.md`

## Summary

Add the clarifier skill as the first `before_specify` hook in `.specify/extensions.yml` so that `/speckit-specify` optionally prompts users to run `/clarifier` before generating the spec. The clarified Q&A is carried forward through Claude Code conversation context and incorporated into the generated spec automatically. Implementation is a single YAML entry — no skill files or playbook changes required.

## Technical Context

**Language/Version**: N/A — Markdown + YAML configuration files only  
**Primary Dependencies**: `.specify/extensions.yml` (hook registry), `.claude/skills/clarifier/SKILL.md` (already implemented)  
**Storage**: Filesystem (YAML, Markdown)  
**Testing**: Manual — run `/speckit-specify <description>` and verify clarifier hook is presented  
**Target Platform**: Claude Code CLI  
**Project Type**: Configuration (YAML + Markdown skill definitions)  
**Performance Goals**: N/A (human-turn-based interaction, no automated execution)  
**Constraints**: Must not break existing `before_specify` hooks (ubiquitous-language, speckit.git.feature)  
**Scale/Scope**: Single YAML entry addition

## Constitution Check

*Constitution is an unfilled template (no project-specific principles ratified). No governance gates apply.*

Re-check after Phase 1: N/A — no violations found.

## Project Structure

### Documentation (this feature)

```text
specs/008-clarify-pretrigger-specify/
├── plan.md              ← this file
├── research.md          ← Phase 0 output
├── data-model.md        ← Phase 1 output
├── quickstart.md        ← Phase 1 output
├── contracts/
│   └── before-specify-hook.md  ← Phase 1 output
├── checklists/
│   └── requirements.md
└── tasks.md             ← Phase 2 output (/speckit-tasks — not yet created)
```

### Source Code (repository root)

```text
.specify/
└── extensions.yml       ← modify: add clarifier entry to before_specify (first position)
```

**Structure Decision**: Configuration-only change. No src/ or tests/ directories are needed because the feature is a YAML entry, not executable code. Verification is manual (run the slash command and observe hook output).

## Complexity Tracking

No constitution violations. Table omitted.
