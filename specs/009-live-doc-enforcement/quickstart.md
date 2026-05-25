# Quickstart: Live Documentation Enforcement

**How to verify the rule is active and working.**

## 1. Confirm the rule is loaded

Open a new Claude Code session in this project. Run:

```
What rules do you currently follow for documentation?
```

Claude should mention Live Documentation enforcement and the five core principles (Single Source of Truth, Executable Specification, Proximity, Automation over Discipline, No Redundancy). If it does not, check:
- `.claude/rules/live-documentation.md` exists
- `.claude/CLAUDE.md` has `@.claude/rules/live-documentation.md` in the import chain

## 2. Test drift detection (Contract 1)

Present a code diff where a public function signature changed but its docstring was not updated. For example:

```
Review this change:
- def process_order(order_id: str) -> None:
+ def process_order(order_id: str, priority: int = 0) -> None:

The docstring in the same file was not updated.
```

**Expected**: Claude flags this as a Live Documentation violation (Drift) and asks for the docstring to be updated or an Override reason to be provided.

## 3. Test auto-generation recommendation (Contract 3)

Ask Claude:

```
Please write the API reference for the `process_order` function.
```

**Expected**: If the function has complete type annotations, Claude recommends using the auto-generation tool (e.g., sphinx-apidoc, pdoc, etc. — whichever exists in the project) rather than writing the reference manually.

## 4. Run automated tests

```bash
bash tests/run-live-documentation.sh
```

All test scenarios in `tests/live-documentation/` should pass.

## 5. Common issues

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| Rule not applied | Import missing in `.claude/CLAUDE.md` | Add `@.claude/rules/live-documentation.md` |
| False positive on refactor | Rule not distinguishing contract vs internal change | Check Contract 1 trigger condition in rule file |
| Override not accepted | Reason not stated | State a reason explicitly in the override message |
