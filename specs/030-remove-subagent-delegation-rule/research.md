# Phase 0 Research: Remove subagent-delegation Rule

No `NEEDS CLARIFICATION` markers remain in plan.md's Technical Context — this
is a plain three-file text change with no technology unknowns. The one
substantive decision made before planning is recorded below for traceability.

## Decision: Full deletion, not a trim

**Decision**: Delete `.claude/rules/subagent-delegation.md` in its entirety,
including the harness-specific facts it contained (no `AskUserQuestion` in
subagents; the `context: fork` vs. `skills:`-preload vs. direct-delegation
mechanism table). No content is relocated into `CLAUDE.md` or any other rule
file.

**Rationale**: The stated priority for this change is reducing
`.claude/CLAUDE.md`'s always-loaded context size. A trimmed version (keeping
only the harness-specific facts) was drafted and reviewed with the user
first, but it still carries a non-zero always-loaded cost every session.
Once the user named context-length reduction as the priority, full deletion
dominates the trim on that specific axis, so it was chosen instead.

**Alternatives considered**:

- **Trim to harness-specific facts only** (drafted earlier in the session):
  keeps the `AskUserQuestion`-unavailable note and the mechanism-selection
  table, drops the generic "delegate when / stay when" judgment heuristics.
  Rejected once the priority was stated as context-length reduction — this
  alternative still loads non-trivial text every turn.
- **Leave the file unchanged**: rejected per the user's original premise —
  the generic delegation judgment is something the Claude model already
  performs correctly by default, so the file's marginal behavioral value is
  low relative to its always-loaded cost.

## Decision: No ADR

**Decision**: No Architecture Decision Record is proposed for this removal.

**Rationale**: ADR policy (`adr` skill, `.claude/CLAUDE.md` close-out
section) reserves ADRs for architecturally significant, hard-to-reverse
decisions with a rejected implementation alternative. Deleting a rules file
is a two-way-door edit to instruction text, fully reversible via git. This
matches the precedent of specs/018-remove-solo-practice and
specs/029-remove-codex-plugin, neither of which produced an ADR — unlike
specs/025–027, which changed enforcement mechanisms (hooks, permissions
config, scripts) and did warrant ADRs 0005–0007.

## Decision: Historical specs left untouched

**Decision**: `specs/020-subagent-delegation-rule/` (which created the file),
`specs/021-codex-official-import/`, `specs/024-remove-verify-config/`, and
any other historical `specs/NNN-*/` directory referencing
`subagent-delegation.md` are not edited.

**Rationale**: Established precedent across specs/018, 024–027, and 029 —
historical specs are a record of what was true when written, not living
documentation. Retroactively editing them would misrepresent the repository's
history.

**Alternatives considered**: Updating historical specs to note the file's
removal — rejected as inconsistent with the established convention and as
scope creep beyond the three files identified in spec.md.
