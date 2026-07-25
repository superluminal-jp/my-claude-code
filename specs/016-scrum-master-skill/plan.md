# Implementation Plan: Integrate the `scrum-master` skill into the shared skill set

**Branch**: `016-scrum-master-skill` | **Date**: 2026-07-25 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/016-scrum-master-skill/spec.md`

## Summary

Vendor the `scrum-master` skill (playbook, nine reference documents, one Python helper) from `/Users/taikiogihara/work/scrum-master-skill/scrum-master/` into `.claude/skills/scrum-master/`, and wire it into the four systems that make a skill a first-class member of this repository's set: routing (three guidance files), distribution (`install.sh` plus the `.agents/` mirror), documentation (three READMEs), and regression coverage (two suites).

The technical approach is almost entirely additive — the repository's existing mechanisms already handle nested skill directories. Research surfaced one substantive correction: the source skill's `allowed-tools: Bash(python3 ${CLAUDE_SKILL_DIR}/...)` declaration is inert under Claude Code's actual skill semantics and its path variable does not exist, so the narrowly-scoped permission moves to `.claude/settings.json` — the mechanism this repository already uses for exactly that purpose — and the playbook's invocation example is corrected to a resolvable path.

## Technical Context

**Language/Version**: Bash (installer, test harnesses, guardrails); Markdown (skills, rules, docs); JSON (`settings.json`); Python 3 for the vendored helper only (verified 3.14.3 locally, `#!/usr/bin/env python3`, stdlib-only)

**Primary Dependencies**: Claude Code CLI (skill discovery, `settings.json` permissions), Codex CLI (`~/.agents/skills` discovery), `jq` (required by the installer and suites), `git`

**Storage**: Files in the repository tree; no database, no state

**Testing**: `tests/run-skill-routing.sh` (needs a live `claude` CLI; routing behaviour), `tests/run-codex-sync.sh` (deterministic where repo-only, SKIPs post-install checks when `~/.codex` is absent), plus the other `tests/run-*.sh` suites as a regression gate

**Target Platform**: Developer machines running macOS/Linux with Claude Code and optionally Codex CLI

**Project Type**: Agent configuration repository — the deliverable is configuration and documentation, not an application

**Performance Goals**: Not applicable. The one budget that exists is a size constraint, not a speed one: `.codex/AGENTS.md` must stay under 32 KiB (SYNC-03), with a warning above 28 KiB.

**Constraints**:
- Least privilege — any new permission must be scoped to the single script (`permissions.md`; FR-015)
- Additive only — no existing routing decision or suite result may change (FR-008, FR-020)
- No synchronisation machinery back to the external source directory (FR-022)
- Documentation moves in the same change as the thing it describes (`live-documentation.md`)

**Scale/Scope**: 11 files vendored, 10 existing files edited, 1 file created, 1 symlink added

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` is the **unmodified Spec Kit template** — every principle is still a `[PRINCIPLE_N_NAME]` placeholder. There are no ratified project gates to evaluate against, so no constitutional gate can pass or fail.

In its place, the governing constraints for this repository are its own always-on rules, which this plan is checked against:

| Rule | Gate | Status |
|---|---|---|
| `permissions.md` — least privilege, fail-safe defaults | Any new permission scoped to one script, no broadening | **PASS** — two anchored `Bash(python3 …/flow_metrics.py *)` entries; R0 explicitly rejects `Bash(python3 *)` |
| `permissions.md` — no credential exposure | No secret-adjacent paths touched | **PASS** — no such files in scope |
| `live-documentation.md` § 1 Drift | Public contract changes carry their docs in the same change | **PASS** — the skill inventory is the contract; all six documentation touchpoints (R6) are in this change, not a follow-up |
| `live-documentation.md` § 2 Separate-doc-PR | Not a docs-only change trailing shipped code | **PASS** — docs ship with the skill |
| `live-documentation.md` § 3 Auto-generation | Prefer generated over hand-written docs | **PASS** — no generator exists for skill inventories here; hand-written is the only path, so § 4 applies instead |
| `live-documentation.md` § 4 Proximity | Docs as close to the subject as possible | **PASS** — the skill documents itself in its own `SKILL.md`; the README/AGENTS entries are inventory pointers, which is what those files are for |
| `live-documentation.md` § 5 No Redundancy | Do not duplicate existing information | **PASS** — each of the six touchpoints states the skill in a different register (routing, deployment mapping, human inventory); the playbook content is not copied into any of them |
| `git-workflow.md` | Conventional Commits, one logical change, short-lived branch | **PASS** — single feature branch `016-scrum-master-skill` |
| `.claude/CLAUDE.md` — Spec Kit for non-trivial work | Multi-file behaviour-changing work planned through Spec Kit | **PASS** — this is that process |

**Post-Phase-1 re-check**: still **PASS**. The Phase 1 design added no new permission surface, no new dependency, and no new distribution channel beyond what Phase 0 settled. The one design decision with any weight — moving the tool permission from skill frontmatter to `settings.json` — strengthens the `permissions.md` posture rather than weakening it, because it relocates the scope declaration from a field with no enforced semantics to the file that is actually enforced.

**Complexity Tracking**: not required — no gate violations to justify.

## Project Structure

### Documentation (this feature)

```text
specs/016-scrum-master-skill/
├── plan.md              # This file
├── research.md          # Phase 0 output — R0..R8
├── data-model.md        # Phase 1 output — entities and invariants
├── quickstart.md        # Phase 1 output — validation guide
├── contracts/
│   └── skill-integration.md   # Phase 1 output — the contract a skill must satisfy
├── checklists/
│   └── requirements.md  # Spec quality checklist (from /speckit-specify)
├── spec.md              # Feature specification
└── tasks.md             # Phase 2 output (/speckit-tasks — NOT created here)
```

### Source Code (repository root)

```text
my-claude-code/
├── .claude/
│   ├── CLAUDE.md                      # EDIT — add to mandatory-routing list (FR-007)
│   ├── settings.json                  # EDIT — scoped Bash permission for the helper (FR-014/015)
│   ├── rules/
│   │   └── skill-routing.md           # EDIT — Scrum category + non-Scrum boundary (FR-006/007a)
│   └── skills/
│       └── scrum-master/              # NEW — vendored payload (FR-001)
│           ├── SKILL.md               #   frontmatter minus allowed-tools (R0); body path fixed (R1)
│           ├── references/            #   9 files, verbatim
│           │   ├── scrum-framework.md
│           │   ├── scrum-master-role.md
│           │   ├── event-playbooks.md
│           │   ├── facilitation-and-coaching.md
│           │   ├── measurement-and-diagnostics.md
│           │   ├── scaling-frameworks.md
│           │   ├── anti-patterns-and-coaching.md
│           │   ├── solo-practice.md
│           │   └── sources.md
│           └── scripts/
│               └── flow_metrics.py    #   verbatim, executable bit preserved
├── .agents/
│   └── skills/
│       └── scrum-master -> ../../.claude/skills/scrum-master   # NEW symlink (FR-011, SYNC-01)
├── .codex/
│   ├── AGENTS.md                      # EDIT — routing bullet (FR-009, SYNC-03)
│   └── README.md                      # EDIT — deployment map counts 6 → 7
├── install.sh                         # EDIT — CUSTOM_SKILLS gains scrum-master (FR-011)
├── README.md                          # EDIT — inventory, deployment table, tree (FR-017/018)
├── README.ja.md                       # EDIT — same three shapes; count 6 → 7 (FR-017/018)
└── tests/
    ├── run-codex-sync.sh              # EDIT — SYNC-03 skill list (FR-009 enforcement)
    ├── run-skill-routing.sh           # EDIT — inline rule list + output enum (R3, FR-019)
    └── skill-routing/
        └── 007-scrum-facilitation.md  # NEW — routing regression case (FR-019)
```

**Structure Decision**: This repository has no `src/` — its "source" is the `.claude/`, `.codex/`, and `.agents/` configuration trees plus the installer that deploys them, with `tests/` holding behaviour suites that assert on those trees. The layout above is the existing structure with the new skill slotted into the place its six siblings already occupy; no new directory concept is introduced. The one genuinely new *kind* of thing is a skill directory with `references/` and `scripts/` subdirectories, which the installer's recursive copy already supports without modification (R4).

## Implementation Sequencing

Five groups, ordered by dependency. Groups 3–5 are mutually independent once group 2 lands.

1. **Vendor the payload** — copy the eleven files, apply the two `SKILL.md` corrections (R0 frontmatter, R1 body path), verify the executable bit and that all nine reference links resolve. Delivers most of User Story 1.
2. **Grant the permission** — add the two anchored entries to `.claude/settings.json`, then *observe* whether an actual invocation runs without a prompt (R1 flags this as needing confirmation, not assumption).
3. **Routing** — `.claude/CLAUDE.md`, `.claude/rules/skill-routing.md`, `.codex/AGENTS.md`. Completes User Story 1 and FR-007/007a/009.
4. **Distribution** — `install.sh` `CUSTOM_SKILLS`, `.agents/skills/scrum-master` symlink. Delivers User Story 2.
5. **Docs and tests** — three READMEs; `tests/run-skill-routing.sh` rule list and enum, new case file, `tests/run-codex-sync.sh` SYNC-03 list. Delivers User Story 3. Finish by running every `tests/run-*.sh` for FR-020/SC-008.

## Risks

| Risk | Likelihood | Handling |
|---|---|---|
| The `settings.json` permission pattern does not match the real invocation, so a prompt still appears | Medium — pattern semantics inferred from existing entries, not from a spec | Verify by observation (quickstart step 4). Fallback is one prompt per session: degrades FR-014, breaks nothing else. |
| Widening the always-loaded routing list pulls in non-Scrum project-management requests | Medium — this is the known cost of the FR-007 answer | FR-007a requires an explicit negative boundary in `skill-routing.md`; SC-009 makes it verifiable |
| `tests/run-skill-routing.sh` cannot run without a live `claude` CLI | High in CI, low locally | The suite already hard-errors without the CLI; the case file is authored to the existing format and run where the CLI exists (stated spec assumption) |
| The Japanese playbook body reduces routing accuracy for English prompts | Low — `when_to_use` is already English and carries the trigger phrases | SC-001 mandates at least one English and one Japanese probe, so the risky case is exercised rather than assumed |
