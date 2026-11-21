---
name: define-problem
description: Turns a vague sense that something is wrong into one verifiable problem statement - the gap between the current state and the wanted state - kept apart from causes and solutions, in any domain (technical, business, organizational, personal). Use when the person wants to pin down what the problem actually is before analyzing causes or choosing a fix. Not for root-cause analysis, comparing solutions, or planning the work.
---

# Define a problem

A problem is the gap between how things are and how they should be. A statement that names a solution ("we need a cache") or an unverified cause ("the database is slow") closes off better answers before anyone has looked, so this skill writes the gap alone.

## Steps

1. **Collect what is observed.** Ask for or find the facts: what happens, where, since when, how often, who is affected, how it was noticed. Mark each item as observed, reported by someone, or assumed.

2. **Separate what came bundled.** People usually arrive with a cause or a fix attached. Set each aside under its own label - hypothesis or proposed solution - and keep it out of the statement. They are inputs for later, not part of the problem.

3. **State the current state** in measurable or checkable terms: a number, a rate, a concrete event. "Deploys take 40 minutes", not "deploys are slow".

4. **State the wanted state** the same way, and where it comes from: a target, a standard, a commitment, an earlier level, a comparison. When nobody can say what "good" is, that is the first thing to settle; say so and stop there.

5. **State the gap and why it matters:** who bears it, what it costs or risks, and what happens if nothing changes. A gap nobody bears is not yet a problem worth solving.

6. **Check the statement.** It passes when:
   - it contains no solution and no unverified cause;
   - two people reading it would agree on whether the problem is solved;
   - it covers one problem; split it when the current states, owners, or measures differ.

7. **Hand it back** in this form and ask the person to confirm or correct it:

   ```
   Current state: ...
   Wanted state:  ... (source: ...)
   Gap:           ...
   Why it matters: ...
   Set aside - hypotheses: ...   proposed solutions: ...
   Not yet known: ...
   ```

## Done when

- The person agreed to a statement that passes step 6.
- Every bundled cause and solution is listed as set aside, not lost.
- Facts still missing are listed with how each could be obtained.
