# Pilot: does the evidence-based review save time without losing quality?

Adopt the evidence-based review (arm B) over the current one (arm A) only when, for comparable original requests, the median human minutes per request falls by at least the target fixed beforehand, and every quality gate fixed beforehand holds for arm B. Time saved never offsets a broken gate. `scripts/pilot.py` applies that rule to the records; running the pilot — choosing requests, assigning them, timing people — is work for people, and the script cannot tell real records from invented ones.

## 1. Before the first case: preregister

Write `preregistration.json` and commit it before any case starts. Its date must not be later than the first case, or the decision is `insufficient`.

```json
{"schema_version": 1, "pilot_preregistration": {
  "registered_at": "2026-11-10",
  "target_reduction": 0.2,
  "minimum_cases_per_arm": 5,
  "time_items": ["request", "rereading", "instructions", "reading", "review", "rework", "approval"],
  "quality_gates": ["required_ci_kept", "no_new_missed_known_defect", "parent_failure_rejected", "no_unapproved_high_risk"]}}
```

- `target_reduction` is the fraction the median must fall by (0.2 is 20%). Fix it here; do not change it after seeing results.
- `time_items` are the parts of a person's working time that are recorded for every case: understanding the request, re-understanding the problem, instructing the AI, reading logs and diffs, reviewing, returning work, re-checking fixes, approving. Waiting for the AI is not working time and is not recorded.
- `quality_gates` are the conditions every arm B case must keep, each recorded as true or false — for example: the required CI was not weakened; no known critical defect in the evaluation set was missed; a case built so that leaves pass and the parent fails was rejected; no high-risk operation ran without approval.

Also decide and write down, outside this file: which past requests are used (10 to 20 is a starting size, too small to prove that rare incidents do not increase), how they are paired or assigned to arms and reviewers so that the same person does not learn a request in one arm and reuse it in the other, who times the work and how, and what counts as a critical defect.

## 2. During the pilot: record each case

```json
{"schema_version": 1, "pilot_cases": [
  {"case_id": "C-01", "request_id": "TICKET-123", "arm": "B", "stratum": "api", "completed": true,
   "started_at": "2026-11-12",
   "minutes": {"request": 3, "rereading": 2, "instructions": 4, "reading": 6, "review": 12, "rework": 0, "approval": 2},
   "quality": {"required_ci_kept": true, "no_new_missed_known_defect": true, "parent_failure_rejected": true, "no_unapproved_high_risk": true}}]}
```

- One original request is one sample per arm: do not count the subtasks of one request as separate cases.
- `stratum` groups comparable cases (for example `api`, `iac`, `security`); compare within strata.
- Record cases that were abandoned or interrupted with `completed: false` and the minutes spent so far. Never drop them.
- `quality` is required for every completed arm B case and optional otherwise.

## 3. After the pilot: decide

```sh
python3 <skill-dir>/scripts/pilot.py [--format text|json] preregistration.json cases.json
```

| Decision | When | Exit |
|---|---|---|
| `adopt` | the median reduction of completed cases is at least the target (computed exactly from the numbers as written, so 10 and 8 minutes against a target of 0.2 meet it), no quality gate failed in arm B, and arm B is not slower than arm A in any stratum | 0 |
| `not_adopted` | the reduction is below the target, any quality gate failed in arm B, or arm B is slower in some stratum (a pooled median can improve while every stratum gets slower when cases are spread unevenly over strata) | 1 |
| `insufficient` | the preregistration is later than the first case, an arm has fewer completed cases than the preregistered minimum, a stratum has completed cases in one arm only, or arm A's median is 0 | 1 |

Records that break the format give violations instead of a decision (exit 1): E-00 for missing or wrongly typed fields (minutes must be finite numbers, so `Infinity` and `NaN` are refused; `schema_version` must be the integer 1), time items or quality gates that differ from the preregistration, and E-01 for a `case_id` used twice or an original request counted twice in one arm. Unreadable input exits 2.

The result shows, per arm, the completed and incomplete counts, the median of completed cases, and the median with incomplete cases included (their minutes as lower bounds); per stratum, both medians, the reduction, and whether arm B was slower; and every failed quality gate with its case. It does not run a statistical test: with this sample size a reduction above the target does not establish the true size of the effect, so report the distribution and the strata along with the decision, and keep watching rework, incidents, and vulnerabilities after adoption.
