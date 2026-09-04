---
name: problem-definition
description: Turn a vague sense that "something's wrong" into a single, verifiable problem statement — the gap between the current state and the ideal state — grounded in structured problem-definition frameworks. Domain-agnostic: applies to a business, technical, personal, or organizational problem alike. Separates the problem itself from any solution or unverified cause the user brings along with it. Use when the user wants to pin down what a problem actually is before analyzing its cause or proposing a fix, in any domain. Out of scope: root-cause analysis, evaluating or proposing solutions, or building an execution plan (a separate, later concern this skill does not own); confirming scope or acceptance criteria on an already-agreed single feature (a separate requirements-clarification capability's job); and formulating a broader strategy or roadmap around an already-understood problem (a separate capability's job).
---

# Problem Definition

A problem is the gap between the current state and the ideal state — a definition that converges independently across quality management, structured problem-solving, business analysis, and Lean thinking (see [Framework toolbox](#framework-toolbox)). This skill elicits that gap precisely enough to hand off to whatever comes next, and produces it as a single standalone problem statement.

## Scope

**Covers**: turning a vague complaint into a problem statement — current state, ideal state, the gap itself, and why it matters now — in any domain.

**Out of scope** (a separate concern, not this skill's job):

- Root-cause analysis, solution evaluation, or execution planning. This skill's job ends when the problem statement is produced.
- Confirming the scope or acceptance criteria of a single, already-agreed feature.
- Formulating a broader strategy, vision, or roadmap once a problem is already understood.

This skill has no dependency on, and does no integration with, any other skill's content or output — it stands entirely on its own, and never forces itself into a flow the user hasn't explicitly asked it to join.

## How it works

1. **Elicit the current state and the ideal state separately**, then formulate their gap as the problem statement ([Framework toolbox](#framework-toolbox), [Eliciting the four elements](#eliciting-the-four-elements)).
2. **Watch for contamination** — solutions, unverified causes, conflicting ideals, or multiple bundled gaps presented as if they were the problem itself ([Keeping the problem statement clean](#keeping-the-problem-statement-clean)).
3. **Check whether a problem statement already exists at the output location; if so, confirm overwrite vs. new version with the user** ([Overlapping with an existing statement](#overlapping-with-an-existing-statement)).
4. **Produce the problem statement** ([Output shape](#output-shape)). If interrupted, follow [Handling interruption](#handling-interruption).

## Framework toolbox

Every element below is grounded in a named, dated, citable source — no uncited framework.

- **Current state**: the current-state analysis in the International Institute of Business Analysis (IIBA), *A Guide to the Business Analysis Body of Knowledge (BABOK Guide)*, v3, 2015, and the "Current Condition" element of Toyota's A3 process as documented in John Shook, *Managing to Learn: Using the A3 Management Process*, Lean Enterprise Institute, 2008.
- **Ideal state**: Kaoru Ishikawa, *Guide to Quality Control*, Asian Productivity Organization, 1976 — the QC-story tradition's framing of a problem as the gap between what should be and what is; BABOK's "future state"; A3's "Target Condition."
- **The gap itself (the problem statement)**: Charles H. Kepner & Benjamin B. Tregoe, *The New Rational Manager*, Princeton Research Press, 1981 — a problem as a deviation from an expected performance standard; A3's problem statement as a measured gap between current and target conditions.
- **Significance** (why this deserves attention now): Kepner-Tregoe's criterion that a deviation is only a "problem" worth analyzing when it's significant enough to warrant corrective action.

## Eliciting the four elements

A completed problem statement includes all four of the following. Never fabricate a fact about the situation when the user or the project offers no evidence — ask, or record it as an open point instead ([Recording open points](#recording-open-points)).

1. **Current state**: what's actually happening, grounded in fact or data where available.
2. **Ideal state**: what should be happening — the standard, expectation, or target.
3. **The gap**: the problem statement itself — the difference between the two, stated as precisely as possible (e.g., A3's "from X to Y by Z" form when the current and ideal states are measurable).
4. **Significance**: why this gap is worth addressing now.

When quantitative data isn't available for the current or ideal state, switch to a qualitative description and flag the absence of data explicitly — don't let the lack of precision block elicitation.

If the current and ideal states turn out to match — no real gap exists — say so plainly rather than manufacturing a problem.

### Recording open points

Record unresolved material points explicitly rather than deciding silently:

```markdown
**Open point**: <what's unresolved>
**Default**: <the recommended default answer>
**Alternative**: <another realistic option>
**Impact**: <what changes depending on the choice>
```

## Keeping the problem statement clean

A problem statement gets contaminated the same few ways every time. Watch for each of these and handle it before it reaches the gap itself:

- **A solution presented as the problem** ("we should add X"): identify it explicitly as a proposed solution, then separately elicit the current-state/ideal-state gap that solution is trying to close. Never let the solution's content stand in for the gap.
- **An unverified cause presented as the problem** ("the cause is surely X"): identify it as an unverified hypothesis and return the elicitation to the gap itself rather than pursuing root-cause analysis — root-cause analysis is a separate, later concern this skill never performs (see [Scope](#scope)).
- **Conflicting ideal states among stakeholders**: don't adopt one side unilaterally. Present both, and ask the user which should govern, using the [open-point format](#recording-open-points).
- **Multiple distinct gaps bundled into one complaint**: don't force them into a single statement. Decompose into separate problem-statement candidates and present them individually.

## Output shape

Produce the problem statement as a single, self-contained document under the target context — under its `problem.md` inside an existing `specs/<N>-*` convention if the project already uses one, otherwise a project-appropriate default location (e.g., `docs/problems/<slug>.md`). **Never write into or modify a file you didn't create** — this skill has no dependency on, or integration with, any other tool's files or workflow.

Lead with a machine-readable status marker:

```markdown
# Problem Statement: <subject>

**Status**: Complete | Draft (incomplete)
**Generated**: <YYYY-MM-DD>
```

When `Complete`, the body includes all four elements from [Eliciting the four elements](#eliciting-the-four-elements). When a solution or unverified cause was identified along the way, record it separately rather than folding it into the gap:

```markdown
## Identified solution (not part of the problem statement)

<the solution the user proposed>. The gap it's trying to close: <the corresponding current-state/ideal-state contrast>
```

```markdown
## Identified unverified cause (not part of the problem statement)

<the causal hypothesis the user proposed>, recorded as unverified. Root-cause analysis is a separate, later concern this skill does not perform.
```

When stakeholders disagree on the ideal state:

```markdown
## Disagreement on the ideal state

- <stakeholder A's view>
- <stakeholder B's view>

Which should govern is unresolved — see the open point above.
```

### Overlapping with an existing statement

Before writing, check whether a problem statement already exists at the target location. If it does, don't silently overwrite it or silently pile up versions — ask the user which they want:

1. Overwrite the existing file.
2. Save as a new version in a separate file (e.g., `problem-<YYYY-MM-DD>.md`).

### Handling interruption

If the elicitation session ends before all four elements are answered, don't discard what was gathered. Save it as a draft with this marker:

```markdown
**Status**: Draft (incomplete)

## Unanswered elements

- <list the unanswered element names>
```

This draft is a legibility safeguard, not a resumable session — a later run either starts fresh or, per [Overlapping with an existing statement](#overlapping-with-an-existing-statement), asks the user about overwriting or versioning the file it finds.
