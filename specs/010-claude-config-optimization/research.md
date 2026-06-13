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

## R3 — Standing-context minimization (FR-004, FR-011, SC-002, SC-008)

**Decision**: Treat the import chain `root CLAUDE.md → .claude/CLAUDE.md → {skill-routing.md, live-documentation.md, mcp.md}` as the standing-context budget. Reduce by: (a) collapsing the duplicated clarification guidance that appears in both `.claude/CLAUDE.md` "Response Preflight" and `rules/clarifier.md`; (b) tightening verbose prose to imperative bullets; (c) removing meta-commentary. Measure before/after with `wc -l`/`wc -c` on the import set. Target ≥20% reduction.

**Rationale**: Current standing files total ~46 (`.claude/CLAUDE.md`) + 7 (`skill-routing.md`) + 59 (`live-documentation.md`) + 26 (`mcp.md`) lines. The biggest redundancy is clarification guidance restated three times (CLAUDE.md preflight, `clarifier.md` rule, `clarifier` skill). Consolidation removes the most tokens with zero behavior loss.

**Alternatives considered**: Aggressive removal of `live-documentation.md` detail — rejected: it encodes enforced review behavior (drift detection) that must survive per FR-012.

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
