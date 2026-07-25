# Phase 1 Data Model: Integrate the `scrum-master` skill

**Feature**: 016-scrum-master-skill | **Date**: 2026-07-25 | **Plan**: [plan.md](./plan.md)

There is no runtime data store here. The "model" is the set of configuration entities the repository maintains, their fields, and the invariants that must hold across them — the things the behaviour suites assert on. Each entity below is described as it exists after this feature lands.

---

## Entity: Skill

A named, on-demand playbook an agent loads when a request matches its triggers.

| Field | Source | Value for `scrum-master` |
|---|---|---|
| `name` | `SKILL.md` frontmatter | `scrum-master` |
| `description` | `SKILL.md` frontmatter | Japanese; empiricism + Scrum Guide 2020 framing, team and solo scope |
| `when_to_use` | `SKILL.md` frontmatter | English trigger phrases, incl. indirect ones ("our stand-ups are dragging") |
| `allowed-tools` | `SKILL.md` frontmatter | **absent** — removed during vendoring (research R0) |
| body | `SKILL.md` | Japanese playbook; links to `references/*` |
| references | `references/*.md` | 9 files |
| scripts | `scripts/*.py` | 1 file, executable |

**Validation rules**

- V1. `name` MUST equal the containing directory name (`.claude/skills/scrum-master/`).
- V2. `name`, `description`, and `when_to_use` MUST match the source byte-for-byte (FR-002).
- V3. Every relative link in the body MUST resolve to a file inside the skill directory (FR-003, SC-005).
- V4. Any script MUST retain its executable bit and its `#!/usr/bin/env python3` shebang.
- V5. The frontmatter MUST NOT declare a tool permission that the permission system does not enforce (research R0).
- V6. Any command the body tells a caller to run MUST be resolvable as written — no undefined variables (research R1).

**Relationships**: referenced by exactly one Routing rule; enumerated by every Skill inventory; deployed to every Distribution target; exercised by at least one Routing regression case.

---

## Entity: Routing rule

The mapping from a request category to exactly one skill, plus the precedence that resolves compound requests.

**Instances that must carry `scrum-master`**

| Location | Register | Requirement |
|---|---|---|
| `.claude/CLAUDE.md` | Always-loaded mandatory-routing list | FR-007 |
| `.claude/rules/skill-routing.md` | Full category map, incl. negative boundary | FR-006, FR-007a |
| `.codex/AGENTS.md` | Codex bullet list with `@.agents/skills/<name>/SKILL.md` path | FR-009 |

**Validation rules**

- V7. The three locations MUST agree — a skill present in one and absent from another is drift.
- V8. The rule MUST state a negative boundary excluding non-Scrum project management (FR-007a), since the always-loaded placement widens the trigger surface.
- V9. Adding the rule MUST NOT change the category → skill mapping for any pre-existing category (FR-008).
- V10. The `.codex/AGENTS.md` path form MUST be `@.agents/skills/scrum-master/SKILL.md` exactly — `tests/run-codex-sync.sh` matches this string literally.

---

## Entity: Skill inventory

An enumeration of available skills stated for humans. Three instances, each with its own shape, and two of them carry a literal count.

| Location | Shapes present | Count to update |
|---|---|---|
| `README.md` | prose list (§ skills), deployment table row, directory tree | — |
| `README.ja.md` | same three shapes in Japanese | 「6 個のスキルリンク」→ 7 |
| `.codex/README.md` | two deployment-map rows | 「手書き 6 件」→ 7 (both rows) |

**Validation rules**

- V11. Every inventory MUST list `scrum-master` (FR-017).
- V12. Any stated count MUST equal the actual number of hand-written skills — 7 after this change.
- V13. The directory-tree renderings MUST show that this skill carries `references/` and `scripts/`, not a bare `SKILL.md` (FR-018), since it is the first skill in the set to do so.

---

## Entity: Distribution target

A per-agent, user-scope location from which a skill is discoverable outside this repository.

| Target | Path | Produced by | Form |
|---|---|---|---|
| Claude Code, user scope | `~/.claude/skills/scrum-master/` | `install.sh` → `sync_path "skills"` | recursive copy |
| Codex CLI, user scope | `~/.agents/skills/scrum-master` | `install.sh` → `CUSTOM_SKILLS` loop | symlink → `~/.claude/skills/scrum-master` |
| Codex CLI, repo scope | `.agents/skills/scrum-master` | tracked in git | relative symlink → `../../.claude/skills/scrum-master` |

Cursor is deliberately not a target (research R8).

**Validation rules**

- V14. Both user-scope targets MUST be reachable after one installer run (FR-010, FR-011, SC-003).
- V15. Symlinks MUST resolve to the installed copy, never to this repository's working tree — so the link survives the clone being moved or deleted (FR-011).
- V16. A second installer run MUST produce an identical end state (FR-012, SC-004). `sync_path` achieves this by `rm -rf` before `cp -R`; the loop by `ln -sfn`.
- V17. No symlink under `.agents/skills/` may dangle (SYNC-01/02).
- V18. The `speckit-*` exclusion MUST continue to apply and MUST NOT catch `scrum-master` (FR-013).

---

## Entity: Permission grant

A scoped authorisation letting the helper script run without an ad-hoc prompt.

| Field | Value |
|---|---|
| Location | `.claude/settings.json` → `permissions.allow` |
| Entries | `Bash(python3 .claude/skills/scrum-master/scripts/flow_metrics.py *)` and the `~/.claude/...` variant |
| Scope | The one script, at the two locations it can be loaded from (research R1) |

**Validation rules**

- V19. The grant MUST NOT widen general command execution (FR-015) — no `Bash(python3 *)`.
- V20. The destructive-command guardrail MUST return `allow` for the invocation (verified, research R2).
- V21. The grant's effectiveness MUST be confirmed by observation, not assumed (research R1); failure degrades to one prompt and does not block the feature.

---

## Entity: Routing regression case

A recorded prompt plus its expected skill.

| Field | Value |
|---|---|
| Path | `tests/skill-routing/007-scrum-facilitation.md` |
| Format | `# Test:` / `**Category**` / `**ID**` / `## Input Prompt` (fenced) / `## Expected Skill` / `## Expected Behavior` / `## Pass Criteria` / `## Baseline` |
| Expected skill | `scrum-master` |

**Validation rules**

- V22. The runner's inline rule list and output enum in `tests/run-skill-routing.sh` MUST both include `scrum-master`, or the case can never pass regardless of the real routing rules (research R3).
- V23. Pre-existing cases MUST keep resolving to their recorded skills (FR-020, SC-002).
- V24. The baseline block MUST use `___` placeholders so the runner can fill them on first execution.

---

## Cross-entity invariants

These are the properties the behaviour suites exist to protect:

- **I1 — Catalog agreement.** The set of skill directories in `.claude/skills/` (excluding `speckit-*`), the `CUSTOM_SKILLS` list in `install.sh`, the links in `.agents/skills/`, the routing lists in all three guidance files, the `SYNC-03` list in `tests/run-codex-sync.sh`, and the three human inventories MUST all name the same seven skills. This feature adds the seventh; every one of those places is a site that must change together.
- **I2 — Single source of truth.** `.claude/skills/scrum-master/` is authoritative. No process reads back from `/Users/taikiogihara/work/scrum-master-skill/` (FR-021, FR-022).
- **I3 — Additive only.** No pre-existing routing decision, permission, or suite result changes (FR-008, FR-020).
