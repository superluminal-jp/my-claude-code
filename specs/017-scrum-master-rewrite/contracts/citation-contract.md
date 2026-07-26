# Contract: Citation and quotation correctness

**Feature**: 017-scrum-master-rewrite | **Date**: 2026-07-26

## Purpose

This feature's externally-visible guarantee is not an API — it is that **every claim a reader of `SKILL.md` or `references/*.md` can check, can be checked**: traced to a quoted primary source, an explicitly labeled complementary source with its scope intact, or explicitly marked as the skill's own stance. This contract states what "a claim is properly cited" means, so it can be checked sentence-by-sentence during implementation and review, rather than assumed from the presence of a bracketed tag.

## C1 — Every normative sentence carries proof, not just a label

A sentence stating a Scrum Guide rule, accountability, event purpose/timebox, artifact, commitment, or value MUST carry both a `[SG20, p.X]` tag and a short direct quotation from that exact page.

**Check**: for each such sentence, the quotation appears verbatim (modulo whitespace/punctuation) in the corresponding page of `Scrum-Guide-2020.pdf` (or `Scrum-Guide-2020-Japanese.pdf` if the quotation is in Japanese, adjusted for the +1 page offset per `research.md` R2).

## C2 — Complementary claims keep their tier and their scope note

A sentence drawing on `[NXG]`, `[KGS21]`, `[EBM24]`, `[DORA26]`, `[AM01]`, `[EDM99]`, `[ART]`, `[ICA]`, `[SAP]`, `[ZBS]`, `[AAP]`, `[LESS]`, `[SAFE]`, or a newly documented tag MUST carry that tag plus a short quotation/precise paraphrase, and MUST NOT be phrased so it reads as a Scrum Guide requirement.

If `sources.md` already attaches a scope/caveat note to that source (DORA's software-delivery-only scope, EBM's outcome framing, psychological safety's non-causal framing), the note MUST travel with the claim at its point of use, not only live in `sources.md`.

**Check**: grep each in-body citation tag; confirm it resolves to a `sources.md` entry; confirm the scope note (if one exists in `sources.md` for that tag) appears at least once near each in-body use, either inline or via an unambiguous cross-reference.

## C3 — No unlabeled factual claims survive

A sentence making a factual or normative assertion MUST carry either a citation (C1/C2) or an explicit label identifying it as the skill's own stance or a context-dependent technique with no single source.

**Check**: read every declarative sentence in `SKILL.md` and each `references/*.md`; classify as (a) cited claim, (b) labeled stance/contextual technique, or (c) neither. Zero sentences in category (c) (SC-003).

## C4 — Skill-stance statements are not misattributed

A statement of the skill's own methodological position (e.g., "diagnose systems, not individuals") MUST NOT carry a source tag that does not itself make that claim, even where the stance is built on a cited boundary.

**Check**: for each stance statement, confirm any adjacent citation supports only the boundary/fact it actually names, and the imperative/stance layered on top is unattributed or explicitly self-attributed ("本スキルの方針として").

## C5 — One canonical location per explanation

Where `data-model.md`'s "Canonical location" table names a cluster (event timeboxes, SM accountability boundary, support-mode taxonomy), the full explanation MUST exist in exactly the designated canonical file; every other file's occurrence MUST be a short pointer/link, not a restatement of the same figures or table.

**Check**: diff the non-canonical location's text against its pre-rewrite version; confirm the specific restated figures/table are gone and replaced by a link; confirm the canonical file still contains the full content.

**Non-goal**: this clause does not apply to the acceptable summary→detail layering listed in `data-model.md`'s "Non-duplication note" — those are preserved as-is.

## C6 — Evidence tier is legible at point of use

Each section making claims of a single evidence tier (規範/公式補完/研究・実務知見/文脈依存の技法) MUST make that tier identifiable from its own heading, a leading label, or its grouping — without requiring the reader to open `sources.md`.

**Check**: open each `references/*.md` file in isolation; for each section, confirm the tier is stated or unambiguous from structure (SC-008).

## C7 — Frontmatter, routing, and distribution are untouched

`SKILL.md`'s YAML frontmatter (`name`, `description`, `when_to_use`), `.claude/rules/skill-routing.md`, any installer/distribution mechanism, and `scripts/flow_metrics.py` (including its declared permission) MUST be byte-identical to their pre-rewrite state.

**Check**: `git diff` shows no changes to these paths; `tests/run-skill-routing.sh`, `tests/skill-routing/007-scrum-facilitation.md`, and `tests/run-codex-sync.sh` pass unchanged (FR-012).

## C8 — Links resolve

Every internal Markdown link between `SKILL.md` and `references/*.md`, and among the reference files, MUST resolve to an existing file and (where a heading anchor is given) an existing heading.

**Check**: extract each `](...)` target that is not an external URL; resolve relative to the containing file; assert existence (SC-006).
