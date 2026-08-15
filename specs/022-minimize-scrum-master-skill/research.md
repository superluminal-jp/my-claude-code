# Phase 0 Research: Minimize scrum-master Skill to Official Scrum Guide Content

## Scope of this research

`spec.md` fixes the FR-001–FR-012 outcome (only `[SG20]` citations remain; five files are deleted; event guidance is limited to purpose+timebox) but leaves two things unresolved at the WHAT level: (1) exactly how the remaining files absorb the handful of directly Scrum-Guide-quoted statements that currently live only in files marked for deletion, and (2) which files *outside* `.claude/skills/scrum-master/` reference the artifacts being deleted and must change in the same commit to avoid drift or dead references. Both are resolved here so Phase 1 design and `/speckit-tasks` have a concrete file list to work from.

## Decision 1: Disposition of `references/event-playbooks.md`

**Decision**: Delete the file. Before deleting, fold its three directly Scrum-Guide-quoted statements that are not already captured elsewhere into the files that already own that content:

- Sprint Review "スプリントレビューはワーキングセッションであり…プレゼンテーションだけに限定しないようにする" [SG20, p.9] and "…価値をリリースするための関門と見なすべきではない" [SG20, p.12] → append to `scrum-framework.md`'s event description for Sprint Review.
- Product Backlog Refinement's Guide-quoted definition, "プロダクトバックログアイテムがより小さく詳細になるように、分割および定義をする活動である" [SG20, p.10], including the point that it is not a formal Scrum event → add as a short new subsection in `scrum-framework.md` (the events table currently only covers the five timeboxed events; Refinement has no timebox and needs one sentence, not a table row).
- The impediment-removal duty, "スクラムチームの進捗を妨げる障害物を排除するように働きかける" [SG20, p.6] → already present in `scrum-master-role.md`'s "Scrum Teamへの奉仕" list ("チームの前進を妨げる障害の除去を主導する"); no new content needed, just confirm it survives FR-007's trim.

**Rationale**: `scrum-framework.md`'s events table already states every event's Guide-defined purpose and timebox (FR-008's target state). A trimmed `event-playbooks.md` that repeated only that same purpose+timebox would duplicate `scrum-framework.md` line for line — a Live Documentation "No Redundancy" violation. Every paragraph in `event-playbooks.md` beyond the purpose+timebox quote (準備, 三つの論点の進行例, 完了条件, 5段階のレトロ構造, レトロ形式の一覧, 改善実験フォーマット, 障害除去の記録表, アンチパターン) is either a non-SG20 practitioner convention (already excluded by FR-008) or a duplicate of `scrum-framework.md`/`scrum-master-role.md`. Nothing distinctive and Guide-grounded is left to justify a separate file.

**Alternatives considered**:
- *Keep `event-playbooks.md`, trimmed to purpose+timebox only.* Rejected: redundant with `scrum-framework.md`'s existing table (see above).
- *Move `scrum-framework.md`'s event content into `event-playbooks.md` instead, and delete `scrum-framework.md`.* Rejected: `scrum-framework.md` is titled "規範層" (normative layer) and is the file every other surviving file already cross-references for event purpose/timebox (`event-playbooks.md`'s own 共通設計 section points there); it is the more natural single home.

## Decision 2: Disposition of `references/sources.md` after trimming to `[SG20]` only

**Decision**: Keep the file, but collapse its structure. Remove the four-tier evidence-strength explanation (規範 / 公式補完 / 研究・実務知見 / 文脈依存の技法) and the sections for every removed source ([NXG], [AM01], [EBM24], [KGS21], [DORA26], [EDM99], [ART], [ICA], [SAP], [ZBS], [AAP], [LESS], [SAFE], [SC@S]). What remains: the `[SG20]` entry (bibliographic reference, both PDF paths, the page-numbering note for the Japanese edition already present today) and a single citation rule ("Scrumの必須事項を述べるときは`[SG20, p.X]`を付ける").

**Rationale**: A tiering system with one populated tier is not a tiering system — keeping the four-tier framing after the other three tiers go empty would misrepresent the file's own content (a Live Documentation accuracy concern, not just brevity). FR-001 requires the file to cite only the Scrum Guide; a single-entry bibliography with one citation rule is the minimal form that satisfies FR-001 without leaving vestigial structure that implies sources that no longer exist.

**Alternatives considered**: Delete `sources.md` entirely and inline the `[SG20]` citation directly in `scrum-framework.md`. Rejected: every surviving file (`scrum-framework.md`, `scrum-master-role.md`) already links to `sources.md` for the full bibliographic entry rather than repeating it inline; keeping one canonical citation file avoids re-duplicating the PDF paths and page-numbering caveat in every file that quotes the Guide.

## Decision 3: Files outside `.claude/skills/scrum-master/` that reference deleted artifacts

A repo-wide search for references to the files/paths this feature deletes turned up four locations FR-001–FR-012 don't mention because they sit outside the skill directory, but which will contain dead references or dead tests once the deletions land:

| File | What it references | Why it must change in this feature |
|---|---|---|
| `README.md` (L39, L283–286, L321–327) | Lists `scrum-master` as covering "flow metrics"; shows `scripts/flow_metrics.py (cycle time, work item age, throughput, WIP)` in the file-tree diagram; states `references/` has "8 on-demand reference documents"; instructs readers to run `tests/run-flow-metrics.sh` after changing `flow_metrics.py` | `.claude/CLAUDE.md`'s Live Documentation rule (Drift Detection): README describes the skill's public capability list and file tree, which this feature changes. Leaving it as-is would describe capabilities (flow metrics) and a script that no longer exist. |
| `.claude/settings.json` (`permissions.allow`, two entries) | `Bash(python3 .claude/skills/scrum-master/scripts/flow_metrics.py *)` and the `~/.claude/...` equivalent, added per ADR 0003 specifically to scope execution of this one script | Once `scripts/flow_metrics.py` is deleted (FR-006), these two allow-list entries permit a command that can never succeed — dead permission grants are a least-privilege hygiene issue (`.claude/rules/permissions.md`), not a live-documentation contract, but leaving them serves no purpose and should be removed in the same change. |
| `tests/run-flow-metrics.sh` | Runs `python3 -m unittest discover -s tests -p "test_flow_metrics.py"` | Tests a script FR-006 deletes; keeping it would either fail (module not found) or silently discover nothing. Delete alongside the script. |
| `tests/test_flow_metrics.py` (+ `tests/__pycache__/test_flow_metrics.cpython-314.pyc`) | Unit tests for `flow_metrics.py`'s CLI and calculations | Same reasoning as above — tests for code that no longer exists. |

**Decision**: Update all four in the same change as the skill-directory deletions.

**Rationale**: This is not new scope beyond what `spec.md` already committed to — FR-006 says `scripts/flow_metrics.py` "MUST be deleted"; a deletion that leaves its test suite, its README description, and its settings.json permission grant behind is an incomplete deletion, not a smaller one. `.claude/CLAUDE.md`'s Live Documentation rule independently requires the README update regardless of what `spec.md` enumerates, since it governs every diff that changes a public contract.

**Alternatives considered**: Leave README/settings.json/tests untouched and file them as follow-up work. Rejected — `tests/run-flow-metrics.sh` failing on the next test run, and `.claude/settings.json` granting a permission for a command that can't exist, are correctness defects introduced by this feature, not pre-existing ones; deferring them would ship the feature broken.

## Decision 4: No conflict with existing ADRs

`docs/adr/0003-vendor-scrum-master-skill.md` (Accepted) decided this repository is the sole source of truth for the skill and chose where its narrow `flow_metrics.py` permission lives (`.claude/settings.json`). It did not decide that `flow_metrics.py` or the skill's multi-source content must exist forever. Deleting the script and its permission entries is a downstream content change, not a reversal of ADR 0003's vendoring/permission-mechanism decision — the ADR's Decision and Consequences sections remain accurate as a historical record of *that* choice. Per the Live Documentation rule's Out-of-Scope note ("New standalone ADRs... not derived from existing code" and — by the same logic — accepted ADRs already recorded are never rewritten), ADR 0003 is left untouched. No new ADR is warranted either: removing a script and trimming reference content is reversible (recoverable from git history) and was reached through the ordinary `/clarifier` → `/speckit-specify` flow already used for the two prior scrum-master ADR-adjacent specs (016, 017), not a fresh one-way-door architectural choice.

## Resolved Technical Context

All items below were "NEEDS CLARIFICATION" candidates in the plan template; each is resolved by the nature of this feature (editing/deleting existing skill-content and doc files — no new software is written).

- **Language/Version**: N/A — no new source code is authored. The one Python file in scope (`scripts/flow_metrics.py`) is deleted, not modified.
- **Primary Dependencies**: N/A.
- **Storage**: N/A — flat Markdown/Python/JSON files only.
- **Testing**: The repository's existing suites gate this change: `tests/skill-routing/007-scrum-facilitation.md` (via the skill-routing regression harness) must keep passing unchanged, since routing (`when_to_use`) is explicitly out of scope (spec.md Assumptions); `tests/run-flow-metrics.sh` + `tests/test_flow_metrics.py` are deleted (Decision 3); `.claude/settings.json` must remain valid JSON after the permission entries are removed. `spec.md`'s Success Criteria (SC-001–SC-005) are verified by grep/link-check commands documented in `quickstart.md`, not by a new automated test — this feature doesn't introduce a testable software behavior beyond "the files say what they say."
- **Target Platform**: Claude Code (and Codex CLI via the existing mirror/sync mechanism described in ADR 0003) skill file system, within this repository only.
- **Project Type**: Single — a documentation/skill-content package edited in place; no src/tests application split applies.
- **Performance Goals**: N/A.
- **Constraints**: Must not alter `when_to_use` / skill-routing triggers (spec.md Assumption); must leave zero dead relative links inside the skill (FR-009) and zero dead references in README/settings.json/tests (Decision 3); must not touch ADR 0003 (Decision 4).
- **Scale/Scope**: ~10 files deleted or emptied (`references/scaling-frameworks.md`, `references/measurement-and-diagnostics.md`, `references/anti-patterns-and-coaching.md`, `references/facilitation-and-coaching.md`, `references/event-playbooks.md`, `scripts/flow_metrics.py`, `scripts/__pycache__/*`, `tests/run-flow-metrics.sh`, `tests/test_flow_metrics.py`, `tests/__pycache__/test_flow_metrics.cpython-314.pyc`); 4 files edited in place (`references/sources.md`, `references/scrum-master-role.md`, `references/scrum-framework.md`, `SKILL.md`); 2 files edited outside the skill directory (`README.md`, `.claude/settings.json`).
