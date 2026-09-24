# Implementation Plan: Model and Effort Routing Rule

**Branch**: `040-model-routing-rule` | **Date**: 2026-09-24 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/040-model-routing-rule/spec.md`

## Summary

Add one always-on rule, `.claude/rules/model-routing.md`, carrying the source draft's tiers, escalation limits, hand-back rule, effort levels, and delegation preferences, reshaped to the sibling rule layout. Add its Japanese counterpart, extend the structure check from five to six rules with an ownership assertion, and synchronize every artifact that states the rule count or lists the rules. No apex, skill, existing rule, or ADR changes (ADR declined in clarification).

The approach is test-first: change the structure check to expect six rules and the new ownership assertion (red), add the rule files (green), then synchronize documentation.

## Technical Context

**Language/Version**: Markdown (rule content and docs); Bash (structure contract test). No runtime code.

**Primary Dependencies**: Claude Code's unconditional loading of every file under the rules directory (no `paths:` frontmatter), and the installer that mirrors the rules directory to the user configuration.

**Storage**: Files under version control only.

**Testing**: `tests/run-config-pyramid.sh` (rule contract), `tests/run-install.sh` (rules directory matches the repository after install). The behavioral scenarios in the spec (SC-001) are a manual read-through in [quickstart.md](./quickstart.md), not automated.

**Target Platform**: Claude Code on macOS/Linux/Windows; installer is POSIX shell.

**Project Type**: Agent-configuration repository; the deliverable is a rule file plus its documentation and check.

**Performance Goals**: Not applicable. Context cost is bounded by keeping the file within the sibling size range (22–39 lines; target ≤ 40).

**Constraints**:
- FR-011 / existing RULE-02..04: no configuration path, authored-skill name, slash command, or sibling-rule filename in the file, and no sibling names this file.
- FR-016 / spec 036: existing rules, apex, and skills stay byte-identical; `specs/001`–`039` untouched.
- SC-005: only the draft's tiers, escalation conditions, and effort levels; framing text may be added.

**Scale/Scope**: 2 new rule files (EN + JA), 1 test file edited, 3–4 docs edited (`README.md`, `README.ja.md`, `docs/claude-config-design.md`), plus this feature's spec artifacts.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` is still the unfilled template, so there is no ratified principle to gate on; the gate passes formally. As in earlier features, the gate is instead evaluated against the repository's five always-on rules.

| Rule | Gate | Status |
|---|---|---|
| Requirements certainty | Are all material gaps resolved? | **PASS**: the one material gap (ADR or not) was resolved in clarification; placement and form are assumptions recorded in the spec. |
| Documentation integrity | Are changed public contracts synchronized in the same change? | **PASS**: FR-013/014/015 cover the test, both READMEs, both design-doc locations that state the count, and the mirror. The [contract](./contracts/rule-file-contract.md) enumerates them. |
| Authorization and safety | Does the change add permissions or touch sensitive material? | **PASS**: no tool permission, credential, or external effect. The rule steers model choice only. |
| Reader-facing structure | Are requirements and outputs grouped comparably? | **PASS**: FRs are grouped by artifact (rule content, structure check, docs, non-regression). |
| Reasoning completeness | Are dependencies and branches explicit? | **PASS**: test change precedes rule creation; docs follow rule content; escalation is a closed condition set (FR-006). |

**Post-design re-check**: **PASS**. Phase 0 found two facts the spec did not have (the Japanese mirror, and a second "five" in the design doc's §5 and table); both are folded into FR-015 and the contract. No unresolved violation remains.

## Project Structure

### Documentation (this feature)

```text
specs/040-model-routing-rule/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── rule-file-contract.md
├── checklists/
│   └── requirements.md
└── tasks.md             # Created by /speckit-tasks
```

### Source Code (repository root)

```text
.claude/rules/model-routing.md          # NEW: the rule (English)
.claude-ja/rules/model-routing.md       # NEW: Japanese counterpart
tests/run-config-pyramid.sh             # EDIT: RULE-01 six-file set; add RULE-11
README.md                               # EDIT: rules tree line, rules paragraph
README.ja.md                            # EDIT: rules paragraph
docs/claude-config-design.md            # EDIT: §3.1 heading + rows, §5 count and table
```

**Structure Decision**: No new directories. The rule lives with its siblings; every edited file already exists and already states the rule count or lists the rules (evidence in [research.md](./research.md) D6).

## Complexity Tracking

No constitution violations to justify.
