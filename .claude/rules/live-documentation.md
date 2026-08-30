# Documentation Integrity

Documentation is part of the public contract. Keep it accurate, canonical, close to the scope where it is true, and synchronized with the behavior it explains.

## Contract synchronization

- For every changed public interface—exported API, command option, configuration field, schema, or user-visible behavior—identify the existing artifact that explains it and update that artifact in the same change.
- Flag a drift violation when a changed contract leaves an existing explanation stale. Name the stale artifact and do not report the change complete until it is synchronized or a reasoned override is recorded.
- Do not require documentation churn for formatting, private renames, or internal refactors that leave the public contract unchanged.
- A standalone decision record, onboarding guide, or design document is not contract drift merely because it is created separately from code.

## Canonical source by scope

Place a fact at the smallest stable scope for which it is true:

1. repository-wide facts in the repository introduction;
2. subsystem or directory facts at that boundary;
3. one file's public contract in its leading documentation;
4. a non-obvious local invariant next to the relevant block.

Use a more distant artifact when its audience or cross-cutting scope genuinely requires it, and state what makes that location canonical. A higher-level summary may compress a lower-level source when it identifies that source, preserves its meaning, and does not create a competing definition.

## Generation and duplication

- Prefer generation from code, schemas, annotations, or other authoritative data when the result remains readable, reviewable, and sufficient for its audience. Do not claim generation is preferable when it would omit necessary intent or usage guidance.
- Maintain one canonical definition of a fact. Replace competing copies with a summary or a link; update every unavoidable projection in the same change.
- Treat generated outputs as derived artifacts, not a second source of truth.

## Process-artifact isolation

Shipped documentation must not depend on temporary planning notes, task lists, research scratchpads, or checklists whose paths and wording are expected to change. Move durable rationale to a stable decision or design artifact and state user-facing behavior directly. Process artifacts may cite one another inside their own bounded workspace.

## Overrides

Accept an exception only when its reason, affected artifact, owner, and follow-up condition are recorded. Reject a silent request to skip synchronization; an exception without a durable reason is indistinguishable from drift.

## References

- Cyrille Martraire, *Living Documentation*, Addison-Wesley, 2019.
