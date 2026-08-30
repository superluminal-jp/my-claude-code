# Feature Specification: CLAUDE.md as Pyramid Apex — Rules Layer Independence

**Feature Branch**: `036-rule-layer-independence`

**Created**: 2026-08-30

**Status**: Draft

**Input**: User description: "CLAUDE.md, rules, skillsの順番の構造として、上位の対応ファイルにのみ依存し、同じ階層においては互いに独立するように構成・内容を改善。これをclaude codeの基本構成ルールとしてドキュメントを残す" — clarified via `/clarifier` into: prohibit same-layer named cross-references among `.claude/rules/*.md` files (each rule depends only on `CLAUDE.md`, never on a sibling rule); scope the audit to the rules layer plus the eight self-authored skills already coupled to rules (`clarifier`, `coder`, `adr`, `minto-builder`, `minto-reviewer`, `minto-rewriter`, `scrum-master`, `digital-agency-frontend`); keep downward references (`CLAUDE.md` → rule, rule → its skill) allowed; record the decision in `docs/claude-config-design.md` plus a new ADR, not a new always-loaded rule file. Followed by: "CLAUDE.md を頂点としたピラミッド構造を構築する" — restating the same requirement in Minto Pyramid Principle terms, which this configuration already cites (`.claude/rules/pyramid-principle.md`, `.claude/rules/live-documentation.md` §7.1): `CLAUDE.md` is the single apex thought; each rule is a first-level supporting box that answers to the apex and to nothing beside it; each rule-coupled skill is a second-level box supporting its one owning rule. Minto's pyramids relate boxes vertically (child supports parent) and group siblings horizontally by MECE logic — a box never cites a lateral sibling directly. This feature is that discipline applied to the configuration's own file structure, not only to documents it produces.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A rule reads and executes correctly in isolation (Priority: P1)

As a maintainer (or Claude itself, loading `.claude/rules/` at session start) reading any single file under `.claude/rules/`, I want that file to be fully self-contained — stating its own criteria without requiring me to also open a sibling rule file to know what a term or check means — so that partial context loss, out-of-order reading, or future deletion of a sibling rule never breaks this one.

**Why this priority**: Rules are unconditionally loaded every session; a broken or dangling same-layer reference degrades every session's context quality, not just one feature. This is the case the request specifically named, and it currently has 4 concrete violations across 3 files.

**Independent Test**: Read each of `.claude/rules/clarifier.md`, `.claude/rules/git-workflow.md`, and `.claude/rules/pyramid-principle.md` in isolation (no other rule file open). Confirm each fully explains every criterion it lists without naming another file under `.claude/rules/`.

**Acceptance Scenarios**:

1. **Given** `clarifier.md` currently ends its "Risk" bullet with `(permissions.md)` and its "Related" section with `(permissions.md)`, **When** the change is complete, **Then** neither parenthetical exists and both statements remain fully meaningful read alone.
2. **Given** `git-workflow.md` currently reads "Destructive git operations require confirmation — see `permissions.md`.", **When** the change is complete, **Then** the sentence states the requirement without pointing to another rule file.
3. **Given** `pyramid-principle.md` currently names `thinking-lenses.md` (twice) and `live-documentation.md` (once), **When** the change is complete, **Then** no rule filename appears in `pyramid-principle.md`'s body, and the file still states a complete, actionable self-check.
4. **Given** the four violations are resolved, **When** every other file under `.claude/rules/` is grep'd for the basenames of its sibling rule files, **Then** zero matches are found.

---

### User Story 2 - Skills already coupled to rules stay independent (Priority: P2)

As a maintainer, I want confirmation that the eight self-authored skills already tied to a rule (`clarifier`, `coder`, `adr`, `minto-builder`, `minto-reviewer`, `minto-rewriter`, `scrum-master`, `digital-agency-frontend`) still contain no same-layer sibling-skill references, so the layer-independence property holds across both the rules layer (this feature) and the skills layer (delivered by spec 028).

**Why this priority**: Lower risk than User Story 1 — spec 028 already enforced this for skills — but the rule being documented in this feature claims to cover both layers, so the claim must be verified, not assumed.

**Independent Test**: Grep each of the eight skills' `SKILL.md` for the other seven skill names. Confirm zero matches (already true as of this feature's clarification pass; this story is a verification gate, not a code change).

**Acceptance Scenarios**:

1. **Given** the eight skills' `SKILL.md` files, **When** each is checked against the other seven's names, **Then** no same-layer mention is found.
2. **Given** zero matches, **When** the completion report is produced, **Then** it states explicitly that User Story 2 required no file changes and names spec 028 as the prior work that already delivered it.

---

### User Story 3 - The layering rule is recorded so future rule authoring doesn't regress (Priority: P1)

As the maintainer authoring new rules or skills in future sessions, I want the "depends only on the layer above, independent within a layer" rule written down in a stable, discoverable place with its rationale and rejected alternatives, so I (or Claude, when asked to edit `.claude/rules/`) can check new content against it without re-deriving the reasoning each time.

**Why this priority**: Equal to User Story 1 in the sense that the request explicitly asked for this to be "documented as the basic configuration rule" — without it, the fixes in User Story 1 are a one-off cleanup that will silently erode again next time a rule is edited.

**Independent Test**: Read `docs/claude-config-design.md` alone. Confirm it states the layering rule (upward-only dependency, same-layer independence, downward routing permitted), which layers and file sets it covers, and points to the ADR for the decision record. Confirm the ADR exists under `docs/adr/` with Context, Decision, Rejected Alternatives, and Consequences.

**Acceptance Scenarios**:

1. **Given** `docs/claude-config-design.md`, **When** the change is complete, **Then** it contains a new subsection (extending its existing "変更するとき" / "when changing" guidance) stating the layering rule in the same style as its existing content.
2. **Given** the rejected alternatives surfaced during clarification (ban content-dependency only vs. ban all named mentions; scope to the eight coupled skills vs. all of `.claude/skills/`), **When** the ADR is read, **Then** both are recorded as rejected with the reason the stricter/narrower option was chosen instead.
3. **Given** the new documentation, **When** `.claude/rules/` or `.claude/CLAUDE.md` is inspected, **Then** no new unconditionally-loaded rule file was added — the decision lives only in `docs/` and the ADR, per the explicit scope decision to keep session context cost at zero.

### Edge Cases

- What happens to `pyramid-principle.md`'s existing "Siblings MECE and one logic per group" check, which today explicitly defers to `thinking-lenses.md` ("already self-checked by ... do not re-derive here")? Removing the name without a replacement leaves a dangling "do not re-derive [what?]." Resolution: the bullet is removed from `pyramid-principle.md`'s "What to check" list; the MECE/one-logic-per-group check remains available exactly once, via `CLAUDE.md`'s existing separate instruction to self-check against `thinking-lenses.md`. No content is duplicated (per the project's existing No Redundancy rule) and no rule becomes silently incomplete, since `CLAUDE.md` (the upward layer) still names both files independently — that is routing, not a same-layer dependency.
- What happens to `CLAUDE.md`'s own prose, which names several rule files (`rules/clarifier.md`, `rules/thinking-lenses.md`, `rules/pyramid-principle.md`, `rules/live-documentation.md`, `rules/skill-routing.md`, `rules/mcp.md`)? Nothing — `CLAUDE.md` is the top layer routing down to its children; this is the allowed downward direction, not a same-layer reference, and is explicitly out of scope for this feature.
- What happens to rules that route down to skills (e.g. `skill-routing.md`'s skill table, `pyramid-principle.md`'s pointers to the `minto-*` skills, `live-documentation.md`'s pointer to the `adr` skill, `clarifier.md`'s pointer to the `clarifier` skill and `/speckit-clarify`)? These remain unchanged — rule-to-skill is a downward reference (parent layer to its own child), not a same-layer reference, and was explicitly confirmed as allowed during clarification.
- What if a future rule or skill needs to state something that today lives only in a sibling? Per the layering rule, the fact must be either restated in the file's own terms (accepting the minor duplication only where no single canonical home exists) or hoisted to the shared parent (`CLAUDE.md` for rules, the owning rule for skills), never solved by naming the sibling.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: No file under `.claude/rules/` MUST contain the basename (with or without extension) of another file under `.claude/rules/` anywhere in its body.
- **FR-002**: Each of the eight rule-coupled skills' `SKILL.md` files (`clarifier`, `coder`, `adr`, `minto-builder`, `minto-reviewer`, `minto-rewriter`, `scrum-master`, `digital-agency-frontend`) MUST NOT contain the name of any other of these eight skills.
- **FR-003**: `.claude/CLAUDE.md` naming a file under `.claude/rules/`, and a file under `.claude/rules/` naming its corresponding skill(s) below it, MUST remain permitted (downward reference from parent layer to child layer).
- **FR-004**: Resolving each same-layer violation MUST NOT remove any enforceable behavior the violating sentence currently carries — the resulting sentence must state the same criterion in a self-contained way, not merely delete it.
- **FR-005**: `clarifier.md`'s two `permissions.md` references MUST be replaced with self-contained statements of the same criteria (the "Risk" gap-trigger bullet, and the "destructive actions need confirmation" note in "Related").
- **FR-006**: `git-workflow.md`'s `permissions.md` reference MUST be replaced with a self-contained statement that destructive git operations require confirmation.
- **FR-007**: `pyramid-principle.md`'s two `thinking-lenses.md` references MUST be resolved: the "same status as" comparison MUST be restated without naming the file; the "Siblings MECE and one logic per group" bullet MUST be removed from the check list rather than restated, since that check already has a canonical home reachable via `CLAUDE.md`.
- **FR-008**: `pyramid-principle.md`'s `live-documentation.md` reference (in "Where full structure already lives") MUST be restated so the sentence's guidance (a shipped Documentation Artifact's structure is governed by a granularity/layering scheme with four Minto conditions) stands without naming the rule file — pointing instead to the concept in general terms, or removing the sentence if it adds no information beyond what `CLAUDE.md`'s own routing already provides.
- **FR-009**: `docs/claude-config-design.md` MUST be updated with a new subsection documenting the layering rule, framed explicitly as a pyramid with `CLAUDE.md` as the single apex: rules depend only on `CLAUDE.md`; rule-coupled skills depend only on their owning rule and `CLAUDE.md`; same-layer named references are prohibited in both sets (no lateral citation between sibling boxes); downward (parent-to-child) references remain permitted (a parent box may name its own supporting children).
- **FR-010**: A new ADR under `docs/adr/` MUST record this decision with Context, Decision, at least the two rejected alternatives surfaced during clarification (content-dependency-only ban; scope extended to all of `.claude/skills/`), and Consequences (including the `pyramid-principle.md` MECE-bullet removal). The Decision MUST cite Minto's Pyramid Principle (already the grounding for `.claude/rules/pyramid-principle.md` and `.claude/rules/live-documentation.md` §7.1) as the rationale for why sibling boxes at one level never cite each other directly.
- **FR-011**: This feature MUST NOT add a new unconditionally-loaded file under `.claude/rules/` to state the layering rule itself.
- **FR-012**: This feature MUST NOT modify any rule's or skill's downward references to skills (e.g. `skill-routing.md`'s routing table), any Spec Kit standard skill, any utility skill outside the eight listed, or `.claude/CLAUDE.md`'s own structure.

### Key Entities

- **Rule file**: One of the 8 files under `.claude/rules/` (`permissions.md`, `live-documentation.md`, `mcp.md`, `clarifier.md`, `pyramid-principle.md`, `git-workflow.md`, `skill-routing.md`, `thinking-lenses.md`). Unconditionally loaded every session. Its only permitted upward dependency is `.claude/CLAUDE.md`.
- **Rule-coupled skill**: One of the 8 skills already referenced by a rule file (`clarifier`, `coder`, `adr`, `minto-builder`, `minto-reviewer`, `minto-rewriter`, `scrum-master`, `digital-agency-frontend`). Its permitted upward dependencies are its owning rule(s) and `.claude/CLAUDE.md`.
- **Same-layer reference**: A rule file naming another rule file, or one of the eight rule-coupled skills naming another of the eight, anywhere in its body. Prohibited by this feature.
- **Downward reference**: `.claude/CLAUDE.md` naming a rule file, or a rule file naming its corresponding skill(s). Explicitly permitted and unchanged by this feature.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A search of every file under `.claude/rules/` for the basename of every other file under `.claude/rules/` returns zero matches.
- **SC-002**: A search of the eight rule-coupled skills' `SKILL.md` files for each other's skill names returns zero matches (already true; re-verified as part of this feature).
- **SC-003**: `docs/claude-config-design.md` and a new ADR under `docs/adr/` both state the layering rule; a maintainer reading either document can name, without opening any rule file, which same-layer references are prohibited and why the two named alternatives were rejected.
- **SC-004**: The total byte count of `.claude/rules/*.md` does not increase by more than the length of the replacement sentences in FR-005–FR-008 (no new always-loaded content beyond what is strictly needed to keep each rule self-contained).
- **SC-005**: Every existing rule or skill behavior that a violating sentence enforced (destructive-action confirmation, risk-based clarification gate, Pyramid Principle self-check) is still enforced somewhere after the change — verified by reading `CLAUDE.md` + the edited rule together and confirming no criterion silently disappeared.
- **SC-006**: A maintainer can draw the configuration as a 3-level pyramid (`CLAUDE.md` apex → 8 rules → 8 rule-coupled skills) from `docs/claude-config-design.md` alone, with every edge in that drawing pointing downward from parent to child and none drawn between two boxes at the same level.

## Assumptions

- The eight rule-coupled skills list (`clarifier`, `coder`, `adr`, `minto-builder`, `minto-reviewer`, `minto-rewriter`, `scrum-master`, `digital-agency-frontend`) is fixed for this feature per the user's explicit scoping decision; Spec Kit standard skills and utility skills (`apple-notes`, `apple-reminders`, etc.) are out of scope.
- "Depends on" / "same-layer reference" is defined at the strictest level the user selected: any named mention of a sibling file's basename, regardless of whether the mention is a content dependency or a mere discovery pointer.
- No new automated test/lint enforcing this rule going forward is in scope for this feature (out of scope per the explicit "no new always-loaded rule file" decision); enforcement is by convention, documented in `docs/claude-config-design.md` and the ADR, checked manually when a rule is next edited.
- The existing `docs/claude-config-design.md` and `docs/adr/` are the correct canonical homes for this decision, consistent with the precedent set by commit `f61e76f` (which moved rule cross-references to external stable sources for the same self-containment reason) and by spec 028 (which did the equivalent work for the skills layer).
