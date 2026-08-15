# Tasks: Remove scripts/ Entirely

**Input**: Design documents from `/specs/027-remove-scripts/`

**Delegation**: Direct execution — exact content already drafted in research.md.

## Phase 3: User Story 1 - No dangling references (Priority: P1) 🎯 MVP

- [X] T001 [US1] Delete `scripts/` entirely (guardrails/ 4 files + check-mcp-consistency.sh)
- [X] T002 [US1] Delete the 4 guardrail test suites (`tests/run-{destructive-command,pre-edit,post-edit-format,prompt-secret}-guard.sh`)
- [X] T003 [US1] Edit `install.sh`: replace conditional guardrails sync with unconditional cleanup (research.md R2)
- [X] T004 [US1] Edit `README.md`: 5 locations (research.md R1)
- [X] T005 [US1] Edit `README.ja.md`: 3 locations (research.md R1)
- [X] T006 [US1] Edit `.claude/rules/permissions.md`: 1 location
- [X] T007 [US1] Edit `.claude/rules/mcp.md`: 1 location
- [X] T008 [US1] Run grep validation (quickstart.md step 2)

## Phase 4: User Story 2 - Decision recorded as its own ADR (Priority: P2)

- [X] T009 [US2] Run every remaining `tests/run-*.sh` suite and confirm all pass
  - User-approved exception: 5 suites passed; the 3 suites that require an
    authenticated Claude CLI were treated as skipped after returning
    `Not logged in`.
- [X] T010 [US2] Draft `docs/adr/0007-remove-scripts.md` via the `adr` skill; confirm ADR-0005/0006 unchanged

## Phase 5: User Story 3 - Installer reflects the managed repository state (Priority: P1)

**Goal**: Make `install.sh` synchronize the declared managed paths exactly,
including `agents/`, while preserving unrelated user files.

**Independent Test**: `bash tests/run-install.sh` passes with an isolated home,
stubbed external commands, seeded stale managed paths, and unrelated user files.

- [X] T011 [US3] Add the failing isolated-home installer contract in `tests/run-install.sh` for FR-012/FR-013 and verify it fails before implementation
- [X] T012 [US3] Refactor the declared managed-path sync, `agents/` handling, generated-skill cleanup, preflight dependencies, and retired-path cleanup in `install.sh` until T011 passes

## Phase 6: User Story 4 - Remaining tests are locally runnable and current (Priority: P1)

**Goal**: Retain only actionable suites with active subjects and no Claude CLI
authentication dependency.

**Independent Test**: No retained `tests/run-*.sh` invokes `claude -p`, every
fixture directory has a retained runner and subject, and every retained suite
runs in its documented environment.

- [X] T013 [P] [US4] Delete `tests/run-live-documentation.sh`, `tests/run-skill-routing.sh`, `tests/run-type-safety-coder.sh`, and their `tests/{live-documentation,skill-routing,type-safety-coder}/` fixtures
- [X] T014 [P] [US4] Delete the orphaned `tests/ubiquitous-language/` fixture directory
- [X] T015 [US4] Update live-surface discovery and remove retired RULE-09 and nonexistent `scripts/` handling in `tests/run-codex-references.sh`

## Phase 7: User Story 5 - draw.io MCP is not configured (Priority: P1)

**Goal**: Remove every live definition and routing surface for the draw.io
capability.

**Independent Test**: The quickstart live search finds no draw.io MCP, skill,
routing, plugin, package, or installer reference outside historical specs and
ADRs.

- [X] T016 [P] [US5] Remove the draw.io server entry from `.mcp.json`
- [X] T017 [P] [US5] Delete the `.claude/skills/drawio/` skill directory
- [X] T018 [P] [US5] Remove the draw.io catalog row, examples, and exemption from `.claude/rules/mcp.md`
- [X] T019 [P] [US5] Remove draw.io composition routing from `.claude/rules/skill-routing.md`
- [X] T020 [P] [US5] Remove the draw.io related-rule pointer from `.claude/skills/coder/SKILL.md`
- [X] T021 [US5] Run the draw.io absence validation in `specs/027-remove-scripts/quickstart.md` step 4

## Phase 8: Polish and cross-cutting validation

- [X] T022 Update installer ownership, dependency, and test inventory documentation in `README.md` and `README.ja.md`, removing retired-capability references
- [X] T023 Run `shfmt`, `shellcheck`, JSON syntax checks, and `git diff --check` for `install.sh`, `tests/run-*.sh`, `.mcp.json`, and `.claude/settings.json`
- [X] T024 Run every remaining `tests/run-*.sh` suite and confirm all pass
- [X] T025 Run every validation scenario in `specs/027-remove-scripts/quickstart.md` and confirm ADR-0005/0006 remain unchanged

## Dependencies and execution order

- T011 must fail before T012 changes `install.sh`; T012 completes US3.
- T013-T015 (US4) and T016-T021 (US5) touch disjoint files and can proceed
  independently after the clarified spec and plan.
- T022 follows US3-US5 so documentation describes the final behavior.
- T023-T025 are the final quality gates and run after all implementation tasks.

## Implementation strategy

1. Complete US3 test-first so installer behavior has a deterministic contract.
2. Remove obsolete test assets (US4) and draw.io capability surfaces (US5).
3. Synchronize English/Japanese documentation.
4. Run formatting, lint, all retained suites, and the complete quickstart.

## Notes

Commit only when asked.
