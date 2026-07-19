# Feature Specification: Type Safety Enforcement in Coder Skill

**Feature Branch**: `011-type-safety-coder`

**Created**: 2026-07-19

**Status**: Draft

**Input**: User description: "coderスキルなどで、型安全性を確保するように指示を追加"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Type-Annotated Public Interfaces by Default (Priority: P1)

A developer asks Claude to implement or modify a function, class, or module in a codebase whose language supports static or gradual typing. Claude adds explicit type annotations to public interfaces (function signatures, exported values, class members) as part of the change, matching the codebase's existing typing convention, without being asked separately for "type safety."

**Why this priority**: Untyped or loosely typed public interfaces are the most common source of downstream type errors and unclear contracts. Making annotation the default behavior (not an opt-in ask) closes the largest gap.

**Independent Test**: Can be fully tested by asking Claude to add a new function to a TypeScript, Python, or other gradually-typed codebase and verifying the resulting function signature carries parameter and return types consistent with the project's typing conventions.

**Acceptance Scenarios**:

1. **Given** a statically or gradually typed codebase with an established typing convention, **When** Claude implements a new public function or class, **Then** Claude adds type annotations to its parameters and return value matching that convention.
2. **Given** an existing typed function that Claude modifies, **When** the change alters the function's inputs or outputs, **Then** Claude updates the type annotations to match, not just the implementation.
3. **Given** a codebase with no typing convention in place (plain dynamically-typed code, no type hints anywhere), **When** Claude implements a change, **Then** Claude follows the existing repo convention rather than unilaterally introducing a new typing system.

---

### User Story 2 - No Unsafe Type Escapes Without Justification (Priority: P2)

A developer asks Claude to fix a type error or implement a feature under time pressure. Instead of silencing the type checker with an unsafe escape hatch (`any`, `unknown` casts, `# type: ignore`, non-null assertions, etc.), Claude fixes the underlying type mismatch. When an escape is genuinely unavoidable, Claude adds it with a one-line comment stating why, and flags it to the user.

**Why this priority**: Escape hatches are how type safety erodes silently over time; catching this at the point of introduction prevents accumulation of untyped surface area.

**Independent Test**: Can be tested by asking Claude to resolve a type error and verifying it narrows or corrects the type rather than suppressing the checker, except where it explicitly justifies and flags an unavoidable escape.

**Acceptance Scenarios**:

1. **Given** a type-checking error caused by a genuine type mismatch, **When** Claude fixes it, **Then** Claude corrects the type (narrowing, proper typing, or a small refactor) rather than adding a suppression annotation.
2. **Given** a case where a type escape is truly unavoidable (e.g., an untyped third-party library), **When** Claude adds the escape, **Then** Claude adds a comment explaining why and states the trade-off to the user.
3. **Given** a request to "just make the type error go away," **When** the fastest path is an unsafe escape, **Then** Claude still prefers the type-correct fix and only falls back to a justified escape if no reasonable correct fix exists within scope.

---

### User Story 3 - Type Checker Runs Before Work Is Reported Done (Priority: P2)

A developer asks Claude to complete a coding task in a project that has a type checker configured (e.g., `tsc`, `mypy`, `pyright`). Before reporting the task complete, Claude runs the type checker alongside the existing test/lint/format checks and resolves any type errors introduced by the change.

**Why this priority**: Without this, type annotations can be added but silently wrong; running the checker is what actually verifies type safety rather than just its appearance.

**Independent Test**: Can be tested by making a change that introduces a type error and confirming Claude's own verification step catches it before declaring the task done.

**Acceptance Scenarios**:

1. **Given** a project with a configured type checker, **When** Claude finishes a code change, **Then** Claude runs the type checker as part of its pre-completion verification, alongside tests/lint/format.
2. **Given** the type checker reports a new error caused by Claude's change, **When** Claude is about to report done, **Then** Claude fixes the error first (or, if out of scope, explicitly surfaces it rather than silently ignoring it).
3. **Given** a project with no type checker configured, **When** Claude completes a change, **Then** Claude does not block on or fabricate a type-checking step.

---

### User Story 4 - Validate and Narrow Types at System Boundaries (Priority: P3)

A developer asks Claude to handle data coming from outside the type system's guarantee — user input, an external API response, deserialized JSON/config, environment variables. Claude validates and narrows this data into the application's known types at the boundary, rather than trusting an assumed or cast type deeper in the code.

**Why this priority**: This closes the remaining gap where "type safety" looks satisfied by the compiler but is actually violated at runtime by untrusted external data; it is lower priority than P1/P2 because it applies only where boundary-crossing data exists.

**Independent Test**: Can be tested by asking Claude to handle a parsed JSON payload or API response and verifying it validates/narrows the shape before using it as a typed value, rather than casting it directly.

**Acceptance Scenarios**:

1. **Given** data crossing a system boundary (user input, external API, deserialized payload), **When** Claude writes code to consume it, **Then** Claude validates or narrows it into the expected type before use, consistent with the project's existing boundary-validation approach.
2. **Given** internal, already-typed data with no boundary crossing, **When** Claude writes code, **Then** Claude does not add redundant validation for states the type system already guarantees.

---

### Edge Cases

- What happens when the codebase's stack has no type system at all (e.g., plain untyped JavaScript, shell scripts)? Claude follows the existing repo convention and does not introduce an unrelated typing system as a drive-by change.
- How does Claude handle a request that explicitly asks to bypass type safety (e.g., "just cast it, don't worry about types")? Claude may comply for truly local, reversible cases but still surfaces the trade-off; it does not silently accumulate escape hatches.
- What happens when adding correct types would require a broader refactor beyond the requested task? Claude keeps the immediate change type-correct and flags the broader gap to the user rather than performing an unrequested large refactor.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The coder skill MUST instruct that, when implementing or modifying code in a statically or gradually typed language, public interfaces (function signatures, exported values, class members) carry explicit type annotations consistent with the project's existing typing convention.
- **FR-002**: The coder skill MUST instruct that type annotations be updated in the same change whenever a modification alters a function's or interface's inputs or outputs.
- **FR-003**: The coder skill MUST instruct against introducing unsafe type escapes (e.g., `any`, blanket casts, suppression comments, non-null assertions) as a default fix for type errors, requiring instead that the underlying type mismatch be corrected.
- **FR-004**: The coder skill MUST instruct that when a type escape is genuinely unavoidable, it is accompanied by a short comment explaining why, and the trade-off is surfaced to the user.
- **FR-005**: The coder skill MUST instruct that, when a type checker is configured in the project, it is run as part of pre-completion verification alongside existing tests/lint/format checks, and any type errors introduced by the change are resolved before reporting done.
- **FR-006**: The coder skill MUST instruct that data crossing a system boundary (user input, external API responses, deserialized payloads, environment/config values) is validated or narrowed into the application's known types at the boundary, rather than trusted or cast without verification.
- **FR-007**: The coder skill MUST instruct that type-safety work follows the existing repo convention: it does not introduce a new typing system, add type annotations to untouched code, or perform unrelated typing refactors beyond the agreed task.

### Key Entities

- **Coder skill instruction set**: The existing playbook (`~/.claude/skills/coder/SKILL.md`) that governs how Claude implements and modifies code; this feature adds a type-safety instruction block to it.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: When Claude implements a new public function or class in a typed codebase, the resulting code includes type annotations consistent with the project's convention, without the user needing to separately request "add types."
- **SC-002**: When Claude resolves a type error, it does not introduce a suppression/escape annotation unless it also states, in the same response, the reason and the trade-off.
- **SC-003**: When a project has a configured type checker, Claude's pre-completion verification includes running it, in addition to existing test/lint/format checks.
- **SC-004**: Code Claude writes to consume external or boundary-crossing data validates or narrows that data's shape before treating it as a typed internal value.

## Assumptions

- "Type safety" in scope means: type annotations on public interfaces, avoidance of unsafe escape hatches, running the project's configured type checker, and boundary validation — not adopting a new type system in a codebase that has none.
- The instruction is added to the `coder` skill (and may reference the same convention already followed for linter/formatter/test runner) rather than creating a new standalone skill, since it governs behavior during implementation, not a separate workflow.
- Projects without any type checker or typing convention are unaffected; Claude continues to match existing repo conventions per the coder skill's existing "Language and stack conventions" section.
- This feature does not change the TDD/SDD workflow order — type safety instructions compose with, not replace, the existing red→green→refactor and spec-driven requirements.
