---
name: debug-failure
description: Finds the cause of a failure - a failing test, an error, a crash, a wrong result, a flaky or slow run - by reproducing it, narrowing where it happens, and confirming the cause before fixing it. Use when something does not work and the cause is not yet known, or when a previous fix did not hold. Not for implementing a change whose cause is already confirmed.
---

# Debug a failure

A fix made before the cause is known usually moves the symptom. Find the cause first, show that it is the cause, then fix it.

## Steps

1. **Read what the failure says.** Read the complete error, stack trace, or log, including the first error, since later ones are often consequences. Note the exact message, the file and line, and the input.

2. **Reproduce it.** Find the smallest command that fails the same way and note how often it fails. If it cannot be reproduced, gather more evidence (logs, versions, environment, timing) and say so; do not guess a fix.

3. **Find what changed.** Compare with a state that works: an earlier commit (`git log`, `git diff`, `git bisect` for a long range), another environment, another input, a dependency version.

4. **Narrow it.** Halve the search space each step: check the value at the midpoint of the path from input to failure, and move toward the half where it first goes wrong. Add temporary logging or assertions to see actual values rather than reasoning about what they must be.

5. **State one hypothesis** as "X causes the failure because Y", and predict something it implies that you have not yet observed.

6. **Test the hypothesis with one change.** Make the smallest change that would confirm or refute it. If refuted, undo the change and return to step 4 with what was learned; stacking further changes on a wrong guess hides the evidence.

7. **Fix the cause.** Write a check that reproduces the failure, watch it fail, fix the cause where it originates rather than where it surfaces, and watch the check pass. Run the project's full checks.

8. **Clean up and report.** Remove temporary logging. Report the cause, the evidence that confirms it, the fix, the check that now guards it, and anything still unexplained.

## When it does not converge

- After three refuted hypotheses, stop and re-read the evidence from step 1; an assumption made early is probably wrong. List what is confirmed and what was only assumed.
- A failure that comes and goes points to shared state, ordering, timing, or the environment. Run the test alone, in a different order, and repeatedly, and record the failure rate before and after any change.
- When the cause lies outside what can be changed (a dependency, a service, the environment), report the evidence and the options rather than patching around it silently.

## Done when

- The failure was reproduced, or the report says it was not and what evidence is missing.
- The stated cause is backed by an observation that would have been different if the cause were something else.
- A check that failed because of the cause now passes, and the project's other checks still pass.
- Temporary debugging changes are gone.
