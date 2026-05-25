# Research: Live Documentation Enforcement

**Phase 0 output for `009-live-doc-enforcement`**

## Rule File Conventions (this project)

**Decision**: New rule delivered as `.claude/rules/live-documentation.md`, imported via `@.claude/rules/live-documentation.md` in `.claude/CLAUDE.md`.

**Rationale**: All always-on guidance in this project lives under `.claude/rules/`. The CLAUDE.md `@`-import chain is the established loading mechanism. Files stay focused (≤ 200 lines per tools.md convention). Each rule file owns one concern.

**Alternatives considered**:
- Inline in `.claude/CLAUDE.md` directly — rejected: file would exceed 200-line guideline, violates single-concern principle.
- New skill file — rejected: user chose Rule (always-on) over Skill (on-demand) in spec clarification.

---

## Live Documentation Rule Content Patterns

**Decision**: Rule file is organized into five enforcement sections aligned with the five Live Documentation principles: (1) Drift Detection, (2) Separate-PR Detection, (3) Auto-generation Recommendation, (4) Proximity Enforcement, (5) No Redundancy. A sixth section covers Override Handling.

**Rationale**: One section per principle is MECE, mirrors the spec's FR-001–FR-007, and makes individual principles auditable and extendable independently.

**Alternatives considered**:
- Trigger-first format (list all triggers, then all actions) — rejected: harder to scan; coupling between trigger and response is the readable unit.
- Single bullet-list format (as in skill-routing.md) — rejected: Live Documentation enforcement requires conditional logic and examples that don't compress well to bullets.

---

## Integration: CLAUDE.md Import Chain

**Decision**: Add `@.claude/rules/live-documentation.md` to `.claude/CLAUDE.md` alongside existing rule imports.

**Rationale**: Consistent with how `clarifier.md`, `permissions.md`, `skill-routing.md`, `advisor.md`, and `tools.md` are loaded. The existing `@path` import syntax is the only mechanism Claude Code uses to chain rule files.

**Alternatives considered**:
- Import in root `CLAUDE.md` only — rejected: root file delegates entirely to `.claude/CLAUDE.md` via `@.claude/CLAUDE.md`; rules must be in `.claude/CLAUDE.md` to be in the chain.

---

## Test Infrastructure Pattern

**Decision**: Tests live in `tests/live-documentation/NNN-scenario.md` with a runner `tests/run-live-documentation.sh`. Format matches existing `tests/skill-routing/` and `tests/run-skill-routing.sh` — Markdown scenario files with `## Input Prompt`, `## Expected Behavior`, `## Pass Criteria`, and `## Baseline` sections. Runner calls `claude -p` with a structured evaluation query.

**Rationale**: Reusing the established pattern means zero new tooling, no new dependencies, and the test files are self-documenting scenarios. The `claude -p` headless evaluation already validates rule-driven behavior in `tests/run-skill-routing.sh`.

**Alternatives considered**:
- pytest / shell bats framework — rejected: adds dependencies; project currently has no test framework beyond bash.
- No automated tests — rejected: spec SC-001–SC-005 require verifiable outcomes; manual-only testing violates "Automation over Discipline" (the very principle being enforced).

---

## Override Mechanism

**Decision**: Override is accepted when the developer states a reason in-context ("I acknowledge this is a Live Documentation violation because [reason]"). Claude records the acknowledgment and proceeds. No persistent override store is needed for v1.

**Rationale**: The spec defines Override as requiring a "stated reason" but does not require persistence. Recording in the conversation is sufficient for the current scope (single project, single session). This keeps v1 minimal.

**Alternatives considered**:
- Persist overrides in `.claude/overrides.json` — rejected: out of scope for v1 per spec Assumptions.
- Require git commit message annotation — rejected: implementation detail that leaks into rule scope.

---

## Rule File Line Budget

**Decision**: Rule file targets ≤ 150 lines to stay within CLAUDE.md import truncation threshold (200 lines noted in memory system instructions).

**Rationale**: The tools.md note about CLAUDE.md imports states "files focused and under ~200 lines." 150 lines provides headroom for future additions without truncation risk.
