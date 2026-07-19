# Phase 0 Research: Type Safety Enforcement in Coder Skill

No `[NEEDS CLARIFICATION]` markers remain in the Technical Context — this feature is a well-scoped instruction addition to an existing skill file, with no unresolved unknowns. This document records the design decisions made and the alternatives rejected.

## Decision 1: Where the instruction lives

**Decision**: Add a new "Type Safety" section to the existing `coder` skill (`~/.claude/skills/coder/SKILL.md`), placed after "Documentation Sync" and before "Code quality and security" (or folded into "Code quality and security" as a subsection) — not a new standalone skill.

**Rationale**: Type safety is a property of *how code is implemented*, which is exactly the `coder` skill's domain. The skill already carries an analogous instruction ("run the repository's configured linter, formatter, type-checker, and test runner… before reporting done" in "Language and stack conventions"). A separate skill would fragment implementation guidance across two always-loaded documents for what is one concern, and would require its own routing trigger in `rules/skill-routing.md` for no added precision — the `coder` skill's existing "when to use" triggers (implement/modify/refactor/debug code) already cover every situation where type safety applies.

**Alternatives considered**:
- *New standalone `type-safety` skill*: rejected — duplicates the "when to use" trigger surface with `coder`, and splits one coherent implementation concern into two skill loads for every coding task.
- *Only a `rules/*.md` file*: rejected — rules are always-on and imported via `CLAUDE.md`, appropriate for cross-cutting policy (permissions, git workflow), but type safety is implementation-technique guidance that belongs with TDD/SDD/docs in the `coder` skill's own playbook, consistent with how OWASP security guidance already lives there rather than in a separate rule.

## Decision 2: Scope of "type safety" instructions

**Decision**: Four instruction points, matching the four user stories: (1) type-annotate public interfaces by default, (2) no unsafe type escapes without justification, (3) run the project's configured type checker before reporting done, (4) validate/narrow types at system boundaries.

**Rationale**: These four map onto the places type safety actually breaks down in practice — missing annotations, silent suppression, unverified annotations (checker never run), and untyped external data flowing into typed code. Each is independently observable and testable (an annotation is present or not; an escape hatch appears with or without a comment; the checker runs or doesn't; boundary code validates or casts blindly).

**Alternatives considered**:
- *A single generic instruction ("write type-safe code")*: rejected — too vague to be testable or actionable, violates the same testability standard the `clarifier`/`coder` skills already hold requirements to.
- *Prescribing a specific type system or annotation style (e.g. mandate strict mode, mandate Pydantic)*: rejected — the `coder` skill is explicitly language-agnostic ("this is the single coding skill; it is language-agnostic... match existing repo conventions rather than importing external defaults"); prescribing a specific tool would contradict that existing, working convention.

## Decision 3: Interaction with "no speculative abstractions" and "no drive-by refactors"

**Decision**: Explicitly state that type-safety work follows the existing repo convention and does not license unrelated typing refactors or annotation of untouched code (FR-007).

**Rationale**: Without this guardrail, "ensure type safety" could be read as license to touch every function in a file to add types, which directly conflicts with the skill's existing "Add no unsolicited code improvements: no drive-by refactors... beyond the agreed task" rule. Stating the interaction prevents the new instruction from silently overriding an existing one.

**Alternatives considered**: Leaving the interaction implicit — rejected, since the whole point of adding an explicit instruction is to make behavior unambiguous; leaving a foreseeable conflict unaddressed would reintroduce exactly the kind of ambiguity `clarifier.md` flags as a gap.

## Decision 4: Test scenario format

**Decision**: Reuse the existing `tests/live-documentation/` and `tests/skill-routing/` pattern — one Markdown file per behavioral scenario (`# Test:`, `## Input Prompt`, `## Expected Behavior`, `## Pass Criteria`, `## Baseline`), driven by a bash runner using `claude -p` for headless evaluation.

**Rationale**: This repo has an established, working convention for behaviorally testing skill/rule instructions without needing a live multi-turn session; matching it keeps the new tests discoverable and consistent with `tests/run-live-documentation.sh` and `tests/run-skill-routing.sh`, and lets the runner be added to the same allow-listed `tests/run-*.sh` permission bucket already configured in `.claude/settings.json`.

**Alternatives considered**: A new test format/tooling — rejected, no benefit over the existing pattern and would add unnecessary maintenance surface.
