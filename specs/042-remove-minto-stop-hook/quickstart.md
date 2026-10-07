# Quickstart: Validate the Minto Stop Hook Removal

Run every command from the repository root unless a step says otherwise.
Contract clauses are in [contracts/minto-package.md](contracts/minto-package.md).
The entity states are in [data-model.md](data-model.md).

## Prerequisites

- Python 3 (stdlib only), Bash, `jq`
- `claude` CLI on `PATH` (for `claude plugin validate`)
- Baseline recorded on 2026-10-07: 5/5 package tests pass, and `claude plugin validate --strict` reports `Validation passed`

## V1. Red: the new test fails before the deletion (C1.4)

After replacing `test_stop_hook` with `test_declares_no_hooks`, and before deleting the hook file:

```bash
(cd .claude/skills/minto-pyramid && python3 -B -m unittest discover -s tests -v)
```

**Expected**: exactly one failure, `test_declares_no_hooks`. The other 4 tests pass.

## V2. Green: the package declares no hooks (C1.1–C1.4, C2.1, C2.3)

```bash
test ! -e .claude/skills/minto-pyramid/hooks && echo "no hooks dir"
jq -e 'has("hooks") | not' .claude/skills/minto-pyramid/.claude-plugin/plugin.json
jq -r .version .claude/skills/minto-pyramid/.claude-plugin/plugin.json
(cd .claude/skills/minto-pyramid && python3 -B -m unittest discover -s tests -v && claude plugin validate --strict .)
```

**Expected**:

- the first command prints `no hooks dir`;
- `jq -e` prints `true`;
- the version is `0.3.0+local.no-stop-hook`;
- 5/5 tests pass, and the validator reports `Validation passed`.

## V3. Unchanged content and no regressions (C2.2, FR-007, FR-009)

```bash
git diff --stat main -- .claude/skills/minto-pyramid/{SKILL.md,rules,templates,references,evals} \
  ':!.claude/skills/minto-pyramid/references/anthropic-guidance.md' \
  .claude/skills/maintaining-living-documentation .claude/settings.json .claude/rules install.sh archive
git diff --numstat main -- .claude/skills/minto-pyramid/references/anthropic-guidance.md
for t in tests/run-*.sh; do bash "$t" >/dev/null 2>&1 && echo "PASS $t" || echo "FAIL $t"; done
```

**Expected**:

- the first `git diff` prints nothing;
- the `--numstat` line reads `1\t1\t…anthropic-guidance.md` (only line 24 changed; analysis A1);
- each suite that passed on `main` still prints `PASS`.

If a suite already fails on `main`, record that before blaming this change.

## V4. Documentation matches (C3, SC-004)

```bash
grep -n -i "stop" README.md README.ja.md .claude/skills/minto-pyramid/README.md | grep -i minto
grep -n -i "stop" .claude/skills/minto-pyramid/references/anthropic-guidance.md
grep -n -i "verbatim" tests/run-config-pyramid.sh
grep -n "上流のまま" docs/claude-config-design.md
python3 ~/.claude/skills/maintaining-living-documentation/scripts/check_links.py --changed
```

**Expected**:

- No line describes a Minto `Stop` hook as current behavior. A line about its *removal* is acceptable.
- In `references/anthropic-guidance.md`, only the general Claude Code facts (lines 21–23) mention `Stop`; no line says this plugin uses a hook.
- The design doc and the `tests/run-config-pyramid.sh` comment no longer call `minto-pyramid` an unmodified upstream copy.
- The link check reports no broken links.
- Read `README.md` and `README.ja.md` side by side and confirm that they state the C3.1–C3.3 facts identically.

## V5. Installed copy updated (FR-002, SC-001) — user-run or user-approved

```bash
./install.sh
test ! -e ~/.claude/skills/minto-pyramid/hooks && echo "installed copy has no hooks"
```

**Expected**: the second command prints `installed copy has no hooks`.

## V6. Live session behavior (User Story 1, SC-002) — manual

1. Start a **new** Claude Code session. A running session keeps the hooks it loaded at start ([hooks reference](https://code.claude.com/docs/en/hooks)).
2. Run `/hooks` and confirm that no `minto-pyramid` `Stop` hook is listed.
3. Complete 5 substantive turns.

**Expected**:

- 0 Minto correction requests across the 5 turns.
- The `minto-pyramid` skill is still listed and usable.
- A block from the `maintaining-living-documentation` Stop hook is out of scope and does not count as a failure.
