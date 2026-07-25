# Implementation Plan: Digital Agency Frontend Skill

**Branch**: `015-digital-agency-frontend` | **Date**: 2026-07-20 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/015-digital-agency-frontend/spec.md`

## Summary

Add one globally distributed `digital-agency-frontend` skill for React and Tailwind CSS frontend work based on the Digital Agency Design System and dashboard guidebook. Keep the core workflow concise in `SKILL.md`, place source-backed implementation and dashboard guidance in two progressively loaded references, expose the authored Claude skill to Codex through the existing symlink model, and extend static contract, installer, sync, and documentation coverage.

## Technical Context

**Language/Version**: Markdown with YAML frontmatter; POSIX-oriented Bash tests; Python 3 for the standard skill validator

**Primary Dependencies**: Agent Skills `SKILL.md` format, existing `clarifier` and `coder` skills, Digital Agency Design System v2 sources, Digital Agency React/Tailwind examples, Digital Agency dashboard guidebook

**Storage**: Repository files only; no runtime data store

**Testing**: New deterministic shell contract suite, `skill-creator` `quick_validate.py`, `tests/run-codex-sync.sh`, `tests/run-codex-sync-drift.sh`, `tests/run-live-documentation.sh`, `tests/run-post-edit-format-guard.sh`, `git diff --check`

**Target Platform**: Claude Code and Codex CLI user-level configuration on macOS/Linux-compatible shells

**Project Type**: Cross-agent configuration and reusable skill package

**Performance Goals**: The always-visible routing metadata remains one concise description; the main skill stays below 500 lines; dashboard-only detail is not loaded for general frontend work

**Constraints**: React/Tailwind CSS only; web artifacts only; no Power BI generation; one authored skill body; official live sources override bundled summaries; JIS X 8341-3:2016 AA and WCAG 2.2 AA baselines; no wholesale copies of official publications

**Scale/Scope**: One skill package, two bundled reference files, one UI metadata file, one cross-agent symlink, one dedicated contract suite, and synchronized installer/routing/user documentation updates

## Constitution Check

*GATE: Passed before Phase 0 and re-checked after Phase 1.*

The repository constitution is still an unfilled template, so enforce the operative repository guidance instead:

- **Spec-driven**: `spec.md` contains testable behavior and no unresolved clarification markers. Pass.
- **TDD**: Add the dedicated contract suite and make it fail before creating the skill or sync registration. Pass by task ordering.
- **Single source**: Author only under `.claude/skills/digital-agency-frontend`; expose Codex through a relative symlink and installed global symlink. Pass.
- **Progressive disclosure**: Keep workflow in `SKILL.md`; load DADS and dashboard details from direct references only when needed. Pass.
- **Live documentation**: Update installer, routing guidance, deployment map, and both README languages in the same change. Pass.
- **Security and licensing**: Use official HTTPS sources, copy no secrets, vendor no external executables, and record attribution/licensing guidance. Pass.
- **No one-way door**: Extend existing skill and sync patterns without introducing a new agent mechanism or dependency. No ADR required.

Post-design re-check: the planned two-reference structure, deterministic validation, and existing symlink deployment model satisfy all gates without exceptions.

## Project Structure

### Documentation (this feature)

```text
specs/015-digital-agency-frontend/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── skill-interface.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
.claude/
├── CLAUDE.md
└── skills/
    └── digital-agency-frontend/
        ├── SKILL.md
        ├── agents/
        │   └── openai.yaml
        └── references/
            ├── dads-react-tailwind.md
            └── dashboard-design.md

.agents/
└── skills/
    └── digital-agency-frontend -> ../../.claude/skills/digital-agency-frontend

.codex/
├── AGENTS.md
└── README.md

tests/
├── run-digital-agency-frontend-skill.sh
├── run-codex-sync.sh
└── run-codex-sync-drift.sh

README.md
README.ja.md
install.sh
```

**Structure Decision**: Follow the repository's existing authored-Claude-skill plus Codex-symlink architecture. Include `agents/openai.yaml` as skill UI metadata and exactly two first-level reference files. Do not add scripts or assets because there is no deterministic transformation or reusable output artifact that would justify them.

## Complexity Tracking

No constitution or repository-guidance violations require justification.
