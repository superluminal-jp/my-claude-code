# Quickstart: Validate the permissions Block Removal

## 1. Confirm both settings files have no `permissions` key

```sh
jq 'has("permissions")' .claude/settings.json .claude/settings.local.json
```
Expected: `false` twice.

## 2. Confirm settings.local.json's other keys survive

```sh
jq 'keys' .claude/settings.local.json
```
Expected: `["prefersReducedMotion","spinnerTipsEnabled"]` (no `permissions`).

## 3. Confirm no live reference remains outside historical specs

```sh
grep -rniE "permissions\.deny|allow/ask/deny|stay on .ask.|the one guardrail|remains as a Claude Code|not removed\b" . \
  --include="*.md" --include="*.sh" --include="*.json" \
  --exclude-dir=.git \
  | grep -Ev "^(\./)?specs/(0[0-9][0-9]|1[0-9][0-9]|2[0-5][0-9])-" \
  | grep -Ev "^(\./)?specs/026-remove-permissions-config/"
```
Expected: no output.

## 4. Run the remaining behavior suites

```sh
for t in tests/run-*.sh; do
  echo "== $t =="
  bash "$t" || echo "FAILED: $t"
done
```
Expected: every suite passes; `run-codex-references.sh` no longer has a RULE-09 line in its output.

## 5. Confirm ADR-0005 is untouched and a new ADR exists

```sh
git diff --stat docs/adr/0005-remove-claude-hooks.md
ls docs/adr/ | sort | tail -3
```
Expected: empty diff for 0005; a new `0006-*.md` present.
