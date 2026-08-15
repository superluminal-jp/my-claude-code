# Research: Remove /verify-config Verification Feature

## R1 — Actual current footprint (vs. the original request's assumed footprint)

**Decision**: Scope the removal to the files and references that actually exist today, verified by direct inspection, not to the file list implied by the original feature request (which referenced `tests/run-codex-sync.sh` SYNC-08/09 and a `.codex/README.md` deploy-map row).

**Rationale**: `specs/021-codex-official-import` (ADR-0004, "no longer ships a Codex port") already deleted the entire hand-ported `.codex/` tree, including `.codex/prompts/verify-config.md`, `.codex/README.md`, and `tests/run-codex-sync.sh` (replaced by `tests/run-codex-sync.sh`'s successors, `tests/run-codex-references.sh` and `tests/run-codex-drift.sh`, neither of which references this feature — confirmed by grep). `.codex/` is now git-ignored and regenerated locally per developer via Codex's own `/import`. Continuing to plan around files that no longer exist would produce tasks that silently no-op or error.

**Alternatives considered**: Keep the original FR list as written and let `/speckit-tasks` discover the discrepancy. Rejected — `spec.md` is supposed to be accurate before planning proceeds (Core Principle: Accuracy); carrying a known-false requirement forward just defers the correction.

**Verified current footprint** (`grep -rln` for `verify-config|verification-runner`, repo root, excluding `.git`):

| File | In scope? | Why |
|---|---|---|
| `.claude/skills/verify-config/SKILL.md` | Delete | The skill itself |
| `.claude/agents/verification-runner.md` | Delete | The agent itself |
| `tests/run-verification-agent.sh` | Delete | Dedicated test suite for the two files above |
| `README.md` (lines ~13-19, 40, 282, 288, 297-325) | Edit | Lines 40/282/288/297-325 describe the live feature (in scope). Lines ~13-19 are pre-existing unrelated drift (out of scope, see R2). |
| `README.ja.md` (lines ~24, 165-182) | Edit | Japanese mirror of the same live-feature description |
| `README.md` line 192, `README.ja.md` line 125 | Leave unmodified | "If you installed an earlier version" cleanup list — describes what an *old* install left behind, independent of whether the feature exists today |
| `specs/019-verify-fork-test-runner/`, `specs/014-codex-config-port/`, `specs/021-codex-official-import/` | Leave unmodified | Historical Spec Kit decision record (append-only convention) |
| `.claude/settings.json`, `.claude/settings.local.json`, `.mcp.json` | No change needed | Grep confirmed zero references |
| `.codex/README.md`, `tests/run-codex-sync.sh` | N/A — do not exist | Already removed by spec-021 |
| `AGENTS.md` (repo root) | Edit | **Missed during this research pass** — grep at research time was scoped to README.md/README.ja.md and did not check AGENTS.md. Caught by the T006 validation grep during implementation: line 71 told Codex CLI sessions to "run the checks in `.claude/skills/verify-config/SKILL.md` inline" — a live, load-bearing instruction pointing at a file this feature deletes. Fixed by removing the line (not replacing it with equivalent inline guidance — the user's decision was to remove the verification feature entirely, including its Codex-inline fallback, not to reimplement it in prose). |
| `install.sh` line 67-70 (comment) | Leave unmodified | Explains, in past tense, why the `sync_path "commands"` step still exists (to clean up `.claude/commands/verify-config.md` from pre-spec-019 installs). Not an instruction, command, or active component per FR-007's own wording — it is historical rationale for an unrelated sync step, discovered during T006 validation and judged in-scope-exempt rather than requiring a new requirement. |

## R2 — Pre-existing README drift found during research (explicitly out of scope)

**Decision**: Do not touch README.md's introductory paragraph ("`install.sh` also deploys a Codex CLI counterpart ... and a verification prompt ..."), even though "a verification prompt" is a residual reference to the retired Codex-side artifact.

**Rationale**: That paragraph already contradicts the repository's current state (the "Codex CLI support" section states plainly "This repository no longer ships a Codex port"). This contradiction predates and is independent of removing `/verify-config` — fixing it is a separate documentation-drift cleanup with its own scope (the whole paragraph's claims about what `install.sh` deploys, not just the verification-prompt clause). Bundling an unrelated fix into this removal would blur the diff's intent (one logical change per commit, per `git-workflow.md`).

**Alternatives considered**: Fix it inline since it's a one-line edit. Rejected — scope discipline; flagged to the maintainer instead (see spec.md Edge Cases) so it can be handled as its own change if wanted.

## R3 — No `contracts/` artifact needed

**Decision**: Skip the `contracts/` directory for this feature.

**Rationale**: This is a repository-internal maintenance change (deleting files, editing docs) with no external API, CLI surface, or service boundary exposed to a separate consumer. The plan template explicitly allows skipping contracts for "purely internal" changes.

**Alternatives considered**: Treat the removed skill's frontmatter contract (`name`, `context: fork`, `agent: verification-runner`, `allowed-tools`) as a "contract" to document. Rejected — there is no forward-looking contract to specify since the interface is being deleted, not defined.
