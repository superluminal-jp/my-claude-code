# Quickstart: Validating the Model and Effort Routing Rule

Run from the repository root.

## 1. Structure and installer checks (automated)

```bash
bash tests/run-config-pyramid.sh
bash tests/run-install.sh
```

Expected: no `FAIL` lines. `RULE-01` reports six files, `RULE-02`–`RULE-04` report no path, skill-name, or sibling-filename violation, and `RULE-11` passes. The installer test confirms the rules directory still matches after install and after a second run.

Before the rule file exists, `RULE-01` and `RULE-11` must fail; that failing state is the red step.

## 2. Non-regression (automated)

```bash
git diff --stat main -- .claude/rules/clarifier.md .claude/rules/live-documentation.md .claude/rules/permissions.md .claude/rules/pyramid-principle.md .claude/rules/thinking-lenses.md .claude/CLAUDE.md .claude/skills install.sh docs/adr
```

Expected: empty output.

## 3. Stale-count search (automated)

```bash
grep -nE "5 independent|5つのルール|5個のユニバーサル|（5件）|\(5件\)|exactly five" README.md README.ja.md docs/claude-config-design.md tests/run-config-pyramid.sh
```

Expected: no matches.

## 4. Behavioral read-through (manual, SC-001)

Read only `.claude/rules/model-routing.md`, then answer without other files:

| Unit of work | Expected tier / effort |
|---|---|
| Repository-wide text search | `haiku` / `low` |
| Well-scoped bug fix | `sonnet` / `medium` |
| Non-trivial refactor | `opus` / `high` |
| Cross-cutting architecture decision | `fable` / `high` or above |
| Large mechanical rename | do not escalate; decompose or parallelize |
| Current tier cannot decide correct behavior | escalate |
| Architecture resolved, implementation remains | hand back to a lower tier |
| Trivial single-file edit | do directly, no subagent |
| Three independent parallel searches | subagents, `haiku` / `low` |

Expected: 9 of 9 match.

## 5. Alias check (manual, plan D9)

Confirm `fable`, `opus`, `sonnet`, `haiku` against the official Claude Code model configuration documentation. Record the result in `research.md` D9 when done.

## 6. Mirror check (manual)

Confirm `.claude-ja/rules/model-routing.md` has the same six elements in the same order as the English file.
