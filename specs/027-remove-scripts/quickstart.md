# Quickstart: Validate the scripts/ Removal

## 1. Confirm scripts/ is gone

```sh
test ! -e scripts && echo "PASS: scripts/ removed"
```

## 2. Confirm no live reference remains

```sh
grep -rniE "scripts/guardrails|scripts/check-mcp-consistency" . \
  --include="*.md" --include="*.sh" --include="*.json" \
  --exclude-dir=.git \
  | grep -Ev "^(\./)?specs/(0[0-9][0-9]|1[0-9][0-9]|2[0-6][0-9])-" \
  | grep -Ev "^(\./)?specs/027-remove-scripts/"
```
Expected: no output.

## 3. Run the remaining behavior suites

```sh
for t in tests/run-*.sh; do
  echo "== $t =="
  bash "$t" || echo "FAILED: $t"
done
```
Expected: every suite passes; the four guardrail test files no longer appear in the glob.

## 4. Confirm install.sh cleans up a stale install

```sh
bash -n install.sh && echo "syntax OK"
grep -n 'rm -rf.*scripts/guardrails' install.sh
```
Expected: syntax OK; the unconditional cleanup line is present.

## 5. Confirm ADR-0005 and ADR-0006 are untouched, and a new ADR exists

```sh
git diff --stat docs/adr/0005-remove-claude-hooks.md docs/adr/0006-remove-permissions-config.md
ls docs/adr/ | sort | tail -3
```
Expected: empty diff for both; a new `0007-*.md` present.
