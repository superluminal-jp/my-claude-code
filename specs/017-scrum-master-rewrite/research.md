# Phase 0 Research: Restructure `scrum-master` into a citation-grounded pure Scrum Master playbook

## R1 — How to source and verify quotations

**Decision**: Every quotation and page/section citation is produced by directly opening the corresponding file in the locally supplied corpus (`/Users/taikiogihara/Downloads/scrum_official_docs/`) with the Read tool, copying the exact wording, and recording the page shown in that PDF — never reconstructed from memory or from the current prose already in `sources.md`.

**Rationale**: Core Principle #1 (verify with tools before asserting; never fabricate citations, paths, or numbers) is a hard constraint here, not a style preference, because the deliverable's entire value proposition is "every claim is traceable." A rewrite that adds quotation marks around a remembered paraphrase would look more rigorous while being less trustworthy than the current text.

**Alternatives considered**: Relying on the existing `sources.md` summaries (already page-cited) as the source of quotes was rejected — those summaries are themselves paraphrases, and quoting a paraphrase as if it were the primary text would misattribute the paraphraser's wording to Schwaber & Sutherland (or the other authors). Fetching the documents fresh from the web was unnecessary and slower: the user supplied local files precisely to avoid that, and the environment note bundled in the corpus (`公式文書リンク集.md`) records that a prior sandboxed session couldn't reach `scrumguides.org` at all — so the local corpus is also the more reliable path.

## R2 — Scrum Guide page-number convention across languages

**Finding**: The locally supplied English and Japanese Scrum Guide 2020 PDFs do **not** share pagination. Verified by direct inspection:

| Section | English PDF page | Japanese PDF page |
|---|---|---|
| Scrum Definition / スクラムの定義 | p.3 | p.4 |
| Scrum Team / スクラムチーム | p.5 | p.6 |
| Scrum Master / スクラムマスター | p.6 | p.7 |
| Scrum Events / スクラムイベント | p.7 | p.8 |
| Scrum Artifacts / スクラムの作成物 | p.10 | p.11 |
| End Note | p.13 | p.14 |

The Japanese edition is offset by **+1 page** throughout the body, because its table of contents spans two pages (it lists extra end-matter sections — 翻訳について, 用語集, 変更点 — that the English TOC doesn't carry as separate entries) where the English TOC fits on one page. Existing `sources.md` citations (e.g. `p.3` for the Scrum definition) match the **English** pagination, which is also the pagination scrumguides.org and the wider English-language Scrum literature use as the de facto universal reference.

**Decision**: Keep the English edition's page numbers as the canonical `[SG20, p.X]` reference (no change to the existing convention), continue quoting the Japanese official translation's wording for the Japanese-language skill body, and add one clarifying line to `sources.md`'s `[SG20]` entry stating that page numbers follow the English edition and that the Japanese PDF is offset by +1 page from "スクラムの定義" onward. This is cheaper and more maintainable than dual-citing every instance, and it directly prevents a reader who opens the Japanese PDF from concluding a citation is wrong when it is just a different edition's pagination.

**Alternatives considered**: Dual-citing every claim as `[SG20, EN p.X / JA p.Y]` was rejected as disproportionate — it would roughly double the citation apparatus's visual weight for a fact (the offset) that is constant and only needs to be stated once. Switching entirely to Japanese-edition page numbers was rejected because it would break alignment with the existing `[SG20, p.X]` citations already scattered through the skill and with how the guide is cited in English-language material the skill also references.

**Verification obligation carried into tasks.md**: The same page-alignment check must be repeated per source during implementation (not assumed) — Nexus Guide, Kanban Guide, and EBM Guide each have their own English/Japanese PDF pair in the corpus, and each must be spot-checked for the same kind of offset before its citations are finalized, rather than assuming they match or all share the Scrum Guide's +1 pattern.

## R3 — Corpus-to-citation-tag mapping

**Decision**: Map the locally supplied corpus to the existing `sources.md` tags so implementation tasks know which local file backs which citation:

| Tag | `sources.md` title | Local file |
|---|---|---|
| `[SG20]` | The Scrum Guide | `Scrum-Guide-2020.pdf`, `Scrum-Guide-2020-Japanese.pdf` |
| `[NXG]` | The Nexus Guide | `Nexus-Guide-2021.pdf`, `Nexus-Guide-2021-Japanese.pdf` |
| `[KGS21]` | The Kanban Guide for Scrum Teams | `Kanban-Guide-2021.pdf`, `Kanban-Guide-2021-Japanese.pdf` |
| `[EBM24]` | Evidence-Based Management Guide | `Evidence-Based-Management-Guide-2024.pdf`, `...-Japanese.pdf` |
| `[AM01]` | Manifesto for Agile Software Development | `アジャイルソフトウェア開発宣言.md` (JA translation) |
| (new, optional — FR-015) | Scrum@Scale Guide | `scrum-at-scale-guide-v2_1.pdf` (EN), `scrum-at-scale-guide-v1_02-japanese.pdf` (JA — note version mismatch, v1.02 JA vs v2.1 EN; if used, the citation must say which version it quotes) |
| (not currently tagged) | Scrum Guide Expansion Pack | `Scrum_Guide_Expansion_Pack/content/**/_index*.md` — community-authored, complementary tier only (see R4) |

`[DORA26]`, `[EDM99]`, `[ART]`, `[ICA]`, `[SAP]`, `[ZBS]`, `[AAP]`, `[LESS]`, `[SAFE]` have no corresponding local file (books, journal article, and web-only blog series); their existing `sources.md` citations remain as page/URL references without a local verification step, since no primary copy was supplied for them. Quotation from these stays at the same short-phrase standard already used, drawn from `sources.md`'s existing accurate paraphrase where no local primary text is available to re-verify against.

## R4 — Treatment of the Scrum Guide Expansion Pack

**Finding**: `Scrum_Guide_Expansion_Pack/` is a set of community-authored essays (`content/<topic>/_index.md`, multiple languages) distributed under its own `LICENSE` file, published by the Scrum Guide's authors' broader community initiative — not part of the Scrum Guide itself and not co-authored by Schwaber/Sutherland as the core Guide is. Topics present include `psychological-safety-in-scrum-teams`, `complexity`, `ai-and-scrum`, `product-thinking`, `holistic-testing`, among others.

**Decision**: Treat as tier 3/4 (research・実務知見 or 文脈依存の技法) per `sources.md`'s existing hierarchy, never as tier 1 (規範). Cite it only where it directly supplements an existing claim already in the skill (e.g., `psychological-safety-in-scrum-teams` alongside `[EDM99]` in `facilitation-and-coaching.md`; `complexity` alongside the "Scrum addresses complex problems" claim in `scrum-framework.md`). Do not use it to introduce new topics not already in the skill's scope — that would expand scope beyond the user's request.

## R5 — Scrum@Scale: bounded, optional addition

**Finding**: The corpus includes the official Scrum@Scale Guide (English v2.1, Japanese v1.02 — versions do not match; if the Japanese translation is quoted, its own version must be named rather than implied to be a translation of v2.1). `scaling-frameworks.md` today covers Nexus, LeSS, SAFe in one short paragraph each with a single source tag; Scrum@Scale is a well-known fourth scaling approach in the same reference class and the guide is now on hand to source it properly, unlike before.

**Decision**: Per spec FR-015, this is an optional, proportionate addition — one paragraph matching the existing LeSS/SAFe brevity and citation style, added only if it doesn't require expanding the file's structure. Not required for the feature's other requirements to be satisfied.

## R6 — Classifying "duplication worth fixing" vs. acceptable summary/detail layering

**Finding**: Not every place the same topic appears twice is a problem. The skill already uses a working pattern: `SKILL.md` states a compressed principle or one-paragraph summary and links to a reference file for the full treatment (e.g., the anti-pattern summary in `SKILL.md`'s "アンチパターンを検知する（要点）" section explicitly links to `anti-patterns-and-coaching.md` for "検知の全リストと自己点検"; the flow-metrics script instructions live in full in `SKILL.md` and are referenced, not repeated, from `measurement-and-diagnostics.md` and `solo-practice.md`). That layering is intentional and should be preserved, not "fixed away."

The duplication FR-006 targets is where the **same level of specificity** is restated — the same numbers, the same table, the same worked explanation — in two files with neither being a compressed pointer to the other. Concretely identified in this rewrite (detailed in `data-model.md`):

1. Event timeboxes/purposes: fully stated in `scrum-framework.md`'s events table AND restated at the same numeric detail in `event-playbooks.md`'s "共通設計" section.
2. SM accountability boundary: `SKILL.md`'s "アカウンタビリティの境界" table restates, at the same detail level, what `scrum-master-role.md`'s "中核的なアカウンタビリティ" plus `scrum-framework.md`'s accountability paragraph already cover.
3. Coaching/support-mode taxonomy: three overlapping enumerations exist — `SKILL.md`'s "支援モードを選ぶ" table (5 modes), `facilitation-and-coaching.md`'s "スタンス" section (4 modes), and `scrum-master-role.md`'s "コーチングスタンス" table (6 stances) — covering materially the same teach/mentor/facilitate/coach spectrum from three angles with no single canonical source.

**Decision**: For each of the three, designate one canonical file (see `data-model.md`) and convert the others to short pointers, following the existing anti-pattern/flow-metrics layering as the model to replicate, not invent.

## R7 — Copyright-safe quotation length

**Decision**: Quotations added during implementation are capped at roughly one sentence or clause (well under a paragraph), consistent with `sources.md`'s pre-existing citation rule ("原文引用は必要最小限にし"). The Scrum Guide, Nexus Guide, Kanban Guide, and EBM Guide are Scrum.org/Schwaber-Sutherland publications offered under Creative Commons Attribution-ShareAlike 4.0 (confirmed on the cover/back matter of the locally supplied PDFs themselves — see the license notice on `Scrum-Guide-2020.pdf` page 2), which explicitly permits this kind of attributed reuse. Quotations from copyrighted books or a journal article (Edmondson 1999, Adkins 2010, Derby & Larsen 2006) are held to the same short-phrase cap even though no local copy was supplied to verify them against.

## Output

All `NEEDS CLARIFICATION` items from the Technical Context are resolved above (R1–R7). No unresolved unknowns remain; proceeding to Phase 1.
