# Rule Behavioral Contract: Live Documentation Enforcement

**Artifact type**: Rule file behavioral specification  
**Rule file**: `.claude/rules/live-documentation.md`  
**Contract version**: 1.0

> This contract defines the observable trigger → response pairs that the rule file MUST produce. Each entry is independently testable via `tests/live-documentation/`.

---

## Contract 1: Drift Detection (FR-001)

**Trigger**: Developer presents a code diff or commit where source code with a public contract has changed, but no Documentation Artifact covering that contract has been updated in the same change.

**Required Response**:
1. Identify the specific changed code and its stale Documentation Artifact (by path).
2. State that this is a Live Documentation violation (Drift).
3. Refuse to mark the review complete or provide a passing verdict until one of:
   - The developer updates the Documentation Artifact in the same change, OR
   - The developer provides an Override with a stated reason.
4. Do NOT flag pure internal refactors (no contract change) as drift.

**Postcondition**: Review is blocked until drift is resolved or overridden.

---

## Contract 2: Separate Documentation PR Detection (FR-002)

**Trigger**: Developer presents a PR or diff that contains only Documentation Artifact changes, with no corresponding Code Change in the same diff.

**Required Response**:
1. Ask whether the described code was already shipped in a prior commit.
2. If yes: flag the separation as a Live Documentation violation and recommend amending the original code commit.
3. If the developer states the separation is intentional (retroactive documentation sprint or similar): accept the Override and record the reason.
4. Do NOT flag documentation-only changes that introduce new architectural decision records (ADRs), onboarding docs, or other non-code-derivative artifacts.

**Postcondition**: Violation is flagged; developer must either rebase or provide Override.

---

## Contract 3: Auto-generation Recommendation (FR-003)

**Trigger**: Developer asks Claude to write or update a Documentation Artifact that could be derived automatically from the code (e.g., API reference from type signatures, parameter list from function signature, schema description from type definitions).

**Required Response**:
1. Identify the auto-generation path (e.g., "this can be produced by running `X`").
2. Recommend the automated path instead of hand-writing the content.
3. Decline to produce the hand-written artifact.
4. If no auto-generation tool exists in the project: proceed with hand-writing, placed at the nearest co-located location.

**Postcondition**: Hand-written content is not produced when auto-generation is available.

---

## Contract 4: Proximity Enforcement (FR-004)

**Trigger**: Developer asks Claude to add documentation for a module, function, or component.

**Required Response**:
1. Place the documentation in the physically closest location to the described code:
   - Inline docstring if the language supports it
   - `README.md` in the same directory if a file-level overview is needed
   - Co-located spec file adjacent to the source
2. Warn if the developer proposes a remote or centralized location (e.g., top-level `docs/`, external wiki).
3. Offer the nearest co-located alternative.

**Postcondition**: Documentation is co-located with the code it describes.

---

## Contract 5: No Redundancy (FR-005)

**Trigger**: Developer asks Claude to write documentation when the same information already exists elsewhere in the repo (in another doc, a docstring, or a spec file).

**Required Response**:
1. Point to the existing source.
2. Decline to create a duplicate.
3. Offer to add a cross-reference link if the developer needs discoverability from the new location.

**Postcondition**: No duplicate Documentation Artifact is created.

---

## Contract 6: Override Acceptance (FR-006)

**Trigger**: Developer explicitly states they are aware of a Live Documentation violation and provides a reason for accepting it.

**Required Response**:
1. Accept the Override if and only if a reason is stated.
2. Record the acknowledgment in the response ("Override accepted: [stated reason]").
3. Proceed with the requested action.
4. Reject silent overrides ("just skip the doc check") with a request for a stated reason.

**Postcondition**: Violation is acknowledged; action proceeds; reason is on record in the conversation.

---

## Out-of-Scope Behaviors (non-violations)

The following do NOT trigger enforcement:
- Pure internal refactors (private method renames, formatting changes) with no contract change.
- Generated files (migration files, build artifacts, lock files) — these are not Documentation Artifacts.
- New architectural decision records or onboarding documents that are not code-derivative.
- Test files describing behavior — these are Executable Specifications and are treated as Documentation Artifacts co-located with the tested code; drift check applies only when the tested interface changes.
