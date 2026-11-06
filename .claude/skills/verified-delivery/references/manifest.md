# The verification manifest and the bundled checker

`scripts/assure.py` reads a verification manifest, a version 2 requirements graph, the challenge report and the assurance review, and JUnit XML reports. It reads its inputs and nothing else: it writes no file, opens no network connection, starts no process, and never executes input content. It needs Python 3.9 or later and its standard library only.

```sh
python3 <skill-dir>/scripts/assure.py [--format text|json] check MANIFEST
python3 <skill-dir>/scripts/assure.py [--format text|json] gate GRAPH MANIFEST [--report REPORT] [--review REVIEW]
python3 <skill-dir>/scripts/assure.py collect-junit REPORT --graph GRAPH --commit SHA --ref REF [--kind ci_job|local_run]
python3 <skill-dir>/scripts/assure.py [--format text|json] card --problem CARD --graph GRAPH --manifest MANIFEST [--report REPORT] [--review REVIEW] [--lang en|ja]
```

Exit codes (the same for `card`, after its own rules): 0 for `pass` or no violation, 1 for `fail`, `blocked`, or violations, 2 when an input cannot be interpreted (unreadable, not a regular file, over 5 MiB, not UTF-8, invalid JSON or XML, a repeated key, a number too long to read, an XML `DOCTYPE` or `ENTITY`, a wrong top level, a challenge report for another problem, an assurance review for another change, bad arguments) or the checker itself failed.

## The manifest

```json
{"schema_version": 1, "verification_manifest": {
  "change_id": "CHG-001", "problem_id": "PRB-001",
  "reviewed_commit": "0f5a148c2d7a9e1b3f6a8c0d2e4f6a8b0c2d4e6f", "implementer": "claude",
  "risk": {"class": "high", "rationale": "changes authorization"},
  "approvals": [{"by": "owner-a", "decision": "approved", "scope": "authorization change and residual risk"}],
  "checks": [{"check_id": "TEST-LEAF-001", "status": "passed",
              "evidence": {"kind": "ci_job", "ref": "<CI job URL>", "commit": "0f5a148c2d7a9e1b3f6a8c0d2e4f6a8b0c2d4e6f"}}],
  "test_changes": [{"path": "tests/test_orders.py::test_legacy", "change": "deleted", "approved_by": "owner-a"}],
  "infra_changes": [{"kind": "permission_expansion", "ref": "<line of the infrastructure diff>"}]}}
```

- `reviewed_commit` and every evidence `commit`: 7 to 40 lowercase hex digits and nothing else.
- `risk.class`: `low`, `medium`, `high`, or `unclassified`. `approvals[].decision`: `approved` or `rejected`.
- `checks[].status`: `passed`, `failed`, `not_run`, `blocked` (the evidence could not be collected), or `not_applicable` (needs a `reason`; an `L2` or `L3` check also needs `approved_by`, someone other than the implementer who agreed that it does not apply). `evidence.kind`: `ci_job`, `local_run`, `scanner`, `human_review`, or `ai_review`.
- `test_changes[].change`: `deleted`, `skipped`, or `weakened`. `infra_changes[].kind`: `permission_expansion`, `public_exposure`, `resource_deletion`, or `resource_replacement`.

| Rule | Passes when |
|---|---|
| M-00 | required fields are present, values have the right types and defined values, and no field is undefined |
| M-01 | every `check_id` is non-empty and unique |
| M-02 | a `passed` check has evidence; a `not_applicable` check has a reason |

## The gate

`gate GRAPH MANIFEST [--report REPORT] [--review REVIEW]` answers `pass` only when every rule holds. A failed check or a rejected approval makes it `fail`; anything else that does not hold makes it `blocked`. Both are not a pass. The result lists each reason with its rule and effect, and counts the statuses per level (`L1`, `L2`, `L3`), counting a passed check whose evidence was refused, and an `L2` or `L3` check marked `not_applicable` without the approval A-06 needs, as `blocked`. Manifest violations (M-xx) also block. With `--format json` the result also has `checks`: for every acceptance criterion, its `check_id`, `level`, `requirement`, the status the gate used, and the recorded `evidence` object (or `null`).

| Rule | Holds when |
|---|---|
| A-01 | the graph has at least one acceptance criterion, each has exactly one check, no check names an id outside the graph, and the manifest is for the graph's problem |
| A-02 | the evidence of a passed check is not `ai_review` only, has a reference, and is for `reviewed_commit` (the same string: a short SHA and the full SHA of one commit do not match, so write both in full) |
| A-03 | every check is `passed` or `not_applicable` with a reason, and no requirement has only `not_applicable` checks |
| A-04 | the risk is `low`, `medium`, or `high` |
| A-05 | no approval is `rejected` (at any risk), and a `high` change has an `approved` approval by someone other than the implementer |
| A-06 | every test change, and every `L2` or `L3` check marked `not_applicable`, is approved (`approved_by`) by someone other than the implementer |
| A-07 | a change with infrastructure changes is `high` |
| A-08 | a `high` change comes with the challenge report for its problem (`--report`), and every finding of a given report is answered and targets the problem or a requirement of the graph |
| A-09 | the graph's structure holds where the decision depends on it: requirement ids are non-empty and unique; every listed child is a requirement of the graph and is listed once; following children never returns to a requirement; a `LEAF` has no children and an `AND` or `OR` has at least two; exactly one requirement has no parent; every requirement has an acceptance criterion; and every `AND` or `OR` has an `L2` or `L3` criterion of its own |
| A-10 | a `medium` or `high` change comes with the assurance review (`--review`) of `reviewed_commit`, and every finding of a given review is answered and targets a requirement, an acceptance criterion, or the change (`change_id`) |

A finding is answered when it is an object whose `id` no other finding has, whose `target` is one the rule names, whose `disposition` is `accepted` or `rejected`, and whose `resolution` is not empty. Anything else — `open`, another spelling, an undefined value, a missing resolution — leaves it unanswered.

Names are compared after Unicode NFKC normalization, with format characters such as zero-width spaces removed, and ignoring case and surrounding spaces, so `Claude`, ` claude `, the fullwidth `ｃｌａｕｄｅ`, and `clau` + zero-width space + `de` are the same person as `claude`. A name that is empty in that form approves nothing.

The gate reads the graph's problem id, its acceptance criteria, and the structure A-09 lists, so a graph whose own checker never ran cannot pass. It does not check field shapes or `OR` selections, which stay with the graph's own checker (`requirements-decomposition`): every alternative's criteria need their own checks anyway. An acceptance id used by two criteria, an undefined level, or a requirement without an `acceptance` array is refused (exit 2), so a leaf's check cannot stand for a parent's own check.

`--report` takes the challenge report written in the decomposition step (`requirements-decomposition`), in which the challenger's findings are answered. Its top level is exactly `schema_version` 1 and `challenge_report`, which has exactly `problem_id` (the graph's), `reviewer`, `context_given` (non-empty strings), and a `findings` array; anything else cannot be interpreted (exit 2). The gate decides on its findings by A-08. A `high` change without a report is `blocked`, so run the challenger for every high-risk change.

## The assurance review

`--review` takes the record of the independent assurance review ([reviewer.md](reviewer.md)), in which the reviewer's findings are answered. A `medium` or `high` change without one is `blocked`.

```json
{"schema_version": 1, "assurance_review": {
  "change_id": "CHG-001", "reviewed_commit": "0f5a148c2d7a9e1b3f6a8c0d2e4f6a8b0c2d4e6f",
  "reviewer": "read-only subagent (Explore), 2026-11-06",
  "context_given": ["requirements graph", "diff of 0f5a148", "CI log of run 1"],
  "findings": [{"id": "AR-01", "kind": "parent_by_children", "target": "TEST-PARENT-001", "severity": "medium",
                "statement": "<what is wrong and the line that shows it>", "disposition": "rejected",
                "resolution": "<why it does not hold, or what changed>"}]}}
```

- Exactly these fields; `change_id`, `reviewed_commit`, and `reviewer` are non-empty strings, `context_given` lists exactly what the reviewer was given, and `findings` is an array, empty when the reviewer found nothing material. Otherwise, or when `change_id` is not the manifest's, the input cannot be interpreted (exit 2).
- `reviewed_commit` must be the manifest's `reviewed_commit`, written the same way; a review of another commit is stale and A-10 blocks it.
- Each finding has `id`, `kind` (`parent_by_children`, `evidence_mismatch`, `uncovered_path`, `weakened_test`, `risk_mismatch`, or `other`, after the reviewer prompt), `target`, `severity` (`high`, `medium`, `low`), `statement`, `disposition`, and `resolution` once answered. The gate reads `id`, `target`, `disposition`, and `resolution`; the card also shows the others.

## Review card

`card --problem CARD --graph GRAPH --manifest MANIFEST [--report REPORT] [--review REVIEW] [--lang en|ja]` prints a Markdown review card and exits like the gate; a graph the gate blocks under A-09 still gets a card that shows why. It reads each file once, runs the gate on that content, and shows its decision, its counts per level, and its reasons. It refuses (exit 2) a problem card that is not `verified`, a problem card or challenge report for another problem than the graph and the manifest, and an assurance review for another change. The challenge report and the assurance review go to the gate, so a missing record or an unanswered finding in one is `blocked` by A-08 or A-10; otherwise the card never decides on its own. With `--format json` it prints `{output_version, input_file, decision, markdown}`. In order, it shows: the decision (✅ only on `pass`), the problem (current, ideal, gap), the change and its risk, the checks by level, every check that did not pass, the unresolved items (gate reasons and the unanswered findings of the challenge report and the assurance review), what a person has to decide, a Mermaid diagram of the decomposition three levels deep with each requirement drawn once (deeper requirements are listed; a requirement's colour covers its own checks and everything below it, and one with only `not_applicable` checks is not green), and the evidence of every check. All input text is treated as untrusted: Markdown emphasis, code, heading, and link characters, HTML angle brackets, and control characters are escaped, the decision marks are replaced by words everywhere (in code, tables, and the diagram too), a URL with any scheme followed by `://`, a `www.` host, or an e-mail address inside text is shown as code in any letter case, `#` in the diagram is written as `#35;` so that no entity can be formed, backslashes in code are shown as recorded, and an evidence reference becomes a link only when it is a plain `http` or `https` URL.

## JUnit XML

`collect-junit` prints an array of checks to put in the manifest. A test case belongs to an acceptance criterion when its property `acceptance_id` equals the id, or when the id appears as a separate word (not inside a longer id or name) in its `classname` or `name`, for example `test_other_user[TEST-LEAF-001]`. A separate word means the id is not next to a letter, digit, `_`, `-`, or `.`, so `TEST-LEAF-003.extra` does not count for `TEST-LEAF-003`. A criterion whose test cases all passed is `passed`; one with any failure or error is `failed`; any other mix (some skipped, or none found) is `not_run`, with the counts in its reason. A report with a `DOCTYPE` declaration, where entities are declared, is refused. The XML parser finds the declaration, so such text inside a comment, an instruction, or CDATA is not taken for one, and none can hide behind them.
