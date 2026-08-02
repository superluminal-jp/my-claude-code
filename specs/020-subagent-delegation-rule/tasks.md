# Tasks: A grounded rule for when to delegate work to a subagent

**Feature**: `020-subagent-delegation-rule` | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

Tests first (TDD).

## Phase 1 — Test

- [x] **T001** Write `tests/run-subagent-delegation.sh` asserting: the rule file exists; it carries the house `Purpose:` opening and a `## References` section; it states both delegate-when and stay-inline conditions; it names the missing capabilities (no conversation history, cannot ask the operator); it warns that returned results cost context; it covers both delegation mechanisms; it cites both documentation pages with dates; `.claude/CLAUDE.md` imports it; the § Execution section points at it rather than restating it; and `.codex/README.md` carries the SYNC-08 row. Confirm red.

## Phase 2 — The rule

- [x] **T002** Write `.claude/rules/subagent-delegation.md`. Decision criteria only (D1), every behavioural claim traceable to research R3's table, size in line with `skill-routing.md`/`clarifier.md`.
- [x] **T003** Add `@.claude/rules/subagent-delegation.md` to `.claude/CLAUDE.md`.
- [x] **T004** Narrow `.claude/CLAUDE.md` § "Execution: parallelize whenever valid" so it owns *how* to issue independent calls and defers *whether to delegate* to the new rule (D2, FR-008).
- [x] **T005** Run `bash tests/run-subagent-delegation.sh`. Only the deployment-map assertion may still fail.

## Phase 3 — Parity and inventory

- [x] **T006** Add the `.claude/rules/subagent-delegation.md` row to `.codex/README.md` as `対象外` with the stated reason (D4, SYNC-08 requires the literal path).
- [x] **T007** `README.md`: add the rule to the `.claude/rules/` bullet and to the `rules/` tree block.
- [x] **T008** `README.ja.md`: mirror T007.

## Phase 4 — Verification

- [x] **T009** `bash tests/run-subagent-delegation.sh` — all green.
- [x] **T010** `bash tests/run-codex-sync.sh` — SYNC-08 passes; no regression.
- [x] **T011** Remaining suites: `run-verification-agent.sh`, `run-codex-sync-drift.sh`, `run-speckit-update.sh`, `run-destructive-command-guard.sh`, `run-pre-edit-guard.sh`, `run-post-edit-format-guard.sh`, `run-prompt-secret-guard.sh`, `run-digital-agency-frontend-skill.sh`, `run-flow-metrics.sh` — no new failures.
- [x] **T012** Verify every `@`-import in `.claude/CLAUDE.md` resolves (the check `/verify-config` step 2 performs).
- [x] **T013** `git status` — only intended files changed.

## Dependencies

T001 → T002 → T003, T004 → T005. T006 depends on T002 (the path must exist). T007, T008 depend on T002. T009–T013 last.

T003 and T004 touch the same file; do them in sequence. T006, T007, T008 are independent of each other.

## Not doing

- Encoding version-gated specifics — research R3.
- A Codex counterpart to the rule — Codex has no subagent mechanism (D4).
- Any change to the `coder` skill or to skill routing; delegation is orthogonal to which skill loads.

## Verification record

All suites green: `run-subagent-delegation.sh` 25, `run-verification-agent.sh` 31, `run-codex-sync.sh` 9 (5 skipped — undeployed `~` paths), `run-codex-sync-drift.sh` 9, `run-speckit-update.sh` 6, `run-destructive-command-guard.sh` 23, `run-pre-edit-guard.sh` 10, `run-post-edit-format-guard.sh` 3, `run-prompt-secret-guard.sh` 15, `run-digital-agency-frontend-skill.sh` 52, `run-flow-metrics.sh` OK. All six `@`-imports resolve. Rule size 4,494 bytes — in line with `clarifier.md` (4,589), as plan.md required.

**Not run**: `shellcheck` / `shfmt` on `tests/run-subagent-delegation.sh` — neither tool is installed in this environment, the same gap recorded for feature 019 T016. The script matches the formatting of the existing suites but has not been machine-verified.
