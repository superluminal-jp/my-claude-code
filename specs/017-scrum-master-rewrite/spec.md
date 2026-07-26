# Feature Specification: Restructure `scrum-master` into a citation-grounded pure Scrum Master playbook

**Feature Branch**: `017-scrum-master-rewrite`

**Created**: 2026-07-26

**Status**: Draft

**Input**: User description: "scrum-masterスキル（.claude/skills/scrum-master/）を、Scrum Guide 2020とその他の規範的出典に厳密に準拠した「純粋なスクラムマスター」プレイブックへ再構成する。現状の記述から出典に基づかない一般論・冗長な説明・余剰の言い換えを排除し、規範的な主張（Scrum Guideの必須事項、役割の境界、イベントの目的等）には既存のsources.md出典タグ（例: [SG20, p.X]）に基づく直接引用または明確な参照を付与して強化する。SKILL.mdおよびreferences/配下の各ファイル（event-playbooks.md, anti-patterns-and-coaching.md, facilitation-and-coaching.md, measurement-and-diagnostics.md, scaling-frameworks.md, scrum-framework.md, scrum-master-role.md, solo-practice.md, sources.md）を対象に、必要に応じて構成・見出し・参照リンク構造を再設計する。既存のルーティング（skill-routing.md記載のトリガー文言）や配布の仕組み（install.sh等)は変更しない。"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Every normative claim is directly traceable to its source (Priority: P1)

A user relying on the `scrum-master` skill's advice — "the Sprint Retrospective is timeboxed to three hours," "the Scrum Master does not own the Sprint Backlog" — can find, next to that claim, a short direct quotation and page citation from the source that says so, rather than a paraphrase they have to trust on faith.

**Why this priority**: This is the core of "strengthen with direct citation." Without it, the rest of the restructuring is cosmetic — the skill's authority claims remain unverifiable, which is exactly what the request is trying to fix.

**Independent Test**: Sample every sentence in `SKILL.md` and each `references/*.md` file that states a Scrum Guide-defined rule, accountability, event, artifact, or value; confirm each carries a `[SG20, p.X]`-style citation accompanied by a short quoted phrase from that page, not a citation alone.

**Acceptance Scenarios**:

1. **Given** a statement about an event's timebox or purpose (e.g., Sprint Review, Daily Scrum), **When** the reader checks its citation, **Then** a short direct quotation from the Scrum Guide page cited appears alongside the paraphrase.
2. **Given** a statement about an accountability boundary (Product Owner / Developers / Scrum Master), **When** the reader checks its citation, **Then** the boundary is backed by a direct quotation from `[SG20]`, not an unsourced assertion.
3. **Given** a statement drawn from a complementary source (Kanban Guide, EBM, DORA, Nexus Guide, anti-pattern articles, research papers), **When** the reader checks its citation, **Then** the source tag matches one already defined in `sources.md` (or a newly added, equally documented entry) and the tier of evidence (normative / official complement / research / contextual) is legible at the point of the claim, not only in `sources.md`'s abstract usage section.
4. **Given** the skill's own operating stance (e.g., "don't impose answers," "diagnose systems, not people"), **When** the reader checks its citation, **Then** it is presented as the skill's own methodological stance and is not dressed up as a Scrum Guide requirement.

---

### User Story 2 - Extraneous, unsourced, or duplicated text is removed (Priority: P2)

A user reading the playbook no longer encounters generic advice that cites nothing, or the same explanation restated in two or three places (e.g., the anti-pattern summary appearing in both `SKILL.md` and `anti-patterns-and-coaching.md`, or event timeboxes restated across `scrum-framework.md`, `sources.md`, and `SKILL.md`).

**Why this priority**: This is the "purity" half of the request — the citation work in User Story 1 only reads as rigorous if it isn't buried in restated filler. It depends on User Story 1's inventory of claims to know what to keep.

**Independent Test**: Diff the restructured files against the current versions; confirm no sentence survives that both (a) makes a factual claim and (b) carries no source tag and no explicit "this is the skill's own stance / a context-dependent technique with no single source" label; confirm each explanation exists in exactly one canonical file with other locations cross-linking to it instead of repeating it.

**Acceptance Scenarios**:

1. **Given** the current text contains a generic, unsourced claim presented as fact (not as the skill's own stance), **When** the restructuring is complete, **Then** the claim is either removed, rewritten as an explicitly labeled stance, or backed by a citation.
2. **Given** the same explanation currently appears in more than one file, **When** the restructuring is complete, **Then** it exists in one canonical location and other locations reference it by link instead of repeating the prose.
3. **Given** the total content the skill now carries, **When** measured against the current version, **Then** it is materially shorter (fewer words/lines) while still covering the three support-mode scenarios (teaching/mentoring, facilitation/coaching, solo practice) the skill currently serves.

---

### User Story 3 - The structure makes the evidence hierarchy and file boundaries legible (Priority: P3)

A contributor opening any single reference file can tell, from its own headings and cross-links, what is Scrum-Guide law, what is official complementary guidance, what is research-backed practice, and what is a context-dependent technique the team must decide for itself — without cross-referencing `sources.md`'s abstract framework to figure it out.

**Why this priority**: This makes User Stories 1 and 2 maintainable going forward, but the skill is already usable and citation-honest without a structural overhaul — this is polish on top of correctness.

**Independent Test**: Open each `references/*.md` file in isolation and confirm its table of contents and section headings reflect the evidence tiers and topics actually present; confirm every internal link resolves to a file that exists.

**Acceptance Scenarios**:

1. **Given** any single reference file, **When** a reader scans its heading structure, **Then** the evidence tier of each section (normative / official complement / research / contextual) is identifiable without opening `sources.md`.
2. **Given** the full set of internal links across `SKILL.md` and `references/*.md`, **When** each is followed, **Then** it resolves to an existing file and section.

---

### Edge Cases

- **A claim that blends a Scrum Guide rule with a complementary practice in one sentence** (e.g., "the Daily Scrum is 15 minutes and often uses Kanban WIP limits") — the two must carry separate citations at their appropriate tier, not one citation covering both.
- **A source that does not offer a clean short quotation** (e.g., a table of contents-only entry, or a claim aggregated from an entire guide rather than one page) — falls back to the existing "direct quotation or clear reference" allowance already named in the user's request; a precise paraphrase with page citation is acceptable when no single quotable sentence exists.
- **The skill's own operating stance overlaps with something Scrum Guide also implies** (e.g., "don't act as project manager" echoes the Guide's accountability boundaries) — cite the Guide for the boundary itself, and separately label the imperative tone ("don't do X") as the skill's own guidance built on that boundary.
- **A reference file shrinks enough that its table of contents or a whole section becomes unnecessary** — remove the now-empty structure rather than leaving a stub.
- **The YAML frontmatter (`name`, `description`, `when_to_use`) and the routing rules in `skill-routing.md`** are load-bearing for skill discovery and are explicitly out of scope for this rewrite — restructuring must not alter their wording.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Every sentence in `SKILL.md` or `references/*.md` that states a Scrum Guide-defined rule, accountability boundary, event purpose/timebox, artifact, commitment, or value MUST carry a `[SG20, p.X]`-style citation accompanied by a short direct quotation from the cited page.
- **FR-002**: Every sentence that states a claim from a complementary source (Nexus Guide, Kanban Guide, EBM Guide, DORA, Agile Manifesto, anti-pattern articles, cited research, cited practitioner books) MUST carry that source's existing tag from `sources.md` (or a new tag added to `sources.md` with the same documentation standard as existing entries), plus a short quotation or precise paraphrase, and MUST remain visibly distinguished from Scrum Guide requirements.
- **FR-003**: Direct quotations MUST be short (a phrase or clause, not an extended passage) — the rewrite reinforces claims with proof of source, not with reproduced text volume, consistent with `sources.md`'s existing "原文引用は必要最小限にし" citation rule.
- **FR-004**: Any statement presenting the skill's own methodological stance (e.g., "don't impose decisions," "diagnose systems, not individuals") MUST be clearly marked as the skill's own guidance rather than attributed to a source that does not make that claim.
- **FR-005**: Any sentence that makes a factual or normative claim and carries neither a source citation nor an explicit "this is the skill's own stance" or "this is a context-dependent technique" label MUST be removed or rewritten to satisfy FR-001/FR-002/FR-004.
- **FR-006**: An explanation that currently appears in more than one file (e.g., anti-pattern lists, event timeboxes, accountability boundaries) MUST be consolidated into exactly one canonical file; other locations MUST link to it instead of restating it.
- **FR-007**: The rewrite MUST NOT reduce topical coverage — every situation currently routed to a specific reference file (per `SKILL.md`'s reference table) MUST still be addressed by some file after restructuring.
- **FR-008**: Section headings and tables of contents in each `references/*.md` file MAY be restructured to make each section's evidence tier (normative / official complement / research / contextual) identifiable at the point the claim is made.
- **FR-009**: Every internal link between `SKILL.md` and `references/*.md`, and among the reference files themselves, MUST resolve to an existing file (and, where a specific section is linked, an existing heading).
- **FR-010**: The YAML frontmatter of `SKILL.md` (`name`, `description`, `when_to_use`) MUST remain unchanged in wording.
- **FR-011**: The rewrite MUST NOT modify `.claude/rules/skill-routing.md`, any installer/distribution mechanism (`install.sh` and equivalents), or `scripts/flow_metrics.py` and its declared permission.
- **FR-012**: The rewrite MUST NOT change the routing regression suite's expected outcomes (`tests/run-skill-routing.sh`, `tests/skill-routing/007-scrum-facilitation.md`, `tests/run-codex-sync.sh`) — those suites MUST continue to pass unchanged.
- **FR-013**: Where a complementary source's own scope note already exists in `sources.md` (e.g., DORA's "only for software delivery, not cross-team comparison," EBM's outcome focus, psychological safety's non-causal framing), that scope note MUST remain attached wherever the source is cited in `SKILL.md` or reference files, not dropped during trimming.
- **FR-014**: Every quotation and page/section citation added or changed during implementation MUST be verified by directly reading the corresponding primary-source file in `/Users/taikiogihara/Downloads/scrum_official_docs/` — not reconstructed from memory or from the current prose in `sources.md` — before it is written into `SKILL.md` or a reference file.
- **FR-015** (optional): `scaling-frameworks.md` MAY gain one additional entry for Scrum@Scale, in the same brief, one-paragraph-plus-link style as the existing LeSS and SAFe entries, sourced from the locally supplied Scrum@Scale Guide. This is a bounded addition, not a new deep-dive section, and is not required for the rewrite to satisfy its other requirements.

### Key Entities

- **Normative claim**: A statement asserting what the Scrum Guide itself requires or defines (rule, accountability, event, artifact, commitment, value). Requires a `[SG20, p.X]` citation plus short direct quotation.
- **Complementary claim**: A statement drawn from an official complementary guide, research, or practitioner source distinct from the Scrum Guide. Requires its own existing or newly documented source tag, kept visually distinct from normative claims.
- **Skill stance statement**: A statement of the skill's own methodological position (not itself a citable external claim), explicitly labeled as such.
- **Canonical location**: The single file where a given explanation lives in full; all other files reference it by link.
- **Evidence tier**: One of the four tiers already defined in `sources.md` (規範 / 公式補完 / 研究・実務知見 / 文脈依存の技法), now made legible at each claim's point of use, not only in the abstract usage section.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of sampled normative claims (Scrum Guide rules, accountabilities, event purposes/timeboxes, artifacts, commitments, values) across `SKILL.md` and `references/*.md` carry both a page citation and a short direct quotation from that page.
- **SC-002**: 100% of sampled complementary-source claims carry a source tag traceable to an entry in `sources.md`, with the applicable scope/caveat note preserved.
- **SC-003**: Zero sentences remain that state a factual or normative claim without a citation or an explicit stance/contextual-technique label.
- **SC-004**: Zero duplicated explanations remain across files — each explanation exists in exactly one canonical location, with cross-references elsewhere.
- **SC-005**: The combined word count of `SKILL.md` plus `references/*.md` is reduced relative to the current version, while every reference-file routing entry in `SKILL.md`'s table still points to a file that covers its stated situation.
- **SC-006**: Zero broken internal links across the restructured files.
- **SC-007**: The existing routing regression suites (`tests/run-skill-routing.sh`, `tests/run-codex-sync.sh`) pass unchanged after the rewrite.
- **SC-008**: A reader opening any single `references/*.md` file can identify the evidence tier of each of its sections without consulting `sources.md`.

## Assumptions

- **"Direct citation" means short, attributed quotation, not extended reproduction.** The user's request to add direct quotations is read alongside `sources.md`'s own existing rule that original-text quotation should be minimal; the rewrite adds a short quoted phrase per normative claim rather than reproducing paragraphs of the Scrum Guide or other cited works. The Scrum Guide, Nexus Guide, Kanban Guide for Scrum Teams, and EBM Guide are each published by Scrum.org under terms that permit attributed reuse, which is why short quotation from them is workable at all; quotations from copyrighted books or journal articles (e.g., Edmondson 1999, Adkins 2010, Derby & Larsen 2006) are kept to the same short-phrase standard.
- **A local primary-source corpus is available and is the source of truth for quotations.** The user has supplied `/Users/taikiogihara/Downloads/scrum_official_docs/`, containing the Scrum Guide 2020, Nexus Guide 2021, Kanban Guide 2021, EBM Guide 2024, and Scrum@Scale Guide (v1.02 JA / v2.1 EN), each in English and Japanese where applicable, plus a Japanese Agile Manifesto translation and the community-authored Scrum Guide Expansion Pack. Every quotation and page citation added during implementation MUST be verified against these primary files (opened and read directly) rather than reconstructed from memory or from `sources.md`'s existing prose — this is a direct application of the Core Principle to verify with tools before asserting and never fabricate citations or page numbers. Where the skill body is Japanese, quotations are drawn from the Japanese-language edition of the same document so the page/section reference matches what a Japanese-reading user would open.
- **The Scrum Guide Expansion Pack is complementary community material, not normative.** It is Scrum.org-community-authored supplementary essays (e.g., psychological safety, complexity, AI and Scrum), not part of the Scrum Guide itself. It may be cited at the "research・実務知見" or "文脈依存の技法" tier where directly relevant to an existing claim (e.g., supplementing the psychological-safety or complexity discussion already in the skill), but MUST NOT be cited as if it were Scrum Guide content.
- **Scrum@Scale is newly available in full but is not currently part of the skill.** `scaling-frameworks.md` today briefly covers Nexus, LeSS, and SAFe only. Adding a parallel one-paragraph Scrum@Scale entry (matching the existing brevity of the LeSS/SAFe entries, now backed by the actual guide rather than absent) is in scope as a proportionate, optional addition — not a deep new section — since the user supplied the official guide alongside the others already cited. A deeper Scrum@Scale treatment is out of scope.
- **"Pure Scrum Master" does not mean removing complementary practice.** The skill's remit (facilitation technique, anti-pattern diagnosis, flow/quality measurement, scaling frameworks) is unchanged; "purity" is about grounding every claim in a legible source or explicit label, not about narrowing scope to the Scrum Guide alone.
- **Frontmatter and routing are frozen.** `name`, `description`, `when_to_use` in `SKILL.md`, and the routing rule text in `.claude/rules/skill-routing.md`, are load-bearing for skill discovery and out of scope, per the user's explicit instruction.
- **Distribution and tooling are frozen.** `install.sh`-equivalent distribution mechanisms and `scripts/flow_metrics.py` (including its declared tool permission) are unchanged; this is a content/structure rewrite only.
- **No research beyond the supplied corpus and existing `sources.md` entries is required.** If a specific normative claim needs a source not yet in `sources.md` and not present in the supplied corpus, a new entry may be added following the same documentation standard as existing entries, but the rewrite does not need to survey literature beyond what filling such gaps requires.
