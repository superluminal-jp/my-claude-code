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
  | grep -Ev "^(\./)?docs/adr/" \
  | grep -Ev "^(\./)?specs/(0[0-9][0-9]|1[0-9][0-9]|2[0-6][0-9])-" \
  | grep -Ev "^(\./)?specs/027-remove-scripts/"
```
Expected: any output is limited to negative removal explanations or the
installer's unconditional upgrade-cleanup path. Nothing describes either
deleted script as existing, runnable, or current logic.

## 3. Validate the installer against an isolated home

```sh
bash tests/run-install.sh
```

Expected: current managed paths are installed, stale managed paths are removed,
unrelated user files remain unchanged, `agents/` is managed, all current MCPs
are upserted, and the real home directory is untouched.

## 4. Confirm obsolete tests and draw.io are gone

```sh
test ! -e tests/run-live-documentation.sh
test ! -e tests/run-skill-routing.sh
test ! -e tests/run-type-safety-coder.sh
test ! -e tests/ubiquitous-language
! rg -n 'claude[[:space:]]+-p' tests/run-*.sh
! rg -n -i 'drawio|draw\.io' .mcp.json install.sh .claude/skills .claude/rules
```

Expected: every command exits successfully with no output from either search.

## 5. Run the remaining behavior suites

```sh
for t in tests/run-*.sh; do
  echo "== $t =="
  bash "$t" || echo "FAILED: $t"
done
```
Expected: every suite passes; no retained runner requires Claude CLI
authentication.

## 6. Check shell and JSON quality

```sh
bash -n install.sh && echo "syntax OK"
grep -n 'rm -rf.*scripts/guardrails' install.sh
shfmt -d -i 2 install.sh tests/run-*.sh
shellcheck install.sh tests/run-*.sh
jq empty .mcp.json .claude/settings.json
```

Expected: syntax and lint pass; the unconditional retired-guardrail cleanup
line remains present.

## 7. Confirm ADR-0005 and ADR-0006 are untouched, and ADR-0007 remains

```sh
git diff --stat docs/adr/0005-remove-claude-hooks.md docs/adr/0006-remove-permissions-config.md
ls docs/adr/ | sort | tail -3
```
Expected: empty diff for both; a new `0007-*.md` present.
