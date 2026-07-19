# Phase 1 Data Model: Cross-Agent Guardrail & Rule Migration Decision Record

This feature's "data" is the content of a Markdown document, not application state. The entities below describe the structure the final `decision-record.md` must follow so it satisfies `spec.md`'s Success Criteria (SC-001–SC-004).

## Migration Item

One of the 14 named Claude Code hooks/rules under review.

| Field | Type | Notes |
|---|---|---|
| `id` | string (Q1–Q14) | Stable reference matching the Clarifications session order in `spec.md` |
| `name` | string | e.g. `pre-bash.sh` destructive-command blocking |
| `source_file` | path | e.g. `.claude/hooks/pre-bash.sh`, `.claude/rules/tools.md` |
| `current_behavior` | enum | `hard_block` \| `soft_warning` \| `automation` \| `ui_only` |
| `priority_group` | enum | `P1` (low-cost unification), `P2` (per-tool tradeoff), `P3` (no cross-agent hook equivalent) |

14 instances exist, one per item enumerated in `spec.md`'s Input description.

## Decision Verdict

The outcome recorded for one Migration Item (or, for Q13/Q14, two verdicts sharing one acceptance scenario — Memory and Subagents were decided independently despite being grouped in a single spec scenario).

| Field | Type | Notes |
|---|---|---|
| `migration_item_id` | string | FK to Migration Item |
| `verdict_class` | enum | `unify_full` (共通化 with real enforcement/hook), `unify_weak` (弱い共通化 — prose-only `AGENTS.md` note, no enforcement), `claude_only` (kept Claude Code-specific, not written anywhere else), `infra_migration` (moved to a non-agent-level control, e.g. Branch Protection — considered for Q9, ultimately not chosen) |
| `codex_verdict` | string \| null | Populated only when the verdict differs from `cursor_verdict` (per-tool split pattern from User Story 2) |
| `cursor_verdict` | string \| null | Populated only when it differs from `codex_verdict` |
| `rationale` | string | The "why," including which recommended option (if any) was overridden by the maintainer |
| `unconfirmed_dependency` | string \| null | Reference to a research finding (R1–R4 in `research.md`) whose confidence is Medium or lower, per FR-009 |

**Relationship**: 1 Migration Item → 1 Decision Verdict, except Q13/Q14 (`tools.md` Memory + Subagents) which share one spec acceptance scenario but produced 2 independent Decision Verdicts (Memory: `unify_weak`; Subagents: `unify_full`, no hook needed since it's a principle, not an enforcement mechanism).

## Decision Record

The final Markdown artifact (`decision-record.md`).

| Field | Type | Notes |
|---|---|---|
| `items` | list[Migration Item × Decision Verdict] | All 14, grouped by `priority_group` |
| `format` | structure | Each item independently readable per SC-002 — current behavior, options considered, chosen verdict, rationale, without requiring the rest of the document as context |

## Verdict distribution (from `spec.md` Clarifications, for reference)

| Verdict class | Items |
|---|---|
| `unify_full` — no degradation, source was already non-enforcing prose in Claude Code, straightforward (possibly genericized) transcription | Q1 (`pre-edit.sh` CI/settings/production warnings), Q2 (`tools.md` dedicated-tools/parallel-calls principles), Q3 (`skill-routing.md`), Q4 (`mcp.md` catalog + usage rule) |
| `unify_full` — real enforcement reproduced via a native hook per tool | Q6 (`pre-bash.sh` destructive-command blocking — shared script + Codex `PreToolUse` + Cursor `beforeShellExecution` adapters) |
| `unify_full` — principle-only content, no hook was ever needed | Q14 (`tools.md` Subagents section) |
| `unify_weak` — degraded from a real Claude Code mechanism (hard block, throttle cache, or automation) to a prose-only `AGENTS.md` note with no enforcement | Q5 (secret detection), Q7 (`post-edit-format.sh`), Q8 (`recommend-speckit.sh` — loses its throttle cache), Q9 (main/master block), Q10 (`.git/` block), Q11 (`session-start.sh`), Q12 (`speckit-expand-update.sh`), Q13 (`tools.md` Memory section) |
| `infra_migration` (considered, declined) | Q9 — GitHub Branch Protection was the recommended option for the main/master block; the maintainer chose `unify_weak` (prose-only note) instead |

Total: 6 `unify_full` + 8 `unify_weak` = 14 items, matching SC-001.
