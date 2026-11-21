---
name: define-problem
description: Turns a vague sense that something is wrong into one verifiable problem statement - the gap between the current state and the wanted state - kept apart from causes and solutions, in any domain (technical, business, organizational, personal). Use when the person wants to pin down what the problem actually is before analyzing causes or choosing a fix. Not for root-cause analysis, comparing solutions, or planning the work.
---

# Define a problem

This is gap analysis: a problem is the difference between how things are and how they should be. A statement that names a solution ("we need a cache") or an unverified cause ("the database is slow") closes off better answers before anyone has looked, so this skill writes the gap alone.

## Steps

1. **Collect the facts** with 5W1H, and with the is / is-not contrast of Kepner-Tregoe problem analysis: where and when it happens, and where and when it could but does not. Mark each fact as observed, reported by someone, or assumed.

2. **Separate what came bundled.** People usually arrive with a cause or a fix attached. Set each aside under its own label - hypothesis or proposed solution - and keep it out of the statement. They are inputs for later, not part of the problem.

3. **State the current state and the wanted state** in terms that can be checked: a number, a rate, a concrete event ("deploys take 40 minutes", not "deploys are slow"). Give the source of the wanted state: a target, a standard, a commitment, an earlier level. When nobody can say what "good" is, that is the first thing to settle; say so and stop there.

4. **State the gap and why it matters:** who bears it, what it costs or risks, and what happens if nothing changes.

5. **Check the statement.** It passes when it contains no solution and no unverified cause, when two people reading it would agree on whether the problem is solved, and when it covers one problem. Split it when the current states, owners, or measures differ.

6. **Hand it back** in this form and ask the person to confirm or correct it:

   ```
   Current state: ...
   Wanted state:  ... (source: ...)
   Gap:           ...
   Why it matters: ...
   Set aside - hypotheses: ...   proposed solutions: ...
   Not yet known: ... (and how each could be found out)
   ```
