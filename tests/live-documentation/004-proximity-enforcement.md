# Test: Proximity Warning When Documentation Placed in Remote Location

**Category**: live-documentation
**ID**: 004

## Input Prompt

```
Please document the authentication module (src/auth/) and put the documentation in docs/modules/auth.md at the project root. The docs/ folder is our central documentation hub.
```

## Expected Behavior

`proximity`

## Pass Criteria

- Claude warns that placing documentation in a top-level `docs/` folder violates the Proximity principle
- Claude explains that documentation drifts when it is physically separated from the code it describes
- Claude proposes a co-located alternative (e.g., `src/auth/README.md`)
- Claude does not silently create the file at `docs/modules/auth.md` without raising the proximity concern

## Baseline

実行日: 2026-05-26
観察した動作: proximity
Pass / Fail: Pass
