# Feature Specification: Minimize scrum-master Skill to Official Scrum Guide Content

**Feature Branch**: `022-minimize-scrum-master-skill`

**Created**: 2026-08-15

**Status**: Draft

**Input**: User description: "@.claude/skills/scrum-master/references/2020-Scrum-Guide-US.pdf @.claude/skills/scrum-master/references/2020-Scrum-Guide-Japanese.pdf 公式スクラムガイドの内容に基づくものに @.claude/skills/scrum-master/ スキルを最小化。/clarifier"

## Clarifications

### Session 2026-08-15

- Q: scrum-masterスキルを「公式Scrum Guide(2020)ベース」に最小化するとして、どこまで削るか？ → A: Scrum Guideのみに厳格化— SG20(英語版/日本語版PDF)に明記された定義・役割・イベント・作成物・価値基準のみを残し、Nexus Guide, EBM Guide, Kanban Guide, DORA, 心理的安全性研究, Agile Retrospectives, Coaching Agile Teams, アンチパターン記事(SAP/ZBS/AAP), LeSS/SAFe/Scrum@Scaleへの参照・引用・推奨内容を全て削除する。
- Q: scripts/flow_metrics.py（Kanban Guide由来）はどうするか？ → A: 削除する。
- Q: Scrum Guideが規定しないHOW（レトロスペクティブの進め方、コーチングスタンス、ファシリテーション技法）はどうするか？ → A: 削除し、Scrum Guideが言う各イベントの目的とタイムボックスのみ残す。

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Strip references to a single normative source (Priority: P1)

As a maintainer of the scrum-master skill, I want the skill's reference material to cite only the official Scrum Guide (2020 edition), so that every claim in the skill can be traced to the single normative source instead of being diluted by supplementary frameworks and research the skill currently blends in.

**Why this priority**: This is the core of the request — without it, nothing else in the minimization has happened. It is also the highest-risk step (largest deletion), so validating it first surfaces any content that turns out to be load-bearing.

**Independent Test**: Search every file under `.claude/skills/scrum-master/` for a citation tag other than `[SG20]` (e.g. `[NXG]`, `[AM01]`, `[EBM24]`, `[KGS21]`, `[DORA26]`, `[EDM99]`, `[ART]`, `[ICA]`, `[SAP]`, `[ZBS]`, `[AAP]`, `[LESS]`, `[SAFE]`, `[SC@S]`); confirm zero matches remain, and that `references/sources.md` lists only the Scrum Guide entry.

**Acceptance Scenarios**:

1. **Given** the current skill cites 14 distinct sources in `references/sources.md`, **When** the minimization is applied, **Then** `references/sources.md` retains only the Scrum Guide (2020) entry and the citation rule for it.
2. **Given** `references/scaling-frameworks.md`, `references/measurement-and-diagnostics.md`, `references/anti-patterns-and-coaching.md`, `references/facilitation-and-coaching.md`, and `scripts/flow_metrics.py` (plus its `__pycache__`) exist today and are sourced entirely from non-Scrum-Guide material, **When** the minimization is applied, **Then** none of these files exist in the skill directory.
3. **Given** `references/scrum-master-role.md` contains a "コーチングスタンス" section that the file itself marks as absent from the Guide (cited to `[ICA]`), **When** the minimization is applied, **Then** that section is removed from the file.

---

### User Story 2 - Limit event guidance to the Guide's stated purpose and timebox (Priority: P2)

As a Scrum Master using the skill, I want guidance on Scrum events limited to what the Scrum Guide itself states about each event's purpose and timebox, so that the skill never presents practitioner conventions (retrospective formats, facilitation agendas, coaching-stance selection) as if the Guide required them.

**Why this priority**: This is the second-largest source of non-Guide content by volume and the part most likely to be silently reintroduced (e.g., by copying "helpful" facilitation detail back in) if not explicitly scoped. It depends on User Story 1's source-citation cleanup being in place first.

**Independent Test**: Ask the skill "How do I run a Sprint Retrospective?" and confirm the answer states only the Guide's purpose ("plan ways to increase quality and effectiveness") and timebox (3 hours for a one-month Sprint), without a staged facilitation structure or named retrospective formats.

**Acceptance Scenarios**:

1. **Given** a user asks about Sprint Retrospective facilitation, **When** the minimized skill responds, **Then** it states only the Guide's purpose and timebox for that event and does not offer a stage-by-stage facilitation structure, named retro format, or improvement-experiment template.
2. **Given** a user asks which coaching stance (teacher/mentor/facilitator/coach) to take, **When** the minimized skill responds, **Then** it does not present a stance taxonomy, since the Guide defines no such stances.
3. **Given** a user asks about Daily Scrum, Sprint Planning, Sprint Review, or Product Backlog Refinement, **When** the minimized skill responds, **Then** the answer is limited to the purpose, participants, and timebox (where the Guide defines one) stated in the Scrum Guide.

---

### User Story 3 - Keep the skill's own routing free of dead links and scope overreach (Priority: P3)

As a maintainer of this repository, I want `SKILL.md`'s reference-file table and workflow instructions to only point at files and practices that still exist after minimization, so that the skill doesn't produce dead links or contradict its own narrowed scope.

**Why this priority**: This is cleanup that depends on User Stories 1 and 2 being complete — it has no independent content of its own, only consistency with what remains. Lowest risk, but required for the skill to be usable at all after the deletions above.

**Independent Test**: Read `SKILL.md` (and any surviving `references/*.md`) after the change; confirm every relative markdown link resolves to a file that still exists, and no section instructs the skill to compute flow metrics, recommend a scaling framework, or select a coaching stance.

**Acceptance Scenarios**:

1. **Given** `SKILL.md`'s reference-file table currently has a row for each of the deleted files, **When** the minimization is applied, **Then** every remaining row points to a file that still exists.
2. **Given** a user asks something outside the new scope (e.g., "compute our team's cycle time" or "which scaling framework should we adopt"), **When** the minimized skill responds, **Then** it states that this is out of scope for a Scrum-Guide-only skill rather than answering from the removed material.

---

### Edge Cases

- What happens when a user explicitly asks for a Nexus/LeSS/SAFe/Scrum@Scale recommendation after minimization? The skill states this is out of scope and does not answer from memory of the removed content.
- What happens when a user asks the skill to compute flow metrics (Cycle Time, WIP, Throughput, Work Item Age) from ticket data? The skill states that capability was removed as out of scope and does not attempt an ad hoc computation or substitute estimate.
- What happens to cross-references inside files that are kept (e.g., `scrum-master-role.md` or `scrum-framework.md` linking to a now-deleted file)? Those links must be removed or updated so no dead link remains anywhere in the skill.
- What happens to the previously delivered scrum-master specs (016, 017, 018) that established the richer, multi-source design this feature narrows? They are not modified retroactively; this feature is treated as a superseding scope decision where it conflicts with their broader design.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The skill's source list (`references/sources.md`) MUST cite only the official Scrum Guide (2020 edition, English and Japanese PDFs already present under `references/`) as a normative or supplementary source; all other source entries currently present (Nexus Guide, Manifesto for Agile Software Development, Evidence-Based Management Guide, The Kanban Guide for Scrum Teams, DORA metrics, Edmondson's psychological-safety research, Agile Retrospectives, Coaching Agile Teams, Scrum.org/Zombie Scrum/Agile Alliance anti-pattern material, LeSS, SAFe, Scrum@Scale) MUST be removed.
- **FR-002**: `references/scaling-frameworks.md` MUST be deleted, since none of its content (Nexus, LeSS, SAFe, Scrum@Scale) is defined by the Scrum Guide.
- **FR-003**: `references/measurement-and-diagnostics.md` MUST be deleted, since its metric guidance (flow metrics, EBM Key Value Areas, DORA metrics) is sourced from the Kanban Guide, the EBM Guide, and DORA rather than the Scrum Guide.
- **FR-004**: `references/anti-patterns-and-coaching.md` MUST be deleted, since its anti-pattern taxonomy is sourced from Scrum.org, Zombie Scrum, and Agile Alliance material rather than the Scrum Guide.
- **FR-005**: `references/facilitation-and-coaching.md` MUST be deleted, since its facilitation techniques and coaching-stance model are sourced from Coaching Agile Teams, psychological-safety research, and unsourced practitioner convention rather than the Scrum Guide.
- **FR-006**: `scripts/flow_metrics.py` and its `__pycache__` artifacts MUST be deleted, since the flow metrics it computes (Cycle Time, Work Item Age, Throughput, SLE) are Kanban Guide concepts, not Scrum Guide concepts.
- **FR-007**: `references/scrum-master-role.md` MUST retain only the Scrum-Guide-grounded content on the Scrum Master's core accountabilities, service to the Team/Product Owner/organization, and role boundaries; its coaching-stance taxonomy (teacher/mentor/facilitator/coach/conflict navigator) MUST be removed.
- **FR-008**: Any guidance for a Scrum event (Sprint, Sprint Planning, Daily Scrum, Sprint Review, Sprint Retrospective, Product Backlog Refinement) retained anywhere in the skill MUST be limited to the purpose, participants, and timebox the Scrum Guide itself states; process techniques, retrospective formats, agenda breakdowns, improvement-experiment templates, or facilitation steps not stated in the Scrum Guide MUST NOT remain.
- **FR-009**: No file remaining in the skill MUST link to, reference, or route to a file or practice deleted under FR-002 through FR-006 (coaching stances, anti-pattern taxonomy, flow-metrics script, scaling frameworks, measurement/diagnostics guidance) — every relative link must resolve to a file that still exists.
- **FR-010**: `SKILL.md`'s description, `when_to_use` trigger text, and stated principles MUST describe the skill as scoped to the official Scrum Guide (2020) only, without implying coverage of scaling, flow-metrics computation, anti-pattern taxonomies, or facilitation-technique coaching.
- **FR-011**: When a user asks about a topic the minimized skill no longer covers (e.g., Nexus/LeSS/SAFe/Scrum@Scale scaling, flow-metrics/velocity computation, a specific retrospective format, or coaching-stance selection), the skill MUST state that this is out of scope for its Scrum-Guide-only guidance rather than answering from the removed material.
- **FR-012**: All content currently in the skill that is directly grounded in the Scrum Guide — the three pillars of empiricism, the five Scrum values, the accountabilities of Product Owner/Scrum Master/Developers, each event's Guide-stated purpose and timebox, the artifact commitments, the "enacting only parts of Scrum is not Scrum" statement (Guide p.13), and the Scrum Master's boundaries as literally stated by the Guide — MUST remain accessible in the minimized skill.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Searching every file in the skill for a citation other than the Scrum Guide (2020) returns zero matches.
- **SC-002**: The skill's `references/` directory contains only the two Scrum Guide PDFs plus markdown files whose content traces solely to the Scrum Guide; its `scripts/` directory contains no computation script.
- **SC-003**: For each of the six Scrum events, asking the skill "how do I run this event" returns only the Guide-stated purpose, participants, and timebox — no additional facilitation technique, format, or template appears in the answer.
- **SC-004**: Asking the skill about a removed topic (scaling framework choice, flow-metric computation, coaching-stance selection, anti-pattern taxonomy) results in an explicit out-of-scope statement, not an answer drawn from the removed material, in 100% of trials.
- **SC-005**: Every relative markdown link remaining anywhere in the skill resolves to a file that exists in the skill directory (zero dead links).

## Assumptions

- The two Scrum Guide PDFs already present under `references/` (`2020-Scrum-Guide-US.pdf`, `2020-Scrum-Guide-Japanese.pdf`) remain the sole normative source documents; no new source material is introduced by this change.
- "Official Scrum Guide" means the November 2020 edition (Ken Schwaber and Jeff Sutherland), the same edition currently cited as `[SG20]` in `references/sources.md`; no other edition or future revision is in scope.
- The Japanese Scrum Guide PDF's own translator appendix (the "2020年版での変更点" section, JA pp.16–17) is treated as part of the official Guide document itself, since it ships inside the official translated PDF rather than being third-party material, and may remain cited as `[SG20, JA pp.16–17]`.
- This minimization supersedes the broader-scope design established by the prior scrum-master specs (`016-scrum-master-skill`, `017-scrum-master-rewrite`, `018-remove-solo-practice`) wherever the two conflict; those specs are not retroactively edited.
- The skill's invocation triggers (`.claude/rules/skill-routing.md`, the `when_to_use` field) are unaffected — this feature narrows the skill's content, not when it is routed to.
- No migration guide or user-facing announcement is required beyond the skill's own out-of-scope responses (FR-011); a conversation that previously relied on removed material (scaling advice, flow metrics, coaching stances) will simply be told, going forward, that the topic is out of scope.
