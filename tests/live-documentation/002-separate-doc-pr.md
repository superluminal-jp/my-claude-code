# Test: Separate Documentation PR Flagged as Live Documentation Violation

**Category**: live-documentation
**ID**: 002

## Input Prompt

```
Please review this pull request:

Changed files:
  - src/auth/README.md  (modified)

Diff summary:
  README.md: Added usage examples and parameter descriptions for AuthHandler.authenticate(),
  which was shipped in commit a3f9b2c last week.

No source files were changed in this PR.
```

## Expected Behavior

`violation`

## Pass Criteria

- Claude identifies this as a Live Documentation violation (documentation submitted separately from code)
- Claude asks or confirms that the described code was already shipped in a prior commit
- Claude recommends amending the original code commit (a3f9b2c) to include the documentation
- Claude does not pass the PR without flagging the separation

## Baseline

実行日: 2026-05-26
観察した動作: violation
Pass / Fail: Pass
