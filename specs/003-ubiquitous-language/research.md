# Research: Ubiquitous Language Skill Simplification

**Feature**: 003-ubiquitous-language
**Date**: 2026-05-09

## Decision 1: CLAUDE.md Auto-Detection Pattern

**Decision**: Content-based trigger — activate `ubiquitous-language` skill when business event expressions (verb+noun past/passive form) or domain-specific vocabulary appears in conversation.

**Rationale**: File-presence check (previous: `.specify/ubiquitous-language/`) required the user to have already created a UL store. Content-based detection enables the bootstrap prompt even before files exist, matching FR-013/FR-015. The pattern also aligns with how other always-on skills are described in CLAUDE.md — a one-line condition + behavior description.

**Alternatives considered**:
- File-presence check on `docs/ubiquitous-language.md` — rejected: misses bootstrap opportunity when file does not yet exist
- Directory-presence check on `docs/` — rejected: too broad; activates on projects with `docs/` unrelated to UL

**CLAUDE.md routing line (replacement)**:
```
- `ubiquitous-language` — activate when conversation contains business event expressions (past/passive verb+noun: e.g., 「注文が確定された」) or domain vocabulary candidates; passively queues candidates without interrupting; surfaces them at natural pauses (no new candidates in preceding turn)
```

---

## Decision 2: SKILL.md Structure

**Decision**: Linear flow with a single branch at file-presence check. Sections: Pre-check → Bootstrap (if no file) or Maintenance (if file exists) → Passive Collection rules → Invariants.

**Rationale**: The previous SKILL.md used Mode A/B/C labels with 10+ sub-steps each, creating reading overhead. A single decision point (file exists?) with two branches is the minimum needed. Mode labels are internal implementation details and do not need to appear in the playbook prose.

**Alternatives considered**:
- Keep mode labels, reduce prose — rejected: labels add cognitive load with no user-visible benefit
- Single flat procedure — rejected: bootstrap and maintenance flows differ enough to warrant distinct branches

---

## Decision 3: Storage Schema

**Decision**: Single file `docs/ubiquitous-language.md` with three optional sections:
1. File header (project name, last updated, total entries)
2. `## Watchlist` — project-specific vague-term additions/removals
3. One or more `## Bounded Context: <name>` sections, each containing the 7-field UL table

Context map at `docs/context-map.md` (separate file, created at bootstrap alongside UL file).

**Rationale**: Single-file approach (v1) keeps all UL data browsable in one place. `## Watchlist` in the same file avoids a third file while keeping watchlist data persistent. Separate `context-map.md` is justified because it records cross-context relationships that are conceptually distinct from term definitions.

**Alternatives considered**:
- Per-Bounded-Context files under `docs/` — deferred to v2 per spec Assumptions
- Watchlist in a dedicated `docs/watchlist.md` — rejected: unnecessary file proliferation for v1

---

## Decision 4: Passive Collection Trigger

**Decision**: Surface queued candidates when (a) queue has ≥ 1 entry AND (b) the most recent user turn contained zero new business-vocabulary candidates.

**Rationale**: One-turn quiet is sufficient signal that the user has moved on from active domain discussion. Two-turn quiet (alternative) adds unnecessary latency to feedback.

---

## No Unresolved Items

All spec clarifications resolved. No external dependency research required — the skill is a prompt playbook with no library dependencies.
