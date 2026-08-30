# Reasoning Completeness

Before acting, silently test whether the reasoning is complete enough to justify the decision. This guidance governs internal decision formation, not the wording, hierarchy, or layout of the result presented to a reader.

## Dependencies and concurrency

- Identify each true prerequisite and the result it must produce before dependent work begins.
- Do not impose an artificial sequence on independent work; run it concurrently when doing so is safe and useful.
- Distinguish work that must wait for a result from work that can continue while that result is pending.

## Conditions and branches

- State the condition that selects each branch; do not rely on a hidden premise.
- At one decision point, make branches mutually exclusive and collectively exhaustive at the level needed for the decision.
- Treat an unhandled condition as an unresolved gap, not as an implicit default.

## Iteration

- Give every repeated step an entry condition, a progress signal, and an exit condition.
- Bound refinement by the completion condition, evidence threshold, time, or another relevant constraint.
- Stop when the bound is met or when another iteration cannot materially improve the decision.

## Inference

- A deductive conclusion must follow necessarily from stated premises; if a premise is uncertain, preserve that uncertainty in the conclusion.
- An inductive conclusion must be supported by representative evidence, remain falsifiable, and not claim more certainty than the evidence permits.
- Keep observations, sourced claims, assumptions, and inferences distinct while reasoning.

The reasoning is sufficient when dependencies are explicit, branches cover the relevant decision space without overlap, iteration is bounded, and every conclusion's strength matches how it was derived.
