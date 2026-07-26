# Feature Specification: Remove solo-practice individual-use capability from `scrum-master`

**Feature Branch**: `018-remove-solo-practice`

**Created**: 2026-07-26

**Status**: Draft

**Input**: User description: "scrum-masterスキルから、個人利用（ソロプラクティス）に関する機能を完全に削除する。対象は .claude/skills/scrum-master/references/solo-practice.md ファイルの削除、SKILL.mdのfrontmatter（description, when_to_use）からソロ/個人利用への言及の除去、SKILL.md本文の「個人利用（ソロプラクティス）」セクションと参照ファイル表の該当行の削除。加えて、この機能をルーティング対象として明記している既存のドキュメント（.claude/rules/skill-routing.md、.claude/CLAUDE.md、.codex/AGENTS.md、README.md）からも、ソロ/個人利用に関する記述を除去し、スキルの実際の対応範囲とドキュメント上の宣言を一致させる。既存のScrum Guide直接引用の強化（017-scrum-master-rewriteでの変更）は維持し、後退させない。"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A solo/individual-use request no longer routes to `scrum-master` (Priority: P1)

A user who asks for help with a personal, non-team task — "自分ひとりの作業を週次で振り返りたい", "help me run my own weekly planning" — no longer has that request auto-routed to `scrum-master`, since the skill's actual remit is scoped to team Scrum practice.

**Why this priority**: This is the core of "remove the capability" — until routing itself stops offering solo support, the feature isn't removed, only its documentation is thinner.

**Independent Test**: Issue a solo-practice-flavoured prompt in an agent session and confirm `scrum-master` is not the skill that loads (it falls through to whatever the next-best match is — likely `clarifier` or no skill — rather than to `scrum-master`'s now-deleted solo content).

**Acceptance Scenarios**:

1. **Given** an agent session in this repository, **When** the user asks "自分ひとりの作業を週次で振り返りたい" (a prompt the skill previously handled via solo-practice), **Then** `scrum-master` does not load on the basis of solo/individual framing alone.
2. **Given** the same session, **When** the user asks a team-facing Scrum question (e.g., "うちのデイリースクラムが報告会になっている"), **Then** `scrum-master` still loads exactly as before — team-facing routing is unaffected.

---

### User Story 2 - The skill's declared capability matches its actual content (Priority: P1)

A reader of `SKILL.md`'s frontmatter, or of any of this repository's routing/inventory documents, no longer sees a promise of solo/individual-use support that the skill body can no longer deliver.

**Why this priority**: A frontmatter or routing-rule claim that outlives the content behind it is exactly the kind of drift this repository's Live Documentation practice exists to catch. Equal priority to Story 1 because leaving even one of these documents stale re-creates the mismatch the removal is meant to fix.

**Independent Test**: Grep `SKILL.md`, `.claude/rules/skill-routing.md`, `.claude/CLAUDE.md`, `.codex/AGENTS.md`, and `README.md` for solo/individual-practice language; confirm none remains.

**Acceptance Scenarios**:

1. **Given** `SKILL.md`'s frontmatter (`description`, `when_to_use`), **When** it is read, **Then** it makes no claim about solo, personal, or individual-use support.
2. **Given** `.claude/rules/skill-routing.md`'s `scrum-master` entry, **When** it is read, **Then** it no longer states that self-facilitation for individual work routes here.
3. **Given** `.claude/CLAUDE.md`'s mandatory routing table and `.codex/AGENTS.md`'s routing list, **When** each is read, **Then** neither describes `scrum-master` as covering solo or individual retrospectives.
4. **Given** `README.md`'s skill inventory, **When** it is read, **Then** its `scrum-master` entry no longer mentions solo/individual use.

---

### User Story 3 - Team-facing content and the Scrum Guide citation work survive untouched (Priority: P2)

A user relying on `scrum-master` for team Scrum facilitation, event playbooks, anti-pattern diagnosis, measurement, or scaling guidance sees no change or regression in that content, and the direct-quotation/citation rigor added in the prior rewrite (`017-scrum-master-rewrite`) is preserved.

**Why this priority**: Lower priority than Stories 1–2 because it's a non-regression guarantee rather than new capability — but still required, since a careless removal could accidentally delete or break adjacent team-facing content or citations.

**Independent Test**: Diff the team-facing sections of `SKILL.md` and every reference file other than `solo-practice.md` against their pre-removal state; confirm no unintended changes; confirm every citation added in `017-scrum-master-rewrite` is still present and every internal link still resolves.

**Acceptance Scenarios**:

1. **Given** `SKILL.md` and the remaining reference files, **When** diffed against their state at the end of `017-scrum-master-rewrite`, **Then** the only changes are the deletions/edits this feature specifies — no team-facing content or citation is altered or lost.
2. **Given** the full set of internal links across `SKILL.md` and the remaining `references/*.md` files, **When** each is followed, **Then** it resolves to an existing file and heading (no link is left pointing at the deleted `solo-practice.md`).

---

### Edge Cases

- **A prompt that blends team and solo framing** ("うちのチームは私しかいないので一人でスプリントを回している") — this is an edge case for the routing rule's judgment, not something this feature must resolve definitively; the routing rule should no longer carve out an explicit solo exception, and ambiguous single-person-team cases fall to whatever the routing rule's general Scrum-practice test decides.
- **A file elsewhere in the skill links to `solo-practice.md` after its deletion** — must not happen; every reference is removed in the same change (verified per FR-009).
- **The routing regression suite currently has no solo-specific test case** — confirmed by inspection; removing solo capability requires no test-suite change, only confirmation that the existing team-facing case (`tests/skill-routing/007-scrum-facilitation.md`) still passes.
- **User-scope installed copies of the routing/CLAUDE.md files** (e.g., `~/.claude/rules/skill-routing.md`) mirror the project source via the installer — this feature edits only the project source; redistribution to user scope happens the next time the installer runs, which is out of scope here (consistent with how skill content changes are always handled in this repository).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `.claude/skills/scrum-master/references/solo-practice.md` MUST be deleted.
- **FR-002**: `SKILL.md`'s frontmatter `description` MUST no longer state or imply solo/individual/personal-use support.
- **FR-003**: `SKILL.md`'s frontmatter `when_to_use` MUST no longer state or imply solo/individual/personal-use support.
- **FR-004**: `SKILL.md`'s body MUST no longer contain the "個人利用（ソロプラクティス）" section or any equivalent content.
- **FR-005**: `SKILL.md`'s reference-file routing table MUST no longer list a row pointing to `solo-practice.md`.
- **FR-006**: `.claude/rules/skill-routing.md`'s `scrum-master` entry MUST no longer state that self-facilitation for individual/solo work routes to `scrum-master`.
- **FR-007**: `.claude/CLAUDE.md`'s mandatory routing table entry for `scrum-master` MUST no longer mention solo retrospectives or individual use.
- **FR-008**: `.codex/AGENTS.md`'s routing entry for `scrum-master` MUST no longer mention solo or individual retrospectives.
- **FR-009**: `README.md`'s skill inventory entry for `scrum-master` MUST no longer mention solo/individual use.
- **FR-010**: No file remaining after this change MUST contain a link or reference to the deleted `solo-practice.md`.
- **FR-011**: Every citation, quotation, and structural change made in `017-scrum-master-rewrite` to files other than `solo-practice.md` MUST remain intact — this feature is a scope reduction, not a re-opening of the citation work.
- **FR-012**: The routing regression suites (`tests/run-skill-routing.sh`, `tests/skill-routing/007-scrum-facilitation.md`, `tests/run-codex-sync.sh`) MUST continue to pass unchanged; no test file requires modification since none currently exercises solo-specific routing.
- **FR-013**: Team-facing routing behavior (Scrum events, facilitation, anti-patterns, measurement, scaling) MUST be unaffected — only the solo/individual-use trigger surface is removed.
- **FR-014**: This feature MUST NOT modify installed user-scope copies (e.g., `~/.claude/...`) directly; only the project source under version control is in scope, consistent with how this repository always treats distribution as the installer's job.

### Key Entities

- **Solo-practice capability**: The removed feature — self-facilitation for an individual's own work (weekly planning, daily check-in, personal retrospective) framed as a one-person Scrum Master/Product Owner/Developer split.
- **Routing declaration**: Any of the five documents (`SKILL.md` frontmatter, `skill-routing.md`, `CLAUDE.md`, `AGENTS.md`, `README.md`) that states what a skill covers and is therefore a place drift can occur if content is removed but the declaration is not.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Zero occurrences of solo/individual/personal-use language remain across `SKILL.md`, `.claude/rules/skill-routing.md`, `.claude/CLAUDE.md`, `.codex/AGENTS.md`, and `README.md`'s `scrum-master`-related content.
- **SC-002**: `solo-practice.md` no longer exists, and zero remaining files link to it.
- **SC-003**: A sample of at least 3 previously-solo-routed prompts no longer routes to `scrum-master`.
- **SC-004**: A sample of at least 3 team-facing prompts that routed to `scrum-master` before this change still route there unchanged.
- **SC-005**: Every citation added in `017-scrum-master-rewrite` (spot-checked against that feature's `quickstart.md` sampling method) is still present and unaltered in the surviving files.
- **SC-006**: Zero broken internal links across the surviving `scrum-master` skill files.
- **SC-007**: The existing routing regression suites pass unchanged.

## Assumptions

- **"Complete removal" means content, frontmatter, and every routing-declaration document, not just the file.** The user's request explicitly lists all five documentation surfaces, so this is read as a full drift-elimination pass, not merely `rm solo-practice.md`.
- **No new routing regression test is required.** Inspection confirmed no existing test exercises solo-specific routing, so FR-012 is satisfied by confirming the existing suite still passes, not by adding new cases (adding a "solo no longer routes here" negative test would be a reasonable future addition but is not requested and is out of scope).
- **User-scope installed files are out of scope.** Per this repository's existing distribution model (installer copies project source to user scope), this feature only touches the project source; a subsequent `install.sh` run is how the change reaches `~/.claude/...`, and is the user's call, not part of this feature.
- **This feature builds directly on `017-scrum-master-rewrite`'s uncommitted work.** Both branches currently carry the same working-tree state (the citation rewrite was not yet committed when this branch was created); FR-011 exists specifically to guard that work through this second change.
