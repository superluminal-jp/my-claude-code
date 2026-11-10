---
name: specify-requirements
description: Turn an agreed problem into requirements that can be checked before implementation - a problem card that keeps evidence, hypotheses, and fixes apart, a requirements graph in which every requirement and every parent carries its own acceptance criterion, an independent read-only challenge for risky changes or weak evidence, and the bundled gate, which answers ready or blocked. Use before implementing a nontrivial, security-relevant, or multi-part change, and when asked to write acceptance criteria, to decompose requirements, or to check a requirements graph. Do not use to define a vague problem in the first place, to analyze root causes, to implement or review code, or to judge test evidence after implementation.
metadata:
  kind: worker
  permission: workspace_write
  sandbox: inside
  consumes: a problem statement the person has agreed to
  produces: a problem card, a requirements graph, an optional challenge report, and the gate's answer
---

# Specify requirements

A change may start only when its problem is backed by evidence, its requirements trace to that problem, and every objection raised against them has been answered. This skill writes the three records that make this checkable and runs the bundled checker's gate over them. The gate is deterministic and reads structure only. Finding errors of meaning, such as a solution stated as the problem or a parent that fails while all its children pass, is the challenger's job, and the challenger is a model whose errors can correlate with yours.

The bundled files write `$SKILL` for this skill's base directory, which is `${CLAUDE_SKILL_DIR}`.

## Steps

Keep the records together, for example in the project's specification or change directory. After each step run `python3 "${CLAUDE_SKILL_DIR}/scripts/check_graph.py" FILE`: exit 0 passes, 1 lists violations, 2 means the file cannot be read.

1. **Problem card** (`problem-card.json`). Start from a problem statement the person has agreed to. If there is none, stop: defining the problem is a separate capability.
   - Copy the ideal state, the current state, the gap, and why it matters.
   - Put every observation that supports the current state in `evidence` with its source (a test, a log, a scanner alert, a reproduction), and every observation against it in `counter_evidence`.
   - Keep causes in `hypotheses` and fixes in `proposed_solutions`. Never let either leak into `gap`.
   - Set `status` to `verified` only when the evidence shows the current state, `refuted` when counter-evidence shows the problem does not exist as stated, and `unverified` otherwise. Explain the status in `status_rationale` whenever there is counter-evidence.
2. **Requirements graph** (`requirements-graph.json`, `schema_version` 2, with the card's id as `problem_id`).
   - Make one root: the requirement that closes the gap.
   - Decompose with `AND` when every child is needed, and with `OR` only for real alternatives, giving each alternative its selection condition and scope.
   - Give every parent its own acceptance criterion at `L2` (integration across its children) or `L3` (the whole system), never only its children's `L1` checks. List in `counterexamples` how all children could pass while the parent fails.
   - Write each criterion in a checkable form; read `references/criteria-forms.md` when a sentence is vague or a quality target has no number.
   - Give a criterion that can only be verified after deploy `"stage": "post_deploy"`. Decide this here, where the challenger sees it, and never move a criterion that could be verified earlier. Every requirement, and every parent's own `L2` or `L3` level, also needs a criterion verifiable before deploy.
   - When a person directed a requirement rather than it following from the gap, record who and where in `origin`. Never put `origin` on a requirement you derived, and never name an agent in `by`.
   - Stop decomposing a node when it is one requirement with a clear acceptance criterion that can be verified on its own with a small change.
   - The graph is the only place for the acceptance criteria. A project that also keeps a specification, such as Spec Kit's `spec.md`, cites the graph's acceptance ids instead of restating them.
3. **Challenge** (`challenge-report.json`). Run it when the change touches authentication, authorization, secrets or personal data, data migration, infrastructure permissions, or anything hard to undo; when the evidence is thin or contested; or when the same agent wrote the card and the graph and will implement them. Read `references/challenge.md` and follow it. The challenger is a new `read-only-reviewer` subagent that gets a copy of the card without the proposed solutions, and the graph, so that it cannot inherit your fix. If no subagent of that name is available, stop and tell the person; do not start another type in its place.
4. **Gate.** Run `python3 "${CLAUDE_SKILL_DIR}/scripts/check_graph.py" --gate problem-card.json requirements-graph.json [challenge-report.json]`.
   - `ready`: hand the graph to implementation, which is a separate capability, and report the result with `challenge: recorded` or `challenge: not_run` as it is.
   - `blocked`: go back to the step the reason names. G-01 is the card, G-02 the graph, G-03 the report, G-04 the open findings.

Stop and ask the person instead of looping when the gate gives the same reason three times in a row, when a finding needs a decision that belongs to the person (accepting a risk, changing the scope), or when the evidence cannot be obtained with the access you have.

## What the gate does not show

- `ready` does not mean the decomposition is sufficient. The checker cannot read the meaning of a statement, and no finding is not the same as no error.
- A challenger running on the same model family is a second opinion, not independent evidence. For a high-risk change, a person with the authority to accept the risk still decides.

## Other declarations the checker reads

The same script checks a skill composition graph (`skills`), the `## Child skills` declarations of a skills directory (`--skills-dir DIR`), and a version 1 requirements graph without a problem. `permission` and `role` in a skill graph are declarations; enforcement belongs to the runtime's permission settings.

## Done when

- The card, the graph, and any challenge report pass the checker, and the gate has answered.
- Every finding of a challenge is recorded as the challenger gave it and is answered; none was deleted.
- The gate's answer is reported unchanged, including whether a challenge ran.

## Bundled files

| File | Read or run when |
|---|---|
| `references/checker.md` | Writing any of the records: the formats and every rule the checker applies |
| `references/criteria-forms.md` | Writing an acceptance criterion or a requirement sentence (step 2) |
| `references/challenge.md` | The challenge runs (step 3): the procedure, the prompt, and how findings are answered |
| `scripts/check_graph.py` | After each step and for the gate. Reads its inputs only; writes no file |
| `examples/` | One complete set of records whose gate is ready, to imitate |
