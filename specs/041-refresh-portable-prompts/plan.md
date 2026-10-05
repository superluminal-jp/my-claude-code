# Implementation Plan: Refresh Portable System Prompts

**Branch**: `041-refresh-portable-prompts` | **Date**: 2026-10-05 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/041-refresh-portable-prompts/spec.md`

## Summary

Rewrite `chatgpt-system-prompt.md` and `claude-ai-system-prompt.md` so each (a) conveys the universal behaviors of the current `.claude/` rules, (b) states only service facts verified on 2026-10-05 from official pages, and (c) records its own provenance and omissions in the file. Research ([research.md](./research.md)) found three material drifts in the current files: ChatGPT's limit is plan-dependent (1,500 Free/Go, 5,000 paid) and the "More about you" field is undocumented officially; ChatGPT cannot be told to change its thinking level and memory cannot be set off from a prompt; Claude.ai's field is "Instructions for Claude" with no documented limit, memory is system-managed, and agent-tooling sections (parallel calls, delegation) have no verified equivalent.

Approach is check-first: write the quickstart's length/forbidden-content check (red against the current files), rewrite the files (green), then run the documentation checks.

## Technical Context

**Language/Version**: Markdown; Python 3 one-liner for length measurement. No runtime code.

**Primary Dependencies**: Official vendor help pages listed in research.md (read 2026-10-05).

**Storage**: Files under version control.

**Testing**: [quickstart.md](./quickstart.md) steps 1–2 are scriptable (length, forbidden terms); steps 3–4 are a manual read-through. No existing test covers the root prompt files (`grep` of `tests/`, `README*`, `docs/`, `install.sh` found no reference).

**Target Platform**: ChatGPT (web/desktop/mobile) and Claude.ai (web/desktop/mobile), pasted manually.

**Project Type**: Documentation / configuration artifacts.

**Constraints**: FR-010 — touch only the two root files and this feature's specs; `.claude/`, installer, tests unchanged. Budgets in [data-model.md](./data-model.md).

**Scale/Scope**: 2 files rewritten; 3 paste blocks.

## Constitution Check

`.specify/memory/constitution.md` is still the unfilled template, so no ratified principle gates this feature; the gate passes formally. Evaluated instead against the repository's always-on rules: authorization (no `.claude/` or external changes — pass), requirements certainty (spec has no open markers — pass), living documentation (service facts carry source and date; see below — pass), reader-facing structure (prompts lead with the answer — pass).

Post-design re-check: pass; no new violations introduced by design artifacts.

## Project Structure

### Documentation (this feature)

```text
specs/041-refresh-portable-prompts/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/portable-prompt-contract.md
└── tasks.md          # created by /speckit-tasks
```

### Deliverables (repository root)

```text
chatgpt-system-prompt.md      # rewritten
claude-ai-system-prompt.md    # rewritten
```

**Structure Decision**: Provenance (verified facts, omissions) lives **inside each prompt file**, closest to the scope where it is true; full evidence stays in `research.md`. No new `docs/` file and no ADR (none requested; the decision is reversible and local — propose only if the owner wants one).

## Design Decisions

| # | Decision | Reason (research ref) |
|---|---|---|
| D1 | ChatGPT: keep two blocks; main block ≤1,500 so it pastes on all plans; note paid 5,000 | R1 |
| D2 | Label "More about you" as UI-observed, officially undocumented | R1 |
| D3 | Drop "Memory off—this thread only"; no model names; no thinking-level instructions | R2 |
| D4 | Recommend base style "Efficient" in the file header, as an owner-side setting | R2 |
| D5 | Claude.ai: label "Instructions for Claude"; add placement header; no documented limit, self-budget ≤ ~4,000 | R3 |
| D6 | Claude.ai: replace memory-write and Execution Efficiency sections; port authorization and reasoning completeness | R4, R6 |
| D7 | Wording: positive phrasing, short rationales, no all-caps emphasis, explicit brevity | R5 |
| D8 | model-routing and skills recorded under "Not ported" in both files | R2, R6 |

## Complexity Tracking

No constitution violations to justify.

## Documentation Impact

`README.md` / `README.ja.md` do not mention these files; no sync required unless the implementation changes that. Re-verify with `grep` after editing.
