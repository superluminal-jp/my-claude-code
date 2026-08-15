# Quickstart: Validate the .claude/hooks/ Removal

## Prerequisites
- Working tree on branch `025-remove-claude-hooks`
- `bash`, `grep`, `jq` available

## 1. Confirm the directory is gone

```sh
test ! -e .claude/hooks && echo "PASS: .claude/hooks removed"
```

## 2. Confirm settings.json has no hooks/statusLine wiring

```sh
jq 'has("hooks") or has("statusLine")' .claude/settings.json
```

Expected: `false`

## 3. Confirm no live reference remains outside historical specs

```sh
grep -rniE '\.claude/hooks|pre-bash\.sh|pre-edit\.sh|post-edit-format\.sh|user-prompt-submit\.sh|speckit-expand-update\.sh|statusline\.sh' . \
  --include="*.md" --include="*.sh" --include="*.json" \
  --exclude-dir=.git \
  | grep -Ev "^(\./)?specs/(0[0-9][0-9]|1[0-9][0-9]|2[0-4][0-9])-" \
  | grep -Ev "^(\./)?specs/025-remove-claude-hooks/"
```

Expected: no output. (The regex excludes all `specs/NNN-*` directories numbered below 025, i.e. every spec that predates this one, plus this feature's own directory — matching the convention from spec-024's quickstart, generalized since this feature found references in more historical specs than anticipated at first glance.)

## 4. Confirm the Codex comparison table reads correctly

```sh
grep -A10 "What Codex enforces" README.md
```

Manually confirm: Claude Code column shows "no" for destructive-command blocking, prompt-secret scanning, edit protection, post-edit formatting, and Spec Kit prompt expansion; "yes" only for allow/prompt command policy. Codex column shows "yes, once trusted" for destructive-command blocking and prompt-secret scanning.

## 5. Run the remaining behavior suites

```sh
for t in tests/run-*.sh; do
  echo "== $t =="
  bash "$t" || echo "FAILED: $t"
done
```

Expected: every suite passes; `tests/run-speckit-update.sh` no longer appears in the glob (deleted).

## 6. Confirm install.sh has no dangling hook-chmod step

```sh
bash -n install.sh && echo "syntax OK"
grep -n 'chmod +x.*hooks' install.sh || echo "PASS: no dangling chmod on hooks/*.sh"
```
