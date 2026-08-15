# Quickstart: Validate the /verify-config Removal

## Prerequisites
- Working tree on branch `024-remove-verify-config`
- `bash`, `grep`, `find` available (no other tooling required — this feature has no build step)

## 1. Confirm the three files are gone

```sh
test ! -e .claude/skills/verify-config/SKILL.md && \
test ! -e .claude/agents/verification-runner.md && \
test ! -e tests/run-verification-agent.sh && \
echo "PASS: all three removed"
```

Expected: `PASS: all three removed`

## 2. Confirm no live reference remains outside historical specs

```sh
grep -rniE "verify-config|verification-runner" . \
  --include="*.md" --include="*.sh" --include="*.json" \
  --exclude-dir=.git \
  | grep -vE "specs/(014-codex-config-port|019-verify-fork-test-runner|021-codex-official-import|024-remove-verify-config)/"
```

Expected: no output (empty). Any line printed here is a dangling reference (FR-007).

## 3. Confirm the historical-cleanup list in both READMEs is untouched

```sh
grep -n "codex/prompts/verify-config.md" README.md README.ja.md
```

Expected: exactly one match per file (the "If you installed an earlier version" / 旧バージョンからの移行 cleanup list), per FR-010 — this line must survive.

## 4. Run the remaining behavior suites

```sh
for t in tests/run-*.sh; do
  echo "== $t =="
  bash "$t" || echo "FAILED: $t"
done
```

Expected: every suite reports success; none fail due to a missing file this removal deleted (SC-002).

## 5. Confirm `install.sh` still runs cleanly

```sh
bash install.sh
```

Expected: completes with `Synced managed paths from ... -> ...` and no error (SC-003). (Requires `claude`, `uvx`, `jq` on `PATH` per the script's own preflight — skip this step if those aren't installed locally; CI/verification of `install.sh` logic itself is out of scope for this feature.)
