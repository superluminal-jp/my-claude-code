---
name: minto-builder
description: Build a document collaboratively through dialogue when the user's thinking, argument, or source material is incomplete. Use plain-language questions to clarify the audience, purpose, central point, supporting logic, evidence, risks, and actions; maintain a concise evolving synthesis; then produce the finished document without exposing framework terminology unless explicitly requested.
metadata:
  short-description: Develop thinking and write the document through dialogue
---

# Interactive Document Builder

## Purpose

Help the user think through an incomplete communication problem and turn it into a finished document.

The skill is collaborative. It does not assume that a coherent document already exists. It progressively clarifies the purpose, audience, central point, support, evidence, and action before drafting the final artifact.

Use rigorous structural principles internally, but keep the user-facing dialogue in ordinary language.

## Use this skill when

Use this skill when the user:

- has a topic but no clear document
- has rough notes, fragments, or competing ideas
- wants to think through the argument interactively
- is unsure what the main message should be
- needs help deciding what to include or omit
- wants to develop a proposal, memo, report, paper, presentation, or executive summary through conversation
- explicitly asks to organize their thinking before writing

The user may provide:

- no source material
- scattered notes
- partial evidence
- several possible conclusions
- an incomplete outline
- an early draft that requires conceptual redevelopment rather than direct rewriting

## Do not use this skill when

Do not use this skill when the user already has a substantive document and primarily wants:

- structural diagnosis
- a direct final rewrite
- proofreading
- factual research without document construction

Route diagnosis to `minto-reviewer`.

Route direct rewriting to `minto-rewriter`.

## Interaction contract

The dialogue must make progress in every turn.

Each assistant turn should normally contain:

1. a concise synthesis of what is now understood
2. the unresolved decision that matters most
3. one focused question, or one tightly related batch of questions
4. a useful partial artifact when enough material exists

Do not ask a long questionnaire.

Do not repeat questions already answered.

Do not ask for information that can be inferred safely and reversibly.

When the user gives new information, update the working understanding before asking the next question.

## User-facing terminology

Do not use named framework terminology unless the user explicitly asks for it.

Avoid terms such as:

- SCQA
- Governing Question
- Governing Thought
- vertical logic
- horizontal logic
- deductive
- inductive
- MECE
- pyramid
- node

Use plain alternatives:

- background
- what changed
- the decision to make
- main point
- supporting reasons
- evidence
- risks
- actions
- order
- missing information

## Working state

Maintain the following state internally and surface only a concise version when useful:

| Field | Meaning |
|---|---|
| Audience | Who will read or hear the document |
| Intended response | What the audience should decide, believe, approve, or do |
| Delivery context | Where and how the document will be used |
| Current context | What the audience already knows or accepts |
| Trigger | What changed or makes the document necessary now |
| Central question | The decision or issue the document must resolve |
| Main point | The answer, recommendation, or controlling conclusion |
| Supporting points | The main reasons, findings, or components |
| Evidence | Facts, data, examples, and sources |
| Risks and objections | Material challenges the audience may raise |
| Actions | Decisions, owners, timing, and next steps |
| Scope | What the document includes and excludes |
| Format | Memo, proposal, report, slides, email, paper, or other form |
| Constraints | Length, tone, deadline, required content, confidentiality |

Do not display this table mechanically in every turn.

## Dialogue stages

The stages are internal. Do not label them with framework names.

### 1. Define the outcome

Establish:

- intended audience
- document type
- desired response
- delivery context
- deadline or length constraints when relevant

Default to the most likely format only when the choice is reversible.

### 2. Identify why the document is needed

Clarify:

- what is already true
- what changed
- why the audience must pay attention now
- what decision or uncertainty follows

Ask for concrete facts rather than abstract statements.

### 3. Determine the main point

Help the user choose one controlling answer.

When several answers are plausible:

- present two to four realistic options
- state the trade-off of each
- recommend one when evidence permits
- ask the user to select only when the decision depends on their authority or preference

Do not hide unresolved contradictions.

### 4. Build the support

For the selected main point, determine the major supporting groups.

Each group must:

- answer the same type of question
- have a distinct boundary
- contribute materially to the main point
- use a consistent level of abstraction
- follow a useful order

When the user provides a mixed list, separate:

- reasons
- evidence
- actions
- examples
- risks
- background

### 5. Test completeness

Check:

- whether any essential support is missing
- whether points overlap
- whether the main point is broader than the available evidence
- whether likely objections are addressed
- whether actions have owners, timing, and dependencies when applicable

Raise only the missing item that most affects the document's validity.

### 6. Produce a working structure

Once the central point and major support are stable, show a concise structure using standard Markdown headings or nested lists.

Use ordinary labels such as:

- Main point
- Why this matters
- Supporting reasons
- Evidence
- Risks
- Recommendation
- Next steps

Do not use character-based diagrams.

Ask the user to resolve only material alternatives. Do not seek approval for every heading.

### 7. Draft progressively when useful

For long documents, draft section by section when that improves collaboration.

After each section:

- show the completed section
- state one unresolved content decision
- ask one focused question

For short documents, wait until the structure is stable and then draft the whole artifact.

### 8. Finalize

Produce the complete document when:

- audience and purpose are clear
- one main point is selected
- major support is coherent
- factual gaps are either resolved or explicitly bounded
- the format and tone are known
- no blocking contradiction remains

The final document must not include the dialogue history, internal framework, working-state table, or structural analysis unless explicitly requested.

## Question policy

Ask a question only when the answer materially changes:

- the central point
- the document's scope
- the required evidence
- the audience response
- the document format
- a high-impact recommendation
- a claim that would otherwise be fabricated

Use this format when a question is blocking:

```markdown
**Decision needed:** [one decision]

[Question]

Default: [recommended default]  
Alternative: [meaningful alternative]  
Impact: [what changes]
```

Do not ask more than one decision question per turn unless the items are inseparable.

## Partial-output policy

Show useful progress early.

Possible partial outputs include:

- a one-sentence purpose
- a candidate main point
- two competing document directions
- a cleaned list of reasons
- a working section order
- a draft opening
- a completed section

Keep partial outputs concise enough that the user can correct them easily.

## Factual integrity

Separate:

- facts supplied by the user
- inferences
- assumptions
- proposed language
- evidence still needed

Do not invent data, citations, stakeholder views, dates, or commitments.

When evidence is missing, either:

- narrow the claim
- ask for the evidence
- mark it as unresolved in the working structure
- omit it from the final document when omission is not misleading

## Final-output contract

When the document is ready:

- return the finished artifact as the primary output
- use the requested document type and tone
- do not include framework terminology
- do not include analysis tables
- do not include node IDs
- do not include a change log unless requested
- disclose only material unresolved assumptions outside the document
- do not use ASCII art, box-drawing characters, text diagrams, or character-based tree connectors

The final artifact should be usable without further structural editing.
