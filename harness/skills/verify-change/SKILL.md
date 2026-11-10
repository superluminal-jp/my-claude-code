---
name: verify-change
description: Record, for every acceptance criterion of a change, which check ran on which commit with what result, have the evidence read by an independent read-only reviewer when the risk calls for it, and run the bundled gate, which answers pass, fail, or blocked and never builds a parent's pass out of its children's. Use when a change with a requirements graph must be accepted by its evidence rather than by rereading every diff, and when asked to check a verification manifest or to turn JUnit or Jest results into one. Do not use for a trivial local edit, for a code review that decides nothing, or for operating CI itself.
metadata:
  kind: worker
  permission: workspace_write
  sandbox: inside
  consumes: a problem card, a version 2 requirements graph, and the committed change
  produces: a verification manifest, the gate's decision, and a review card
---

# Verify a change by its evidence

A change can be accepted without rereading it when every acceptance criterion - of each leaf, of each parent, and of the system - has its own evidence from the commit under review, and nothing about risk, approval, or weakened tests is left open. The bundled checker decides that from the records. It cannot tell whether an evidence reference really shows what it claims, which is why a statement by an AI never counts as evidence.

The bundled files write `$SKILL` for this skill's base directory, which is `${CLAUDE_SKILL_DIR}`.

## Steps

1. **Commit, then classify the risk.** Commit the change first; that commit is `reviewed_commit`. Classify the risk in this order and stop at the first that applies:
   - `high`: authentication, authorization, secrets or personal data, data migration, payments, infrastructure permissions, network or public exposure, or anything hard to undo.
   - `medium`: an API, a data flow, or several modules.
   - `low`: a local change that touches no permission and no external contract.
   - otherwise `unclassified`, which the gate blocks.
2. **Write the manifest** (`verification-manifest.json`). Read `references/manifest.md`: its first section says which record goes into which commit and how evidence is saved, and the rest gives the format and every rule.
   - Write one check per acceptance criterion. Mark one `not_applicable` only with a reason.
   - Turn test reports into checks with `python3 "${CLAUDE_SKILL_DIR}/scripts/assure.py" collect-junit REPORT --graph GRAPH --commit SHA --ref REF`, or `collect-jest` with the same arguments for the output of `jest --json`.
   - Record an AI review as `ai_review`; it never passes a check.
   - List every deleted, skipped, or weakened test, and every permission expansion, public exposure, deletion, or replacement in an infrastructure diff.
3. **Assurance review, for `medium` and `high` risk.** Read `references/assurance-review.md` and follow it for every round. The reviewer is a new `read-only-reviewer` subagent that is given the review bundle and nothing else: not the conversation and not your summary. If no subagent of that name is available, stop and tell the person; do not start another type in its place. Copy its findings as they are and answer each one. You made the change, so wanting to reject a finding is not evidence that it is wrong. Never delete a finding.
4. **Gate.** Run these commands, passing each record to the gate whenever there is one. The first confirms that the commits after `reviewed_commit` change only the record directory and that the evidence the manifest cites is committed. The gate checks the graph's structure and both records again itself, so a step that was skipped blocks the change instead of passing it.

   ```sh
   python3 "${CLAUDE_SKILL_DIR}/scripts/review_prep.py" check --records <record directory>
   python3 "${CLAUDE_SKILL_DIR}/scripts/assure.py" check verification-manifest.json
   python3 "${CLAUDE_SKILL_DIR}/scripts/assure.py" gate requirements-graph.json verification-manifest.json \
     --report challenge-report.json --review assurance-review.json
   ```

   - `pass`: present the decision with its counts per level.
   - `fail`: a check failed or an approval was rejected. The implementation, or the requirement itself, has to change; say which.
   - `blocked`: obtain the missing evidence, classify the risk, answer the open findings, or ask for the approval the reason names. A `high` change without a challenge report is blocked: its requirements have to be challenged first, which is a separate capability. A `medium` or `high` change without an assurance review of `reviewed_commit` is blocked: go back to step 3.
   - For a graph with criteria that can only be verified after deploy, decide before deploying with `--stage pre_deploy`; its `pass` means the change may be deployed, not that it is accepted. After deploy, record those checks and run the gate without `--stage`.
   - Never change a status, a commit, a risk class, a criterion's stage, or a finding's disposition only to get past the gate.
5. **Review card.** Run the command below and give the person the card it prints as the first thing they read. Never write your own summary of the result in its place.

   ```sh
   python3 "${CLAUDE_SKILL_DIR}/scripts/assure.py" card --problem problem-card.json --graph requirements-graph.json \
     --manifest verification-manifest.json [--report challenge-report.json] [--review assurance-review.json] [--lang ja]
   ```

Stop and ask the person when the same reason blocks or fails the gate three times in a row; before the sixth assurance review round of a change and every fifth round after it; when fixing a finding would undo the fix for an earlier finding; when the next step needs authority you do not have (a commit, push, or pull request the person has not asked for, a deployment, production access, a credential, accepting a risk); or when evidence can only come from a system you may not touch.

## Inside the Bash sandbox

- The review bundle is written to a new directory under `$TMPDIR`. It must be outside the repository so that it is never committed, and `$TMPDIR` is the place outside the repository where a sandboxed command can write.
- Pushing a commit and reading a CI result need the network. When the sandbox blocks the host, report the host and what could not be collected, and record the check as `blocked`; do not work around the sandbox.

## What a pass does not show

- That the change is secure or complete beyond its acceptance criteria. The gate checks the records against the requirements graph, and the graph can miss a requirement.
- That an approval is genuine. The records hold names, and the checker does not verify identities.
- That the checks are strong. A weak test that passes is still a passed check; the assurance review and the person's own reading are what catch that.

## Done when

- Every acceptance criterion has exactly one check, and every passed check cites evidence for `reviewed_commit` that is committed in the record directory.
- For `medium` and `high` risk, the latest assurance review is of `reviewed_commit` and every finding is answered.
- The gate was run on the committed records and its decision is reported unchanged, with the review card.

## Bundled files

| File | Read or run when |
|---|---|
| `references/manifest.md` | Writing the records and the manifest (step 2); reading a gate reason (step 4); the card and the JUnit and Jest collectors |
| `references/assurance-review.md` | Every round of the assurance review (step 3) |
| `references/pilot.md` | Deciding whether this procedure saves review time compared with the current review |
| `scripts/assure.py` | Steps 2, 4, and 5. Reads its inputs only; writes no file |
| `scripts/review_prep.py` | Before each review round: checks the commits and writes the review bundle |
| `scripts/pilot.py` | The decision of the pilot that `references/pilot.md` describes |
| `examples/` | One complete set of records whose gate passes, to imitate |
