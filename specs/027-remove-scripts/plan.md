# Implementation Plan: Remove scripts/ Entirely

**Branch**: `027-remove-scripts` | **Date**: 2026-08-16 | **Spec**: [spec.md](./spec.md)

## Summary

Delete `scripts/guardrails/` (4 files), its 4 dedicated test suites, and the
unrelated `scripts/check-mcp-consistency.sh` — the third and final step in
the specs/025→026→027 decision arc. `scripts/` disappears entirely.
`install.sh`'s conditional guardrails-sync block becomes an unconditional
cleanup step (uninstall path), mirroring specs/025's `sync_path "hooks"`
precedent. Corrects README.md/README.ja.md (bullets, file tree, Verification
command list, two Codex-comparison sentences), `permissions.md`, and
`mcp.md`. Records the decision in a new ADR (0007) referencing ADR-0005 and
ADR-0006 without editing either.

## Technical Context

**Language/Version**: N/A — Markdown/Bash edits and deletions only.

**Testing**: 4 test suites deleted (their subject is gone); remaining suites
unaffected.

**Scale/Scope**: 9 file deletions, 5 file edits, 1 new ADR.

## Constitution Check

No project-specific constitution ratified. Applicable rules satisfied:
`clarifier.md` (two `AskUserQuestion` rounds completed before this spec),
`adr` skill policy (0005/0006 not edited — FR-008), `live-documentation.md`
(cascading corrections in the same change).

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
├── install.sh                            # edit: unconditional cleanup step
├── README.md                             # edit: 5 locations
├── README.ja.md                          # edit: 3 locations
├── .claude/rules/
│   ├── permissions.md                    # edit: 1 location
│   └── mcp.md                            # edit: 1 location
├── scripts/                              # delete: entire directory
└── tests/
    ├── run-destructive-command-guard.sh  # delete
    ├── run-pre-edit-guard.sh             # delete
    ├── run-post-edit-format-guard.sh     # delete
    └── run-prompt-secret-guard.sh        # delete
```

Plus `docs/adr/0007-remove-scripts.md` (new).

## Complexity Tracking

Not applicable.
