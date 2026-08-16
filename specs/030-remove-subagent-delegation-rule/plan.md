# Implementation Plan: Remove subagent-delegation Rule

**Branch**: `030-remove-subagent-delegation-rule` | **Date**: 2026-08-16 | **Spec**: [spec.md](./spec.md)

## Summary

Delete `.claude/rules/subagent-delegation.md` in full and remove every live
pointer to it: the `@`-include and cross-reference sentence in
`.claude/CLAUDE.md`'s "Execution: parallelize whenever valid" section, and
the file-tree listing line in `README.md`. No replacement guidance is added
anywhere — the rule's judgment content is treated as default model behavior
that does not need to be spelled out, and the removal's stated purpose is
reducing the always-loaded context size of `.claude/CLAUDE.md`. Historical
`specs/` directories that mention the file are left untouched, matching the
precedent set by specs/018, 024–027, and 029.

## Technical Context

**Language/Version**: Markdown only (no code, no build, no runtime).

**Primary Dependencies**: None — plain file edits.

**Storage**: N/A.

**Testing**: Repository-wide text search (`grep -r`) verifying zero live
references outside `specs/` and `docs/adr/`; manual read-through of the two
edited files (`CLAUDE.md`, `README.md`) for internal coherence, mirroring
how specs/025–027 verified documentation-only changes.

**Target Platform**: N/A — repository instruction files consumed by Claude
Code sessions.

**Project Type**: Internal tooling / instruction-file maintenance (not a
software project with a runtime).

**Performance Goals**: N/A. The only "performance" dimension is the
always-loaded context reduction captured in spec.md SC-003 (line-count
delta), not a runtime metric.

**Constraints**: No replacement content added anywhere (per spec FR-007).
Historical `specs/` and `docs/adr/` untouched (per spec FR-006).

**Scale/Scope**: Three files touched: one deletion
(`.claude/rules/subagent-delegation.md`), two edits (`.claude/CLAUDE.md`,
`README.md`).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

No project-specific constitution has been ratified (`.specify/memory/constitution.md`
is still the unfilled template). Applicable repository-level rules instead:

- `rules/live-documentation.md` — this change touches no source code with a
  public contract; it edits instruction/rule prose directly, so Drift
  Detection (§1) does not apply. No new Documentation Artifact is created,
  so §§3–5 (auto-generation, proximity, no-redundancy) do not apply either.
- `rules/git-workflow.md` — branch already created via
  `030-remove-subagent-delegation-rule` per convention; commits only on
  explicit request.
- Close-out ADR check (`.claude/CLAUDE.md`): no ADR proposed — this is a
  two-way-door, git-reversible removal of instruction text, not an
  architecturally significant decision with a rejected implementation
  alternative (spec.md Assumptions), consistent with specs/018 and 029.

Gate: PASS. No violations to justify.

## Project Structure

### Documentation (this feature)

```text
specs/030-remove-subagent-delegation-rule/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── quickstart.md        # Phase 1 output (verification guide)
└── tasks.md             # Phase 2 output (/speckit-tasks command)
```

No `data-model.md` or `contracts/` — this feature has no entities and no
external interface; it deletes a file and edits prose in two others.

### Source Code (repository root)

```text
my-claude-code/
├── .claude/
│   ├── rules/
│   │   └── subagent-delegation.md   # delete entirely
│   └── CLAUDE.md                    # edit: drop @-include + cross-reference sentence
└── README.md                        # edit: drop file-tree listing line
```

## Complexity Tracking

Not applicable — no constitution violations.
