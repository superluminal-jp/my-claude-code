---
name: change-assurance
description: "Carry a change from an agreed problem to an evidence-backed acceptance decision: define and decompose the problem, implement it, record for every acceptance criterion which check ran on which commit with what result, and run the bundled checker's gate, which answers pass, fail, or blocked and never builds a parent's pass out of its children's. Use for a nontrivial, security-relevant, or multi-part change to a work or production system when the person wants to accept it by its evidence rather than by rereading every diff, and when asked to check a verification manifest or to turn JUnit results into one. Do not use for a trivial local edit, for a code review that decides nothing, or for operating CI itself. A pass shows only that the records are consistent; high-risk changes still need a person's approval, and the gate does not prove the change secure."
---

# Change assurance

A person can accept a change without rereading all of it when every acceptance criterion — of each leaf, of each parent, and of the system — has its own evidence from the commit under review, and nothing about risk, approval, or weakened tests is left open. This skill applies its children in order, records that evidence in a verification manifest, and lets the bundled checker decide. The checker cannot tell whether an evidence reference really shows what it claims; that rests on the system that produced it, which is why AI statements never count as evidence.

## Child skills

- `problem-definition`
- `goal-refinement`
- `coder`

## Steps

1. **Problem.** If there is no problem statement the person has agreed to, apply `problem-definition` first.
2. **Decomposition.** Apply `goal-refinement` to write the problem card and the version 2 requirements graph and to run its gate. Go on only when that gate says `ready`.
3. **Implementation.** Apply `coder`, one leaf requirement at a time: observe the failing check before the fix, keep each change small, and do not delete, skip, or weaken a test to make it pass.
4. **Verification manifest** (`verification-manifest.json`; format in [references/manifest.md](references/manifest.md)). Set `reviewed_commit` to the commit under review and `implementer` to whoever made the change. Classify the risk in this order and stop at the first that applies: `high` for authentication, authorization, secrets or personal data, data migration, payments, infrastructure permissions, network or public exposure, or anything hard to undo; `medium` for an API, a data flow, or several modules; `low` for a local change that touches no permission and no external contract; otherwise `unclassified`. Write one check per acceptance criterion. Turn test reports into checks with `python3 <skill-dir>/scripts/assure.py collect-junit REPORT --graph GRAPH --commit SHA --ref REF`, where `<skill-dir>` is this skill's base directory (Claude Code shows it when the skill loads). Record a CI job by its URL and the commit it ran on, a scanner by its run or alert, and a person's check as `human_review`; an AI review goes in as `ai_review` and never passes a check. List every deleted, skipped, or weakened test in `test_changes` and every permission expansion, public exposure, deletion, or replacement from an infrastructure diff in `infra_changes`.
5. **Gate.** Run `python3 <skill-dir>/scripts/assure.py check verification-manifest.json`, then `python3 <skill-dir>/scripts/assure.py gate requirements-graph.json verification-manifest.json`. On `pass`, present the decision with its counts per level. On `fail`, go back to step 3 for the failing check, or to step 2 if the requirement itself is wrong. On `blocked`, obtain the missing evidence, classify the risk, or ask for the approval the reason names. Never change a status, a commit, or a risk class only to get past the gate.
6. **Assurance review** (for `medium` and `high` risk). Start a new subagent that can only read and search, with the prompt in [references/reviewer.md](references/reviewer.md), and give it the requirements graph, the diff, and the raw evidence (logs, reports) — not the conversation or your own summary. Answer each objection by fixing the change or the manifest, or by stating why it does not hold, before presenting the change. Its agreement is an opinion, not evidence.
7. **Review card.** Run `python3 <skill-dir>/scripts/assure.py card --problem problem-card.json --graph requirements-graph.json --manifest verification-manifest.json [--report challenge-report.json] [--lang ja]` and give the person the card it prints — in the pull request description, for example — as the first thing they read. The card shows the gate's decision as it is; never write your own summary of the result in its place.

Stop and ask the person when the same reason blocks or fails the gate three times in a row, when the next step needs authority you do not have (a deployment, production access, a credential, accepting a risk), or when evidence can only be obtained from a system you may not touch.

## Measuring whether this saves time

To decide whether to keep using this skill, compare it with the current review on comparable past requests, following [references/pilot.md](references/pilot.md): preregister the target and the quality gates before the first case, record each person's working minutes and each gate per case, and run `python3 <skill-dir>/scripts/pilot.py preregistration.json cases.json`. Adopt only on `adopt`; a shorter time with a broken quality gate is `not_adopted`.

## What a pass does not show

- That the change is secure or complete beyond its acceptance criteria: the gate checks the records against the requirements graph, and the graph can miss a requirement.
- That an approval is genuine: `approvals` records names, and the checker does not verify identities.
- That the checks are strong: a weak test that passes is still a passed check. The assurance review and the person's own reading are what catch that.
