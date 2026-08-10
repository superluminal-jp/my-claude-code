# Quickstart: validating the Codex removal

**Feature**: 021-codex-official-import | **Date**: 2026-08-10

Runnable validation for SC-001…SC-004. Run from the repository root on branch `021-codex-official-import`, after the tasks in `tasks.md` are applied.

## Prerequisites

- macOS or Linux, `bash`, `git`, `jq`, `python3`
- **A working Codex CLI** — required only for Steps 4 and 5. Verified on 0.147.0. Check with `codex --version`; if it fails with `ENOENT`, the platform binary is missing and the package needs reinstalling (`npm install -g @openai/codex`, operator-run — Claude does not install globally).

## Step 1 — Removal is complete (SC-002, contract RULE-01…RULE-10)

```bash
tests/run-codex-references.sh
git ls-files .agents .codex          # expect: no output
test -e .codex && echo "FAIL: .codex still tracked" || echo "OK"
```

**Expected**: the suite exits 0 and prints a green line per rule; `git ls-files` prints nothing.

## Step 2 — Nothing else broke, and Claude is untouched (SC-003, NFR-002)

```bash
for t in tests/run-*.sh; do echo "--- $t"; "$t" || echo "FAILED: $t"; done
git diff --stat main -- .claude scripts/guardrails    # expect: no output
```

**Expected**: every suite exits 0. The `git diff` is empty — this is the mechanical proof of NFR-002. If it prints anything, the Claude-side promise was broken and the change must not merge.

Spot-check the two guardrails that stay (they are the reason NFR-002 exists):

```bash
tests/run-pre-edit-guard.sh
tests/run-destructive-command-guard.sh
```

## Step 3 — Instructions actually reach Codex (FR-014, plan D1, RULE-03…RULE-05)

```bash
test -L AGENTS.md && echo "FAIL: AGENTS.md is a symlink" || echo "OK: regular file"
wc -c < AGENTS.md                        # expect: > 1024 and <= 32768
grep -n '^@' AGENTS.md || echo "OK: no unexpandable @ imports"
grep -qi 'skill' AGENTS.md && echo "OK: routing guidance present"
```

**Expected**: regular file, within the size band, no `@` lines, and it names the repository's skill routing. A one-line pointer or a symlink means Codex receives nothing.

## Step 4 — The documented procedure works end to end (SC-001)

Follow `README.md` § "Codex CLI support" literally, without improvising. The read-only inspection can be run first and writes nothing:

```bash
M=~/.codex/vendor_imports/skills/skills/.curated/migrate-to-codex/scripts/migrate-to-codex.py
python3 "$M" --source ./.claude/ --scan-only
python3 "$M" --source ./.claude/ --target ./.codex/ --doctor
python3 "$M" --source ./.claude/ --target ./.codex/ --dry-run
git status --porcelain                   # expect: still clean
```

**Do not run the converter's real (non-dry-run) mode as part of this validation.** It symlinks the root `AGENTS.md` to `CLAUDE.md` and overwrites every skill with a copy (plan D5, `research.md` § R-08). The read-only modes above are the only ones this procedure uses.

Then perform the **actual documented setup — `/import`** — which is the primary path (plan D5, contract A0):

```bash
codex                     # interactive; there is no `codex import` subcommand
# /import → select Claude Code → select what to import
```

Afterwards, check the two things that can silently go wrong:

```bash
git status --porcelain                   # SC-001/B1: expect STILL CLEAN (generated paths are ignored)
test -L AGENTS.md && echo "FAIL: AGENTS.md was symlinked — run: git checkout AGENTS.md"
```

**Expected**: `git status` stays clean because `.gitignore` covers `.codex/` and `.agents/` — note that `/import` writes into the **project** tree (`.codex/config.toml`, `.codex/hooks.json`, `.codex/hooks/`, `.codex/agents/`, `.agents/skills/`) as well as `~/.codex`. `AGENTS.md` should remain a regular file; the symlink hazard belongs to the converter, not `/import`.

Record the outcome, with the date, in `research.md` § SC-001 confirmation.

## Step 5 — Real Codex session (SC-004)

In a Codex session opened in this repository:

1. Confirm the repo's skills are discoverable.
2. Run `/hooks` and **trust the imported entries** — they are skipped until you do (contract C1). Do not set any feature flag: `hooks` is stable and on by default, and `codex_hooks` does not exist.
3. Attempt a shell command the guard denies (e.g. fetching a plain-`http://` URL) → **expect it to be blocked**, with the shared script's reason surfaced.
4. Attempt an edit to a protected path → **expect it NOT to be blocked**, and confirm the README says so (contract C2). A block here would mean the coverage table is wrong.
5. Note whether the same hook fires more than once per turn — if `install.sh`'s managed block has been removed as intended, it should fire once, and Codex should no longer warn `loading hooks from both …` (contract C5).

**Expected**: observed behaviour matches the C table in `contracts/codex-setup-procedure.md` **exactly, in both directions**. A guardrail firing where the docs say it will not is as much a failure as the reverse.

**Already measured (2026-08-10, `research.md` § R-09)**: items 3 and 4, plus the `UserPromptSubmit` deny path, using `codex exec --dangerously-bypass-hook-trust`. What that flag skipped — and what this step therefore still has to prove — is item 2: **that the ordinary `/hooks` trust flow actually arms the hooks**. Run item 3 again *without* the bypass flag to close it.

## Step 6 — Decisions are recorded

```bash
ls docs/adr/                             # expect a new ADR superseding 0002
grep -l "0002" docs/adr/*.md
```

**Expected**: the new ADR exists, references ADR-0002 as superseded, states the rejected alternative (keep the hand-maintained port), and records the accepted cost — Codex configuration is no longer reproducible from this repository alone, and two guardrails are not available in Codex. ADR-0002 itself is unmodified (NFR-001).

## Done when

- [ ] Steps 1–3 pass mechanically
- [ ] Step 4 completed by a human, outcome dated in `research.md`
- [ ] Step 5 completed in a real Codex session, observations recorded
- [ ] Step 6 ADR present and accepted
