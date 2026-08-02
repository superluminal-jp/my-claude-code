# Implementation Plan: Isolate high-volume verification output from the parent context

**Branch**: `019-verify-fork-test-runner` | **Date**: 2026-08-02 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/019-verify-fork-test-runner/spec.md`

## Summary

Move the `/verify-config` procedure into a skill that forks into an isolated context, and introduce a read-only subagent that executes it and the `tests/run-*.sh` behaviour suites. The checks themselves are carried over unchanged; only their execution context moves. Because this repository mirrors `.claude/` into `.codex/` under enforced drift checks, the move is not a single-file rename — it touches the Codex mirror, the deployment map, the sync suite, and the inventory documents in the same change.

## Technical Context

**Language/Version**: Bash (POSIX-ish, `bash` shebangs), Markdown with YAML frontmatter. No compiled language.

**Primary Dependencies**: Claude Code v2.1.220 (present in this environment — `background` frontmatter requires ≥ 2.1.218, so the field is supported); `jq` (hard dependency of the sync suites); `shellcheck`, `shfmt`, `yamllint` (optional, skip-if-absent); `rg`.

**Storage**: N/A — configuration files in the working tree.

**Testing**: `tests/run-*.sh` behaviour suites, house pattern = `check "<name>" "<1|0>"` with PASS/FAIL counters and a `0`/`1` exit. New deterministic suite `tests/run-verification-agent.sh` (already written, currently red).

**Target Platform**: Developer workstations running Claude Code and/or Codex CLI, Linux and macOS.

**Project Type**: Agent-configuration repository — no application source.

**Performance Goals**: N/A. The relevant measure is context tokens returned to the main conversation (SC-001, SC-003), not runtime.

**Constraints**: The forked run has no access to conversation history and cannot use `AskUserQuestion`; the skill body must therefore be self-sufficient. Drift checks SYNC-08 and SYNC-09 in `tests/run-codex-sync.sh` constrain where new files may live.

**Scale/Scope**: 2 new artifacts, 1 file moved, 1 new test suite, ~8 documents updated.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` is the unmodified Spec Kit template — every principle is still a `[PRINCIPLE_N_NAME]` placeholder. **No project-specific constitutional gate applies.** The governing rules for this change are instead `.claude/CLAUDE.md` and `.claude/rules/`:

| Gate | Source | Status |
|---|---|---|
| Failing test before implementation | `coder` skill (TDD) | ✅ `tests/run-verification-agent.sh` written first, 2 passed / 29 failed |
| Spec is the source of truth for what/why | `coder` skill (SDD) | ✅ `spec.md` written before the plan |
| Docs updated in the same change | `rules/live-documentation.md` §1 | Planned — Phase 3 is not optional |
| Documentation placed closest to what it describes | `rules/live-documentation.md` §4 | ✅ skill body co-located in `.claude/skills/verify-config/`; no new top-level `docs/` page |
| No redundant documentation | `rules/live-documentation.md` §5 | ✅ existing README "Verification" sections are updated in place, not duplicated |
| One-way-door decisions recorded | `adr` skill | Assessed in Phase 2 below |

**Post-design re-check**: see [§ Constitution re-check](#constitution-re-check).

## Project Structure

### Documentation (this feature)

```text
specs/019-verify-fork-test-runner/
├── spec.md              # Feature specification (written)
├── research.md          # Phase 0: mechanism decisions R1–R7 (written)
├── plan.md              # This file
└── tasks.md             # Phase 2 output
```

No `data-model.md` or `contracts/` — this feature introduces no data entities and no new inter-component contract beyond the SYNC-09 amendment, which is recorded in the existing contract file it already lives in.

### Source (repository root)

```text
.claude/
├── agents/                          # NEW directory
│   └── verification-runner.md       # NEW read-only subagent (Story 1 + Story 2)
├── skills/
│   └── verify-config/
│       └── SKILL.md                 # MOVED from .claude/commands/verify-config.md
└── commands/                        # emptied by the move

.codex/
├── prompts/verify-config.md         # path reference updated
├── README.md                        # deployment-map rows: skill path + new agents/ row
└── AGENTS.md                        # migration sentence resolved

tests/
├── run-verification-agent.sh        # NEW deterministic suite (written, red)
└── run-codex-sync.sh                # SYNC-09 retargeted to the skill path

README.md, README.ja.md              # inventory + Verification sections
install.sh                           # stale comment + retained commands sync
```

`.claude/CLAUDE.md` is **not** touched: its skill list drives mandatory
auto-routing, and `verify-config` carries `disable-model-invocation: true` so it
stays operator-invoked, exactly as the command it replaces was. Listing it there
would advertise routing that does not exist.

`specs/014-codex-config-port/contracts/sync-check.md` is **not** amended: it
records what feature 014 delivered. The SYNC-09 change belongs to this feature
and is recorded here.

**Structure Decision**: The skill lands at `.claude/skills/verify-config/SKILL.md` — the documented home for `context: fork` (research R2) and, conveniently, a path that SYNC-08 already exempts via its literal `.claude/skills/*` token. The subagent lands at `.claude/agents/verification-runner.md`, the documented project-scope location for subagent definitions. SYNC-08 walks `find .claude -type f` and requires every path to appear in `.codex/README.md`, so the new `agents/` file **requires a deployment-map row** or the sync suite fails.

## Key design decisions

### D1. One subagent serves both user stories

`verification-runner` executes the forked configuration check (Story 1) and receives delegated behaviour-suite runs (Story 2). Both need the same capability envelope: run repository scripts, read files, modify nothing. A second definition would duplicate that envelope for no gain (`rules/live-documentation.md` §5).

### D2. Read-only enforced by the tool allowlist, not by instruction

`tools: Read, Grep, Glob, Bash`. FR-003 and FR-007 become properties of the execution environment. Residual risk recorded in research R4: `Bash` can still write via redirection, so the instruction to report diffs only remains, with `pre-bash.sh` as the backstop.

### D3. The subagent owns the `claude`-CLI skip logic

Newly discovered constraint: `tests/run-skill-routing.sh`, `run-live-documentation.sh`, and `run-type-safety-coder.sh` all hard-`exit 1` when `claude` is absent — identical guard, indistinguishable from a real failure. The existing `/verify-config` body already promises "if `claude` is absent, skip with a note rather than failing", so today that promise is unbacked. The subagent must pre-check `command -v claude` and classify those three suites as skipped. This satisfies FR-006 and closes a latent defect rather than introducing one.

### D4. `.claude/agents/` is **not** added to `install.sh`

`install.sh` deploys user-scope defaults via `sync_path`. `verification-runner` verifies *this repository's* configuration — its steps are meaningless in another project. Leaving it project-scope is the least-privilege choice. `sync_path "commands"` stays as-is: it is a no-op against an empty directory and removing it is unrelated cleanup.

### D5. No ADR

Assessed against the `adr` skill's three-part test. Architecturally significant: marginal. Hard to reverse: **no** — reverting is a file move plus a SYNC-09 edit. Reasonable alternative rejected: yes (research R1–R4). Two of three fail, so the decision record belongs in `research.md`, which is where it is. ADR-0002 (`docs/adr/0002-deploy-codex-configuration-at-user-scope.md`) already governs the user-scope deployment question that D4 defers to.

## Phasing

- **Phase 1 — Artifacts.** Create the subagent, move the skill. Turns the bulk of `tests/run-verification-agent.sh` green.
- **Phase 2 — Cross-agent parity.** SYNC-09 retarget, `.codex/prompts/verify-config.md` path, `.codex/README.md` rows, the normative contract text. Keeps `tests/run-codex-sync.sh` green.
- **Phase 3 — Inventory and documentation.** READMEs, `.claude/CLAUDE.md`, `.codex/AGENTS.md`, `install.sh` comment. Satisfies Story 3 and `rules/live-documentation.md` §1.
- **Phase 4 — Verification.** Full suite run; confirm the working tree is clean (SC-005).

Phases 2 and 3 are not optional follow-ups: a change that lands Phase 1 alone leaves `tests/run-codex-sync.sh` failing and the inventory documents pointing at a deleted path.

## Constitution re-check

Re-checked after the design above. No new gate triggered; D5 records the ADR assessment and its outcome. Documentation is co-located and updated in the same change, so `rules/live-documentation.md` §§1–5 pass by construction rather than by exception.

## Complexity Tracking

> Fill ONLY if Constitution Check has violations that must be justified

No violations. The constitution is an unfilled template and no `.claude/rules/` gate is being deviated from.

## Out of scope — pre-existing drift found while planning

Flagged rather than fixed, per the `coder` skill's instruction not to make unrelated changes:

1. `README.ja.md` § 検証 omits the `tests/run-flow-metrics.sh` block that `README.md` § Verification has.
2. `.codex/rules/guardrails.rules` enumerates the suites individually but omits `tests/run-flow-metrics.sh`.
3. Both READMEs' verification sections list 5 of the 11 suites and never mention `/verify-config`. This change adds the pointer to the entry point but does not re-scope those lists.
