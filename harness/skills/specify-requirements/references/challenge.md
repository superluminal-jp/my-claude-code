# Challenge

Read when the challenge runs. The challenger looks for errors of meaning that the checker cannot see, and it must not start from your conclusions.

## Each challenge

1. **Write a copy of the problem card without `proposed_solutions`**, for example `problem-card.challenger.json`.
2. **Start a new `read-only-reviewer` subagent** with the prompt below, the paths of that copy and of the requirements graph, and the language the records are written in.
3. **Decide whether it reviewed**, by the rule under the prompt. A challenger that did not review writes no report.
4. **Copy its findings into `challenge-report.json` as they are, as `open`,** then answer each one:
   - `accepted`: fix the card or the graph, and write what changed.
   - `rejected`: only for one of two reasons. Either the line of the problem card or the graph that shows the finding does not hold, cited by field; or a decision you asked the person for, written with who answered, when, and their words, and added to the card's `evidence`.
   - Never write as the person's decision what the person has not answered.
   - When the reason rests on something neither file shows (a conversation, a convention, a system you can read and the challenger cannot), add it to the card's `evidence` with its source and cite that; or ask the person.
   - Never delete a finding.

You wrote what is under review, so wanting to reject a finding is not evidence that it is wrong.

## Prompt

Give the text below, unchanged except for the two paths and the language the records are written in, to a new `read-only-reviewer` subagent, whose definition allows only Read, Grep, and Glob, so it cannot edit files, run commands, or reach the network, and starts it without CLAUDE.md (with the plugin's prefix when these skills came as a plugin; when no subagent of that name is available, stop instead of starting another type). Give it a copy of the problem card without `proposed_solutions`, and the requirements graph, only. Do not give it the proposed solutions, the planned implementation, the conversation, or your own assessment: the point is that it does not start from your conclusions.

```text
You are a skeptical, read-only reviewer of a problem definition and its
decomposition. Do not edit files or run commands that change anything.

Read only these two files:
- Problem card: <path to the copy without proposed_solutions>
- Requirements graph: <path to requirements-graph.json>

Do not presume the problem, its cause, or the decomposition is correct.

A requirement with an "origin" of kind "instruction" was directed by the
person named in "by", at the place named in "ref". Treat it as a given
constraint: do not report it as a solution stated as a problem or as a
requirement the gap does not call for. Report it (kind "other") only when
it contradicts the gap or another requirement, when "ref" does not identify
where a person gave that direction, or when "by" does not name a person.

An acceptance criterion with "stage": "post_deploy" is left out of the
decision on whether the change may be deployed. Report it (kind "other")
when it could be verified before the change is deployed.

Look for material errors only:

1. false_positive: is the current state really supported by the evidence,
   or could the problem not exist as stated?
2. alternative_cause: is a hypothesis presented as fact, or is another
   cause equally consistent with the evidence?
3. solution_as_problem: does the gap describe a means (update, migrate,
   add a check) instead of a difference between the current and ideal state?
4. mixed_statement: are observations, hypotheses, and proposed solutions
   mixed together in one field?
5. counterexample: is there a situation in which every child requirement
   holds but the parent does not (another path, another caller, cached
   data, a different user role)?
6. missing_child: is a requirement needed for the parent not listed?
7. or_overlap: for an OR, can several alternatives hold at once, or none?
8. missing_evidence: which claim needs evidence that is not recorded?

Answer with JSON only, in this shape: in "read", the path of every file you
read; in "findings", one finding per material problem, every disposition
"open", and every statement written in <language of the records, for example
Japanese>:

{"read": ["<path>", "<path>"],
 "findings": [
  {"id": "CH-01", "kind": "<one of the eight kinds above, or other>",
   "target": "<the problem card id or a requirement id>",
   "severity": "high | medium | low",
   "statement": "<what is wrong and the concrete case that shows it>",
   "disposition": "open"}
]}

Return an empty findings array if you find nothing material. If one of the
two files cannot be read, answer only "NOT REVIEWED: <path>: <reason>".
Do not suggest style changes.
```

The challenger did not review when it ended with an error, was stopped or timed out, answered `NOT REVIEWED`, returned anything but that JSON, or left either file out of `read`. Start a new one once more with the same input; if that also fails, write no report and tell the person the challenge did not run. Otherwise copy the findings, as they are, into `challenge-report.json` together with `problem_id`, `reviewer` (the subagent type, the agentId the Agent tool returned, the date, and how many files it read), and `context_given` (exactly what the subagent was given), as [checker.md](checker.md) describes.
