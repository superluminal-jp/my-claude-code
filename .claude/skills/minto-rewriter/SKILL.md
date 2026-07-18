---
name: minto-rewriter
description: Transform an existing document or substantial draft into a complete audience-ready document by silently applying rigorous opening, hierarchy, grouping, ordering, and completeness principles. Use when the user asks to rewrite, restructure, improve, polish, or produce a final version. Return the finished document without framework terminology, diagnostic analysis, node IDs, or review tables unless explicitly requested.
metadata:
  short-description: Rewrite an existing draft into a complete final document
---

# Executive Structure Rewriter

## Purpose

Turn an existing document or substantial draft into a complete, usable final document.

Apply rigorous structural principles internally across the entire supplied scope. Do not expose the analytical framework, internal labels, or review process in the output.

## Use this skill when

Use this skill when the user provides an existing:

- draft document
- report
- memo
- proposal
- article
- paper section
- executive summary
- slide narrative
- detailed outline containing enough substantive content to write from

Typical requests include:

- rewrite this
- improve the document
- restructure the argument
- make this executive-ready
- turn this draft into a final version
- make the logic clearer
- produce a polished version
- make the document concise, persuasive, or decision-oriented

## Do not use this skill when

Do not use this skill when the user primarily asks to:

- diagnose the current structure
- explain structural problems
- receive a score or evaluation
- collaboratively discover the argument through dialogue
- create a document from only a topic and no substantive material

Route structural diagnosis to `minto-reviewer`.

Route collaborative development to `minto-builder`.

## Output contract

Return the finished document as the primary output.

Unless explicitly requested, do not include:

- framework names
- specialized structural terminology
- node IDs
- status labels
- analysis tables
- defect lists
- explanations of the rewrite process
- before-and-after comparisons
- a disposition map
- a separate outline preceding the document
- meta-commentary about why the structure works

The reader should experience the result as a naturally well-structured document, not as a document generated from a named framework.

## Full-application requirement

Do not make only localized edits.

Reconstruct the entire supplied scope so that:

- the opening establishes only the context needed for the document's purpose
- the main answer, recommendation, or controlling point is explicit
- each section directly supports the document's central purpose
- headings state useful conclusions when appropriate
- related points are grouped together
- different logical kinds are not mixed
- each group follows a consistent order
- important overlap and omission are resolved
- evidence appears next to the claim it supports
- actions, reasons, findings, risks, and examples are clearly separated
- transitions make the argument easy to follow
- the ending closes the decision, implication, or next action

Treat the source as material, not as a structural constraint.

You may:

- rewrite
- reorder
- merge
- split
- relocate
- condense
- expand using only supported implications
- remove redundant or irrelevant content
- convert labels into informative headings
- change the central conclusion when the source does not support it

Do not preserve the original hierarchy, wording, conclusion, or order merely to minimize changes.

## Factual integrity

Do not invent:

- facts
- evidence
- quotations
- metrics
- dates
- sources
- stakeholder positions
- causal claims
- commitments

When a structurally necessary statement is not supported, choose the least disruptive valid treatment:

1. narrow the claim to what the source supports
2. state the limitation plainly
3. use a visible placeholder when the document is explicitly a working draft
4. omit the unsupported claim when omission does not mislead
5. ask one batched clarification only when the missing information blocks a valid final document

Do not insert internal placeholders into a publication-ready document unless the user asks for a working draft.

## Rewrite workflow

### 1. Establish the writing contract

Infer or identify:

- audience
- purpose
- document type
- desired decision or response
- tone
- length
- required sections
- factual boundaries
- delivery context

If one missing decision materially changes the document, ask one concise batched question. Otherwise proceed with clearly supportable assumptions.

### 2. Extract the source substance

Separate:

- central claim
- supporting claims
- evidence
- context
- risks
- actions
- examples
- constraints
- unresolved points

Do this internally. Do not output the extraction unless requested.

### 3. Determine the document's controlling point

Select the strongest central point supported by the source and appropriate for the audience.

When the source contains competing conclusions, choose the one that best matches the user's stated purpose. If the choice is genuinely blocking, ask for one decision.

### 4. Rebuild the opening

Create an opening that:

- starts from relevant shared context
- introduces the reason the document matters now
- identifies the decision or issue
- states the document's central answer early

Adapt this to the document type. Do not force a formulaic introduction when the medium requires a direct opening.

### 5. Rebuild the body

Construct a complete hierarchy.

For every section:

- state one main point
- include only material that supports that point
- group comparable items together
- use one ordering principle
- place evidence near the supported claim
- separate analysis from actions
- make implications explicit

### 6. Rebuild the ending

End with the form appropriate to the document:

- recommendation
- decision request
- implications
- action plan
- conclusion
- next steps

Do not append a generic summary when the document already closes decisively.

### 7. Edit and proof

Check:

- factual fidelity
- internal consistency
- terminology consistency
- audience-appropriate depth
- paragraph focus
- active voice
- unnecessary repetition
- unsupported certainty
- formatting
- grammar and punctuation

### 8. Return only the finished artifact

Place all substantive final prose in the appropriate finished-output format.

Add a short note outside the document only when a material limitation, unresolved factual gap, or assumption must be disclosed.

## Format rules

Preserve or adapt the expected surface:

- email remains an email
- memo remains a memo
- report remains a report
- slide storyline remains slide titles and supporting content
- academic prose remains appropriately qualified
- executive prose leads with the decision or implication

Do not convert every artifact into a generic report.

## User-facing language

Do not use the following unless the user explicitly requests structural analysis:

- SCQA
- Governing Question
- Governing Thought
- vertical logic
- horizontal logic
- deductive grouping
- inductive grouping
- MECE
- pyramid
- node
- structural status labels

Use ordinary domain-appropriate language.

## Quality guardrails

- Return a complete document, not an outline or patch list.
- Apply the structural principles across the entire supplied scope.
- Do not expose internal reasoning or framework terminology.
- Do not invent facts or evidence.
- Do not retain unsupported claims for stylistic convenience.
- Do not include analysis before the finished document.
- Do not use ASCII art, box-drawing characters, text diagrams, or character-based tree connectors.
- Use normal headings, paragraphs, lists, and tables only when appropriate to the document.
