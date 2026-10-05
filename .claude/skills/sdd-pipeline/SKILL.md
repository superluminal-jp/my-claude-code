---
name: sdd-pipeline
description: Run a whole Spec Kit feature end to end from one request through the project's Spec Kit workflow engine — specification, plan, tasks, analysis, implementation, convergence, review with fixes, commits, push, pull request, and a CI check — with authoritative sources cited at every step. Use when the user wants a feature carried from description to an opened pull request in one hands-off run in a project already initialized with Spec Kit. Do not use to run a single Spec Kit phase, in a project without Spec Kit initialized, to resume or inspect only an existing run, or to publish work the user has not authorized for this run.
---

# SDD Pipeline

Carry one feature from description to an opened pull request by launching the bundled Spec Kit workflow overlay, then supervise the run and report its outcome. The step order, the loop limits, and the citation rule live in the overlay (`references/full-pipeline.yml`), which is the single definition; this skill installs it, starts it, and reports on it.

## Check the preconditions

Stop and report the first one that fails; do not repair a missing one silently.

1. `specify version` succeeds and the project has a `.specify/` directory. Spec Kit is initialized per project; do not initialize it here.
2. The working tree has no uncommitted changes that are not part of this request, and the current branch is not a protected trunk branch unless the workflow's own branch step is expected to leave it.
3. A Git remote exists and `gh auth status` succeeds, because the run pushes and opens a pull request.

## Authority

Invoking this skill authorizes one run to commit, push the feature branch, and open a pull request. It does not authorize a force push, history rewriting, branch deletion, merging, or any change outside the feature branch.

## Install the overlay

1. Ensure the `speckit` workflow is installed and current: `specify workflow list`; if absent, `specify workflow add speckit`.
2. Compare the bundled overlay with the project's installed copy (`specify workflow overlay list speckit`, then a file comparison against `.specify/workflows/overlays/speckit/full-pipeline.yml`). If it is missing or differs, remove any old copy with `specify workflow overlay remove speckit full-pipeline` and add the bundled file with `specify workflow overlay add <path to references/full-pipeline.yml>`. Resolve the path against this skill's base directory.
3. Confirm with `specify workflow resolve speckit` that every step is attributed and no anchor error is reported. If the base workflow changed its step ids, the overlay fails validation: stop and report the error instead of editing the base workflow.

## Run

1. Take the feature description from the request. Pass it only as the value of `-i spec=...` and quote it for the shell; never place it inside a shell step.
2. Start the run in the background, because it is long:
   `specify workflow run speckit -i spec='<description>' -i integration=<the agent this session runs in>`
3. Follow its output. When it pauses or fails, read `specify workflow status <run_id>` and the step's error, report the run id and the failing step, and offer `specify workflow resume <run_id>`. Do not re-run from the start to work around a failure, and do not raise a loop limit.
4. Treat as stop conditions: a failed verification, an unresolved ambiguity the run cannot settle, a rejected push, an authentication or permission error, and a loop limit reached.

## Verify the outcome

A `completed` run status is not proof that work happened. Before reporting success, confirm from the repository itself: a feature branch other than the starting branch exists, it carries new commits, the branch exists on the remote, and `gh pr view` returns an open pull request. If any check fails, report the run as unsuccessful and say which evidence is missing; do not start a new run to compensate.

## Report

Lead with the outcome, then the evidence:

- the pull request URL, or the step where the run stopped and its run id;
- the CI result, whether a fix was attempted, and whether CI still fails;
- what the converge step appended and whether any gap remains after the single permitted pass;
- the cited sources the run recorded, and any claim it marked unverified;
- anything not performed or not verified.

## Limits

- The converge decision cannot be read from a prompt step's response, so the follow-up implementation always runs once and is not conditional.
- Using an agent other than the one this skill was written for is untested, including the review step's equivalent there.
- Shell steps run with the user's privileges and no sandbox; review the overlay before changing it.
