# Phase 0 Research: Claude Code Personal Configuration Optimization

All Technical Context unknowns resolved below. Each entry: Decision / Rationale / Alternatives considered.

## R1 — Memory usage guidance (FR-001, SC-003)

**Decision**: Add a short, testable Memory policy to `.claude/rules/tools.md` (co-located with the existing Subagents section). Write to Memory only durable, cross-session project facts (conventions, decisions, locations of key files, user preferences) that are costly to rederive; read Memory at task start when a task plausibly depends on such facts. Do **not** record transient state, secrets, or anything reconstructable in seconds. The `autoMemoryEnabled: true` flag in `settings.json` enables the capability; the rule governs deliberate use.

**Rationale**: Memory exists as a setting but has zero written guidance, so behavior is undefined. A tools-level rule keeps it next to the Subagent/tool guidance (proximity) and inside the standing-context import path so it always applies. Anti-pattern stated explicitly satisfies SC-003's "when NOT to use".

**Alternatives considered**: (a) Put Memory guidance in `.claude/CLAUDE.md` directly — rejected: bloats standing context with detail better co-located in `tools.md`. (b) Leave Memory undocumented — rejected: violates FR-001 and wastes the enabled capability.

## R2 — Subagent delegation guidance (FR-002, SC-003)

**Decision**: Keep and sharpen the existing `tools.md` "Subagents" section. Delegate when: broad multi-location fan-out search where only the conclusion is needed; protecting the main context from large intermediate output; or explicit user request. Use direct Glob/Grep/Read otherwise. Explicit anti-pattern: never spawn a Subagent for a single-file lookup or a task already scoped to known files.

**Rationale**: The current 3-line section already names the right triggers; it needs only an explicit "when NOT to" and a one-line intent. Aligns with the harness's own Agent-tool guidance (delegate fan-out, keep the conclusion not the file dumps).

**Alternatives considered**: A separate `subagents.md` rule — rejected as redundant; tool-selection guidance belongs together in `tools.md` (no-redundancy principle).

## R3 — Standing-context efficiency, subordinate to comprehension (FR-004, FR-011, SC-002, SC-008)

**Decision**: Treat the import chain `root CLAUDE.md → .claude/CLAUDE.md → {skill-routing.md, live-documentation.md, mcp.md}` as the standing-context budget. Reduce length only by: (a) collapsing the duplicated clarification guidance that appears in both `.claude/CLAUDE.md` "Response Preflight" and `rules/clarifier.md`; (b) tightening verbose prose to imperative bullets; (c) removing meta-commentary. Do **not** reduce by dropping content the model needs. Measure two things separately: **redundancy** (must reach zero — each rule stated once) and **verbosity** (must fall); net line count may move up where R9 supplements/anchors are added. The earlier hard "≥20%" target is replaced by "zero duplication + no verbosity bloat", because comprehension now outranks compression.

**Rationale**: The biggest redundancy is clarification guidance restated three times (CLAUDE.md preflight, `clarifier.md` rule, `clarifier` skill); consolidation removes the most tokens with zero behavior loss. But a pure-shrink target conflicts with the owner's clarified intent that the model must *understand and execute* the config — so the metric shifts from "smaller" to "no duplication, no noise, fully actionable".

**Alternatives considered**: (a) Keep the hard ≥20% target — rejected: it would pressure removal of comprehension-bearing detail. (b) Aggressive removal of `live-documentation.md` detail — rejected: it encodes enforced review behavior (drift detection) that must survive per FR-012.

## R4 — Explicit intent lines (FR-003, SC-001)

**Decision**: Every file under `.claude/rules/` and every owner skill gains a single leading intent sentence: "Purpose: … / Applies when: …". Skills already carry YAML `description`/`when_to_use`; for skills the intent line is the body's first sentence so it reads without parsing frontmatter.

**Rationale**: Cheapest, highest-coverage change for SC-001 (100% coverage). Frontmatter is for routing; a prose intent line serves the human reader and the model scanning the body.

**Alternatives considered**: Rely on existing frontmatter only — rejected: rules have no frontmatter, and SC-001 requires a visible one-line intent in the body.

## R5 — Hook optimization (FR-008, FR-009, SC-004, SC-005)

**Decision**: Keep all six hooks (each maps to a distinct purpose — no redundancy found). Optimizations: add a one-line purpose comment header where missing (already present on most), verify matchers/timeouts, and ensure `pre-edit.sh`/`post-edit-format.sh` (currently mode `0644`) are executable like the others (`0755`). Do not alter the guard logic of `pre-bash.sh` or `user-prompt-submit.sh`. The `Edit|Write|Delete` matcher on `pre-edit.sh` is correct; `post-edit-format.sh` correctly matches only `Edit|Write`.

**Rationale**: Review found no obsolete or duplicated hooks; the safety hooks are well-formed and must stay byte-stable in logic (SC-004). The only concrete defect is the missing execute bit on two scripts (they are invoked via interpreter so may still run, but consistency reduces risk). This keeps "optimization" honest without weakening guards.

**Alternatives considered**: Merge `pre-edit.sh` and `pre-bash.sh` — rejected: different matchers (`Edit|Write|Delete` vs `Bash`) and concerns; merging would entangle unrelated guards.

## R6 — Internal design→plan→task discipline without Spec Kit (FR-006, FR-007, SC-006)

**Decision**: Add a concise "Pre-execution discipline" subsection to `.claude/CLAUDE.md` Response Preflight. For non-trivial tasks (multi-file, new behavior, or irreversible), Claude internally states approach → short plan → task breakdown before editing, reusing the existing clarifier (scope) and advisor (options/recommendation) scaffolding rather than a new framework. Trivial = single-file, reversible, ≤1 logical step → skip ceremony. Threshold stated in testable terms.

**Rationale**: Mirrors the Spec Kit specify→plan→tasks flow internally and proportionately. Reusing clarifier/advisor avoids adding standing-context weight and matches the medium-confidence assumption in the spec. Keeps it "internal" (no verbose user-facing ceremony) unless the task warrants surfacing.

**Alternatives considered**: A new dedicated rule file `planning.md` — rejected: adds an import and overlaps advisor/clarifier (redundancy). Always-on planning — rejected: violates FR-007 (friction on trivial tasks).

## R7 — Documentation best-practice redesign (FR-010, SC-007)

**Decision**: Audit and refactor the config's own docs against `rules/live-documentation.md`: proximity (Memory/Subagent guidance in `tools.md` next to tool rules; per-concern intent inline), no redundancy (single canonical clarification source, cross-referenced), explicit intent (R4), and size discipline (≤200 lines/import, R3). Produce the audit result in `quickstart.md` as a checklist run.

**Rationale**: The repo already endorses these principles; applying them reflexively to the config is the lowest-risk, most consistent "best practice" available and is directly verifiable (SC-007 = zero unresolved violations).

**Alternatives considered**: Import an external doc style guide (e.g., Diátaxis) — rejected: would introduce a competing framework the repo doesn't use; the in-repo Live Documentation rules already cover proximity/redundancy/intent.

## R8 — Behavior inventory as the safety gate (FR-012, SC-002, SC-004)

**Decision**: Before editing, enumerate every enforced behavior across permissions (`settings.json` allow/ask/deny), hook guards (force-push, hard-reset, clean -f, rm -rf, mkfs/dd/fork-bomb, curl|bash, non-HTTPS, credential read/write, sudo, .git/main-branch edits, secret patterns), skill-routing triggers, and skill obligations (TDD/SDD/docs-sync). Record in `contracts/behavior-inventory.md`. After editing, re-verify each line item is still present/firing.

**Rationale**: This is the only objective way to prove "≥20% smaller with zero behavior loss" (SC-002) and "100% safety protections still fire" (SC-004). It turns a subjective trim into a checkable contract.

**Alternatives considered**: Trust diff review alone — rejected: easy to silently drop a deny rule or a trigger; an explicit inventory is the testable artifact.

## R9 — Comprehension supplements and authoritative grounding (FR-014, FR-015, SC-009, SC-010)

**Decision**: During every file edit, run two passes beyond trimming. **Pass A — actionability**: for each directive, name the observable behavior it should produce; if none can be named, the directive is ambiguous → add a concrete clarifying supplement (example, boundary, or precise verb) or delete it if it is genuinely vacuous. **Pass B — grounding**: for each normative "should/must", attach a correctly-attributed authority where one sharpens interpretation, and verify any anchor the config already names.

Authorities to use where they genuinely apply (only as functional anchors, never decorative):

- **Security**: OWASP Top 10 and OWASP ASVS; CWE classes; least-privilege. (Already referenced in `coder` — verify and keep.)
- **Requirements/clarification**: ISO/IEC/IEEE 29148 (requirements quality: unambiguous, verifiable, feasible), INVEST (story quality), Gherkin Given/When/Then, MoSCoW, FURPS+, SMART. (Partly in `clarifier`/`clarifier.md` — verify attribution.)
- **Documentation/writing**: Pyramid Principle (Minto), MECE, SCQA, BLUF; Tufte data-ink and lie-factor; Cleveland–McGill graphical-perception ranking; Strunk & White. (Already in `editor` — verify.)
- **Decision/advice**: one-way vs two-way door, pre-mortem, Fermi estimation. (Already in `advisor` — verify.)
- **Tool/agent use, Memory, Subagents**: ground in the harness's own documented guidance (delegate fan-out, keep the conclusion not the dumps; record only durable cross-session facts) rather than an external standard, since no academic standard governs these.

**Rationale**: The owner clarified that accurate model understanding is a first-class goal: a directive anchored to a named standard ("requirements must be verifiable per ISO/IEC/IEEE 29148") gives the model a precise shared referent, whereas "write good requirements" does not. This raises execution fidelity (SC-009) and is directly auditable (SC-010). Grounding also matches the repo's own priority order (Accuracy > Defensible practice), which already endorses international/industry standards.

**Guardrails**: Anchors must be real and current — the Accuracy principle forbids inventing or misattributing a standard; when unsure, state the rule in plain operational terms instead of guessing a citation. Anchors must be functional: if naming a framework changes no behavior, drop the name and keep the behavior. Anchors stay terse (a parenthetical referent, not a lecture) so grounding does not become verbosity.

**Alternatives considered**: (a) Add citations everywhere for rigor — rejected: decorative jargon violates SC-010 and adds noise. (b) Add no grounding, keep directives plain — rejected: the owner explicitly wants authoritative anchoring where it improves precision; plain-only loses the shared referent that reduces misexecution.
