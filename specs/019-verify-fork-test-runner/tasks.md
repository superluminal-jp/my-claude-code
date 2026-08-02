# Tasks: Isolate high-volume verification output from the parent context

**Feature**: `019-verify-fork-test-runner` | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

Tests come first (TDD). `tests/run-verification-agent.sh` is already written and red — 2 passed, 29 failed — and is the gate for Phase 1.

## Phase 0 — Test (done)

- [x] **T001** Write `tests/run-verification-agent.sh` asserting the subagent's read-only tool allowlist, the skill's fork frontmatter, the preserved `allowed-tools` grants, the carried-over six checks, and that no document references the former command path. Confirm red.

## Phase 1 — Artifacts (Story 1 + Story 2)

- [x] **T002** Create `.claude/agents/verification-runner.md`. Frontmatter: `name`, `description`, `tools: Read, Grep, Glob, Bash`. Body states: run repository verification only, never modify files, report diffs without applying them, pre-check `command -v claude` and mark the three model-driven suites skipped when absent (D3), report failures without fixing them, return a compact checklist.
- [x] **T003** Create `.claude/skills/verify-config/SKILL.md` from `.claude/commands/verify-config.md`, adding `name`, `context: fork`, `background: false`, `agent: verification-runner`, `disable-model-invocation: true`, and carrying `description` and `allowed-tools` over verbatim. The six numbered checks and the `✓`/`✗` report format are unchanged (R7).
- [x] **T004** Delete `.claude/commands/verify-config.md`.
- [x] **T005** Run `bash tests/run-verification-agent.sh`. Everything except the stale-reference check must pass.

**Checkpoint**: `/verify-config` runs in isolation. Phases 2–3 are still required — the repository is not consistent yet.

## Phase 2 — Cross-agent parity

- [x] **T006** Retarget SYNC-09 in `tests/run-codex-sync.sh` (lines ~225–238) from `.claude/commands/verify-config.md` to `.claude/skills/verify-config/SKILL.md`, and update the section comment.
- [x] **T007** Update `.codex/prompts/verify-config.md` to point at the skill path. SYNC-09 greps for the literal string, and for a case-insensitive `do not modify` — both must survive.
- [x] **T008** Update `.codex/README.md`: retarget the `.claude/commands/verify-config.md` row to the skill path, add a row for `.claude/agents/verification-runner.md` (SYNC-08 requires the literal path; `.claude/skills/*` is exempt but `.claude/agents/*` is not), and correct the hardcoded "手書き 8 件" counts on the two `.claude/skills/*` rows.
- [x] **T009** Run `bash tests/run-codex-sync.sh`. SYNC-08 and SYNC-09 must pass.

## Phase 3 — Inventory and documentation (Story 3)

- [x] **T010** `README.md`: add the skill to the prose bullet (~L31–43) and the `skills/` tree (~L187–198); add a `.claude/agents/` tree entry; retarget the Codex command references (L75–76, L92, L168) to the skill path; point the `## Verification` section (L207–228) at `/verify-config`.
- [x] **T011** `README.ja.md`: mirror T010 — skills list (~L18–28), tree (~L80–88), and the `## 検証` section (~L91–101).
- [x] **T012** `.codex/AGENTS.md` L67: rewrite the sentence that says the compatibility prompt "should migrate to a skill if the Claude-side command is retired" — the Claude side is now a skill.
- [x] **T013** `install.sh` L210–212: correct the comment that calls `/verify-config` a command. Keep `sync_path "commands"` (L62) — with the source directory gone it is the uninstall path that clears the retired command from prior installs. Do **not** add `sync_path "agents"` (D4).

## Phase 4 — Verification

- [x] **T014** `bash tests/run-verification-agent.sh` — all green, including the stale-reference check.
- [x] **T015** `bash tests/run-codex-sync.sh`, `bash tests/run-speckit-update.sh`, `bash tests/run-destructive-command-guard.sh`, `bash tests/run-pre-edit-guard.sh`, `bash tests/run-post-edit-format-guard.sh`, `bash tests/run-prompt-secret-guard.sh`, `bash tests/run-digital-agency-frontend-skill.sh`, `bash tests/run-flow-metrics.sh` — no new failures.
- [ ] **T016** `shellcheck tests/run-verification-agent.sh` and `shfmt -d -i 2 tests/run-verification-agent.sh`. **Not run** — neither tool is installed in this environment (`command not found`). The new suite follows the formatting of the existing `tests/run-*.sh` scripts, but it has not been machine-verified; run this where the toolchain is present.
- [x] **T017** `git status` — only intended files changed (SC-005).

## Dependencies

T002 → T003 (the skill's `agent` field names the subagent) → T004 → T005. T006–T008 depend on T004. T010–T013 depend on T003. T014–T017 last.

T006, T007, T008 touch different files and can run together. T010, T011, T012, T013 likewise.

## Not doing

- `.agents/skills/verify-config` symlink and the `install.sh` `CUSTOM_SKILLS` entry. Codex's counterpart is `.codex/prompts/verify-config.md`, not a mirrored skill; adding a link would also require extending the hardcoded SYNC-02/SYNC-03 lists for no behavioural gain.
- `sync_path "agents"` (D4).
- Amending `specs/014-codex-config-port/contracts/sync-check.md`. It records what feature 014 delivered; the SYNC-09 amendment belongs to this feature and is recorded here.
- The three pre-existing drift items listed in plan.md § Out of scope.
