# Data Model: Skill Bodies Independent of Sibling Skills

No runtime data entities — six skill-file edits, one spec correction, one test correction.

## Entities

### `.claude/skills/digital-agency-frontend/SKILL.md`
- **Relationship**: Currently names `coder` (2 places) and `clarifier` (1 place) as dependencies (research R1). Edited to state their substantive content in its own terms. Depends on `specs/015-digital-agency-frontend/spec.md` FR-004 being corrected in the same change (R7), and on `tests/run-digital-agency-frontend-skill.sh` DADS-06/07 being rewritten to match (R8) — these three must land together or the test suite fails between commits.

### `.claude/skills/coder/SKILL.md`
- **Relationship**: Currently names `adr` (research R2). No other file depends on this specific line; independent of the other five edits.

### `.claude/skills/adr/SKILL.md`
- **Relationship**: Currently names `coder` in its purpose statement (research R3). Independent of the other five edits.

### `.claude/skills/minto-builder/SKILL.md`, `minto-reviewer/SKILL.md`, `minto-rewriter/SKILL.md`
- **Relationship**: Mutually reference each other (research R4–R6). The three edits are independent of each other (each file only loses its own two sentences) and independent of the other three entities above. No test currently pins any of the three.

### `specs/015-digital-agency-frontend/spec.md` FR-004 (+ Assumptions line)
- **Relationship**: Directly describes `digital-agency-frontend/SKILL.md`'s contract. Must be corrected in the same change as that file's edit (research R7) — leaving FR-004 unedited while the skill body changes would be a Live Documentation drift violation.

### `tests/run-digital-agency-frontend-skill.sh` DADS-06 / DADS-07
- **Relationship**: Guards `digital-agency-frontend/SKILL.md`'s content directly (research R8). Must be rewritten in the same change or the suite fails red for a reason unrelated to a real regression.

### `tests/run-digital-agency-frontend-skill.sh` SYNC-SKILL-05A
- **Relationship**: Guards `.claude/rules/skill-routing.md`, which is out of scope (FR-007). Not edited; verified to still pass unchanged as evidence the router/skill-body boundary was respected.

## Edit ordering

Two independent groups, no cross-group ordering constraint:
1. `digital-agency-frontend/SKILL.md` + `specs/015-.../spec.md` FR-004 + `tests/run-digital-agency-frontend-skill.sh` DADS-06/07 — land together (see above).
2. `coder/SKILL.md`, `adr/SKILL.md`, `minto-builder/SKILL.md`, `minto-reviewer/SKILL.md`, `minto-rewriter/SKILL.md` — five fully independent single-file edits, no guarding tests, may land in any order or as one combined change.
