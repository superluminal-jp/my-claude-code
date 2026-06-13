---
name: debugger
description: Find and fix the root cause of a defect with a disciplined, evidence-driven method — reproduce, isolate, hypothesize, verify, then lock the fix with a regression test. Use when behavior is wrong and the cause is not yet known: failing tests, crashes, incorrect output, flaky or intermittent failures, performance regressions, or "it works on my machine" reports. Reproduces deterministically first, narrows the fault by bisection and logging, fixes the cause (not the symptom), and adds a failing-first test that proves the bug and prevents regression. Composes with the coder skill's TDD/SDD discipline.
when_to_use: debug failing behavior, find root cause, fix a bug whose cause is unknown, reproduce a defect, investigate crash or exception, diagnose flaky or intermittent test, performance regression, works on my machine, narrow down which change broke it, git bisect
---

# Skill: debugger

Purpose: locate and fix the root cause of a defect by evidence, not guesswork, and prevent its return. Applies when behavior is wrong and the cause is unknown. Grounded in the scientific method (hypothesis → experiment → conclusion) and Zeller's *Why Programs Fail* (systematic isolation). Composes with `coder` — the fix lands behind a failing-first test.

## Method (do not skip steps)

1. **Reproduce deterministically.** Pin down exact inputs, environment, and steps until the failure is reliable. Remove nondeterminism (mock time/randomness, fix seeds). If you cannot reproduce it, say so — do not "fix" by guess.
2. **Capture the evidence.** Record the actual vs expected behavior, full error/stack trace, and relevant logs. State the observed symptom precisely.
3. **Isolate.** Narrow the fault: bisect the input, the code path, or history (`git bisect` for "what change broke it"). Binary-search rather than scan. Add targeted logging or assertions at suspected boundaries.
4. **Hypothesize, then test one variable.** Form a single falsifiable hypothesis about the cause. Change one thing; predict the outcome; run; confirm or reject. Keep a short log of what was ruled out.
5. **Fix the cause, not the symptom.** Once the root cause is confirmed, fix it at the source. Do not paper over with a catch-all, a retry, or a magic sleep.
6. **Lock it with a regression test.** Write a test that **fails before** the fix and **passes after** — this proves both the diagnosis and the fix (TDD). Never delete or disable the failing test.
7. **Verify the fix did not regress neighbors.** Run the relevant suite; check the golden path and edge cases.

## Discipline

- **One hypothesis at a time** — changing several things at once destroys the signal.
- **Trust evidence over intuition** — the bug is often not where it "should" be; follow the data.
- **Keep changes minimal** while diagnosing; revert exploratory edits before shipping the fix.
- If the root cause is environmental or external (dependency, data, infra), report it with evidence rather than forcing a code change.
- **Language**: respond in the language of the current conversation.
