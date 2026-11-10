---
name: define-problem
description: Turn a vague sense that something is wrong into one verifiable problem statement - the gap between the current state and the ideal state - in any domain, business, technical, personal, or organizational, keeping the problem apart from any solution or unverified cause brought along with it. Use when the person wants to pin down what a problem actually is before analyzing its cause or proposing a fix. Do not use for root-cause analysis, for evaluating or proposing solutions, for an execution plan, for confirming the scope of an already-agreed feature, or for a product strategy or roadmap.
metadata:
  kind: worker
  permission: workspace_write
  sandbox: inside
  produces: a problem statement with current state, ideal state, gap, and significance
---

# Define the problem

A problem is the gap between the current state and the ideal state. This skill elicits that gap precisely enough to hand to whatever comes next, as one standalone problem statement. Its job ends there: it does not analyze causes, weigh solutions, or plan.

## Steps

1. **Elicit the four elements**, the current state and the ideal state separately.
   - Current state: what is actually happening, grounded in fact or data where available.
   - Ideal state: what should be happening - the standard, expectation, or target.
   - The gap: the problem statement itself, stated as precisely as possible. When both states are measurable, use the form "from X to Y by Z".
   - Significance: why this gap is worth addressing now.
2. **Keep the statement clean.** Handle each of these before it reaches the gap:
   - A solution presented as the problem ("we should add X"): name it as a proposed solution, then elicit the gap that solution is trying to close.
   - An unverified cause presented as the problem ("the cause is surely X"): name it as an unverified hypothesis and return to the gap.
   - Conflicting ideal states among stakeholders: present both and ask which governs. Do not adopt one side on your own.
   - Several distinct gaps bundled into one complaint: split them into separate problem-statement candidates.
3. **Record what is unresolved instead of deciding silently.** For each open point give what is unresolved, the recommended default, another realistic option, and what changes with the choice.
4. **Check the output location.** If a problem statement already exists there, ask whether to overwrite it or save a new version, such as `problem-<YYYY-MM-DD>.md`.
5. **Write the statement** as one self-contained document: `problem.md` inside the change's directory when the project keeps numbered specification directories, otherwise a project default such as `docs/problems/<slug>.md`. Never write to or modify a file this skill did not create.

Never fabricate a fact about the situation. When there is no quantitative data, describe the state qualitatively and say that data is absent. When the current and ideal states turn out to match, say plainly that there is no gap.

## Output shape

```markdown
# Problem Statement: <subject>

**Status**: Complete | Draft (incomplete)
**Generated**: <YYYY-MM-DD>
```

A complete statement has all four elements. Add these sections only when they apply, so that neither is folded into the gap:

- `## Identified solution (not part of the problem statement)`: the solution the person proposed, and the gap it is trying to close.
- `## Identified unverified cause (not part of the problem statement)`: the causal hypothesis, recorded as unverified.
- `## Disagreement on the ideal state`: each stakeholder's view, with the open point that asks which governs.

If the session ends before all four elements are answered, save a draft with `**Status**: Draft (incomplete)` and a `## Unanswered elements` list. A later run starts fresh or asks about the existing file as in step 4.

## Done when

- The statement has the four elements, or is saved as a draft that lists the unanswered ones.
- No solution or unverified cause stands in for the gap; each is recorded in its own section.
- Every unresolved material point is written as an open point with a default.

## Bundled files

| File | Read when |
|---|---|
| `references/frameworks.md` | Naming or citing the framework an element comes from |
