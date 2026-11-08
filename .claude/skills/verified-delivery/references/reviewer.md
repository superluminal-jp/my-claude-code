# Assurance reviewer prompt

The reviewer reads a bundle, not the repository. Before each round, commit the records and run, from inside the repository:

```sh
python3 <skill-dir>/scripts/review_prep.py check --records <record directory>
python3 <skill-dir>/scripts/review_prep.py bundle --records <record directory> --base <the commit the change started from> \
  --out <a new directory outside the repository> [--previous <the previous round's reviewed_commit> --previous-review <its record>]
```

`check` reports, as `P-01` to `P-03`, a `reviewed_commit` that is not a commit behind `HEAD`, a commit after it that changes a file that is not a record (records are the data files of the record directory, so this includes a file moved into it and a script kept there) or changes a record written before implementation (the problem card, the requirements graph, the challenge report), and a file the gate or the review reads — the manifest, the records written before implementation, the evidence the manifest cites — that is not a plain path inside the repository, missing, untracked, ignored, only staged, or different from its committed version. `bundle` reads the manifest and the evidence as committed at `HEAD`. Fix what it reports, and every gate reason except those that wait for this review, a person, or CI, before starting the reviewer. `bundle` writes into `--out`:

| File | What it holds |
|---|---|
| `change.diff` | the diff of the round's range without the record directory's data files; a script kept there to make evidence stays in it, as part of the change |
| `graph.diff` | the diff of `requirements-graph.json` over the same range |
| `requirements-graph.json` | the graph at `reviewed_commit` |
| `manifest.json` | the verification manifest — checks, risk class, approvals, test and infrastructure changes: the implementer's claims, to check against the diff and the evidence |
| `evidence/` | copies of the files of the repository that the manifest cites, at their paths |
| `excluded.txt` | the names of the record data files changed in the range, left out of `change.diff` |
| `previous-review.json` | the previous round's record, when `--previous-review` is given |
| `scope.json` | `whole` (the range starts at `--base`) or `fixes` (it starts at `--previous`), with the reasons for `whole` |

`--previous` makes the round `fixes` only when the requirements graph changed in its text fields alone (requirements' `statement`, `assumptions`, and `counterexamples`, criteria's `description`, and the conditions of a `selection`), the problem card did not change, and the committed manifest of the previous round has the same risk class. Anything else — a requirement or criterion added or removed, a changed decomposition, child, level, stage, or origin, a missing previous graph, card, or manifest — makes it `whole`. The record directory is the one directory that holds the change's records, `verification-manifest.json` among them. Its records are data files (`.json`, `.md`, `.txt`, `.xml`, `.csv`, `.yaml`, `.yml`, `.html`, `.log`); any other file kept there, such as a script that makes evidence, is part of the change and is reviewed with it. `review_prep.py` runs git with read-only subcommands only, opens no network connection (so it never opens a URL in the evidence), and writes only under `--out`, which must be outside the repository and new or empty. It needs Python 3.9 or later and git.

## First round, and any `whole` round

Give the text below, with the change id, the bundle directory, and the language of the records filled in, to a new subagent whose tools can only read and search. Give it the bundle only — not the conversation, the implementer's reasoning, or a summary written by the implementer.

```text
You are an independent, read-only reviewer of a change's evidence. Do not
edit files or run commands that change anything.

Change id: <change_id>
Read the files of this bundle: <bundle directory>
- change.diff: the change, without its record data files
- requirements-graph.json and graph.diff: the requirements and how they changed
- manifest.json: the implementer's claims (each criterion's check, the risk
  class, approvals, test and infrastructure changes), to check against the
  diff and the evidence, not to trust
- evidence/: the evidence files those claims cite
- excluded.txt: the names of the record files left out of change.diff
- scope.json: the commits the diff spans
Read anything else only when the bundle is not enough to judge a finding,
and say in that finding's statement what you read.

The records that name reviewed_commit (manifest, evidence, reviews, review
card) are committed after it, in commits that change only the record
directory, because a commit cannot contain its own SHA; that they name an
earlier commit than the branch head is expected. Report it only when
evidence names a commit other than reviewed_commit, or when excluded.txt
names a file that is not a record.

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
every disposition "open", and every statement written in <language of the
records, for example Japanese>:

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

Copy the findings, as they are, into the review record together with `change_id`, `reviewed_commit` (the commit the diff ends at), `reviewer` (who ran, and when), and `context_given` (exactly what the subagent was given, including the bundle's range and scope), as [manifest.md](manifest.md) describes. Then answer each finding there; the gate counts a finding as answered only when it is `accepted` or `rejected` with a `resolution`.

## Later rounds whose scope is `fixes`

When a fix made a new commit and the bundle's `scope.json` says `fixes`, give a new subagent the text below and the bundle (made with `--previous` and `--previous-review`). When it says `whole`, use the first-round prompt with that bundle instead.

```text
You are an independent, read-only reviewer of the fixes to a change. Do not
edit files or run commands that change anything.

Change id: <change_id>
Read the files of this bundle: <bundle directory>
- previous-review.json: the previous round's findings and their resolutions
- change.diff: the fixes since the previously reviewed commit, without the
  record data files
- graph.diff: how the requirements graph's text changed in the fixes
- requirements-graph.json, manifest.json (the implementer's claims, not
  facts), evidence/, excluded.txt, scope.json
Read anything else of the repository at the new commit only when the bundle
is not enough to judge a finding, and say in that finding's statement what
you read.

The records that name the reviewed commit are committed after it; report it
only when excluded.txt names a file that is not a record.

The resolutions in the previous record are the implementer's claims, not
facts. Check four things only:

1. For each finding marked accepted, whether the fixes really remove the
   problem it states. Report a finding that is not fixed as kind "other",
   naming the previous finding's id.
2. For each finding marked rejected, whether its resolution really shows
   that the problem does not hold. Report a rejection that does not hold as
   kind "other", naming the previous finding's id.
3. Whether a text change in graph.diff weakens what an acceptance criterion
   or requirement verifies. Report it as kind "other", naming the criterion
   or requirement.
4. Whether the fixes themselves have a material problem of the five kinds:
   parent_by_children, evidence_mismatch, uncovered_path, weakened_test, or
   risk_mismatch.

Answer with JSON only, in the same shape as the first round, one finding
per material problem, ids continuing after the previous round's, every
disposition "open", and every statement written in <language of the
records, for example Japanese>. Return an empty findings array if you find
nothing material. Do not suggest style changes.
```

The gate reads the latest round's record and does not tell a `fixes` round from a `whole` one; the range and scope written in `context_given` are what show it.
