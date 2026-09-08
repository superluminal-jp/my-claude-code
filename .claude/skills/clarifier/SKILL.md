---
name: clarifier
description: Form an explicit shared understanding of what the user intends, then turn that agreement into testable, bounded requirements. Use when the user asks to align on intent, scope, constraints, or acceptance criteria, and when drift shows itself — the previous deliverable is rejected, one point is restated twice, a summary of the request is corrected, a new instruction contradicts an earlier agreement, or two materially different readings would both let work proceed. Stage one states the AI's reading, its assumptions with confidence, what is out of scope, and the open points, with each criterion drawn from a named framework; stage two converts the agreement into acceptance criteria via INVEST, Given/When/Then, MoSCoW, and FURPS+. Do not use merely because a request is brief when it names a recognizable artifact or workflow and gives enough to start, nor for ordinary context gathering inside that work; framing the gap between a current and an ideal state, setting product direction before development begins, and building a document from incomplete material through dialogue each belong to separate capabilities and are out of scope here. When another capability independently matches, run this first as a prerequisite only to clear blocking ambiguity, then continue with that work.
---

# Shared Understanding, Then Formal Requirements

Two stages, in order.

**Stage 1 — shared understanding of intent.** State what the AI understands the user to want,
in terms the user can reject. Converge on a criterion, not on a list of cases.

**Stage 2 — formal requirements.** Convert the agreement into requirements that can be tested.

Stage 2 applies **only after stage 1 holds**. Formalising a reading nobody has confirmed
produces precise requirements for the wrong thing.

## When this applies

Run when the user asks for it, **or** when at least one of these drift signals holds:

1. The user rejects the immediately preceding deliverable and asks for it again.
2. The user restates the same point two or more times.
3. The user corrects the AI's summary or read-back.
4. A new instruction contradicts something already agreed.
5. Two materially different readings of the request both let the work proceed.

If none of these holds and the user has not asked, **do not run**. A short request that names a
recognizable artifact or workflow is not ambiguous by brevity alone.

---

## Stage 1 — Shared understanding of intent

### 1. State the understanding; do not ask for it

Put the AI's reading into words the user can reject. Not a paraphrase of the request — a
statement of what is about to be built, specific enough to be wrong.

Present these **separately**; never blend them:

| Section | Content |
|---|---|
| Understanding | What the AI takes the user to want, stated as what it will produce |
| Assumptions | Each with a confidence marker: high / medium / low |
| Out of scope | What this explicitly does not cover |
| Open points | What remains undecided, and what it would change |

Do not begin implementing the requested work until the user corrects or approves — unless the
user explicitly waives the check ("just build it"), in which case state the adopted reading as
an assumption and proceed.

The reason for restating at all, rather than assuming the request carried across, is in
[Group F](references/design-basis.md). It is the one part of the design basis that may be
named to the user, and only ever as the reason for the AI's own restatement — never as a claim
about the user's mind.

### 2. Present a criterion, not a list of cases

State the **criterion** that decides what is in — the intension. Do not walk the user through
cases one at a time to triangulate the intent — the extension.

- A criterion must be specific enough that the user can produce a counterexample. "Handled
  appropriately" cannot be refuted, so it does not count as a statement.
- **Ask only about what the AI cannot in principle reach**: facts only the user holds,
  preferences between genuinely equivalent options, external constraints and deadlines.
- **Do not ask about interpretations, boundaries, or defaults.** Propose a candidate and wait
  for rejection. Asking hands back work the AI is capable of doing.

The difference matters for convergence. One correction to a criterion fixes every case at once;
one correction to a case fixes one case.

### 3. Ground the criterion in a named framework

Draw each criterion from a named practice, standard, or framework in
[the applied inventory](references/applied-frameworks.md), and name it beside the judgement it
produced.

- **Select by group first.** The kind of gap picks the group; within the group, take the entry
  that most directly generates a criterion. Never scan a flat list.
- **Name at most two per presentation.** More raises the reading cost and starts to look like
  the frameworks are the point.
- **Attach the name to a judgement.** Never present a framework on its own, and never explain
  one before applying it.
- **Name it only if it actually supports the judgement.** Borrowing a name for authority it did
  not earn is the failure this rule exists to prevent.
- **If nothing in the inventory fits, say so.** State that no established framework covers this
  gap and that the criterion rests on the AI's own reasoning. Do not force the gap into the
  nearest available framework.

Naming the framework does two things at once: it makes the criterion checkable against a source
outside this conversation, and it lets the user pick up the vocabulary while working rather
than by studying. The second is a consequence of the first, not a separate feature.

The theory governing this behaviour is in [the design basis](references/design-basis.md).
Groups E and G there are never named to the user; Group F only under the restriction above.

### 4. Bound the exchange at three rounds

At most three rounds of correction. If the reading has not converged, present the fact that it
has not, list the remaining candidate readings, and let the user choose.

This bound is not arbitrary. While the exchange runs on criteria, a single correction repairs
many cases at once, so convergence is the expected behaviour. Failing to converge in three
rounds is therefore a signal about the criteria themselves — they are probably not refutable,
or they are being stated as cases. Re-examine how they are written before adding a fourth round.

### 5. When drift triggered entry, locate the divergence first

Do not rebuild the deliverable under the same reading that was just rejected. Use Group C of
[the applied inventory](references/applied-frameworks.md) to find the rung at which the two
readings parted — the data selected, the meaning assigned, or the assumption added — and state
it. Only then resume.

The AI cannot always detect its own divergence; the signals above are observable proxies, not a
guarantee. The user's explicit request is therefore always available as an entry path and must
never be treated as redundant.

### 6. Record the agreement

On agreement, write a **single self-contained memo**, in this order:

1. The request, in the user's own words
2. The AI's understanding
3. Scope — included and excluded
4. Assumptions, with confidence
5. Observable completion condition
6. Open points and risks

**Where it goes.** If the project uses a numbered `specs/<N>-*` convention, write
`shared-understanding.md` inside that directory. Otherwise use a sensible project default such
as `docs/shared-understanding/<slug>.md`.

**Language.** Write the memo in the language of the conversation. Keep framework names and
sources in their original language — a translated name cannot be checked against its source,
and the user cannot reach the original.

**Never write to or modify a file this capability did not create.**

**If one already exists** at the path resolved above, ask whether to overwrite or save a new
version. Sameness is decided by that path matching — never by how similar the contents look,
since any similarity threshold is arbitrary and cannot be verified.

**If the session ends before agreement**, save what was collected as a draft, marked
explicitly as incomplete. Do not discard it.

---

## Stage 2 — Formal requirements

Applies once stage 1 holds. Group D of
[the applied inventory](references/applied-frameworks.md) is the working set here.

### Ambiguity patterns to flag

- **Vague quantifiers**: "fast", "a lot", "many", "soon", "robust", "scalable",
  "user-friendly" -> demand a number + unit.
- **Undefined pronouns / scope**: "it", "the system", "everything" -> name the target.
- **Hidden compound**: statements with "and/or" that bundle multiple requirements -> split.
- **Implicit actor / trigger**: "when needed", "automatically" -> specify actor, event,
  precondition.
- **Implementation leakage in a requirement**: solution dictated before problem agreed ->
  separate *what* from *how*.
- **Negation without positive**: "should not be slow" -> restate as a measurable positive
  ("p95 < 200ms").

### Elicitation toolbox (use selectively)

- 5W2H for missing dimensions.
- SMART for measurable goals.
- INVEST for user-story quality.
- Given/When/Then for test scenarios.
- MoSCoW for scope prioritization.
- FURPS+ for non-functional requirements.
- EARS, Volere fit criteria, and Planguage when a requirement sentence or a quality target
  needs a stricter form.

### Quality gate

Before moving to implementation, each requirement should be:

- unambiguous,
- feasible,
- verifiable,
- non-conflicting,
- scoped enough to estimate.

### Clarification template

```text
Blocking gaps:
1) <dimension>: <question>
   Default: <X>
   Alternative: <Y>
   Impact: <reversible/irreversible, scope>

Assumptions if proceeding:
- <assumption> (confidence: high/medium/low)
```

---

## Persistent user model

When a fact surfaces that will still hold after this request is finished, **propose** recording
it. Write only after the user explicitly approves.

Keep one file per project: `docs/shared-understanding/user-profile.md`. On a new fact that
contradicts what is recorded, show the contradiction, confirm which one currently holds, and
update.

**Record only facts about how the user wants work done** — preferred granularity, how often to
check in, vocabulary in use, preferred deliverable formats.

**Never record:**

1. Assessments of ability or experience ("unfamiliar with X").
2. Business-sensitive material — unannounced plans, contracts, internal organisational matters.
3. Statements about third parties.

The restriction is on the content, not just on the approval, because this file is committed and
becomes permanently visible to everyone who can read the repository. Approval covers the
judgement made at that moment; permanent visibility outlives it.

---

## Edge cases

| Situation | Response |
|---|---|
| The request admits only one reading | Do not run. Proceed with the work |
| The session ends before agreement | Save a draft marked incomplete; do not discard |
| A memo already exists at the resolved path | Ask: overwrite or new version. Never decide silently |
| The user refuses the check ("just build it") | Stop the exchange, state the adopted reading as an assumption, proceed |
| Several frameworks fit one gap | Pick the group first, then the entry that most directly generates a criterion. At most two names |
| The user already knows the framework well | Keep naming it. Whether they have learned it is not observable, and dropping the name removes the check on whether it supports the judgement |
| Three rounds without convergence | State that it has not converged, list the remaining readings, hand the choice to the user |

## Anti-patterns

- Silently picking one interpretation when several are plausible.
- Asking after the work is done ("I built X, is that what you wanted?").
- Confirming cases one by one instead of stating the criterion that decides them.
- Asking the user to supply an interpretation, boundary, or default the AI could have proposed.
- Stacking clarifications turn-by-turn instead of batching them.
- Treating a materially ambiguous request such as "make it better" as actionable without an
  agreed fit criterion.
- Redirecting a sufficiently defined artifact request into a generic requirements interview.
- Inventing acceptance criteria the user never agreed to.
- Attaching a framework name to a judgement it does not actually support.
- Explaining a framework instead of applying it.

## Framework index

| Layer | Groups | Named to the user? |
|---|---|---|
| [Applied inventory](references/applied-frameworks.md) | A confirming grounding · B conveying intent · C locating the divergence · D writing and verifying requirements | Yes — attached to the judgement it produced, at most two at a time |
| [Design basis](references/design-basis.md) | E design of the learning path · F why restatement is necessary · G theory of coordination | No — except F, as the reason for the AI's own behaviour |

## References

Full bibliography, with the criterion each source generates, lives in
[the applied inventory](references/applied-frameworks.md) and
[the design basis](references/design-basis.md). Those two files are the canonical record; this
one does not repeat them.
