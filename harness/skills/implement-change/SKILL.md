---
name: implement-change
description: Change code, configuration, tests, scripts, interfaces, or other observable behavior test-first, in the smallest coherent step, and verify it before reporting. Use for every such change - a feature, a fix, a refactor, review feedback. Do not use for prose-only documents, for a review that changes nothing, or for research that changes no file.
metadata:
  kind: worker
  permission: workspace_write
  sandbox: inside
  produces: a verified change, with the commands run and their results
---

# Implement a change

A change is done when a check that failed before it passes after it, the repository's own checks still pass, and the documents that state the changed contract say what the code now does. Work through the steps in order; skip a step only when its condition does not hold.

## Steps

1. **Define.** State the purpose, the scope, and the observable completion condition. Resolve a gap that would change the result before editing. When the change has a requirements graph, its acceptance criteria are the completion condition: take one leaf requirement at a time and do not restate the criteria anywhere else.
2. **Specify, when observable behavior is added or altered.** Read `references/spec-first.md` and write or update the specification first.
3. **Red.** Add or identify a deterministic check and watch it fail on what it asserts.
   - For something that does not exist yet (a function, an endpoint, an option), first add it with its final signature returning a wrong result of the right type, then watch the assertion fail. An import, name, compile, or usage error is not a red, because nothing tells it apart from a check that is itself broken.
   - A check that cannot fail before the change, because it pins behavior the change must keep, is shown able to fail by breaking the implementation on purpose, watching the check fail, and restoring it.
   - For prose, policy, or structure that cannot be asserted meaningfully, record the concrete current state and how the result will be compared with it. Do not write a token-presence test only to claim a red.
4. **Green.** Make the smallest change that passes the check, then refactor with the checks still passing.
5. **Verify.** Run the repository's tests, linter, formatter, and type checker, and read the output before claiming success. Report each command with its result, and say which could not run and why.
6. **Synchronize.** Update, in the same change, the document that states each changed public contract: usage, configuration, interface, default. When nothing documented changes, say so in one line with the reason.
7. **Publish only on request.** Committing, pushing, and opening a pull request each need the person's explicit request; a request for one does not cover the others.

Stop and tell the person when a step fails for a reason the change cannot fix, such as a wrong specification or a check that cannot run. Do not skip the step or loosen the check to proceed.

## Constraints on every change

- Tests define the contract. Never delete, skip, or weaken a failing test to pass the suite; fix the cause. A test that is hard to write is a signal about the interface, so fix the interface.
- Name tests by behavior (`user_cannot_login_with_invalid_password`). Use one assertion per test where practical, and several only for one logical outcome. Keep tests deterministic: control time and randomness.
- Match the repository: its language conventions, linter, formatter, type checker, test runner, logger, and error style. Do not import outside defaults.
- Change only what the task needs: no speculative abstraction, no drive-by refactor, no comments or annotations on untouched code. When a nearby improvement would clearly help, say so and leave it.
- Comment the reason and the non-obvious invariant, not the next line.
- Read `references/type-safety.md` when the language is statically or gradually typed.
- Read `references/boundaries.md` when the change touches input from outside, output to users, files, network, databases, external APIs, secrets, error handling, or logging.

## Done when

- The check from step 3 failed for the right reason before the change and passes after it; or, for a change that cannot be asserted, the recorded earlier state and the comparison are reported.
- The repository's own checks pass, each command and its result is reported, and anything not run is named.
- Changed public contracts and their documents agree, or the absence of documentation impact is stated with its reason.
- Nothing was committed, pushed, or published beyond what the person asked for.

## Bundled files

| File | Read when |
|---|---|
| `references/spec-first.md` | The change adds or alters observable behavior (step 2) |
| `references/type-safety.md` | The language is statically or gradually typed |
| `references/boundaries.md` | The change touches a system boundary, secrets, errors, or logging |
