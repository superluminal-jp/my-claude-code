# Data Model: Remove /verify-config Verification Feature

This feature has no runtime data entities — it removes repository files and
documentation. The "entities" below are the artifacts affected and their
dependency relationships, so the removal order avoids leaving a dangling
reference at any intermediate step.

## Entities

### Skill definition — `.claude/skills/verify-config/SKILL.md`
- **Relationship**: `agent: verification-runner` frontmatter field points at the agent entity below. Must be deleted no later than the agent (deleting the agent first would leave this skill pointing at nothing).

### Agent definition — `.claude/agents/verification-runner.md`
- **Relationship**: Referenced by the skill above (as fork target) and by the test suite below (as subject under test). Has no dependents outside this repository (`install.sh` never syncs `.claude/agents/`).

### Test suite — `tests/run-verification-agent.sh`
- **Relationship**: Depends on both entities above existing to have anything to test. Must be deleted in the same change as them (a suite testing deleted files would itself become a dangling reference, or worse, fail).

### README description block — `README.md` §"Verification" (and file-structure tree entries), `README.ja.md` §"検証" (and its tree entries)
- **Relationship**: Describes both entities above for a human reader. Must be edited in the same change so no shipped documentation describes a feature that no longer exists.

### README skill-list entry — `README.md` line ~40, `README.ja.md` line ~24
- **Relationship**: Independent one-line mentions in the "What this provides" skill enumeration; removed alongside the fuller Verification section description.

### Codex inline-verification instruction — `AGENTS.md` (repo root)
- **Relationship**: Told Codex CLI sessions to run the skill's checks inline. Discovered during implementation (missed in the original R1 footprint table — see research.md addendum), not during planning. Depends on the skill entity existing to make sense; removed alongside it.

## Removal ordering

No strict ordering is required *within a single atomic change* (all edits land together), but if done incrementally, the safe order is: test suite → README prose → skill → agent. This ensures no intermediate state has a passing-looking test suite pointing at a half-removed feature.
