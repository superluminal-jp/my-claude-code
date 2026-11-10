---
name: define-product-strategy
description: Formulate product or business strategy before development begins - vision, target users, problem and value proposition, success metrics, prioritized scope, constraints - for a new product or for a new initiative, extension, or pivot of an existing one, as one strategy brief. Use when the person wants to think through product vision, target users, value proposition, success metrics, or scope priorities before starting development work. Do not use for confirming the scope or acceptance criteria of an already-agreed feature, for Scrum events or team facilitation, for a document with no development destination, or for architecture, technology-stack, or build-versus-buy decisions.
metadata:
  kind: worker
  permission: workspace_write
  sandbox: inside
  produces: a product strategy brief with six sections
---

# Define product strategy

Before implementation or specification work begins, elicit the product direction that the features will serve, and write it as one standalone strategy brief. This skill handles only the strategy framing. It runs when the person asks for it and never forces itself into a flow that wants to go straight to implementation.

## Steps

1. **Inspect the project for existing context; do not ask the person to pick a mode.** Treat the project as existing when it has a README that describes the product, an agent-facing instruction file, an earlier strategy brief, or a specification or plan directory.
   - Existing: read what is there first, and do not re-ask for facts already recorded. Elicit only what is new or changing.
   - Several past strategy artifacts that conflict: show the most recent and ask which takes priority. Never merge silently.
   - New, or the sources say nothing about the product: elicit all six sections by interview, and record the missing history as an assumption.
2. **Elicit the six sections**, each grounded in its framework from `references/frameworks.md`:
   1. Vision and problem: what is being built, for whom, and why.
   2. Target users: framed as jobs to be done or as personas.
   3. Value proposition: the value delivered to those users.
   4. Success metrics: outcome metrics - one guiding metric with supporting ones, or a balanced set when one metric would misrepresent a product with several stakeholders.
   5. Scope and priority: expressed as must, should, could, and won't.
   6. Constraints: time, budget, technical, and organizational.
3. **Record what is undecided instead of deciding silently.** For each open point give what is unresolved, the recommended default, another realistic option, and what changes with the choice. List open points at the end of their section.
4. **Check the output location.** If a strategy brief already exists there, ask whether to overwrite it or save a new version, such as `strategy-<YYYY-MM-DD>.md`.
5. **Write the brief** as one self-contained document: `strategy.md` inside the change's directory when the project keeps numbered specification directories, otherwise a project default such as `docs/strategy/<slug>.md`. Never write to or modify a file this skill did not create.

Never fabricate a fact about an existing product, its users, or its metrics. Ask, or record it as an open point.

## Output shape

```markdown
# Product Strategy Brief: <subject>

**Status**: Complete | Draft (incomplete)
**Generated**: <YYYY-MM-DD>
```

A complete brief has the six sections. For an existing project with prior context, add `## Relationship to existing strategy`, stating whether this brief extends, narrows, or replaces the earlier file, with a relative link to it.

If the session ends before all six sections are answered, save a draft with `**Status**: Draft (incomplete)` and a `## Unanswered sections` list. A later run starts fresh or asks about the existing file as in step 4.

## Done when

- The brief has the six sections, or is saved as a draft that lists the unanswered ones.
- Every section is grounded in a framework from the bundled list, and no fact about the product was invented.
- Every undecided material point is written as an open point with a default.

## Bundled files

| File | Read when |
|---|---|
| `references/frameworks.md` | Eliciting a section (step 2): the framework for each section and its source |
