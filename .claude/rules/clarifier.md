# Requirements Certainty

Commit to an outcome only when the user's intent is defined well enough to choose and verify the right work. This guidance resolves uncertainty about the requested result; it neither grants authority to act nor determines whether an action is permitted.

## Material gaps

A gap is material when different reasonable answers would change at least one of:

- the intended outcome or affected parties;
- the included inputs, outputs, systems, or boundaries;
- the observable completion condition;
- a binding compatibility, security, performance, quality, cost, or timing constraint;
- the chosen approach's reversibility, effort, or blast radius;
- which of two conflicting requirements or prior decisions prevails.

Ask before committing when a material gap cannot be resolved from applicable evidence. Do not invent intent, constraints, or acceptance criteria.

## Proportionate resolution

- Resolve every blocking gap together when practical so the user can make one coherent decision.
- State the available context, a recommended default, and how each alternative changes the result, effort, reversibility, or impact.
- Ask one decision per question and make the observable consequence of each answer clear.
- If the gap is immaterial and the default is obvious, local, reversible, and low risk, proceed with the assumption stated explicitly.
- Mark inferred requirements by confidence and keep them distinguishable from requirements the user confirmed.

Definition is sufficient when the purpose, scope, material constraints, and observable completion condition support one bounded course of work. Resolve uncertainty before the affected work, never after presenting it as complete.

## References

- ISO/IEC/IEEE 29148:2018, *Systems and software engineering — Life cycle processes — Requirements engineering* — the international standard for eliciting, analyzing, validating, and managing requirements that this rule's material-gap test operationalizes: <https://www.iso.org/standard/72089.html>
- Barry W. Boehm, *Software Engineering Economics*, Prentice-Hall, 1981 — the empirical basis for resolving a material gap before committing rather than after: cost-to-fix escalates roughly an order of magnitude at each later lifecycle stage.
