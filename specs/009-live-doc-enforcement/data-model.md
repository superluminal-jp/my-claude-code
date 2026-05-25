# Data Model: Live Documentation Enforcement

**Phase 1 output for `009-live-doc-enforcement`**

> Note: This feature delivers a rule file (static text), not a data-persisting system. The "entities" here are conceptual types encoded in the rule's enforcement logic — not database schemas. They give the rule precise vocabulary to reason about.

## Entity: Documentation Artifact

A file or in-source annotation whose primary purpose is describing code behavior.

| Attribute | Description |
|-----------|-------------|
| `path` | File path relative to repo root (e.g., `src/auth/README.md`, `src/auth/handler.py:docstring`) |
| `type` | `docstring` \| `readme` \| `spec` \| `openapi-annotation` \| `changelog-entry` \| `inline-comment` |
| `co_located_code` | Path(s) of the source code this artifact describes |
| `derivable` | Boolean — can this artifact be produced automatically from the code? |

**Invariant**: A Documentation Artifact MUST have at least one `co_located_code` reference. Artifacts with no code reference are standalone design documents and are out of scope for drift detection.

---

## Entity: Code Change

A discrete modification to source code, configuration, or schema that alters observable behavior or public contract.

| Attribute | Description |
|-----------|-------------|
| `scope` | Files changed in this diff/commit |
| `contract_change` | Boolean — does the change alter a public-facing interface? |
| `has_doc_change` | Boolean — does the same diff include a Documentation Artifact update? |

**State transitions**:
- `contract_change = true`, `has_doc_change = false` → **Drift detected** (FR-001 trigger)
- `contract_change = false` (pure internal refactor), `has_doc_change = false` → **No violation** (FR-001 false-positive boundary)

---

## Entity: Drift

A detected state where a Documentation Artifact no longer accurately describes its associated Code Change.

| Attribute | Description |
|-----------|-------------|
| `artifact` | Reference to the stale Documentation Artifact |
| `code_change` | The Code Change that caused the drift |
| `severity` | `contract-break` (public API changed, docs not updated) \| `internal` (private behavior changed) |
| `detected_at` | Conversation turn where drift was identified |

---

## Entity: Override

An explicit developer acknowledgment accepting a Live Documentation violation for a stated reason.

| Attribute | Description |
|-----------|-------------|
| `scope` | `this-change` — applies to the current diff only |
| `reason` | Developer-stated reason (free text, required) |
| `acknowledged_by` | Developer (implicit: whoever issues the acknowledgment) |

**Invariant**: An Override without a stated reason is invalid. Claude MUST reject silent overrides and prompt for a reason.

---

## State Diagram: Code Change Lifecycle Under This Rule

```
Code Change submitted for review
         │
         ▼
  Is contract_change = true?
    ├─ No → Internal change — skip drift check → ✓ Pass
    └─ Yes
         │
         ▼
  has_doc_change = true?
    ├─ Yes → Docs updated in same change → ✓ Pass
    └─ No
         │
         ▼
  Developer provides Override with reason?
    ├─ Yes → Override accepted → record reason → ✓ Pass (acknowledged)
    └─ No  → ✗ Flag as Drift — block review completion
```
