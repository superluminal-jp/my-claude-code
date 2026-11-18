# Assurance review

Read for every round of the assurance review of a `medium` or `high` risk change. `$SKILL` is this skill's base directory.

## Each round

1. **Check before the reviewer does.** Commit the records. Run `review_prep.py check` and the gate, and fix every reason except those that wait for this review, a person, or CI, so that the reviewer is not the one to find a record error a program can find.
2. **Write the bundle** (next section). From the second round on, add `--previous` and `--previous-review`.
3. **Choose the prompt by the bundle's `scope.json`.** `whole` reads the whole change with the first-round prompt. `fixes` reads the fix diff with the later-round prompt.
4. **Start a new `read-only-reviewer` subagent** with that prompt, the bundle directory, and the language the records are written in. Use the plugin's prefix, such as `<plugin>:read-only-reviewer`, when these skills came as a plugin. Its definition allows only Read, Grep, and Glob and starts it without CLAUDE.md, so it cannot run git or the scripts: what it needs must be in the bundle or in the repository's files. A CLAUDE.md in a directory whose files it reads still loads, as do the MCP servers' instructions. If no subagent of that name is available, stop and tell the person; do not start another type in its place.
5. **Decide whether it reviewed**, by the rule under the first-round prompt below. A reviewer that did not review writes no record.
6. **Copy its findings into the review record as they are, as `open`,** then answer each one:
   - `accepted`: fix the change or the manifest, and write what changed.
   - `rejected`: only for one of two reasons. Either the file and line that shows the finding does not hold, in a file the next reviewer can read (the bundle, or a committed file of the repository); or a decision you asked the person for, written with who answered, when, and their words.
   - Never write as the person's decision what the person has not answered.
   - When the reason rests on something no such file shows (a conversation, a convention, a system the reviewer cannot read), write it into a file of the record directory, commit it, and cite that; or ask the person.
   - Never delete a finding.
7. **A fix to the change makes a new commit.** Collect its evidence and start the next round. Keep each round's record, for example `assurance-review-2.<sha>.json`, and give the gate the latest.
8. **Stop and ask the person** before starting the sixth round of the same change, and again before every fifth round after that: whether to run another round, to decide the open findings themselves, or to go back to the requirements. Count a round by the review record it wrote, so a reviewer that did not review is not counted. Ask the same when a finding churns, that is, when fixing it would undo what the fix for an earlier finding of this change changed. Name that earlier finding in the resolution, and when unsure whether a finding churns, ask.

The reviewer's agreement is an opinion, not evidence.

## The bundle

The reviewer reads a bundle, not the repository. Before each round, commit the records and run, from inside the repository:

```sh
python3 "$SKILL/scripts/review_prep.py" check --records <record directory>
python3 "$SKILL/scripts/review_prep.py" bundle --records <record directory> --base <the commit the change started from> \
  --out "$TMPDIR/<a new directory name>" [--previous <the previous round's reviewed_commit> --previous-review <its record>]
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

`--previous` makes the round `fixes` only when the requirements graph changed in its text fields alone (requirements' `statement`, `assumptions`, and `counterexamples`, criteria's `description`, and the conditions of a `selection`), the problem card did not change, and the committed manifest of the previous round has the same risk class. Anything else — a requirement or criterion added or removed, a changed decomposition, child, level, stage, or origin, a missing previous graph, card, or manifest — makes it `whole`. The record directory is the one directory that holds the change's records, `verification-manifest.json` among them. Its records are data files (`.json`, `.md`, `.txt`, `.xml`, `.csv`, `.yaml`, `.yml`, `.html`, `.log`); any other file kept there, such as a script that makes evidence, is part of the change and is reviewed with it. `review_prep.py` runs git with read-only subcommands only, opens no network connection (so it never opens a URL in the evidence), and writes only under `--out`, which must be outside the repository and new or empty (inside the Bash sandbox, a new directory under `$TMPDIR`). It needs Python 3.9 or later and git.

The reviewer is a `read-only-reviewer` subagent ([SKILL.md](../SKILL.md), step 3): its tools are Read, Grep, and Glob, so it cannot run git, these scripts, or the change's tests, and it relies on the bundle and the repository's files. Keep the working tree clean (`git status --short` prints nothing) while it reads: `check` has confirmed that the commits after `reviewed_commit` change only the record directory, so the repository's files outside it are then those of `reviewed_commit`. A version or a command output that neither shows is something the reviewer reports as missing, not something it fetches.

## First round, and any `whole` round

Give the text below, with the change id, the bundle directory, and the language of the records filled in, to a new `read-only-reviewer` subagent. Give it the bundle only — not the conversation, the implementer's reasoning, or a summary written by the implementer.

```text
You are an independent, read-only reviewer of a change's evidence. Do not
edit files or run commands that change anything.

Change id: <change_id>
Read each of these files of the bundle <bundle directory> in full, even
when another file repeats part of it; read the files under evidence/ as
you need them:
- change.diff: the change, without its record data files
- requirements-graph.json and graph.diff: the requirements and how they changed
- manifest.json: the implementer's claims (each criterion's check, the risk
  class, approvals, test and infrastructure changes), to check against the
  diff and the evidence, not to trust
- evidence/: the evidence files those claims cite
- excluded.txt: the names of the record files left out of change.diff
- scope.json: the commits the diff spans
Read anything else only when the bundle is not enough to judge a finding,
and say in that finding's statement what you read. You cannot run commands.
The repository's files outside the record directory are as of
reviewed_commit. When judging a finding needs another version of a file or
the output of a command that neither the bundle nor those files show, report
it as a finding (evidence_mismatch, or other) that names what is missing.

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

Answer with JSON only, in this shape: in "read", the path of every file you
read; in "findings", one finding per material problem, every disposition
"open", and every statement written in <language of the records, for
example Japanese>:

{"read": ["<path>", "<path>"],
 "findings": [
  {"id": "AR-01", "kind": "<one of the five kinds above, or other>",
   "target": "<a requirement id, an acceptance criterion id, or the change id>",
   "severity": "high | medium | low",
   "statement": "<what is wrong and the line of the diff or evidence that shows it>",
   "disposition": "open"}
]}

Return an empty findings array if you find nothing material. If a file
named above cannot be read, answer only "NOT REVIEWED: <path>: <reason>".
Do not suggest style changes.
```

The reviewer did not review when it ended with an error, was stopped or timed out, answered `NOT REVIEWED`, returned anything but that JSON, or left out of `read` a file the prompt names (the files under `evidence/` it reads as needed). Start a new one once more with the same bundle; if that also fails, write no review record and tell the person the review did not run. Otherwise copy the findings, as they are, into the review record together with `change_id`, `reviewed_commit` (the commit the diff ends at), `reviewer` (the subagent type, the agentId the Agent tool returned, the date, and how many files it read), and `context_given` (exactly what the subagent was given, including the bundle's range and scope), as [manifest.md](manifest.md) describes. Then answer each finding there; the gate counts a finding as answered only when it is `accepted` or `rejected` with a `resolution`. A rejection's resolution cites the file and line that shows the finding does not hold, in a file the next reviewer can read, or a decision the person gave when asked, with who, when, and their words ([SKILL.md](../SKILL.md), step 3).

## Later rounds whose scope is `fixes`

When a fix made a new commit and the bundle's `scope.json` says `fixes`, give a new `read-only-reviewer` subagent the text below and the bundle (made with `--previous` and `--previous-review`). When it says `whole`, use the first-round prompt with that bundle instead.

```text
You are an independent, read-only reviewer of the fixes to a change. Do not
edit files or run commands that change anything.

Change id: <change_id>
Read each of these files of the bundle <bundle directory> in full, even
when another file repeats part of it; read the files under evidence/ as
you need them:
- previous-review.json: the previous round's findings and their resolutions
- change.diff: the fixes since the previously reviewed commit, without the
  record data files
- graph.diff: how the requirements graph's text changed in the fixes
- requirements-graph.json, manifest.json (the implementer's claims, not
  facts), evidence/, excluded.txt, scope.json
Read anything else of the repository at the new commit only when the bundle
is not enough to judge a finding, and say in that finding's statement what
you read. You cannot run commands. The repository's files outside the record
directory are as of the new reviewed commit. When judging a finding needs
another version of a file or the output of a command that neither the bundle
nor those files show, report it as a finding (evidence_mismatch, or other)
that names what is missing.

The records that name the reviewed commit are committed after it; report it
only when excluded.txt names a file that is not a record.

The resolutions in the previous record are the implementer's claims, not
facts. Check four things only:

1. For each finding marked accepted, whether the fixes really remove the
   problem it states. Report a finding that is not fixed as kind "other",
   naming the previous finding's id.
2. For each finding marked rejected, whether its resolution really shows
   that the problem does not hold. A resolution can show it in two ways
   only: by citing a file and line you can read that shows it, or by giving
   a decision of a named person with when they answered and their words.
   Report a rejection that does not hold, one whose cited file does not
   show what it claims, and one that cites neither, as kind "other",
   naming the previous finding's id.
3. Whether a text change in graph.diff weakens what an acceptance criterion
   or requirement verifies. Report it as kind "other", naming the criterion
   or requirement.
4. Whether the fixes themselves have a material problem of the five kinds:
   parent_by_children, evidence_mismatch, uncovered_path, weakened_test, or
   risk_mismatch.

Answer with JSON only, in the same shape as the first round: in "read", the
path of every file you read; in "findings", one finding per material
problem, ids continuing after the previous round's, every disposition
"open", and every statement written in <language of the records, for
example Japanese>. Return an empty findings array if you find nothing
material. If a file named above cannot be read, answer only
"NOT REVIEWED: <path>: <reason>". Do not suggest style changes.
```

The gate reads the latest round's record and does not tell a `fixes` round from a `whole` one; the range and scope written in `context_given` are what show it.
