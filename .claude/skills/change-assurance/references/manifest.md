# The verification manifest and the bundled checker

`scripts/assure.py` reads a verification manifest, a version 2 requirements graph, and JUnit XML reports. It reads its inputs and nothing else: it writes no file, opens no network connection, starts no process, and never executes input content. It needs Python 3.9 or later and its standard library only.

```sh
python3 <skill-dir>/scripts/assure.py [--format text|json] check MANIFEST
python3 <skill-dir>/scripts/assure.py [--format text|json] gate GRAPH MANIFEST [--report REPORT]
python3 <skill-dir>/scripts/assure.py collect-junit REPORT --graph GRAPH --commit SHA --ref REF [--kind ci_job|local_run]
```

Exit codes: 0 for `pass` or no violation, 1 for `fail`, `blocked`, or violations, 2 when an input cannot be interpreted (unreadable, not a regular file, over 5 MiB, not UTF-8, invalid JSON or XML, a repeated key, an XML `DOCTYPE` or `ENTITY`, a wrong top level, a challenge report for another problem, bad arguments) or the checker itself failed.

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

`gate GRAPH MANIFEST` answers `pass` only when every rule holds. A failed check or a rejected approval makes it `fail`; anything else that does not hold makes it `blocked`. Both are not a pass. The result lists each reason with its rule and effect, and counts the statuses per level (`L1`, `L2`, `L3`), counting a passed check whose evidence was refused, and an `L2` or `L3` check marked `not_applicable` without the approval A-06 needs, as `blocked`. Manifest violations (M-xx) also block.

| Rule | Holds when |
|---|---|
| A-01 | the graph has at least one acceptance criterion, each has exactly one check, no check names an id outside the graph, and the manifest is for the graph's problem |
| A-02 | the evidence of a passed check is not `ai_review` only, has a reference, and is for `reviewed_commit` (the same string: a short SHA and the full SHA of one commit do not match, so write both in full) |
| A-03 | every check is `passed` or `not_applicable` with a reason, and no requirement has only `not_applicable` checks |
| A-04 | the risk is `low`, `medium`, or `high` |
| A-05 | no approval is `rejected` (at any risk), and a `high` change has an `approved` approval by someone other than the implementer |
| A-06 | every test change, and every `L2` or `L3` check marked `not_applicable`, is approved (`approved_by`) by someone other than the implementer |
| A-07 | a change with infrastructure changes is `high` |
| A-08 | a `high` change comes with the challenge report for its problem (`--report`), and no finding of the given report is `open` |

Names are compared ignoring case and surrounding spaces, so `Claude` and ` claude ` are the same person as `claude`.

The graph is read only for its problem id and its acceptance criteria; an acceptance id used by two criteria is refused (exit 2), so a leaf's check cannot stand for a parent's own check. Check the graph's structure with its own checker before this gate.

`--report` takes the challenge report written in the decomposition step (`goal-refinement`), in which the challenger's findings are answered. The gate reads only its problem id, which must be the graph's (otherwise exit 2), and which findings are `open`; check the report's own format with `goal-refinement`'s checker first. A `high` change without a report is `blocked`, so run the challenger for every high-risk change.

## JUnit XML

`collect-junit` prints an array of checks to put in the manifest. A test case belongs to an acceptance criterion when its property `acceptance_id` equals the id, or when the id appears as a separate word (not inside a longer id or name) in its `classname` or `name`, for example `test_other_user[TEST-LEAF-001]`. A separate word means the id is not next to a letter, digit, `_`, `-`, or `.`, so `TEST-LEAF-003.extra` does not count for `TEST-LEAF-003`. A criterion whose test cases all passed is `passed`; one with any failure or error is `failed`; any other mix (some skipped, or none found) is `not_run`, with the counts in its reason. A report with a `DOCTYPE` declaration, where entities are declared, is refused. The XML parser finds the declaration, so such text inside a comment, an instruction, or CDATA is not taken for one, and none can hide behind them.
