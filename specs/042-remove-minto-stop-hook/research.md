# Research: Remove the Minto Pyramid Stop Hook

**Feature**: `042-remove-minto-stop-hook` | **Date**: 2026-10-07 | **Spec**: [spec.md](spec.md)

Evidence labels used below: **[observed]** — seen directly in this repository or
the local install on 2026-10-07; **[sourced]** — stated by a cited document;
**[inferred]** — a conclusion drawn from the above; **[unverified]** — not
established by any check in this research.

## Sources

| ID | Source | URL |
|----|--------|-----|
| S1 | Anthropic, *Claude Code — Hooks reference* | <https://code.claude.com/docs/en/hooks> |
| S2 | Anthropic, *Claude Code — Plugin manifest reference* | <https://code.claude.com/docs/en/plugins-reference> |
| S3 | Anthropic, *Claude Code — How Claude remembers your project* | <https://code.claude.com/docs/en/memory> |
| S4 | T. Preston-Werner, *Semantic Versioning 2.0.0* (§4 major version zero, §10 build metadata) | <https://semver.org/spec/v2.0.0.html> |
| S5 | K. Beck, *Test-Driven Development: By Example*, Addison-Wesley, 2002 (red → green → refactor) | <https://www.oreilly.com/library/view/test-driven-development/0321146530/> |
| S6 | M. Nygard, "Documenting Architecture Decisions", 2011 (ADR practice) | <https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions> |
| S7 | ISO/IEC/IEEE 26514:2022, *Design and development of information for users* (information must match the system it describes) | <https://www.iso.org/standard/77451.html> |

S1 and S2 were re-fetched on 2026-10-07 for this research. S3 is carried over
from the spec and was not re-fetched. S4 §9–§11 was fetched on 2026-10-07
during analysis remediation and confirms R5 (§10: build metadata "does not
affect version precedence"; §9: pre-release versions rank lower than the
normal version) **[sourced]**. S5–S7 were not fetched; they are cited for
well-established practice, and their exact wording is **[unverified]** here.

## R1. Which artifact carries the hook, and what removing it requires

- **Decision**: Delete `.claude/skills/minto-pyramid/hooks/hooks.json` (and the
  then-empty `hooks/` directory). Leave `.claude-plugin/plugin.json` without a
  `hooks` key (it has none today).
- **Rationale**:
  - The hook is a single `Stop` handler of `"type": "prompt"` in
    `hooks/hooks.json` **[observed]**. The manifest has no `hooks` key
    **[observed]**.
  - Plugin hooks load from `hooks/hooks.json` by default, and a manifest
    `hooks` key *merges* with that file rather than replacing it **[sourced:
    S2, "Standard layout" and "How each key combines with its default
    location"]**. So the default file is the only declaration to remove, and the
    manifest must keep having no `hooks` key (FR-001).
- **Alternatives considered**:
  - *Replace the file with an empty `{"hooks": {}}`*: rejected. It leaves an
    artifact that suggests a hook is expected and adds nothing; deletion is the
    smaller coherent change.
  - *Disable through settings instead of editing the package*: rejected. The
    user asked to retire the hook, not to keep it shipped but switched off, and
    `.claude/settings.json` is out of scope (FR-007).

## R2. Does re-running `install.sh` remove the installed copy?

- **Decision**: No installer change. The plan relies on the existing sync.
- **Rationale**: `install.sh` `sync_path` runs `rm -rf "$dst"` and then
  `cp -R "$src" "$dst"` for `skills/` **[observed: `install.sh` lines 21–30,
  67–80]**, so a file deleted from the source disappears from
  `~/.claude/skills/minto-pyramid/` on the next run. The installed copy
  currently still has `hooks/hooks.json` **[observed]**.
- **Alternatives considered**: An explicit cleanup step for the old hook file:
  rejected as redundant with the exact-replacement sync.

## R3. When does the removal take effect in a session?

- **Decision**: Document "re-run `install.sh`, then start a new session" as the
  activation step.
- **Rationale**: Hooks are snapshotted at session start; plugin hooks take
  effect when the plugin is enabled or reloaded **[sourced: S1]**.
- **Unverified**: How Claude Code loads a plugin that sits in
  `~/.claude/skills/<name>/` (a "skills-directory plugin" in this repository's
  README) is not described on S1 or S2 as fetched. That the hook ran in
  practice is supported only indirectly: commit `753eb52` exists to stop a Stop
  hook "re-output loop" **[observed]**. The plan does not depend on the loading
  path: deleting the file removes the hook under any path that reads it.

## R4. Rationale for the removal

- **Decision**: Record the rationale as two items with explicit evidence labels;
  do not present either as the user's stated reason.
- **Rationale**:
  1. *Per-turn cost*: a prompt hook sends the hook input to a model for a
     single-turn evaluation **[sourced: S1]**, and the package README says the
     hook "adds a small model-call cost at turn completion" **[observed]**.
  2. *Correction rounds keep the turn running*: a blocking `Stop` hook prevents
     the stop and continues the conversation **[sourced: S1]**; commit `753eb52`
     was needed to stop a re-output loop **[observed]**.
  3. *Guidance stays*: `CLAUDE.md` and rules are context, not enforced
     configuration **[sourced: S3]**, and the skill's step 10 already applies
     `rules/completion-check.md` before completion **[observed]**. Structural
     checking therefore continues as advisory self-checking.
  - That these are the user's reasons is **[inferred]**; the user stated only
    "retire the hook".
  - Whether output quality changes without the hook is **[unverified]**; no
    eval was run (spec, Edge Cases).

## R5. Version identifier of the modified package

- **Decision**: Change `version` from `0.3.0` to `0.3.0+local.no-stop-hook`.
- **Rationale**:
  - The field is "a version string, not checked against semver" **[sourced:
    S2, `version`]**, so any string validates.
  - SemVer build metadata (`+…`) marks a build without claiming a new upstream
    release, and is ignored for precedence **[sourced: S4 §10]**. Bumping to
    `0.4.0` would collide with a future upstream `0.4.0` that may still ship the
    hook **[inferred]**.
- **Alternatives considered**:
  - *Leave `0.3.0`*: rejected. The divergence would be invisible in the
    manifest, which is the weak point User Story 3 is guarding against.
  - *Pre-release `0.3.1-local`*: rejected. Pre-release tags rank *below* the
    release they name **[sourced: S4 §9, §11]**, which misstates the
    relationship.

## R6. "Copied verbatim" claim in repository docs

- **Decision**: Replace the verbatim claim for `minto-pyramid` in `README.md`,
  `README.ja.md`, `docs/claude-config-design.md` §87 (the "上流のまま取り込んだ"
  phrase), and the comment in `tests/run-config-pyramid.sh` lines 132–134. Record
  the local divergence: the Stop hook is removed, and the stop-loop edit of
  `753eb52` preceded it.
- **Rationale**:
  - The claim was already inexact before this feature: `753eb52` changed
    `hooks/hooks.json` and the README **[observed]**. Removing the hook makes it
    plainly false.
  - User documentation must describe the system as it is **[sourced: S7]**.
- **Alternatives considered**: Keeping the claim and noting the change only in
  the package README: rejected, because the repository README is where a
  re-vendorer reads the vendoring policy (spec, User Story 3).
- **Addendum (analysis A1, 2026-10-07)**: `references/anthropic-guidance.md`
  line 24 also says "This plugin uses a `Stop` hook only for observable-output
  compliance" **[observed]**. It is rewritten (plan D11, spec FR-003
  exception). Lines 9 and 21–23 state Claude Code facts that S2 still confirms
  **[sourced: S2, re-fetched 2026-10-07]**, so they stay.
- **Scope note**: The `tests/run-config-pyramid.sh` comment is documentation
  inside a test; editing it does not change any assertion (FR-009).

## R7. Test strategy

- **Decision**: Red → green. First replace `test_stop_hook` with
  `test_declares_no_hooks` (asserts that `hooks/hooks.json` is absent and that
  the manifest has no `hooks` key); it fails against the current package. Then
  delete the hook file; it passes.
- **Rationale**: A failing automated check comes before changing an automatable
  contract **[sourced: S5; also this repository's `CLAUDE.md`]**. Baseline
  before change: 5/5 package tests pass and `claude plugin validate --strict .`
  reports "Validation passed" **[observed 2026-10-07]**.
- **Alternatives considered**: Deleting `test_stop_hook` without a replacement:
  rejected. Nothing would then stop a verbatim re-copy from bringing the hook
  back (spec, Edge Cases).

## R8. ADR

- **Decision**: No ADR is created. One is proposed in the completion report.
- **Rationale**: The repository's documentation rule creates ADRs only when the
  user asks **[observed: SessionStart living-documentation rule]**. ADR practice
  records significant decisions **[sourced: S6]**; whether this one qualifies is
  the user's call.

## R9. AWS research

- **Decision**: Not applicable.
- **Rationale**: The feature touches no AWS service (spec, Assumptions), so the
  AWS Knowledge and AWS Documentation MCP servers have nothing to look up.
