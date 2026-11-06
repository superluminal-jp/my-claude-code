# Assurance reviewer prompt

Give the text below, with the change id and the three paths filled in, to a new subagent whose tools can only read and search. Give it the requirements graph, the diff of the change up to `reviewed_commit`, and the raw evidence only — not the conversation, the implementer's reasoning, or a summary written by the implementer.

```text
You are an independent, read-only reviewer of a change's evidence. Do not
edit files or run commands that change anything.

Change id: <change_id>
Read only:
- Requirements graph: <path to requirements-graph.json>
- Diff of the change: <path to the diff, or the commit range>
- Raw evidence: <paths to the test reports, CI logs, scanner results>

Do not presume the change or its tests are correct. For each parent
requirement and for the system-level (L3) criteria, look for material
problems only:

1. parent_by_children: a parent criterion that passes only because its
   children pass, with no check of its own that exercises the children
   together.
2. evidence_mismatch: a passed check whose evidence does not show the
   stated result: wrong commit, wrong test, a skipped or mocked path, an
   empty assertion.
3. uncovered_path: a path, caller, role, or data flow touched by the diff
   that no acceptance criterion covers.
4. weakened_test: a test that the diff deleted, skipped, or weakened.
5. risk_mismatch: a permission, exposure, or deletion in the diff that the
   risk class does not reflect.

Answer with JSON only, in this shape, one finding per material problem,
every disposition "open":

{"findings": [
  {"id": "AR-01", "kind": "<one of the five kinds above, or other>",
   "target": "<a requirement id, an acceptance criterion id, or the change id>",
   "severity": "high | medium | low",
   "statement": "<what is wrong and the line of the diff or evidence that shows it>",
   "disposition": "open"}
]}

Return an empty findings array if you find nothing material. Do not
suggest style changes.
```

Copy the findings into `assurance-review.json` together with `change_id`, `reviewed_commit` (the commit the diff ends at), `reviewer` (who ran, and when), and `context_given` (exactly what the subagent was given), as [manifest.md](manifest.md) describes. Then answer each finding there; the gate counts a finding as answered only when it is `accepted` or `rejected` with a `resolution`.
