# Quickstart: Remove Codex CLI Support and All Codex References

Validation sequence to run after implementation, from the repository root.

## 1. `AGENTS.md` is gone (SC-002)

```sh
test -f AGENTS.md && echo "FAIL: still exists" || echo "OK: deleted"
```

Expected: `OK: deleted`.

## 2. No dangling references to `AGENTS.md` or the deleted test suites

```sh
grep -rn "AGENTS\.md" --exclude-dir=.git --exclude-dir=specs --exclude-dir=docs .
grep -rln "run-codex-references\|run-codex-drift" --exclude-dir=.git --exclude-dir=specs --exclude-dir=docs .
```

Expected: both commands return no output.

## 3. Repository-wide "codex" search (SC-001)

```sh
grep -rli "codex" --exclude-dir=.git --exclude-dir=specs .
```

Expected output set (excluding `specs/`, already excluded by the command above): every file under `docs/adr/` that happens to mention "codex" (not just 0002/0004/0010 — several other Accepted ADRs, e.g. 0003, 0005, 0006, cite Codex as part of their own immutable historical rationale and are not edited by this feature), plus:
```
.specify/integrations/codex.manifest.json
.specify/extensions/.registry
.gitignore
```
(`.gitignore` matches only on its two literal `.codex/`/`.agents/` lines, not its comment — confirm with `grep -ni codex .gitignore` showing exactly two hits, both bare directory paths.)

Any file outside `docs/adr/`, `.specify/integrations/`, `.specify/extensions/.registry`, and `.gitignore` appearing in this list is a defect.

## 4. Test suites this feature edits directly

```sh
bash tests/run-subagent-delegation.sh; echo "exit: $?"
bash tests/run-digital-agency-frontend-skill.sh; echo "exit: $?"
bash tests/run-mcp-startup.sh; echo "exit: $?"
```

Expected: `run-digital-agency-frontend-skill.sh` and `run-mcp-startup.sh` exit 0 (matching their pre-change baseline in research.md R12). `run-subagent-delegation.sh` still exits non-zero — confirm via its output that the **only** failing checks are the pre-existing ones already listed in research.md R12 (missing `.claude/rules/subagent-delegation.md`), and that no check naming "Codex" or "AGENTS.md" appears anywhere in its output at all (neither PASS nor FAIL — the check itself is gone).

## 5. Deleted suites are actually gone

```sh
test -f tests/run-codex-references.sh && echo "FAIL: still exists" || echo "OK: deleted"
test -f tests/run-codex-drift.sh && echo "FAIL: still exists" || echo "OK: deleted"
```

Expected: both `OK: deleted`.

## 6. Full regression baseline (SC-003)

```sh
for t in tests/run-*.sh; do
  bash "$t" >/tmp/qs-$$.log 2>&1
  ec=$?
  echo "$t: exit $ec"
done
```

Compare each suite's exit code against research.md R12's pre-change table. Only
`tests/run-install.sh` (pre-existing, unrelated failure) and
`tests/run-subagent-delegation.sh` (pre-existing, unrelated failure — see step 4)
are expected to be non-zero. Every other suite must be `0`.

## 7. ADR chain (SC-004)

```sh
head -5 docs/adr/0002-deploy-codex-configuration-at-user-scope.md
head -5 docs/adr/0004-adopt-official-codex-import.md
head -5 docs/adr/0010-remove-codex-cli-support.md
git diff --stat main -- docs/adr/0002-deploy-codex-configuration-at-user-scope.md
git diff main -- docs/adr/0004-adopt-official-codex-import.md
```

Expected: `0002`'s `status:` line unchanged (`Superseded by 0004`) and its `git diff --stat` against `main` shows no changes at all. `0004`'s `status:` line reads `Superseded by 0010`, and its `git diff` shows exactly one changed line (the `status:` line). `0010`'s `status:` line reads `Accepted`.

## 8. Untouched trees (SC-005)

```sh
git status --porcelain specs/ ':!specs/031-remove-codex-support'
git status --porcelain .specify/integrations/ .specify/extensions/.registry
```

Expected: both commands return no output (the first command excludes this feature's own spec directory, which is of course created and edited by this feature).
