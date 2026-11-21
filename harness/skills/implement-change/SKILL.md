---
name: implement-change
description: Changes code, configuration, tests, scripts, or other observable behavior test-first, in the smallest coherent step, and verifies the result before reporting. Use for a feature, a fix whose cause is known, a refactor, or review feedback that changes behavior. Not for finding the cause of a failure, prose-only documents, reviews that change nothing, or research.
---

# Implement a change

A change is done when a check that failed before it passes after it, the project's own checks still pass, and the documents that describe the changed behavior are correct.

When the project runs its own workflow (Spec Kit, AI-DLC, or another documented process), that workflow decides the specification, the task order, and where artifacts go. Use this skill for how each task is carried out inside it.

## Steps

1. **Fix the target.** State what will be observably different when the change is done. If acceptance criteria exist, they are the target; work on one at a time.

2. **Read before writing.** Open the code to be changed, its callers, and its tests. Find the project's commands for test, lint, format, type check, and build (README, package manifest, Makefile, CI workflow).

3. **Red.** Add or pick a check and watch it fail on the thing it asserts.
   - For something that does not exist yet, first add it with its final signature and a wrong result, so the failure is the assertion. An import or compile error does not show the check works.
   - For behavior that must stay the same (a refactor), show the existing check can fail: break the code on purpose, see the failure, restore it.
   - Where no automated check is possible, record the current state concretely (output, screenshot, measurement) and how the result will be compared with it.

4. **Green.** Make the smallest change that passes. Then tidy with the checks still passing.

5. **Verify.** Run the project's full checks through the `check-runner` subagent when the output is long, otherwise directly. Read the results; a command that could not run is reported as not run, with the reason.

6. **Update documents.** In the same change, correct each document that describes what changed: usage, configuration, interface, default. When nothing documented changed, say so in one line.

7. **Report** each command and its result, what changed (paths), and what was not done. Committing and pushing wait for the person's request.

## Constraints

- A failing test is evidence. Fix the cause; skipping, deleting, or loosening a test needs the person's agreement that the test is wrong.
- Change only what the target needs. Mention a nearby improvement instead of making it.
- Match the project: its conventions, error style, logger, and libraries. Add a dependency only when the target needs it, and say so.
- Validate data where it enters the system, and handle errors where something can be done about them.
- When a step fails for a reason the change cannot fix - a wrong specification, a check that cannot run - stop and tell the person rather than working around it.

## Done when

- The check from step 3 failed for the intended reason before the change and passes after it, or the recorded before-and-after comparison is reported.
- The project's checks pass, with each command and result reported and anything not run named.
- The documents describing the changed behavior agree with it.
