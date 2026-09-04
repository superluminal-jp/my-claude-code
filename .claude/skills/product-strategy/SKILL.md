---
name: product-strategy
description: Formulate product/business strategy — vision, target users, problem and value proposition, success metrics, MoSCoW-prioritized scope, constraints — before development work begins, including implementation or spec-driven work such as Speckit. Handles both a brand-new product and a new initiative, extension, or pivot on an existing product. Use when the user wants to think through product vision, target users, value proposition, success metrics, or scope priorities before starting development work, for a new or existing project. Out of scope: confirming scope or acceptance criteria on an already-agreed single feature (a separate requirements-clarification capability's job), Scrum events or team facilitation (a separate domain overlay), open-ended document co-creation with no development destination (a separate document-creation capability), and architecture, technology-stack, or build-vs-buy decisions (a separate, later concern this skill does not own).
---

# Product Strategy

Whether the target project is new or existing, before implementation or spec work begins, structure and elicit product/business strategy — vision, target users, problem and value proposition, success metrics, scope priorities, constraints — grounded in citable frameworks, and produce it as a single standalone strategy-brief document.

## Scope

**Covers**: product/business strategy content — vision, target users, problem and value proposition, success metrics, scope priorities, constraints.

**Out of scope** (a separate concern, not this skill's job):

- Architecture, technology-stack, or build-vs-buy decisions. Hard-to-reverse technical calls are handled by a separate capability when it independently applies.
- Confirming the scope or acceptance criteria of a single, already-agreed feature. That's a separate requirements-clarification capability's job; this skill handles the product-level direction those features serve.
- Scrum events or team facilitation.
- Open-ended document co-creation with no development destination (a generic memo, a blog post).
- A general business plan or pitch deck unrelated to upcoming development work.

When another capability independently matches, this skill handles only the strategy framing and doesn't substitute for that other work. If the user wants to skip straight to implementation without a strategy pass, this skill never forces itself into the flow — it activates only on an explicit strategy-framing request.

## How it works

1. **Check for existing context** ([New vs. existing project](#new-vs-existing-project)).
2. **Elicit the six sections, grounded in the matching framework** ([Framework toolbox](#framework-toolbox), [Eliciting the six sections](#eliciting-the-six-sections)).
3. **Check whether a strategy brief already exists at the output location; if so, confirm overwrite vs. new version with the user** ([Overlapping with an existing brief](#overlapping-with-an-existing-brief)).
4. **Produce the strategy brief** ([Output shape](#output-shape)). If interrupted, follow [Handling interruption](#handling-interruption).

## New vs. existing project

Inspect the target project; don't ask the user to pick a mode up front. Treat it as "existing" if any of the following exist: a README describing the product's purpose or current state, an agent-facing document such as CLAUDE.md, a strategy brief this skill previously produced, or a prior spec/plan directory.

- **Existing**: read what's found first, and don't re-ask the user for facts already recorded there — the product name, its existing purpose, its existing user base, and so on. Once you understand how the existing material maps onto the six sections below, elicit only what's new or changing.
  - If multiple past strategy artifacts exist and conflict (e.g., a documented pivot), surface the most recent one and ask the user which should take priority. Never merge silently.
  - If the new strategy conflicts with, narrows, or supersedes the existing context, include a "Relationship to existing strategy" section in the brief (see [Output shape](#output-shape)) that states this explicitly.
  - If none of the context sources physically exist, or exist but are empty or say nothing about the product, fall back to the "new" case below and flag the missing history as an assumption rather than inventing it.
- **New**: elicit all six sections through interview alone.

## Framework toolbox

Every framework this skill applies is grounded in a named, dated, citable source. Never apply an uncited framework.

- **Vision/problem**: Alexander Osterwalder & Yves Pigneur, *Business Model Generation*, Wiley, 2010 (Business Model Canvas). For a leaner treatment, Ash Maurya, *Running Lean*, 2nd ed., O'Reilly, 2012 (Lean Canvas). For the software/tech-product-specific distinction between strategy and a roadmap or backlog, Marty Cagan, *INSPIRED*, 2nd ed., Wiley, 2017/2018 (Silicon Valley Product Group). For the definition of "strategy" itself, Michael E. Porter, "What Is Strategy?," *Harvard Business Review* 74(6), 1996 — a distinct set of activities, not to be conflated with a roadmap or backlog.
- **Target users**: Clayton M. Christensen, Taddy Hall, Karen Dillon & David S. Duncan, "Know Your Customers' 'Jobs to Be Done'," *Harvard Business Review* 94(9), 2016 (Jobs-to-be-Done theory). For how user context is gathered and validated, ISO 9241-210:2019, *Ergonomics of human-system interaction — Human-centred design for interactive systems*. To bridge JTBD's "why" to the actual elicitation "how," Teresa Torres, *Continuous Discovery Habits*, Product Talk LLC, 2021 (Opportunity Solution Tree).
- **Value proposition**: Alexander Osterwalder, Yves Pigneur, Gregory Bernarda & Alan Smith, *Value Proposition Design*, Wiley, 2014 (Value Proposition Canvas).
- **Success metrics**: John Doerr, *Measure What Matters*, Portfolio/Penguin, 2018 (OKRs, tracing to the iMBO practice in Andrew S. Grove, *High Output Management*, Random House, 1983). When a single North Star metric would misrepresent a multi-stakeholder product, the alternative is Robert S. Kaplan & David P. Norton, "The Balanced Scorecard," *Harvard Business Review* 70(1), 1992. The term "North Star" itself traces to Sean Ellis's naming (early 2010s) and Amplitude/John Cutler's systematization ("The North Star Playbook").
- **Scope and priority**: Dai Clegg & Richard Barker, *Case Method Fast-Track: A RAD Approach*, Addison-Wesley, 1994 (MoSCoW). As a lightweight complement to the in/out call — not a replacement — the Kano Model (Noriaki Kano, Nobuhiko Seraku, Fumio Takahashi & Shin-ichi Tsuji, "Attractive Quality and Must-Be Quality," *Quality* 14(2), 1984, pp. 39–48) may optionally identify whether an in-scope item is a baseline expectation or a genuine differentiator.

## Eliciting the six sections

A completed strategy brief includes the following six sections. Ground each one in its matching framework above. When you reach something material the user hasn't decided yet, follow [Recording open points](#recording-open-points). Never fabricate a fact about an existing product, its users, or its metrics when the project offers no evidence — ask, or flag it as an open point instead.

1. **Vision/problem**: what's being built, for whom, and why.
2. **Target users**: the target user(s), framed via JTBD or personas.
3. **Value proposition**: what value this delivers to those users.
4. **Success metrics**: outcome-oriented metrics — a North-Star-style metric plus supporting metrics, or a Balanced Scorecard for a multi-stakeholder product.
5. **Scope and priority**: scope expressed with MoSCoW.
6. **Constraints**: time, budget, technical, and organizational constraints.

### Recording open points

Record unresolved material points explicitly rather than deciding silently, using this structure:

```markdown
**Open point**: <what's unresolved>
**Default**: <the recommended default answer>
**Alternative**: <another realistic option>
**Impact**: <what changes depending on the choice>
```

## Output shape

Produce the strategy brief as a single, self-contained document under the target project — as `strategy.md` inside the existing `specs/<N>-*` convention if the project already uses one, otherwise a project-appropriate default location (e.g., `docs/strategy/<slug>.md`). **Never write into or modify a file you didn't create** — this skill has no dependency on, or integration with, any other tool's files or workflow.

Lead with a machine-readable status marker:

```markdown
# Product Strategy Brief: <subject>

**Status**: Complete | Draft (incomplete)
**Generated**: <YYYY-MM-DD>
```

When `Complete`, the body includes all six sections above. When the target project is existing and has prior context, also include:

```markdown
## Relationship to existing strategy

This brief **extends / narrows / replaces** <relative link to the existing file>.
```

List any open points at the end of the relevant section, in the format from [Recording open points](#recording-open-points).

### Overlapping with an existing brief

Before writing, check whether a strategy brief already exists at the target location. If it does, don't silently overwrite it or silently pile up versions — ask the user which they want:

1. Overwrite the existing file.
2. Save as a new version in a separate file (e.g., `strategy-<YYYY-MM-DD>.md`).

### Handling interruption

If the elicitation session ends before all six sections are answered — the user stops, the session closes, they explicitly say "that's enough for now" — don't discard what was gathered. Save it as a draft with this marker:

```markdown
**Status**: Draft (incomplete)

## Unanswered sections

- <list the unanswered section names>
```

This draft is a legibility safeguard, not a resumable session — a later run either starts fresh or, per [Overlapping with an existing brief](#overlapping-with-an-existing-brief), asks the user about overwriting or versioning the file it finds.

## References

Beyond the primary sources in [Framework toolbox](#framework-toolbox), the following were considered and deliberately left out of the fixed baseline (available to cite as an extension, not required in every brief):

- Steve Blank, *The Four Steps to the Epiphany*, Cafepress, 2005, and Eric Ries, *The Lean Startup*, Crown Business, 2011 — customer development and build-measure-learn. Relevant to *validating* a strategy brief's hypotheses, a follow-on activity this skill's single-pass elicitation doesn't itself perform.
- Marc Andreessen, "The Only Thing That Matters," *pmarchive*, 2007 — product-market-fit vocabulary. Not a structured elicitation method, so not bound to a specific section here.
