# Implementation Plan: Remove scripts/ Entirely

**Branch**: `027-remove-scripts` | **Date**: 2026-08-16 | **Spec**: [spec.md](./spec.md)

## Summary

Complete the scripts-removal follow-up by making `install.sh` an exact,
tested projection of the repository-managed Claude Code configuration. The
installer replaces only its declared managed paths, adds `agents/`, removes
stale formerly-managed paths, preserves unrelated user files, drops unused
dependencies and source-tree mutation, and is verified against an isolated
home directory. Remove Claude-authenticated and orphaned test assets. Remove
the draw.io capability completely (MCP entry, skill, routing, and catalog
documentation), then update live documentation and remaining structural tests.

## Technical Context

**Language/Version**: Bash, Markdown, and JSON only.

**Testing**: New deterministic `tests/run-install.sh`; remaining structural and
MCP startup suites. Claude CLI prompt-evaluation suites are removed by explicit
maintainer decision.

**Scale/Scope**: Installer refactor, one new test runner, removal of three
authenticated runners and four fixture trees, removal of one MCP-backed skill,
and synchronized rule/README/spec updates.

## Constitution Check

No project-specific constitution ratified. Applicable rules satisfied:
`speckit-clarify` recorded five maintainer decisions, `coder` requires the
isolated-home test before the installer refactor, and `live-documentation.md`
requires README/rule updates in the same change. ADR-0005/0006 remain
immutable; ADR-0007 continues to require retired guardrail cleanup.

## Project Structure

### Documentation (this feature)

```text
specs/027-remove-scripts/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── tasks.md
```

### Source Code (repository root)

```text
my-claude-code/
├── install.sh                            # edit: exact declared-path sync
├── README.md                             # edit: installer/test inventory
├── README.ja.md                          # edit: mirrored inventory
├── .mcp.json                             # edit: remove drawio
├── .claude/rules/
│   ├── mcp.md                            # edit: remove drawio catalog entries
│   └── skill-routing.md                  # edit: remove drawio routing
├── .claude/skills/
│   ├── coder/SKILL.md                    # edit: remove drawio composition
│   └── drawio/                           # delete
└── tests/
    ├── run-install.sh                    # add: isolated-home contract
    ├── run-codex-references.sh           # edit: current live surfaces
    ├── run-{live-documentation,skill-routing,type-safety-coder}.sh # delete
    └── {live-documentation,skill-routing,type-safety-coder,ubiquitous-language}/ # delete
```

## Complexity Tracking

Not applicable.
