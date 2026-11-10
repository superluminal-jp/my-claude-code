---
name: deliver-change
description: Carry a change from an agreed problem to an acceptance decision that a person can make from its evidence, by applying four skills in a fixed order - problem, requirements, implementation, verification. Use for a nontrivial, security-relevant, or multi-part change to a work or production system when the person wants to accept it without rereading every diff. Do not use for a trivial local edit, for a review that decides nothing, or when only one of the four steps is asked for.
metadata:
  kind: orchestrator
  permission: workspace_write
  sandbox: inside
  produces: a change with the gate's decision (pass, fail, or blocked) and its review card
---

# Deliver a change by its evidence

A person can accept a change without rereading all of it when the problem was agreed, every requirement has its own acceptance criterion, and every criterion has evidence from the commit under review. This skill only fixes the order of the four skills that produce those; each child decides how its own step is done.

## Child skills

- `define-problem`
- `specify-requirements`
- `implement-change`
- `verify-change`

## Steps

1. **Problem.** If there is no problem statement the person has agreed to, apply `define-problem` first.
2. **Requirements.** Apply `specify-requirements` to write the problem card and the requirements graph and to run its gate. Go on only when that gate says `ready`.
3. **Implementation.** Apply `implement-change`, one leaf requirement at a time: watch the check fail before the fix, keep each change small, and never delete, skip, or weaken a test to make it pass.
4. **Verification.** Apply `verify-change` to record the evidence, run the independent review the risk class calls for, and run the gate.
   - On `pass`, go to step 5.
   - On `fail`, return to step 3 for the failing check, or to step 2 when the requirement itself is wrong.
   - On `blocked`, obtain what the reason names: missing evidence, a risk class, an answer to an open finding, a fix to the graph (step 2), or a person's approval.
5. **Hand over.** Give the person the review card as the first thing they read, for example at the top of the pull request description. Show the gate's decision as it is; never put your own summary in its place.

Stop and ask the person when the same reason blocks or fails a gate three times in a row, when the next step needs authority you do not have (a commit, push, or pull request not asked for, a deployment, production access, a credential, accepting a risk), or when evidence can only come from a system you may not touch.

## Done when

- The gate of step 4 has answered, and its decision and review card were given to the person unchanged.
- Every return to an earlier step was caused by a gate reason, and no status, commit, risk class, or finding was changed only to get past a gate.
- A high-risk change was not presented as accepted without the approval of a person other than the implementer.
