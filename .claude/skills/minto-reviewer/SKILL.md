---
name: minto-reviewer
description: Analyze an existing document, outline, slide storyline, or argument structure for coherence, hierarchy, grouping, ordering, and completeness using Barbara Minto's Pyramid Principle. Use when the user asks for structural diagnosis, critique, evaluation, or an explanation of what is wrong. Return analysis and recommendations, not a silently rewritten final document.
metadata:
  short-description: Diagnose the structure of an existing document
---

# Minto Pyramid Document Reviewer

## Purpose

Analyze an existing communication artifact and explain whether its argument structure works.

The output is a diagnostic deliverable. It must make structural defects visible, identify their consequences, and specify the target-state requirements. It must not silently replace the source with a polished final document.

## Use this skill when

Use this skill when the user provides an existing:

- document or draft
- outline or section plan
- executive summary
- proposal, memo, report, or paper
- slide storyline or action-title sequence
- argument tree or issue tree

Typical requests include:

- analyze the structure
- review the logic
- identify weaknesses
- check whether the argument is coherent
- assess the opening, conclusion, grouping, or flow
- explain why the document is difficult to follow
- recommend a better structure without writing the final prose

## Do not use this skill when

Do not use this skill when the user primarily asks to:

- rewrite the document into a finished version
- produce publication-ready prose
- create a document collaboratively from incomplete thinking
- brainstorm a topic without an existing artifact
- fact-check claims without reviewing structure

Route finished-document rewriting to `minto-rewriter`.

Route collaborative document development to `minto-builder`.

## Input assumptions

The input must contain an existing artifact or a meaningful portion of one.

Record:

- intended audience, when known
- decision, belief, or action expected from the audience
- document type and delivery context
- supplied scope
- explicit constraints
- whether only diagnosis or also a target outline is requested

Do not treat a partial excerpt as a complete document. State the review boundary.

## Analytical model

Evaluate three distinct layers.

### Opening logic

When the input includes an opening, determine whether it:

- establishes relevant shared context
- introduces a meaningful change, problem, tension, or opportunity
- raises a natural central question
- provides a direct central answer
- avoids background that does not help the audience understand the decision

Do not penalize a partial section for lacking an opening when the opening is outside the supplied scope.

### Top-level argument

Determine whether:

- the central answer is explicit
- the central answer addresses the audience's actual question
- the direct supporting points collectively establish that answer
- the central answer is no broader than its support
- the top-level points are comparable and non-overlapping

### Hierarchical argument

For every parent and child group, determine whether:

- the parent is a complete proposition rather than a topic label
- every child answers the same immediate question raised by the parent
- the parent accurately summarizes the children
- sibling statements are at comparable levels of abstraction
- sibling statements are all reasons, actions, findings, risks, evidence, examples, or another single logical kind
- the group follows either a valid reasoning chain or a meaningful category-based grouping
- the ordering principle is consistent
- the stated scope is covered without material overlap or omission

## Statuses

Use exactly:

- **Pass:** The relationship satisfies the relevant structural rule.
- **Weak:** The intended logic is recoverable but ambiguous, incomplete, uneven, or imprecise.
- **Fail:** The relationship violates the structural rule or supports a materially different conclusion.
- **Not assessable:** The supplied material is insufficient to evaluate the relationship.

Do not use a numeric score unless explicitly requested.

## Review workflow

### 1. Define the review boundary

State:

- artifact reviewed
- audience and purpose, explicit or inferred
- supplied scope
- excluded scope
- confidence in the inferred context

### 2. Reconstruct the current structure

Represent the current hierarchy using nested Markdown lists or tables.

Assign stable node IDs when the artifact contains multiple levels.

Preserve the original wording. If a node must be normalized into a proposition, show the original and normalized versions separately.

Do not use character-based diagrams.

### 3. Identify the central question and answer

State:

- the question the document appears to answer
- the answer it appears to give
- whether each is explicit or inferred
- whether the answer directly addresses the question

### 4. Review the opening when applicable

Evaluate:

- context relevance
- significance of the change or problem
- natural emergence of the central question
- directness of the answer
- consistency between the answer and the document's top claim

Report opening quality separately from the body structure.

### 5. Review every parent-child relationship

For each parent:

- state the immediate question raised by the parent
- identify whether each child answers that question
- test whether the children collectively support the parent
- test whether the parent faithfully summarizes the children
- identify unsupported content in the parent
- identify relevant child content omitted from the parent

### 6. Review every sibling group

Classify each group as:

- reasoning chain
- category-based group
- mixed
- unclear

For a reasoning chain, test whether sequence and inference are valid.

For a category-based group, test:

- common logical kind
- common level of abstraction
- distinct boundaries
- sufficient coverage
- consistent ordering

### 7. Separate reasoning from evidence

Identify cases where:

- evidence is presented as a reason
- examples are presented as complete proof
- implementation actions are mixed with reasons
- background facts are mixed with conclusions
- evidence quality is discussed as though it were a separate cause

Report structural validity separately from factual or evidential validity.

### 8. Prioritize and complete the findings

Prioritize the highest-impact defects first, but include every distinct defect that materially prevents full structural compliance.

Repetitive instances may be grouped only when all affected node IDs are listed.

### 9. Provide the target-state requirements

When requested, provide a complete target outline for the reviewed scope.

The target outline may substantially differ from the source, but it remains an outline or structural specification, not finished prose.

Mark unsupported requirements explicitly:

- `[Evidence needed]`
- `[Premise needed]`
- `[Scope decision needed]`
- `[Audience decision needed]`

## Output contract

Use this order.

### Overall judgment

```markdown
- Opening logic: Pass / Weak / Fail / Not assessable
- Body structure: Pass / Weak / Fail / Not assessable
- Overall: Pass / Weak / Fail / Not assessable
```

Follow with one sentence naming the most consequential issue.

### Review boundary

Include audience, purpose, scope, exclusions, and confidence.

### Reconstructed current structure

Use nested Markdown lists or a table.

### Relationship findings

| ID | Scope | Relationship type | Status | Finding | Target-state requirement |
|---|---|---|---|---|---|

### Complete conformance gaps

For each distinct issue include:

- impact
- affected nodes
- violated structural rule
- consequence for the audience
- required target-state condition

### Target outline

Include only when requested.

Do not produce finished prose unless the user explicitly changes the task to rewriting.

## User-facing terminology

This is an analysis skill. Technical terminology may be used when it increases precision.

Define specialized terms briefly when the user has not used them.

Do not turn the report into a tutorial unless requested.

## Quality guardrails

- Do not silently rewrite the document.
- Do not confuse persuasive tone with structural validity.
- Do not infer completeness without defining the relevant scope.
- Do not preserve a defective conclusion merely because it appears in the source.
- Do not invent facts, evidence, audience needs, or business context.
- Do not use ASCII art, box-drawing characters, text diagrams, or character-based tree connectors.
- Use standard Markdown headings, nested lists, and tables.
- Keep source wording and proposed wording distinguishable.
- Report uncertainty explicitly.

## References

- Barbara Minto, *The Minto Pyramid Principle: Logic in Writing, Thinking, and Problem Solving*, 1987.
