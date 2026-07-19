# Contract: Type Safety Behavior of the `coder` Skill

This is a behavioral contract, not an API contract — the "interface" this feature exposes is the observable behavior of Claude when the `coder` skill is loaded and a typed-language coding task is in progress. Each contract below maps to one Functional Requirement in [spec.md](../spec.md) and one test scenario under `tests/type-safety-coder/`.

## Contract 1 — Type-Annotated Public Interfaces by Default (FR-001, FR-002)

**Trigger**: Claude implements a new public function/class, or modifies an existing one's inputs/outputs, in a codebase with an established typing convention.

**MUST**:
- Add type annotations to the new/changed interface's parameters, return value, and public members, matching the repo's existing convention.
- Update annotations in the same change when the interface's inputs/outputs change.

**MUST NOT**:
- Leave a new or changed public interface unannotated when the repo convention calls for annotations.
- Invent a new typing convention not already used in the repo.

**Test scenario**: `001-typed-public-interface.md`

---

## Contract 2 — No Unsafe Type Escapes Without Justification (FR-003, FR-004)

**Trigger**: Claude encounters a type-checking error while implementing or fixing code.

**MUST**:
- Prefer correcting the underlying type mismatch (narrowing, proper typing, small refactor) over suppressing the checker.
- When an escape hatch is genuinely unavoidable, add a one-line comment explaining why, and state the trade-off to the user in the response.

**MUST NOT**:
- Add an unexplained `any`/blanket cast/suppression comment/non-null assertion as the default fix.

**Test scenario**: `002-no-unsafe-escape.md`

---

## Contract 3 — Type Checker Runs Before Work Is Reported Done (FR-005)

**Trigger**: Claude is about to report a coding task complete in a project with a configured type checker.

**MUST**:
- Run the type checker as part of pre-completion verification, alongside existing test/lint/format checks.
- Resolve any type errors the change introduced before reporting done, or explicitly surface them if out of scope.

**MUST NOT**:
- Report a change as done while a type error it introduced is unresolved and unmentioned.
- Fabricate a type-checking step in a project with no type checker configured.

**Test scenario**: `003-type-checker-verification.md`

---

## Contract 4 — Validate and Narrow Types at System Boundaries (FR-006)

**Trigger**: Claude writes code that consumes data crossing a system boundary (user input, external API response, deserialized payload, environment/config value).

**MUST**:
- Validate or narrow the data into the expected type before using it as a typed internal value, consistent with the project's existing boundary-validation approach.

**MUST NOT**:
- Cast or trust boundary-crossing data directly into a typed value without validation.
- Add redundant validation for internal, already-typed data with no boundary crossing.

**Test scenario**: `004-boundary-validation.md`

---

## Out-of-Scope Behaviors (non-violations)

- Adding type annotations to code the current task does not touch.
- Introducing a new type system/checker into a codebase that has none.
- Performing a broad typing refactor beyond the requested task (this should instead be flagged to the user per FR-007 and the skill's existing "no drive-by refactors" rule).
