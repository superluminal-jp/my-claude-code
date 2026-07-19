# Phase 1 Data Model: Type Safety Enforcement in Coder Skill

This feature has no application data model — it modifies an instruction document (a skill file), not a running system with persisted entities. This document instead defines the conceptual entities the instruction text itself must distinguish, so the wording in `SKILL.md` stays unambiguous.

## Entities

### Typed Language Context
A codebase or file the `coder` skill is operating in, classified by its typing posture.

| Attribute | Values | Notes |
|---|---|---|
| `typing_kind` | `static` (e.g., Rust, Go), `gradual` (e.g., TypeScript, Python with type hints), `none` (plain JS, untyped Python, shell) | Determines whether annotation instructions (FR-001, FR-002) apply at all |
| `existing_convention` | inferred from repo (e.g., "this repo type-hints all public functions") | Governs *how* annotations are written — the instruction never invents a new convention (FR-007) |

### Public Interface
A function signature, exported value, or class member visible outside its immediate implementation scope.

| Attribute | Notes |
|---|---|
| `annotated` | boolean — whether parameters/return/members carry type annotations |
| `changed_in_diff` | boolean — whether this change alters the interface's inputs/outputs, triggering FR-002 |

### Type Escape
An annotation or construct that suppresses or bypasses the type checker rather than satisfying it (e.g., `any`, blanket cast, `# type: ignore`, non-null assertion).

| Attribute | Notes |
|---|---|
| `justified` | boolean — whether a one-line comment states why it's unavoidable (FR-004) |
| `surfaced_to_user` | boolean — whether the trade-off was stated in the response (FR-004) |

### Type Checker
The project's configured static type-checking tool (e.g., `tsc --noEmit`, `mypy`, `pyright`), if any.

| Attribute | Notes |
|---|---|
| `configured` | boolean — presence detected from repo config (e.g., `tsconfig.json`, `mypy.ini`, `pyproject.toml` section) |
| `run_before_done` | boolean — whether it was invoked as part of pre-completion verification (FR-005) |

### System Boundary Data
Data entering the typed portion of the codebase from outside the type system's guarantee: user input, external API responses, deserialized payloads, environment/config values.

| Attribute | Notes |
|---|---|
| `validated_or_narrowed` | boolean — whether the boundary code checks/narrows shape before treating the value as a typed internal type (FR-006) |

## Relationships

- A **Typed Language Context** contains zero or more **Public Interfaces**.
- A **Public Interface** may, when a type error occurs during its implementation, produce a **Type Escape** as a fallback.
- A **Typed Language Context** has at most one associated **Type Checker**.
- **System Boundary Data** feeds into a **Typed Language Context** only through boundary-validation code; it is not itself a language-context attribute.

## Validation Rules (derived from spec Functional Requirements)

- FR-001/FR-002: if `typing_kind ∈ {static, gradual}` and `existing_convention` calls for annotations, every new/changed Public Interface MUST have `annotated = true`.
- FR-003/FR-004: a Type Escape MUST NOT appear with `justified = false`.
- FR-005: if a Type Checker is `configured = true`, pre-completion verification MUST set `run_before_done = true`.
- FR-006: System Boundary Data consumed by typed code MUST have `validated_or_narrowed = true` before being treated as an internal type.
- FR-007: instruction application MUST NOT alter Public Interfaces outside `changed_in_diff = true` scope, and MUST NOT set `typing_kind` to a value the repo doesn't already use.
