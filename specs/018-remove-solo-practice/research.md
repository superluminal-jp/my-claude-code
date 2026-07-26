# Phase 0 Research: Remove solo-practice individual-use capability from `scrum-master`

## R1 — Full inventory of solo/individual-practice references

**Method**: `grep -n "ソロ\|solo\|個人"` (plus targeted `scrum-master` greps) across the project source tree, run before writing `spec.md`, to establish the actual blast radius rather than assume it.

**Findings**:

| File | Reference found | Action |
|---|---|---|
| `.claude/skills/scrum-master/SKILL.md` | frontmatter `description` ("チームがなくても、個人の作業に対して自分専用のScrum Masterとして…ソロプラクティスにも対応する。"), `when_to_use` ("Also use for a personal/solo Scrum Master request…"), body section "## 個人利用（ソロプラクティス）", routing table row for `solo-practice.md` | Remove all four |
| `.claude/skills/scrum-master/references/solo-practice.md` | Entire file is solo-practice content | Delete |
| `.claude/rules/skill-routing.md` | "Applies with or without a team: self-facilitation for one person's own work — personal weekly planning, daily check-ins, a solo retrospective — routes here too." | Remove sentence |
| `.claude/CLAUDE.md` | "`scrum-master` — Scrum events, facilitation, impediments, team or solo retrospectives" | Change to "team retrospectives" |
| `.codex/AGENTS.md` | "Scrum events, facilitation, impediment removal, team or solo retrospectives → `scrum-master`" | Change to "team retrospectives" |
| `README.md` | "`scrum-master` (Scrum events, facilitation, impediments, flow metrics; team or solo)." | Change to "team" |
| `tests/` | No file matched `ソロ\|solo\|個人` | No test changes required |
| Other `references/*.md` (`event-playbooks.md`, `measurement-and-diagnostics.md`, `anti-patterns-and-coaching.md`, `facilitation-and-coaching.md`, `scaling-frameworks.md`, `scrum-master-role.md`, `scrum-framework.md`, `sources.md`) | None link to `solo-practice.md` (confirmed via `grep -rln "solo-practice"`, which returned only `SKILL.md`) | No changes needed |
| `~/.claude/rules/skill-routing.md`, `~/.claude/CLAUDE.md` (user-scope installed copies) | Byte-identical to the project source (confirmed by diff-free grep match) | Out of scope — installer's job, per FR-014 |

**Conclusion**: Exactly six files require changes (one deletion, five edits); zero test files require changes; zero other reference files require changes. This confirms the spec's scope is complete and matches spec.md's Assumptions.

## R2 — Risk to `017-scrum-master-rewrite`'s citation work

**Finding**: This branch was created from the tip of `017-scrum-master-rewrite`'s uncommitted working tree (per the git-feature branch script, which branches from current HEAD/working state). All citation and quotation content added in that prior feature is therefore already present in this branch's working tree, not something to re-apply.

**Decision**: Task execution for this feature touches only the six files listed in R1. No task in this feature re-opens `scrum-framework.md`, `scrum-master-role.md`, `event-playbooks.md`, `facilitation-and-coaching.md`, `measurement-and-diagnostics.md`, `scaling-frameworks.md`, `anti-patterns-and-coaching.md`, or `sources.md` — their `017` content is verified present-and-unchanged as a Polish-phase check (FR-011), not re-derived.

## Output

No `NEEDS CLARIFICATION` markers existed in the spec; R1 and R2 fully ground the plan. Proceeding to Phase 1 (quickstart.md; no data-model.md or contracts/ needed per plan.md's Project Structure rationale).
