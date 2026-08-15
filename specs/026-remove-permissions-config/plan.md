# Implementation Plan: Remove the permissions Block Entirely

**Branch**: `026-remove-permissions-config` | **Date**: 2026-08-16 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/026-remove-permissions-config/spec.md`

## Summary

Delete the `permissions` key from `.claude/settings.json` and
`.claude/settings.local.json`, with no replacement — the last automated
protection this repository's Claude Code configuration had, following
directly from spec-025/ADR-0005. Correct six cascading documents that
asserted the permissions block "remains"/"is the one guardrail"/"stays on
ask" (`permissions.md`, README.md, README.ja.md, AGENTS.md,
`git-workflow.md`, `tests/run-codex-references.sh` RULE-09). Record the
decision in a new ADR (0006) rather than editing the now-Accepted,
immutable ADR-0005.

## Technical Context

**Language/Version**: N/A — JSON/Markdown/Bash edits only.

**Primary Dependencies**: None.

**Testing**: Existing `tests/run-*.sh`; one rule (RULE-09) removed from
`run-codex-references.sh`.

**Target Platform**: This repository, and every other project once
`install.sh` next syncs `settings.json`.

**Project Type**: Single project — configuration repository.

**Scale/Scope**: 2 JSON edits, 5 doc edits, 1 test edit, 1 new ADR file.

## Constitution Check

No project-specific constitution ratified (template unfilled). Applicable
repository rules satisfied: `clarifier.md` (scope confirmed via
`AskUserQuestion` before this spec), `permissions.md`/`CLAUDE.md`
close-out (ADR proposed, not silently skipped — FR-009), `adr` skill policy
(ADR-0005 not edited in substance — FR-008), `live-documentation.md`
(cascading doc corrections in the same change, not deferred).

## Project Structure

### Documentation (this feature)

```text
specs/026-remove-permissions-config/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── tasks.md
```

No `contracts/`.

### Source Code (repository root)

```text
my-claude-code/
├── .claude/
│   ├── settings.json                # edit: remove permissions key
│   ├── settings.local.json          # edit: remove permissions key
│   └── rules/
│       ├── permissions.md           # edit: 2 locations
│       └── git-workflow.md          # edit: 1 location
├── README.md                        # edit: 3 locations
├── README.ja.md                     # edit: 3 locations
├── AGENTS.md                        # edit: 1 location
└── tests/
    └── run-codex-references.sh      # edit: remove RULE-09
```

Plus `docs/adr/0006-remove-permissions-config.md` (new, via `adr` skill).

**Structure Decision**: No structural change — deletions/edits within
existing files, one new ADR.

## Complexity Tracking

Not applicable — no constitution violations.
