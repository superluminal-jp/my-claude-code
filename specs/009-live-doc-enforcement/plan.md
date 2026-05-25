# Implementation Plan: Live Documentation Enforcement

**Branch**: `009-live-doc-enforcement` | **Date**: 2026-05-26 | **Spec**: [spec.md](./spec.md)  
**Input**: Feature specification from `specs/009-live-doc-enforcement/spec.md`

## Summary

Create `.claude/rules/live-documentation.md`, an always-on rule that encodes the five Live Documentation principles (Single Source of Truth, Executable Specification, Proximity, Automation over Discipline, No Redundancy) into Claude's default behavior. Register it in `.claude/CLAUDE.md` via `@`-import. Deliver five test scenarios in `tests/live-documentation/` with a bash runner, following the established `tests/skill-routing/` pattern.

## Technical Context

**Language/Version**: Markdown (rule files) + Bash (test runner)  
**Primary Dependencies**: Claude Code CLI (`claude -p` for headless test evaluation)  
**Storage**: File system — `.claude/rules/`, `tests/live-documentation/`  
**Testing**: Bash runner (`tests/run-live-documentation.sh`) + `claude -p` headless evaluation  
**Target Platform**: Claude Code CLI / Desktop (macOS)  
**Project Type**: Configuration/Rules project — deliverable is a Markdown rule file, not application code  
**Performance Goals**: N/A (static rule file; no runtime performance requirements)  
**Constraints**: Rule file ≤ 150 lines (CLAUDE.md import truncation threshold); no new dependencies beyond existing Claude Code CLI; must not break any existing tests  
**Scale/Scope**: Single rule file + CLAUDE.md import update + 5 test scenarios + 1 test runner

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Constitution status**: `.specify/memory/constitution.md` contains the unfilled template — no project constitution has been ratified. No constitutional gates apply.

**Re-check post-design**: No new violations introduced. Rule file is a documentation artifact; no architectural constraints were added.

**Result**: PASS (no gates to evaluate)

## Project Structure

### Documentation (this feature)

```text
specs/009-live-doc-enforcement/
├── plan.md              ← this file
├── research.md          ← Phase 0 output (complete)
├── data-model.md        ← Phase 1 output (complete)
├── quickstart.md        ← Phase 1 output (complete)
├── contracts/
│   └── rule-behavior.md ← Phase 1 output (complete)
├── checklists/
│   └── requirements.md
└── tasks.md             ← Phase 2 output (created by /speckit-tasks)
```

### Source Code (repository root)

```text
.claude/
├── CLAUDE.md                         ← add @-import for new rule
└── rules/
    └── live-documentation.md         ← NEW: always-on enforcement rule

tests/
├── run-live-documentation.sh         ← NEW: bash test runner
└── live-documentation/
    ├── 001-drift-detection.md        ← NEW: Contract 1 scenario
    ├── 002-separate-doc-pr.md        ← NEW: Contract 2 scenario
    ├── 003-autogen-recommendation.md ← NEW: Contract 3 scenario
    ├── 004-proximity-enforcement.md  ← NEW: Contract 4 scenario
    └── 005-override-acceptance.md    ← NEW: Contract 6 scenario
```

**Structure Decision**: Single-project layout. No src/ tree — this project delivers configuration artifacts, not application source. Tests mirror the established `tests/skill-routing/` pattern exactly.

## Implementation Tasks (for /speckit-tasks)

### T001 — Create rule file

**File**: `.claude/rules/live-documentation.md`

Write the rule with six sections (one per behavioral contract from `contracts/rule-behavior.md`):
1. Drift Detection (FR-001)
2. Separate-PR Detection (FR-002)
3. Auto-generation Recommendation (FR-003)
4. Proximity Enforcement (FR-004)
5. No Redundancy (FR-005)
6. Override Handling (FR-006, FR-007)

Constraints:
- ≤ 150 lines
- Imperative language: "When X, Claude MUST Y"
- No implementation details (language/framework names avoided in rule triggers)
- Includes the "Out-of-Scope Behaviors" list from `contracts/rule-behavior.md` as a non-violation section

**Acceptance**: Rule file exists at the correct path; line count ≤ 150; each of the six contracts is represented.

---

### T002 — Register rule in CLAUDE.md import chain

**File**: `.claude/CLAUDE.md`

Add `@.claude/rules/live-documentation.md` after the existing rule imports (after `@.claude/rules/skill-routing.md` import reference).

**Acceptance**: `.claude/CLAUDE.md` contains the import line; existing imports are unchanged; the file remains under the 200-line threshold.

---

### T003 — Write test scenario: drift detection

**File**: `tests/live-documentation/001-drift-detection.md`

Scenario: Code diff changes a public function signature; docstring is unchanged. Expected: Claude flags Drift, blocks review completion.

Format matches `tests/skill-routing/001-code-implement.md` exactly (sections: `# Test:`, `## Input Prompt`, `## Expected Behavior`, `## Pass Criteria`, `## Baseline`).

---

### T004 — Write test scenario: separate-doc-pr detection

**File**: `tests/live-documentation/002-separate-doc-pr.md`

Scenario: PR contains only README updates for a module shipped last week. Expected: Claude flags separation as Live Documentation violation.

---

### T005 — Write test scenario: auto-generation recommendation

**File**: `tests/live-documentation/003-autogen-recommendation.md`

Scenario: Developer asks "write API docs for this fully-annotated function." Expected: Claude recommends using the project's doc tool instead of hand-writing.

---

### T006 — Write test scenario: proximity enforcement

**File**: `tests/live-documentation/004-proximity-enforcement.md`

Scenario: Developer asks Claude to "document the authentication module and put it in docs/." Expected: Claude warns remote placement violates Proximity and offers a co-located alternative.

---

### T007 — Write test scenario: override acceptance

**File**: `tests/live-documentation/005-override-acceptance.md`

Scenario: Developer says "skip the doc check this time — this is an emergency hotfix." Expected: Claude rejects the silent override and asks for a stated reason. Follow-up: developer provides reason → Claude accepts.

---

### T008 — Write test runner

**File**: `tests/run-live-documentation.sh`

Bash script modeled on `tests/run-skill-routing.sh`:
- Iterates over `tests/live-documentation/*.md`
- Calls `claude -p` with a structured evaluation query per scenario
- Compares output against expected behavior
- Reports PASS/FAIL with counts
- Exits non-zero on any failure

**Acceptance**: `bash tests/run-live-documentation.sh` runs without error (all tests pass); script is executable (`chmod +x`).

---

### T009 — Update CLAUDE.md agent context

**File**: `CLAUDE.md` (root)

Update the `<!-- SPECKIT START --> … <!-- SPECKIT END -->` block to reference the new plan:

```
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan
at specs/009-live-doc-enforcement/plan.md
```

## Complexity Tracking

*(No constitution violations to justify.)*
