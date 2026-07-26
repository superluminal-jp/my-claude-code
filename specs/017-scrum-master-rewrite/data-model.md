# Phase 1 Data Model: Restructure `scrum-master` into a citation-grounded pure Scrum Master playbook

This feature has no runtime data model — it restructures Markdown content. The "entities" below are the conceptual units the rewrite manipulates, carried over from `spec.md`'s Key Entities and made concrete against the actual files.

## Entity: Normative claim

A sentence asserting what the Scrum Guide itself requires or defines.

**Attributes**: source tag (`[SG20, p.X]`), a short direct quotation from that page, the claim's own paraphrase.

**Validation rule** (FR-001): tag and quotation both present; quotation verified against the primary PDF per `research.md` R1/R2, not memory.

**Where found today** (citation present, quotation absent — to be reinforced): `SKILL.md` (アカウンタビリティの境界 table, 標準ワークフロー section), `scrum-framework.md` (every `[SG20, p.X]`-tagged paragraph), `scrum-master-role.md` (中核的なアカウンタビリティ), `event-playbooks.md` (every event's 目的/共通設計 section).

## Entity: Complementary claim

A statement drawn from an official complementary guide, research paper, or practitioner book distinct from the Scrum Guide.

**Attributes**: existing or newly documented tag from `sources.md` (`[NXG]`, `[KGS21]`, `[EBM24]`, `[DORA26]`, `[AM01]`, `[EDM99]`, `[ART]`, `[ICA]`, `[SAP]`, `[ZBS]`, `[AAP]`, `[LESS]`, `[SAFE]`), a short quotation or precise paraphrase, an attached scope/caveat note where `sources.md` already defines one (FR-013).

**Validation rule** (FR-002, FR-013): tag resolves to a `sources.md` entry; scope note (e.g., DORA's "software delivery only," EBM's outcome framing, psychological safety's non-causal framing) travels with the claim wherever cited, not only in `sources.md`.

**Where found today**: `measurement-and-diagnostics.md` (`[DORA26]`, `[EBM24]`, `[KGS21]`, `[EDM99]`), `facilitation-and-coaching.md` (`[EDM99]`, `[ICA]`), `anti-patterns-and-coaching.md` (`[SAP]`, `[AAP]`, `[ZBS]`), `scaling-frameworks.md` (`[NXG]`, `[LESS]`, `[SAFE]`), `event-playbooks.md` (`[ART]`, `[KGS21]`, `[EDM99]`), `scrum-master-role.md` (`[ICA]`).

## Entity: Skill stance statement

A statement of the skill's own methodological position — not itself an externally citable claim.

**Attributes**: explicit label distinguishing it from a sourced claim (e.g., a lead-in like "本スキルの方針として" or placement under a heading already scoped as the skill's own guidance).

**Validation rule** (FR-004): must not be dressed up as if `[SG20]` or another tag asserts it, even when it is *built on* a cited boundary.

**Where found today**: `SKILL.md`'s "必ず守る原則" (e.g., "人ではなくシステム...を診断する", "事実、推論、提案を区別する" — these are the skill's own operating rules, not Scrum Guide quotations, and must stay labeled as such even while the adjacent PM-boundary principle is grounded in `[SG20]`'s accountability definitions).

## Entity: Canonical location (duplication resolution)

Three explanation clusters currently exist in more than one file at the same level of detail (`research.md` R6). This table is the concrete plan each implementation task follows.

| Cluster | Current locations | Canonical location (keeps full detail) | Other locations become |
|---|---|---|---|
| Event timeboxes & purposes | `scrum-framework.md` events table; `event-playbooks.md` "共通設計" (restates the same 8h/4h/3h/15min figures) | `scrum-framework.md` | `event-playbooks.md`'s "共通設計" links to `scrum-framework.md`'s events table instead of restating the timebox figures; keeps its own value-add (the 6-point per-event design checklist), which is not duplicated elsewhere |
| Scrum Master accountability boundary | `SKILL.md` "アカウンタビリティの境界" table; `scrum-master-role.md` "中核的なアカウンタビリティ"; `scrum-framework.md`'s accountability paragraph | `scrum-master-role.md` (full accountability + service lists) for the Scrum Master's own role; `scrum-framework.md` keeps the framework-wide PO/Developers/SM/Sprint-cancellation table since it covers all three accountabilities, not just the SM's | `SKILL.md`'s table is replaced by a one-line pointer to `scrum-master-role.md`, consistent with how it already points to `anti-patterns-and-coaching.md` for anti-patterns |
| Teach/mentor/facilitate/coach support-mode taxonomy | `SKILL.md` "支援モードを選ぶ" (5 modes); `facilitation-and-coaching.md` "スタンス" (4 modes); `scrum-master-role.md` "コーチングスタンス" (6 stances) | `scrum-master-role.md` (already the role-identity file; extend its stance table to be the single authoritative enumeration, including the "システム介入/組織への働きかけ" mode currently only in `SKILL.md`) | `SKILL.md` keeps a compact decision aid (situation → mode, one row each) that links to `scrum-master-role.md` for the full stance table instead of restating expected outcomes; `facilitation-and-coaching.md`'s "スタンス" section keeps only the facilitator/content-authority distinction (its actual novel content) and links out for the full taxonomy |

## Entity: Evidence tier

One of the four tiers already defined in `sources.md`'s "使い方" section: 規範 (normative) / 公式補完 (official complement) / 研究・実務知見 (research/practitioner) / 文脈依存の技法 (contextual technique).

**Validation rule** (FR-008, SC-008): legible at the point of each claim — via heading, a leading label, or visual grouping — not only inferable by cross-referencing `sources.md`.

**Application**: each reference file's section headings are checked (not necessarily all rewritten) against this rule; e.g. `scaling-frameworks.md` already groups by framework with a tag per section (公式補完 tier, implicitly) — the rewrite makes tier explicit where a section currently mixes tiers without a marker (e.g., `measurement-and-diagnostics.md`'s "推奨指標" table blends 規範-adjacent flow metrics with DORA's narrower-scope metrics in one table without tier labeling).

## Non-duplication note (acceptable existing layering — do not "fix")

Per `research.md` R6, the following are intentional summary→detail links, not duplication to remove:

- `SKILL.md`'s anti-pattern one-paragraph summary → `anti-patterns-and-coaching.md`'s full taxonomy.
- `SKILL.md`'s full `flow_metrics.py` invocation instructions → referenced (not repeated) from `measurement-and-diagnostics.md` and `solo-practice.md`.
- `SKILL.md`'s compressed "プロジェクトマネージャーとして振る舞わない" principle → `scrum-master-role.md`'s "この役割ではないもの" full explanation.
