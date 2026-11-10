---
name: clarify-intent
description: Form an explicit shared understanding of what the person intends before work continues - state the reading as something they can reject, converge on a criterion rather than on cases, and record the agreement. Use when the person asks to align on intent, scope, or constraints, and when drift shows itself - the previous deliverable is rejected, one point is restated twice, a summary of the request is corrected, a new instruction contradicts an earlier agreement, or two materially different readings would both let work proceed. Do not use merely because a request is brief when it names a recognizable artifact or workflow, for ordinary context gathering inside other work, to frame a problem as a gap, to set product direction, or to write formal requirements.
metadata:
  kind: worker
  permission: workspace_write
  sandbox: inside
  produces: a shared-understanding memo the person has agreed to
---

# Clarify intent

Precise requirements for the wrong thing are worse than none. This skill makes the reading of the request explicit and gets it agreed, and stops there. Turning the agreement into testable requirements is a separate capability.

## When this applies

Run when the person asks for it, or when at least one drift signal holds:

1. The person rejects the immediately preceding deliverable and asks for it again.
2. The person restates the same point two or more times.
3. The person corrects your summary or read-back.
4. A new instruction contradicts something already agreed.
5. Two materially different readings of the request both let the work proceed.

If none holds and the person has not asked, do not run. A short request that names a recognizable artifact or workflow is not ambiguous by brevity alone. You cannot always detect your own divergence, so the person's explicit request is always a valid way in.

## Steps

1. **State the understanding; do not ask for it.** Put the reading into words the person can reject: what is about to be produced, specific enough to be wrong. Present four parts separately:

   | Part | Content |
   |---|---|
   | Understanding | What you take the person to want, stated as what you will produce |
   | Assumptions | Each with its confidence: high, medium, or low |
   | Out of scope | What this explicitly does not cover |
   | Open points | What remains undecided, and what each answer would change |

   Do not begin the requested work until the person corrects or approves. If they waive the check ("just build it"), state the adopted reading as an assumption and proceed.
2. **Present a criterion, not a list of cases.** State the criterion that decides what is in, specific enough that the person can give a counterexample. One correction to a criterion fixes every case at once; one correction to a case fixes one case.
   - Ask only for what you cannot reach: facts only the person holds, a preference between equivalent options, an external constraint or deadline.
   - Do not ask about interpretations, boundaries, or defaults. Propose a candidate and wait for rejection.
3. **Ground the criterion in a named framework** from `references/applied-frameworks.md`. Pick the group by the kind of gap, then the entry that most directly generates a criterion.
   - Name at most two per presentation, each attached to the judgement it produced. Never explain a framework instead of applying it.
   - Name one only if it actually supports the judgement. If nothing fits, say that the criterion rests on your own reasoning.
4. **When drift triggered entry, locate the divergence first.** Do not rebuild the deliverable under the reading that was just rejected. Use Group C of the inventory to find where the two readings parted - the data selected, the meaning assigned, or the assumption added - and state it.
5. **Bound the exchange at three rounds.** If the reading has not converged, say so, list the remaining readings, and let the person choose. Failing to converge usually means the criteria are not refutable or are being stated as cases; re-examine how they are written before a fourth round.
6. **Record the agreement** as one self-contained memo, in this order: the request in the person's own words; your understanding; scope, included and excluded; assumptions with confidence; the observable completion condition; open points and risks.
   - Location: `shared-understanding.md` inside the change's directory when the project keeps numbered specification directories; otherwise a project default such as `docs/shared-understanding/<slug>.md`.
   - Language: that of the conversation. Keep framework names and sources in their original language, so they can be checked against the source.
   - Never write to or modify a file this skill did not create. If a memo already exists at that path, ask whether to overwrite it or save a new version.
   - If the session ends before agreement, save what was collected as a draft marked incomplete.

## Edge cases

| Situation | Response |
|---|---|
| The request admits only one reading | Do not run; proceed with the work |
| The person refuses the check | Stop the exchange, state the adopted reading as an assumption, proceed |
| The person already knows the framework | Keep naming it; dropping the name removes the check on whether it supports the judgement |
| Three rounds without convergence | Say so, list the remaining readings, and hand the choice to the person |

Avoid these: silently picking one of several plausible readings; asking after the work is done; confirming cases one by one; stacking questions turn by turn instead of batching them; redirecting a sufficiently defined request into a requirements interview; borrowing a framework's name for a judgement it does not support.

## Done when

- The person has corrected or approved the stated understanding, or has waived the check and the adopted reading is stated as an assumption.
- On agreement, the memo exists at the resolved path with all six parts; without agreement, a draft marked incomplete exists.
- No file this skill did not create was changed.

## Bundled files

| File | Read when |
|---|---|
| `references/applied-frameworks.md` | Choosing the framework a criterion comes from (steps 3 and 4) |
| `references/design-basis.md` | Explaining to the person why you restate rather than assume: only its Group F may be named to them, and only as the reason for your own restatement |
