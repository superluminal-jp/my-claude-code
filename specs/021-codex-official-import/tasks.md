---
description: Task list for feature 021-codex-official-import
---

# Tasks: Replace the hand-maintained Codex port with OpenAI's official import path

**Input**: Design documents from `/specs/021-codex-official-import/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/](./contracts/)

**Tests**: One test is included because a contract requires it (`contracts/removal-manifest.md` RULE-01…RULE-10, SC-002), not as blanket TDD. It is written before the deletions so it starts red and turns green when the removal is complete.

**Organization**: Grouped by user story. US1 and US2 are both P1 and touch different concerns of the same files; US3 executes the deletions and must come last.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: parallelizable — different file, no dependency on an incomplete task
- **[US#]**: the user story from `spec.md` this task serves

## Path Conventions

Repository root is `/Users/taikiogihara/work/my-claude-code`. All paths below are repo-relative.

---

## Phase 1: Setup

**Purpose**: Establish preconditions and a baseline to compare against.

- [X] T001 Confirm the working tree is clean and the branch is `021-codex-official-import`; abort if `git status --porcelain` shows anything outside `specs/021-codex-official-import/`
- [X] T002 [P] Record the pre-change baseline in `specs/021-codex-official-import/research.md` § R-01: output of `git ls-files .agents .codex`, `ls ~/.codex/hooks ~/.agents/skills`, and the marker-block line numbers in `~/.codex/config.toml`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Record the decision and preserve content **before** anything is deleted. Skipping T004 destroys the only copy of the flattened Codex instructions.

**⚠️ CRITICAL**: No user story work begins until this phase is complete.

- [X] T003 Create `docs/adr/0004-adopt-official-codex-import.md` (MADR format, via the `adr` skill) superseding ADR-0002: context = the maintenance cost of the hand port and the availability of official tooling; decision = delete the port, document a developer-run procedure; rejected alternative = keep the port; consequences = Codex configuration is no longer reproducible from this repo alone, and edit protection plus the allow/prompt policy are unavailable in Codex. Mark `docs/adr/0002-deploy-codex-configuration-at-user-scope.md` as superseded **by adding a status line only** — do not rewrite its body (NFR-001)
- [X] T004 Relocate the flattened instructions: copy the body of `.codex/AGENTS.md` into the repo-root `AGENTS.md`, replacing its current one-sentence pointer. Strip any line beginning with `@`, keep the result between 1 KiB and 32 KiB, and retain the skill-routing and clarification guidance (`data-model.md` § Relocated)
- [X] T005 [P] Add `.codex/` and `.agents/` to `.gitignore` under a comment explaining they are now generated locally by the official tooling (FR-005, RULE-06)
- [X] T006 [P] Create `tests/run-codex-references.sh` implementing RULE-01…RULE-10 from `contracts/removal-manifest.md`, following the existing `tests/run-*.sh` conventions (named check ids, green/red output, non-zero exit on failure, `specs/**` and `docs/adr/**` excluded from RULE-01/02 only — RULE-07's host allowlist applies repo-wide). Run it and confirm it **fails** at this point — the deletion set still exists

**Checkpoint**: The decision is recorded, the instructions are safe at the root, and a failing test defines "done".

---

## Phase 3: User Story 1 — Codex set up from this repo without a hand-maintained port (Priority: P1) 🎯 MVP

**Goal**: A developer can set up Codex by following documented official procedure, with no repo-owned Codex artifact involved.

**Independent Test**: On a fresh clone, follow `README.md` § "Codex CLI support" end to end; Codex sees the repo's skills and instructions, and `git status` stays clean.

- [X] T007 [US1] Rewrite `README.md` § "Codex CLI support" to satisfy assertions A1–A5, B1–B2, D1–D4 and E1–E4 of `contracts/codex-setup-procedure.md`: both entry points, how each is obtained, `/import`'s unavailability contexts, read-only inspection order, generated-and-ignored artifacts, root `AGENTS.md` as the instruction path, the `@`-non-expansion warning, the `AGENTS.md` symlink hazard with its `git checkout AGENTS.md` recovery, and the skills-arrive-as-copies caveat
- [X] T008 [P] [US1] Apply the same rewrite to the Codex section of `README.ja.md`, matching `README.md` in substance
- [X] T009 [US1] Remove the Codex half of `install.sh`: all deployment of `.codex/AGENTS.md`, `.codex/hooks/*`, `.codex/rules/*`, `.codex/prompts/*`, `~/.agents/skills/` symlinks, and both managed marker blocks in `~/.codex/config.toml`. Leave the Claude-side path (`~/.claude` sync, Claude MCP registration) untouched
- [X] T010 [US1] Update the `install.sh` header comment to state that Codex configuration is produced by the developer via the documented procedure, not by this installer
- [X] T011 [US1] Add `contracts/codex-setup-procedure.md` § F (cleanup for existing installs) to both READMEs: what the previous installer left under `~/.codex` and `~/.agents`, and that the new installer does not remove it
- [X] T012 [US1] Verify `quickstart.md` Step 3 passes: root `AGENTS.md` is a regular file, 1 KiB–32 KiB, no `^@` lines, names skill routing

**Checkpoint**: The documented path is complete and the installer no longer deploys Codex artifacts, even though the old files still exist on disk.

---

## Phase 4: User Story 2 — Runtime guardrails are honestly documented (Priority: P1)

**Goal**: What Codex does and does not enforce is written down, and the Claude side is provably unchanged.

**Independent Test**: Read the coverage table in `README.md`; every row matches what `research.md` § R-03 measured. `git diff main -- .claude scripts/guardrails` is empty.

- [X] T013 [US2] Add the guardrail coverage table (contract § C, assertions **C1–C6**) to `README.md`: destructive-command blocking and prompt secret scanning **available** in Codex — both measured working — with the `/hooks` trust step as their only precondition; edit protection, post-edit formatting, allow/prompt policy and Spec Kit prompt expansion **not available**, each with its reason; plus C5 (hooks registered in several config layers fire once per layer) and C6 (copied-but-unregistered hook scripts are not evidence of coverage). **Do not document `[features].codex_hooks`** — that flag does not exist in Codex 0.147.0 (contract C1)
- [X] T014 [P] [US2] Add the equivalent table to `README.ja.md`
- [X] T015 [US2] State in both READMEs that the Claude-side guardrails are unaffected by this change (C3), naming `.claude/hooks/pre-edit.sh` and `.claude/settings.json#permissions` as retained
- [X] T016 [US2] Verify NFR-002 and NFR-003 mechanically: `git diff --stat main -- .claude scripts/guardrails` must print nothing, and all four `scripts/guardrails/*.sh` must still exist and be executable. If either check fails, stop and fix before continuing
- [X] T017 [US2] Run `tests/run-pre-edit-guard.sh`, `tests/run-destructive-command-guard.sh`, `tests/run-post-edit-format-guard.sh`, `tests/run-prompt-secret-guard.sh`; all must pass

**Checkpoint**: Coverage is documented and the Claude-side promise is proven, not asserted.

---

## Phase 5: User Story 3 — Nothing in the repo points at removed files (Priority: P2)

**Goal**: The deletion set is gone and the repository is internally consistent.

**Independent Test**: `tests/run-codex-references.sh` exits 0 and `git ls-files .agents .codex` prints nothing.

**⚠️ Destructive**: T018–T020 delete tracked files. Confirm with the operator before executing (`rules/permissions.md`).

- [X] T018 [US3] Delete the 8 tracked symlinks under `.agents/skills/` (`adr`, `clarifier`, `coder`, `digital-agency-frontend`, `minto-builder`, `minto-reviewer`, `minto-rewriter`, `scrum-master`) per `contracts/removal-manifest.md`
- [X] T019 [US3] Delete the `.codex/` tree: `AGENTS.md`, `README.md`, `hooks/*.sh` (4), `rules/guardrails.rules`, `prompts/verify-config.md`. Confirm T004 already copied the instructions to the root `AGENTS.md` before running this
- [X] T020 [US3] Delete `tests/run-codex-sync.sh` and `tests/run-codex-sync-drift.sh`
- [X] T021 [US3] Run `tests/run-codex-references.sh`; it must now exit 0 with every rule green
- [X] T022 [US3] Sweep manually for stragglers the test may not cover: `grep -rn "\.codex/\|\.agents/\|SYNC-[0-9]" --exclude-dir=specs --exclude-dir=docs --exclude-dir=.git .` — every remaining hit must be the new procedure documentation

**Checkpoint**: All three user stories are complete and independently verifiable.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T023 Run every suite: `for t in tests/run-*.sh; do "$t" || echo "FAILED: $t"; done` — all must pass (SC-003)
- [X] T024 [P] Lint the new test: `shellcheck tests/run-codex-references.sh` and `shfmt -d tests/run-codex-references.sh`
- [X] T025 [P] Update `README.md` and `README.ja.md` file-structure sections and the deployment-map link so they describe the post-removal tree (the `.codex/README.md` link is now dead)
- [ ] T026 Execute `quickstart.md` Step 4 by hand — converter **read-only modes only**, then the real setup via `/import` — confirming `git status` stays clean and `AGENTS.md` is not symlinked. Record the dated outcome in `research.md` § SC-001 confirmation
- [ ] T027 Close the one remaining empirical gap (SC-004): in an interactive Codex session run `/hooks`, trust the imported entries, then repeat a deny test **without** `--dangerously-bypass-hook-trust`, proving the ordinary trust flow arms the hooks. The deny behaviour itself and the dead edit-protection matchers are already measured (`research.md` § R-09) and need no re-run
- [X] T028 Confirm `docs/adr/0002-*` body is unmodified apart from the superseded status line, and that no file under `specs/012-*`, `specs/013-*` or `specs/014-*` was touched (NFR-001)
- [X] T029 Sweep `README.md`, `README.ja.md` and `AGENTS.md` and stamp every behavioural claim about Codex or the converter with the version and date it was measured, e.g. "measured on Codex 0.147.0, 2026-08-10" (FR-015a, contract G1). Add the note that the converter's `references/differences.md` is secondary to a live measurement (G2), and the revalidation trigger (G4)
- [X] T030 [P] Create `tests/run-codex-drift.sh` implementing `DRIFT-01`…`DRIFT-06` from `contracts/codex-setup-procedure.md` § G3. It MUST **SKIP with a yellow warning** when `codex` is not on `PATH`, following `tests/run-codex-sync.sh`'s existing SKIP convention, and MUST NOT fail merely because the environment lacks Codex. Record the reference version (0.147.0) inside the script so `DRIFT-01` has a baseline

---

## Unplanned work discovered during implementation (2026-08-10)

Recorded rather than absorbed silently — the plan did not anticipate it.

- [X] T031 Six behaviour suites asserted against the deleted Codex adapters and the retired deployment map, and broke the moment T018–T020 ran. `run-{pre-edit,destructive-command,post-edit-format,prompt-secret}-guard.sh` lost their "Part 3: Codex CLI adapter" blocks (each replaced by a comment explaining why, and pointing at `research.md` § R-09 where the same behaviour is now verified in a live Codex session). `run-digital-agency-frontend-skill.sh` lost `SYNC-SKILL-01/02/03/04/07/10` and had `SYNC-SKILL-06` repointed at the root `AGENTS.md`. `run-subagent-delegation.sh` had its deployment-map assertion repointed likewise
- [X] T032 Three `contracts/removal-manifest.md` rules needed carve-outs that only surfaced against real files, each documented in the contract: `RULE-01` exempts `.agents/skills/<name>` (deleted as symlinks, regenerated by `/import`), `~/`-prefixed paths (home-cleanup instructions), shell comments, and `.claude/**` (NFR-002 forbids editing it here); `RULE-07` became a host allowlist rather than a banned-string grep; `RULE-10` exempts comment lines

**Known residue, deliberately left**: `.claude/settings.json` still allow-lists `Bash(.codex/hooks/*.sh)`, and two `.claude/hooks/` files carry comments naming the retired adapters. Removing them would violate NFR-002, which the operator reaffirmed on 2026-08-10. They are inert — the paths no longer exist — and cleaning them up belongs to a separate Claude-side change.

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup)
   └─> Phase 2 (Foundational)   ← T004 MUST precede T019
          ├─> Phase 3 (US1)
          ├─> Phase 4 (US2)     ← independent of US1
          └─> Phase 5 (US3)     ← depends on US1 + US2 docs being rewritten first,
                                   otherwise deleting files creates dangling refs
                 └─> Phase 6 (Polish)
```

### User Story Dependencies

- **US1** — depends only on Foundational. Deliverable on its own.
- **US2** — depends only on Foundational. **Independent of US1**; can be done first or in parallel.
- **US3** — depends on US1 and US2, because their rewrites are what remove the references that RULE-01 checks for.

### Within Each Story

Documentation tasks precede verification tasks. `README.md` and `README.ja.md` are separate files and always parallelizable with each other.

### Parallel Opportunities

- T005 and T006 (Foundational): different files, no shared state
- T007 ‖ T008, T013 ‖ T014 (English and Japanese READMEs)
- US1 and US2 phases entirely, if two people are working
- T024 ‖ T025 (Polish)

## Parallel Example: User Story 1

```bash
# T007 and T008 edit different files and can run together:
#   T007 → README.md      § Codex CLI support
#   T008 → README.ja.md   § Codex セクション
# T009/T010 must wait: both edit install.sh.
```

## Implementation Strategy

**MVP = Phase 1 + Phase 2 + Phase 3 (US1).** At that point the official procedure is documented and the installer no longer deploys Codex artifacts — the feature is usable, with the old files still present but inert.

**Increment 2** = Phase 4 (US2): honest guardrail documentation. Ship-able independently.

**Increment 3** = Phase 5 (US3): the irreversible deletions. Deliberately last, so the removal happens only after everything that replaces it is verified in place.

**Stop condition**: if T027 finds that the `/hooks` trust flow does not arm the hooks, do not paper over it — the two "available" rows of the C table become unreachable for an ordinary developer, and the FR-006 decision must be reopened with the operator, per `research.md` § Inventory rows 2–3.
