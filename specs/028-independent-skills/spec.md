# Feature Specification: Skill Bodies Independent of Sibling Skills

**Feature Branch**: `028-independent-skills`

**Created**: 2026-08-16

**Status**: Draft

**Input**: User description: "Make every skill in .claude/skills/ self-contained at the skill-body level: no SKILL.md may instruct loading, routing to, or composing with another skill by name. Supersedes FR-004 of specs/015-digital-agency-frontend/spec.md. Scope is skill-body only — .claude/CLAUDE.md and .claude/rules/skill-routing.md may continue to sequence multiple skills for one task, since that is the router's job, not a skill depending on a skill. Known cross-references: digital-agency-frontend → coder/clarifier (required by FR-004, asserted by tests/run-digital-agency-frontend-skill.sh DADS-06/DADS-07); coder → adr; adr → coder; the minto triad (builder/reviewer/rewriter) routing to each other. Consequential updates: rewrite FR-004, update the two DADS test assertions, verify SYNC-SKILL-05A (targets skill-routing.md, expected to keep passing), and sweep other tests/docs/specs for stale claims."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - digital-agency-frontend works without naming coder or clarifier (Priority: P1)

As a maintainer reading `.claude/skills/digital-agency-frontend/SKILL.md` in isolation, I want its own body to fully describe what it does for DADS/dashboard work — including the minimum TDD, security, and clarification behavior that work actually needs — without instructing the agent to go load a different named skill, so the file can be understood, tested, and modified without also opening `coder` or `clarifier`.

**Why this priority**: This is the specific case the request named, it is the largest of the six cross-references (four separate instructions), and it is the one currently protected by both a functional requirement (spec 015 FR-004) and automated tests (DADS-06, DADS-07) that assert the opposite of the target state — so it carries the most risk of silent regression if done first without care.

**Independent Test**: Read `.claude/skills/digital-agency-frontend/SKILL.md` alone. Confirm it contains no instruction to load, route to, or implement through another named skill, and that its own workflow still specifies a failing-test-first step, a security/validation step, and a documentation-sync step in DADS-specific terms.

**Acceptance Scenarios**:

1. **Given** `.claude/skills/digital-agency-frontend/SKILL.md` currently contains "Load `coder` before changing code; keep TDD, type safety, security, and documentation sync there." and a "### 4. Implement through `coder`" section, **When** the change is complete, **Then** neither instruction exists, and the skill's own text still requires a failing test/behavior check before implementation, boundary validation of external data, and documentation updates in the same change.
2. **Given** `.claude/skills/digital-agency-frontend/SKILL.md` currently contains "Load `clarifier` when the users, task, decision, data meaning, constraints, or success criteria are materially ambiguous.", **When** the change is complete, **Then** that instruction does not exist, and the skill's own text still requires resolving the same material ambiguity (users, task, use context, content/data, constraints, success criterion) before implementation, stated in its own terms rather than by name-dropping `clarifier`.
3. **Given** a developer invokes the skill for a representative DADS page or dashboard task, **When** the assistant follows the rewritten skill, **Then** the resulting workflow (scope discovery → source verification → design → implementation → accessibility gate → close-out) is unchanged in substance from before this feature, only decoupled from naming sibling skills.

---

### User Story 2 - coder and adr describe their own scope without naming each other (Priority: P2)

As a maintainer, I want `coder`'s SKILL.md to describe what to do when a hard-to-reverse decision is settled without instructing "load the `adr` skill," and `adr`'s SKILL.md to describe its own purpose without defining itself in terms of `coder`, so each file stands alone.

**Why this priority**: Same shape of change as User Story 1 but lower risk — no functional requirement or test currently pins this text — and lower value, since each reference is a single sentence rather than a routing subsystem.

**Independent Test**: Read `.claude/skills/coder/SKILL.md` alone; confirm it does not instruct loading `adr`. Read `.claude/skills/adr/SKILL.md` alone; confirm its purpose statement does not name `coder`.

**Acceptance Scenarios**:

1. **Given** `.claude/skills/coder/SKILL.md` currently contains "A significant, hard-to-reverse decision is settled → load the `adr` skill to record it.", **When** the change is complete, **Then** that line is removed and no replacement instructs loading a named sibling skill.
2. **Given** `.claude/skills/adr/SKILL.md` currently states "Complements `coder` (SDD captures *what/why* of a feature) by recording the *decision* itself.", **When** the change is complete, **Then** the purpose statement describes what an ADR records on its own terms, without naming `coder`.

---

### User Story 3 - the minto triad each describe only their own function (Priority: P3)

As a maintainer, I want `minto-builder`, `minto-reviewer`, and `minto-rewriter` to each describe their own scope and boundaries without instructing the agent to route to one of the other two by name, so the routing decision lives in exactly one place (`.claude/rules/skill-routing.md`, which already contains the equivalent decision table) instead of being duplicated three times across the skills themselves.

**Why this priority**: Lowest priority because it is the most symmetric and least urgent — the three skills already have a "Do not use this skill when" section stating the boundary in plain terms; only the trailing "Route ... to `X`" sentences need to go, and no test currently pins them.

**Independent Test**: Read each of the three SKILL.md files alone. Confirm none instructs routing to a named sibling skill, and each retains its own "Do not use this skill when" boundary description.

**Acceptance Scenarios**:

1. **Given** `minto-builder/SKILL.md` currently contains "Route diagnosis to `minto-reviewer`." and "Route direct rewriting to `minto-rewriter`.", **When** the change is complete, **Then** neither sentence exists, and the preceding "Do not use this skill when" list (structural diagnosis, direct final rewrite, proofreading, factual research) still states the same boundary without naming the sibling skill that handles it.
2. **Given** `minto-reviewer/SKILL.md` currently contains "Route finished-document rewriting to `minto-rewriter`." and "Route collaborative document development to `minto-builder`.", **When** the change is complete, **Then** neither sentence exists, with the same boundary-preservation as above.
3. **Given** `minto-rewriter/SKILL.md` currently contains "Route structural diagnosis to `minto-reviewer`." and "Route collaborative development to `minto-builder`.", **When** the change is complete, **Then** neither sentence exists, with the same boundary-preservation as above.

### Edge Cases

- What happens to spec 015's FR-004 ("The skill MUST compose with the repository's existing clarification and coding workflows rather than duplicate their generic requirements...")? It is superseded, not silently left contradicting the code: FR-004 is rewritten in place within `specs/015-digital-agency-frontend/spec.md` to require self-containment instead of composition, with a note that it supersedes the original wording as of this feature. Spec 015 is not renumbered or deleted — only the one requirement it got wrong changes, following this repository's own convention of correcting prior specs in place when a later feature invalidates a specific line (see how `specs/026-remove-permissions-config/` describes correcting `permissions.md`'s claims), while ADR-style specs elsewhere in the repo are left untouched — this is a spec correction, not a historical record, because 015's own FR-004 is the thing being proven wrong by this feature, not a fact this feature merely builds on.
- What happens to `tests/run-digital-agency-frontend-skill.sh` DADS-06 and DADS-07, which currently assert the SKILL.md contains `` `coder` `` and `` `clarifier` ``? They are rewritten to assert the new contract (the skill inlines its own TDD/security/doc-sync and ambiguity-resolution requirements without naming those skills) rather than deleted outright, so the file continues to guard *something* about the skill's completeness.
- What happens to SYNC-SKILL-05A in the same test file, which asserts `.claude/rules/skill-routing.md` composes `coder` and `digital-agency-frontend`? Nothing — that assertion targets the router file, which is explicitly out of scope for this feature (routing-layer composition is not a skill depending on a skill). It is expected to keep passing unmodified; this must be verified by running the suite, not assumed.
- What happens to `.claude/CLAUDE.md`'s and `.claude/rules/skill-routing.md`'s own composition prose (e.g. "load `coder` first, then `digital-agency-frontend`", "Diagnose... -> `minto-reviewer`... Rewrite... -> `minto-rewriter`")? Left untouched — these are the router deciding which skill(s) a request needs and in what order, which remains necessary for the mandatory routing system to function; only the individual SKILL.md bodies stop repeating or acting on that decision internally.
- What happens to README.md, README.ja.md, and AGENTS.md, which list the minto triad and `adr` together and describe compound routing (e.g. "Digital Agency frontend implementation uses `coder` followed by `digital-agency-frontend`")? Left untouched for the same reason as the router files — they document the routing layer's behavior, not a skill's own body, and were not asserted by the request as in scope.
- What happens to `docs/adr/`? No new architecturally significant one-way-door decision is introduced by decoupling skill bodies from each other — the routing/composition mechanism itself (CLAUDE.md + skill-routing.md deciding sequencing) is unchanged; only where the *instruction to compose* lives (router vs. skill body) changes. No ADR is proposed for this feature; see Assumptions.
- What happens to other historical `specs/NNN-*/` directories below 028 (e.g. `specs/016-scrum-master-skill/`, `specs/017-scrum-master-rewrite/`)? Left unmodified — only `specs/015-digital-agency-frontend/spec.md`'s FR-004 is corrected, because it is the one requirement this feature directly supersedes; no other historical spec makes a claim this feature invalidates.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `.claude/skills/digital-agency-frontend/SKILL.md` MUST NOT instruct loading, routing to, or implementing through `coder` or `clarifier` by name. It MUST still require, in its own terms: a failing test or behavior/accessibility check before implementation where automatable, boundary validation of external data, documentation updates in the same change, and resolution of material ambiguity (users, task, use context, content/data, constraints, success criterion) before implementation.
- **FR-002**: `.claude/skills/coder/SKILL.md` MUST NOT instruct loading the `adr` skill by name. Its existing "Related rules" pointers to `rules/git-workflow.md` and `rules/permissions.md` are unaffected (those are rule files, not skills, and out of scope for this feature).
- **FR-003**: `.claude/skills/adr/SKILL.md` MUST NOT define or describe its own purpose by naming the `coder` skill.
- **FR-004**: `.claude/skills/minto-builder/SKILL.md`, `.claude/skills/minto-reviewer/SKILL.md`, and `.claude/skills/minto-rewriter/SKILL.md` MUST NOT instruct routing to another named sibling skill. Each MUST retain its existing "Do not use this skill when" boundary description describing what kind of request it does not handle, without naming which sibling skill handles it instead.
- **FR-005**: `specs/015-digital-agency-frontend/spec.md` FR-004 MUST be rewritten to require self-containment (no naming `coder`/`clarifier` in the skill body) instead of composition, with the requirement text making clear it supersedes the prior wording.
- **FR-006**: `tests/run-digital-agency-frontend-skill.sh` DADS-06 and DADS-07 MUST be rewritten to assert the new contract (the skill's own text covers TDD/security/documentation-sync and ambiguity-resolution without naming `coder` or `clarifier`) rather than left asserting the removed cross-references.
- **FR-007**: `.claude/CLAUDE.md`, `.claude/rules/skill-routing.md`, README.md, README.ja.md, and AGENTS.md — the routing/documentation layer describing which skill(s) a request needs and in what sequence — MUST NOT be modified by this feature; their composition statements are out of scope.
- **FR-008**: The full remaining behavior-suite set (every `tests/run-*.sh`) MUST pass after the change, including confirming SYNC-SKILL-05A in `tests/run-digital-agency-frontend-skill.sh` still passes unmodified.
- **FR-009**: Every other `specs/NNN-*/` directory MUST be left unmodified except `specs/015-digital-agency-frontend/spec.md`'s FR-004.

### Key Entities

- **Skill body**: The instructional content of a single `SKILL.md` file — the thing this feature makes self-contained.
- **Router / routing layer**: `.claude/CLAUDE.md` and `.claude/rules/skill-routing.md`, which decide which skill(s) a request needs and in what order — explicitly out of scope; the layer where cross-skill sequencing is allowed to live.
- **FR-004 (spec 015)**: The specific prior requirement this feature supersedes — it required composition; this feature requires self-containment instead.
- **DADS-06 / DADS-07**: The two test assertions in `tests/run-digital-agency-frontend-skill.sh` that currently pin the removed cross-references and must be rewritten to pin the new contract.
- **SYNC-SKILL-05A**: The test assertion that targets the router file, not the skill body — must be verified to still pass, unchanged, as evidence that the router/skill-body boundary was respected.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A search of all six affected `SKILL.md` bodies (`digital-agency-frontend`, `coder`, `adr`, `minto-builder`, `minto-reviewer`, `minto-rewriter`) for backtick-quoted sibling skill names used as load/route/implement-through instructions returns zero hits.
- **SC-002**: `tests/run-digital-agency-frontend-skill.sh` exits successfully with all checks (including SYNC-SKILL-05A) passing.
- **SC-003**: The complete remaining `tests/run-*.sh` suite exits successfully with zero failures attributable to this change.
- **SC-004**: A reader of `digital-agency-frontend/SKILL.md` alone (without opening `coder` or `clarifier`) can state what test-first, security, documentation, and ambiguity-resolution behavior the skill requires, because that behavior is described in the file itself.
- **SC-005**: `specs/015-digital-agency-frontend/spec.md` FR-004 no longer asserts a composition requirement that contradicts the shipped skill body.

## Assumptions

- The maintainer's choice of "skill-body only" scope (routing-layer composition in `.claude/CLAUDE.md` / `.claude/rules/skill-routing.md` stays, since sequencing multiple skills for one task is the router's job, not a skill depending on a skill) was confirmed via `AskUserQuestion` before this spec was written.
- This feature does not remove any capability end users rely on — the DADS-specific TDD/security/documentation/clarification behavior that `digital-agency-frontend` currently obtains by naming `coder`/`clarifier` is inlined into its own body, not dropped.
- No architecturally significant one-way-door decision is introduced: the routing mechanism (router decides sequencing) is unchanged; only where the instruction to compose is written down (router vs. skill body) changes. No ADR is proposed.
- Following the precedent set by specs 024–027, historical `specs/` directories are left unmodified except the one requirement (spec 015 FR-004) this feature directly supersedes.
- `docs/adr/0001`–`0006` (or however many currently exist) are unaffected; none of them describe skill-to-skill composition.
