# Phase 1 Data Model: Minimize scrum-master Skill to Official Scrum Guide Content

This feature edits a set of documentation/skill-content files; it has no runtime data entities, database schema, or in-memory objects. The structural equivalent — what `/speckit-tasks` needs to enumerate concrete tasks from — is the inventory of affected files below, each with its final disposition and the requirement(s) it satisfies.

## Entity: Skill file (`.claude/skills/scrum-master/`)

| Field | Meaning |
|---|---|
| `path` | File path relative to the skill root |
| `disposition` | `delete` \| `trim` \| `rewrite` \| `unchanged` |
| `satisfies` | The FR(s) from `spec.md` and/or the Decision(s) from `research.md` this disposition implements |
| `post-state summary` | What the file contains after the change |

| path | disposition | satisfies | post-state summary |
|---|---|---|---|
| `references/2020-Scrum-Guide-US.pdf` | unchanged | FR-001 (retained as sole source) | Normative source document, untouched |
| `references/2020-Scrum-Guide-Japanese.pdf` | unchanged | FR-001 | Normative source document, untouched |
| `references/sources.md` | trim | FR-001; Decision 2 | Single `[SG20]` bibliographic entry + one citation rule; four-tier evidence framing and all other 13 source entries removed |
| `references/scrum-framework.md` | trim (small addition) | FR-008, FR-012; Decision 1 | Keeps all existing SG20-grounded content (empiricism pillars, values, accountabilities, events table, artifact commitments, 2020 changes); gains the Sprint Review "working session / not a stage-gate" quotes and a one-sentence Product Backlog Refinement definition folded in from `event-playbooks.md` |
| `references/scrum-master-role.md` | trim | FR-007, FR-012 | Keeps 中核的アカウンタビリティ, 3つの奉仕先, この役割ではないもの, 誰がなれるか; the "コーチングスタンス" section (and its `[ICA]` citation) is removed; confirm the existing impediment-removal line survives untouched |
| `references/event-playbooks.md` | delete | FR-008; Decision 1 | Deleted after its 3 Guide-quoted statements are folded into `scrum-framework.md` / confirmed already present in `scrum-master-role.md` |
| `references/measurement-and-diagnostics.md` | delete | FR-003 | Deleted — entirely `[KGS21]`/`[EBM24]`/`[DORA26]`/`[EDM99]`-sourced |
| `references/anti-patterns-and-coaching.md` | delete | FR-004 | Deleted — entirely `[SAP]`/`[ZBS]`/`[AAP]`-sourced |
| `references/facilitation-and-coaching.md` | delete | FR-005 | Deleted — entirely `[ICA]`/`[EDM99]`-sourced plus unsourced technique layer |
| `references/scaling-frameworks.md` | delete | FR-002 | Deleted — entirely `[NXG]`/`[LESS]`/`[SAFE]`/`[SC@S]`-sourced |
| `scripts/flow_metrics.py` | delete | FR-006 | Deleted — Kanban Guide-sourced computation |
| `scripts/__pycache__/*` | delete | FR-006 | Deleted alongside the script it was compiled from |
| `SKILL.md` | rewrite | FR-009, FR-010, FR-011 | Description/`when_to_use`/principles rescoped to Scrum-Guide-only; reference-file table drops rows for every deleted file; workflow steps and anti-pattern/metrics sections that pointed at deleted files are removed or replaced with an explicit out-of-scope statement (FR-011); flow-metrics script invocation section removed |

## Entity: Repository file outside the skill directory

| path | disposition | satisfies | post-state summary |
|---|---|---|---|
| `README.md` | trim | Decision 3 (Live Documentation drift) | Drop "flow metrics" from the skill's one-line capability summary (L39); drop the `scripts/flow_metrics.py` row from the file-tree diagram (L283–286) or replace with the post-deletion tree; update "8 on-demand reference documents" to the actual post-deletion count; remove the "After changing... `flow_metrics.py` ... run `tests/run-flow-metrics.sh`" instruction block (L321–327) |
| `.claude/settings.json` | trim | Decision 3 | Remove the two `Bash(python3 .../flow_metrics.py *)` entries from `permissions.allow`; file must remain valid JSON |
| `tests/run-flow-metrics.sh` | delete | Decision 3 | Deleted — tests a script that no longer exists |
| `tests/test_flow_metrics.py` | delete | Decision 3 | Deleted — unit tests for a script that no longer exists |
| `tests/__pycache__/test_flow_metrics.cpython-314.pyc` | delete | Decision 3 | Deleted alongside its source test file |

## Entity: File not touched by this feature (confirmed out of scope)

Listed to make the boundary explicit for `/speckit-tasks`, since these came up during research but do not need a task:

| path | why it's out of scope |
|---|---|
| `docs/adr/0003-vendor-scrum-master-skill.md` | Accepted ADR describing the vendoring/permission-mechanism decision, not the skill's content scope; never rewritten (Decision 4) |
| `.claude/rules/skill-routing.md`, `SKILL.md`'s `when_to_use` field | Routing triggers are explicitly unaffected (spec.md Assumptions) |
| `tests/skill-routing/007-scrum-facilitation.md` | Tests routing on a Daily Scrum dysfunction prompt; independent of the content being removed — must still pass unchanged, not be edited |
| `.codex/AGENTS.md`, `install.sh`, `.agents/skills/` mirror | Distribution/discovery mechanism for the skill as a whole; unaffected by trimming the skill's internal content |
