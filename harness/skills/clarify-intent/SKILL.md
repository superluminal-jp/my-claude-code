---
name: clarify-intent
description: Makes the reading of a request explicit and gets it agreed before work continues, by stating what will be produced in a form the person can reject. Use when the person asks to align on intent, scope, or constraints, or when drift shows - a deliverable was rejected, the same point was restated, a summary was corrected, a new instruction contradicts an earlier agreement, or two materially different readings would both let work proceed. Not for a brief request that names a recognizable artifact, nor for writing formal requirements.
---

# Clarify intent

Careful work on the wrong reading is wasted. This skill gets one reading agreed and then stops; it does not write requirements or start the work.

If the request has only one reasonable reading, skip this skill and do the work.

When the project's workflow has its own clarification step (for example Spec Kit's clarify command or the requirements stage of AI-DLC), use that step for the specification, and use this skill for drift inside the conversation.

## Steps

1. **State the reading; do not ask for it.** Write what you take the person to want as the thing you are about to produce, specific enough to be wrong. Present four parts:

   | Part | Content |
   |---|---|
   | Understanding | What will be produced and for whom |
   | Assumptions | Each marked high, medium, or low confidence |
   | Out of scope | What this will not cover |
   | Open points | What is undecided, and what each answer would change |

2. **Offer a criterion, not a list of cases.** State the rule that decides what is in ("every endpoint that returns user data", not five endpoint names). One correction to a rule settles every case; one correction to a case settles one.

3. **Ask only for what you cannot reach yourself:** a fact only the person holds, a preference between equal options, an outside constraint or deadline. For an interpretation, a boundary, or a default, propose one and let the person reject it. Put all questions in one message.

4. **If a rejected deliverable brought you here, find where the readings parted first** - the input you selected, the meaning you gave it, or an assumption you added - and say so. Rebuilding under the same reading repeats the miss.

5. **Stop after three rounds.** If the reading has not converged, list the remaining readings and let the person choose.

6. **Record the agreement** in the conversation as one self-contained summary: the request in the person's words, the agreed understanding, scope in and out, assumptions, and the observable result that will show the work is done. Write it to a file only when the person asks or the project's workflow has a place for it.

When the person waives the check ("just build it"), state the reading you adopt as an assumption in one line and proceed.
