# Implementation Plan: Remove the Minto Pyramid Stop Hook

**Branch**: `042-remove-minto-stop-hook` | **Date**: 2026-10-07 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/042-remove-minto-stop-hook/spec.md`

## Summary

Delete the vendored `minto-pyramid` package's only hook, a `Stop` prompt hook in
`hooks/hooks.json`. Keep the skill, its rules, templates, references, and evals
unchanged. Record the local divergence from upstream in the manifest version and
in the docs.

The approach rests on these points:

- **One declaration to remove.** Plugin hooks load from `hooks/hooks.json`, and
  a manifest `hooks` key only merges with that file [S2]. The manifest has no
  such key, so deleting the file removes every hook (research R1).
- **No installer change.** `install.sh` replaces `skills/` exactly, so the next
  run deletes the installed hook (R2). The change takes effect in the next
  session, because hooks are snapshotted at session start [S1] (R3).
- **Test first.** A new package test asserts "no hooks". It fails before the
  deletion and passes after it, and it guards against a verbatim re-copy that
  would bring the hook back (R7, [S5]).

## Technical Context

**Language/Version**: JSON (plugin manifest and hook config), Markdown (docs), Python 3 stdlib `unittest` (package tests), Bash (repository tests)

**Primary Dependencies**: Claude Code plugin loader and `claude plugin validate` [S2]; none added

**Storage**: Files only (`.claude/skills/minto-pyramid/`, synced to `~/.claude/skills/minto-pyramid/`)

**Testing**: `python3 -B -m unittest discover -s tests` and `claude plugin validate --strict .` in the package; `bash tests/run-*.sh` at the repository root (the CI set: `run-install.sh`, `run-digital-agency-frontend-skill.sh`, `run-removed-guardrails.sh`, `run-mcp-startup.sh`, plus `run-config-pyramid.sh`)

**Target Platform**: Claude Code CLI on macOS/Linux, user-level config under `~/.claude/`

**Project Type**: Configuration repository (user-level Claude Code settings plus vendored skill packages)

**Performance Goals**: One fewer model call at the end of every turn (the hook's prompt evaluation [S1]). The size of the saving is **unverified**: nothing is measured.

**Constraints**: FR-003 (skill content unchanged), FR-007 (`maintaining-living-documentation`, `.claude/settings.json`, `.claude/rules/`, `install.sh` unchanged), README/README.ja sync rule (repository `CLAUDE.md`)

**Scale/Scope**: 1 file deleted, 1 manifest field changed, 1 test replaced, 5 documents edited (package README, package `references/anthropic-guidance.md` line 24, `README.md`, `README.ja.md`, `docs/claude-config-design.md`) plus 1 comment block in a test script (analysis A1, A7)

No NEEDS CLARIFICATION remains; research.md R1–R9 resolve every open point.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` is still the unfilled template **[observed]**, so it defines no gates. In its place, the plan checks the binding rules this repository already applies: its `CLAUDE.md` and `.claude/CLAUDE.md`, `.claude/rules/*`, and the living-documentation rule.

| Gate | Source | Pre-design | Post-design |
|------|--------|------------|-------------|
| Smallest coherent change; no drive-by edits | `.claude/CLAUDE.md` "Execute under control" | PASS: only the hook, its test, the version, and docs that describe the hook | PASS: data-model and contract add no new surface |
| Failing check before changing an automatable contract | `.claude/CLAUDE.md`; [S5] | PASS: R7 orders the test before the deletion | PASS: quickstart V1 records the red step |
| Out-of-scope paths untouched | spec FR-007 | PASS | PASS: Project Structure lists none of them |
| Frozen skill content unchanged except the stated exception | spec FR-003 | PASS | PASS: only `references/anthropic-guidance.md` line 24 is edited (D11, analysis A1) |
| Edit `.claude/` here, never `~/.claude/` directly | repository `CLAUDE.md` | PASS: install only through `install.sh` | PASS |
| README.md and README.ja.md stay in sync | repository `CLAUDE.md` | PASS: both are in scope | PASS: contract C3 states the shared facts |
| Docs updated in the same change; ADR only on request | living-documentation rule; [S6] | PASS: R6, R8 | PASS |
| Sourced vs inferred claims kept distinct | `.claude/CLAUDE.md`; spec FR-008 | PASS: research labels each claim | PASS |

No violations, so Complexity Tracking is empty.

## Decisions and Citations

| # | Decision | Supporting citation / evidence |
|---|----------|--------------------------------|
| D1 | Delete `hooks/hooks.json` and `hooks/`; keep the manifest free of a `hooks` key | [S2] standard layout and merge rule; observed file contents (R1) |
| D2 | No change to `install.sh` | observed `sync_path` exact replacement (R2) |
| D3 | Activation = re-run `install.sh`, then start a new session | [S1] session-start snapshot (R3) |
| D4 | Rationale: per-turn model call and correction rounds; inferred, not user-stated | [S1] prompt hooks and Stop blocking; observed README text and commit `753eb52` (R4) |
| D5 | Self-check retained as advisory guidance | [S3] context vs enforcement; observed `SKILL.md` step 10 (R4) |
| D6 | Version `0.3.0` → `0.3.0+local.no-stop-hook` | [S2] "A version string, not checked against semver"; [S4] §10 build metadata "does not affect version precedence", §9/§11 pre-release ranks lower (both re-fetched 2026-10-07) (R5) |
| D7 | Replace the "copied verbatim" claim for `minto-pyramid` everywhere it appears | observed `753eb52` diff; [S7] docs match the system (R6) |
| D8 | Red → green with `test_declares_no_hooks` | [S5]; observed baseline 5/5 pass, validator passes (R7) |
| D9 | Propose an ADR, do not create one | living-documentation rule; [S6] (R8) |
| D10 | No AWS lookup | spec, Assumptions (R9) |
| D11 | Rewrite `references/anthropic-guidance.md` line 24 only; keep lines 9 and 21–23 | observed: line 24 states the hook as this plugin's behavior, lines 9 and 21–23 state Claude Code facts that S2 still confirms (re-fetched 2026-10-07: `hooks/hooks.json` is the default hooks location and a manifest `hooks` key merges with it); [S7] information matches the system (spec FR-003, analysis A1) |

Sources (full list with URLs in [research.md](research.md#sources)):

- [S1] <https://code.claude.com/docs/en/hooks>
- [S2] <https://code.claude.com/docs/en/plugins-reference>
- [S3] <https://code.claude.com/docs/en/memory>
- [S4] <https://semver.org/spec/v2.0.0.html>
- [S5] <https://www.oreilly.com/library/view/test-driven-development/0321146530/>
- [S6] <https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions>
- [S7] <https://www.iso.org/standard/77451.html>

**Unverified points** carried forward:

- How Claude Code discovers a plugin under `~/.claude/skills/<name>/` (R3). D1 does not depend on it.
- Whether turn quality or eval pass rates change without the hook (spec, Edge Cases).
- The exact section wording of S5–S7, which were not fetched. S4 §9–§11 was fetched on 2026-10-07 and is no longer unverified (analysis A5).
- That `claude plugin validate --strict` accepts `0.3.0+local.no-stop-hook` in practice: S2 says the field is not checked against semver, but no run has confirmed it yet; T016 re-runs the validator after the version change (analysis A2).

## Project Structure

### Documentation (this feature)

```text
specs/042-remove-minto-stop-hook/
├── plan.md              # This file
├── research.md          # Phase 0: decisions R1–R9 with citations
├── data-model.md        # Phase 1: package and installed-copy entities
├── quickstart.md        # Phase 1: validation scenarios V1–V6
├── contracts/
│   └── minto-package.md # Phase 1: C1 hooks, C2 manifest, C3 docs
├── checklists/
│   └── requirements.md  # From /speckit-specify
└── tasks.md             # Phase 2 (/speckit-tasks; not created here)
```

### Source Code (repository root)

```text
.claude/skills/minto-pyramid/
├── .claude-plugin/plugin.json   # EDIT: version → 0.3.0+local.no-stop-hook (D6)
├── hooks/hooks.json             # DELETE (D1); hooks/ removed with it
├── tests/test_package.py        # EDIT: test_stop_hook → test_declares_no_hooks (D8)
├── references/anthropic-guidance.md  # EDIT: line 24 only (D11, FR-003 exception)
└── README.md                    # EDIT: layout, design, enforcement model, portability (FR-005)

README.md                        # EDIT: drop "Stop-hook check" and the verbatim claim for minto-pyramid (lines 56–60); tree comment line 153 (FR-006)
README.ja.md                     # EDIT: same facts as README.md (FR-006)
docs/claude-config-design.md     # EDIT: line 87, "上流のまま取り込んだ2つのプラグイン" (D7, FR-006)
tests/run-config-pyramid.sh      # EDIT: comment lines 132–134 only, no assertion change (D7, FR-006)
```

Unchanged, per FR-003 and FR-007: `SKILL.md`, `rules/`, `templates/`, `references/` (except `anthropic-guidance.md` line 24), `evals/`, `.claude/skills/maintaining-living-documentation/`, `.claude/settings.json`, `.claude/rules/`, `install.sh`, `archive/`.

**Structure Decision**: The change stays inside the existing vendored package and the documents that describe it. No new directories are created.

## Implementation Order

1. **Red**: Replace `test_stop_hook` with `test_declares_no_hooks`, run the package tests, and confirm exactly that test fails (quickstart V1).
2. **Green**: Delete `hooks/hooks.json` and `hooks/`, then set the manifest version (D6). Re-run the package tests and the strict validator (V2).
3. **Docs**: Update the package README and `references/anthropic-guidance.md` line 24, then `README.md` and `README.ja.md` together, then `docs/claude-config-design.md` and the test comment (V4).
4. **Regression**: Re-run V2 in full (package tests, strict validator, and the version check, so the D6 version is validated after it is set; analysis A2), then the repository test suites (V3) and the living-documentation link check (`check_links.py --changed`).
5. **Install** (user's machine, user-run or user-approved): run `install.sh`, confirm that the installed copy has no hooks, and start a new session (V5, V6).

Steps 1→2 are a strict dependency. Step 3 can run in parallel with step 2. Step 4 depends on steps 2 and 3, and step 5 on step 4.

## Complexity Tracking

No Constitution Check violations.

## Analysis Remediation Log

Findings re-derived on 2026-10-07 (the original `/speckit-analyze` output was not persisted; see spec.md, Analysis Remediation Log). Changes made in this file:

| ID | Severity | Finding | Change here |
|----|----------|---------|-------------|
| A1 | HIGH | `references/anthropic-guidance.md` line 24 contradicts the package after the change, but `references/` was frozen | D11, Constitution Check row, Source Code tree, Unchanged list, Implementation Order step 3 |
| A2 | MEDIUM | The manifest version (D6) could be set after the last validator run, so C2.1/C2.3 were never checked on the final state | Implementation Order step 4; new unverified point |
| A4 | LOW | Line references were off: `README.md` minto passage is lines 56–60; the `tests/run-config-pyramid.sh` comment is lines 132–134 (observed) | Source Code tree |
| A5 | LOW | S4 wording was marked unverified | D6 now quotes S4 and S2 as fetched on 2026-10-07 |
| A7 | LOW | Scale/Scope count omitted the reference file | Scale/Scope |
