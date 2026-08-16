# Quickstart: Verify subagent-delegation Rule Removal

Validates spec.md's acceptance scenarios and success criteria after
implementation. No build step, no server, no test framework — plain
filesystem and text checks from the repository root.

## Prerequisites

- Working tree includes the changes from this feature's tasks.md.
- Run from the repository root (`/Users/taikiogihara/work/my-claude-code`).

## 1. The rule file is gone (SC-001)

```sh
test ! -f .claude/rules/subagent-delegation.md && echo "PASS: file absent" || echo "FAIL: file still exists"
```

Expected: `PASS: file absent`.

## 2. No live reference remains outside specs/ and docs/adr/ (SC-002)

```sh
grep -rl "subagent-delegation" . --include="*.md" \
  | grep -Ev "^\.?/?specs/" \
  | grep -Ev "^\.?/?docs/adr/"
```

Expected: no output (empty result = PASS).

## 3. CLAUDE.md reads coherently without the reference (FR-002, FR-003, SC-004)

```sh
grep -n "subagent-delegation" .claude/CLAUDE.md
```

Expected: no output. Then read the "Execution: parallelize whenever valid"
section by eye — it should still make sense on its own, describing only
*how* to issue parallel calls, with no dangling sentence that presupposes a
deleted file.

## 4. README.md file-tree no longer lists the file (FR-004)

```sh
grep -n "subagent-delegation" README.md
```

Expected: no output.

## 5. Historical specs are untouched (FR-006)

```sh
git status specs/020-subagent-delegation-rule specs/021-codex-official-import specs/024-remove-verify-config
```

Expected: no changes reported (these paths do not appear in `git status`
output, or show as unmodified).

## 6. Context-size reduction is real (SC-003)

```sh
git show HEAD:.claude/rules/subagent-delegation.md | wc -l
```

Compare against the pre-removal line count (54 lines, confirmed during
spec-writing) to confirm the always-loaded `@`-include set shrank by that
amount with no offsetting addition elsewhere.
