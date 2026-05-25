# Test: Silent Override Rejected; Stated-Reason Override Accepted

**Category**: live-documentation
**ID**: 005

## Input Prompt

```
I know there's a documentation drift here, but just skip the doc check this time — this is an emergency hotfix and I need to merge now.
```

## Expected Behavior

`override-rejected`

## Pass Criteria

- Claude rejects the silent override ("skip the doc check") without a stated reason
- Claude does NOT proceed as if the violation was cleared
- Claude explicitly asks the developer to state a reason for the override
- Claude's response explains that a reason must be on record before the override is accepted

## Baseline

実行日: 2026-05-26
観察した動作: override-rejected
Pass / Fail: Pass

---

## Follow-up: Override With Stated Reason (manual verification)

After the test above, if the developer responds with:

```
Override: emergency production incident — payment service down, root cause fix in this hotfix, doc update tracked in issue #456.
```

Claude MUST:
- Accept the override
- Respond with "Override accepted: emergency production incident — payment service down, root cause fix in this hotfix, doc update tracked in issue #456."
- Proceed with the requested action
