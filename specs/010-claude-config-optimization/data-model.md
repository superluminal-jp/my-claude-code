# Phase 1 Data Model: Configuration Artifact Inventory

The "entities" are configuration artifacts. Each row records its concern, whether it loads into **standing context** (every session) or **on demand**, current size, and the planned change. Sizes are baseline `wc -l` at spec time.

**Applies to every row below**: beyond the listed change, each edited file also gets the R9 two-pass — (A) make every directive actionable, supplementing ambiguous ones (FR-014); (B) verify existing authority anchors and add correctly-attributed ones where they sharpen a normative directive (FR-015). Net length may rise where this buys fidelity; verbosity is still removed.

## Standing context (loaded every session — primary reduction target)

| Artifact | Concern | Lines | Planned change |
|---|---|---|---|
| `CLAUDE.md` (root) | Imports `.claude/CLAUDE.md`; SPECKIT plan pointer | 8 | Repoint SPECKIT marker to this plan; no growth |
| `.claude/CLAUDE.md` | Core principles, response style, skill routing, preflight, MCP | 46 | Trim verbose prose; consolidate clarification (de-dupe with `clarifier.md`); add Memory/Subagent pointer + pre-execution discipline (R6) |
| `.claude/rules/skill-routing.md` | Routing triggers (`@`-imported) | 7 | Add intent line; keep triggers verbatim (enforced behavior) |
| `.claude/rules/live-documentation.md` | Drift/proximity/redundancy enforcement (`@`-imported) | 59 | Add intent line; tighten prose; preserve all five principles + override handling |
| `.claude/rules/mcp.md` | MCP catalog + usage rule (`@`-imported) | 26 | Add intent line; keep catalog table + usage rule |

## On-demand rules (loaded when referenced)

| Artifact | Concern | Lines | Planned change |
|---|---|---|---|
| `.claude/rules/permissions.md` | deny→ask→allow policy | 33 | Add intent line; keep every rule (enforced) |
| `.claude/rules/clarifier.md` | Clarification gate, triggers, template | 67 | Add intent line; become the single canonical clarification source; CLAUDE.md preflight + clarifier skill cross-reference it |
| `.claude/rules/tools.md` | Tool-preference, parallel calls, **Subagents**, **Memory (new)** | 29 | Add intent line; sharpen Subagent section + anti-pattern; add Memory policy (R1) |
| `.claude/rules/advisor.md` | Answer-quality baseline, options/recommendation | 64 | Add intent line; trim; keep template |

## Owner skills (in scope)

| Artifact | Concern | Lines | Planned change |
|---|---|---|---|
| `.claude/skills/coder/SKILL.md` | TDD/SDD/docs-sync/security | 70 | Body intent line; trim narration; preserve all obligations |
| `.claude/skills/editor/SKILL.md` | Produced artifacts | 66 | Body intent line; trim |
| `.claude/skills/clarifier/SKILL.md` | Formal requirements elicitation | 53 | Body intent line; cross-reference `rules/clarifier.md`, remove duplicated trigger prose |
| `.claude/skills/domain-model/SKILL.md` | DDD modeling | 322 | Body intent line; trim to ≤200 if loss-free; else justify |
| `.claude/skills/ubiquitous-language/SKILL.md` | UL collection/validation | 160 | Body intent line; trim |

## Hooks (in scope; logic of safety hooks frozen)

| Artifact | Event / matcher | Mode | Planned change |
|---|---|---|---|
| `session-start.sh` | SessionStart | 0755 | Keep; purpose header present |
| `pre-bash.sh` | PreToolUse / `Bash` | 0755 | Freeze guard logic; verify purpose comment |
| `pre-edit.sh` | PreToolUse / `Edit\|Write\|Delete` | 0644 | Set executable 0755; freeze logic |
| `post-edit-format.sh` | PostToolUse / `Edit\|Write` | 0644 | Set executable 0755; freeze logic |
| `user-prompt-submit.sh` | UserPromptSubmit | 0755 | Freeze secret-scan logic |
| `speckit-expand-update.sh` | UserPromptExpansion / `speckit.*` | 0755 | Keep |

## Settings

| Artifact | Concern | Planned change |
|---|---|---|
| `.claude/settings.json` | Model, effort, permissions (allow/ask/deny), hook wiring | No semantic change; permissions and hook wiring are part of the behavior inventory and must remain equivalent |

## Out of scope

`.claude/skills/speckit-*/SKILL.md` (12 vendored Spec Kit skills), `.specify/**`, `~/.claude/` except via `install.sh` sync consistency.

## Derived metrics

- **Standing-context baseline** = lines(root CLAUDE.md + .claude/CLAUDE.md + skill-routing.md + live-documentation.md + mcp.md) = 8 + 46 + 7 + 59 + 26 = **146 lines**. Target (SC-002): **zero duplicated guidance** (clarification stated once) and **no verbosity bloat**. Net line count is not a hard gate — it may rise where a recorded comprehension supplement (FR-014) or authoritative anchor (FR-015) is needed; it must not rise from verbosity. Track each net addition with a one-line reason.
- **Actionability** (SC-009): 100% of directives map to a nameable observable behavior.
- **Grounding** (SC-010): every normative directive correctly anchored or self-evidently operational; zero fabricated/decorative anchors.
- **Intent-line coverage** target = 7/7 rules + 5/5 owner skills = **100%** (SC-001).
- **Imports ≤200 lines** each (SC-008): only `domain-model` (322) exceeds; it is a skill, not a CLAUDE.md import, so SC-008 is already met for imports — but it is still reviewed under FR-003/FR-014 where loss-free.
