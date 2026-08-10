# Contract: The documented Codex setup procedure

**Feature**: 021-codex-official-import | **Date**: 2026-08-10

What `README.md` § "Codex CLI support" and `README.ja.md` must contain after the change. Written as assertions so the procedure can be checked, not just read. Satisfies FR-004, FR-006, FR-008, FR-011, FR-012, FR-013, FR-014.

## A. Entry points (FR-004, FR-012)

- **A0** — Designates **`/import` as the primary path** and `migrate-to-codex` as a secondary inspection tool. `research.md` § R-08 measured the two on the same input and they are **not equivalent**: `/import` leaves the root `AGENTS.md` and existing skills alone, while the converter symlinks `AGENTS.md` to `CLAUDE.md` and overwrites all 23 skills with copies. The procedure MUST NOT present them as interchangeable.
- **A1** — Names both official entry points: `/import` (Codex CLI, interactive, TUI-only — there is no `codex import` subcommand) and the `migrate-to-codex` curated skill.
- **A2** — States how each is obtained. `migrate-to-codex` ships in Codex's curated skill set and caches locally under `~/.codex/vendor_imports/skills/skills/.curated/migrate-to-codex/`; it also carries a non-interactive CLI at `scripts/migrate-to-codex.py`.
- **A3** — States that `/import` **is not available** during a running task, in a remote session, or while connected to a local app-server daemon.
- **A4** — Links only to `developers.openai.com/codex/*` (or its `learn.chatgpt.com/docs/*` redirect target). No third-party documentation host.
- **A5** — States that the developer runs this manually; neither `install.sh` nor CI performs it.

## B. Generated artifacts (FR-005)

- **B1** — States that `.codex/` and `.agents/` are generated locally and git-ignored; an import must never produce a commit-ready diff.
- **B2** — Recommends inspecting before writing: `--scan-only`, `--plan`, `--doctor`, then `--dry-run`, then the real run, then `--validate-target`.

## C. Guardrails — what Codex gets and does not get (FR-006, FR-011, FR-013)

The section MUST contain a coverage statement equivalent to this table. Wording may differ; the four verdicts may not.

| Guardrail | Claude Code | Codex |
|---|---|---|
| Destructive command blocking | Yes (`PreToolUse`/Bash) | **Yes** — measured 2026-08-10: the tool call is blocked and the shared script's reason string is surfaced verbatim |
| Prompt secret scanning | Yes (`UserPromptSubmit`) | **Yes** — measured 2026-08-10: the turn is blocked and no model response is produced |
| Edit protection (`.git/`, `main`/`master`) | Yes (`PreToolUse` on `Edit\|Write\|Delete`) | **No.** Codex fires `PreToolUse`/`PostToolUse` for shell commands only; edits go through `apply_patch`. Not restorable through any supported path |
| Post-edit formatting | Yes (`PostToolUse`) | **No**, same reason |
| Allow/prompt command policy | Yes (`settings.json#permissions`) | **No.** The converter has no path for `settings.json#permissions` |
| Spec Kit prompt expansion | Yes (`UserPromptExpansion`) | **No.** No Codex equivalent event |

- **C1** — Includes the two "Yes" rows *with their precondition*: the **`/hooks` trust step** must be completed, because non-managed hooks are skipped until reviewed and trust is keyed to the hook's hash. The procedure MUST NOT tell developers to set `[features].codex_hooks` — that flag does not exist in Codex 0.147.0; the real flag is `hooks`, which is `stable` and enabled by default (measured, `research.md` § R-08). Any third-party guide saying otherwise is stale.
- **C5** — Warns that hooks registered in more than one config layer **fire once per layer**: Codex merges layers rather than overriding them, so an `~/.codex/hooks.json` plus a `~/.codex/config.toml` `[hooks]` block plus a project `.codex/hooks.json` means the same guard runs three times per turn, and Codex prints `warning: loading hooks from both … prefer a single representation for this layer`. The procedure must tell developers to keep one representation per layer. (Removing `install.sh`'s managed block, per FR-002, eliminates one of the three sources.)
  - *Not* a concern: the doubly-quoted `"command": "'/abs/path.sh'"` string `/import` writes. Measured 2026-08-10 — it executes correctly. No fix-up needed.
- **C6** — Notes that `/import` copies Claude hook *scripts* it never registers (`speckit-expand-update.sh`, `statusline.sh` appear in `.codex/hooks/` with no entry in `.codex/hooks.json`); their presence is not evidence they run.
- **C2** — Includes the four "No" rows explicitly. Silence is a contract violation: an operator must be able to learn what is missing without running an experiment.
- **C3** — States that the Claude-side equivalents are unaffected.
- **C4** — Notes that Codex `PreToolUse`/`PostToolUse` also do not fire for hosted tools (e.g. WebSearch).

## D. Instructions (FR-014, plan D1)

- **D1** — States that this repository's operating rules reach Codex through the **repo-root `AGENTS.md`**, which Codex reads natively by directory-walk composition.
- **D2** — Warns that **Codex does not expand `@` imports** (`openai/codex` issue #17401 is open), so `AGENTS.md` must stay flat — it cannot delegate to `.claude/rules/*.md` the way `CLAUDE.md` does.
- **D3** — Warns that **a `migrate-to-codex` run** (not `/import` — measured, `research.md` § R-08) reports `symlinked: AGENTS.md - Linked to CLAUDE.md` and replaces the root `AGENTS.md` with a symlink to the one-line `CLAUDE.md`, destroying the flattened content. Instructs the developer to restore it (`git checkout AGENTS.md`) if that happens.
- **D4** — States that user-scope Codex guidance (`~/.codex/AGENTS.md`) is no longer deployed by `install.sh`; project scope covers work in this repository.

## E. Known conversion gaps (FR-008)

- **E1** — States the skill behaviour per path: `/import` adds only missing skills and leaves existing ones alone; **`migrate-to-codex` overwrites every skill with a copy**, replacing symlinks, so edits to `.claude/skills/` then require a re-run to propagate.
- **E2** — States that generated subagent definitions under `.codex/agents/` exist but **this repository does not rely on them** — Codex custom agents set defaults rather than isolating context from the parent turn, so they do not provide what `verification-runner` needs.
- **E3** — Notes the converter's own readiness signal for this repo at the time of writing: `readiness: low`, 24 manual-review items, mostly Claude-only skill frontmatter (`when_to_use`, `metadata`, `argument-hint`, `context`) that becomes prose.
- **E4** — Notes that `speckit-*` skills are regenerated per project by `specify init --integration codex` (ADR-0001) and need not be migrated.

## F. Cleanup for existing installs

- **F1** — Lists what the previous `install.sh` left in the user's home, so a developer can remove it deliberately: `~/.codex/hooks/*-adapter.sh`, `~/.codex/rules/guardrails.rules`, `~/.codex/prompts/verify-config.md`, `~/.agents/skills/` (8 symlinks), and the two `# >>> my-claude-code managed …` marker blocks in `~/.codex/config.toml`.
- **F2** — States that the new `install.sh` does **not** remove these automatically, because it does not touch user-owned Codex configuration.

## G. Staying true as upstream changes (FR-015)

Both entry points are moving targets. This section defines how the documentation survives that.

- **G1 — Stamp every behavioural claim.** Any statement about what Codex or the converter does carries the version and date it was measured, e.g. "measured on Codex 0.147.0, 2026-08-10". Unstamped behavioural claims are contract violations.
- **G2 — Name the converter's own staleness.** `references/differences.md` self-reports a "Docs last checked" date and was measurably wrong on two points as of 2026-08-10. The procedure must tell readers to treat it as secondary to a live measurement.
- **G3 — Drift check.** `tests/run-codex-drift.sh` asserts the upstream facts the documentation rests on. It **SKIPs** with a warning when `codex` is not installed (existing convention: `tests/run-codex-sync.sh`), and never fails for that reason alone.

  | Id | Assertion | Why the docs depend on it |
  |---|---|---|
  | `DRIFT-01` | `codex --version` matches the recorded version; a change emits a warning, not a failure | Every stamped claim was measured against that version |
  | `DRIFT-02` | `codex features list` contains `hooks` in an enabled state | The "guardrails work in Codex" rows assume hooks are on by default |
  | `DRIFT-03` | `codex features list` does **not** contain `codex_hooks` | The procedure explicitly tells developers not to set it (C1) |
  | `DRIFT-04` | `codex --help` exposes **no** `import` subcommand | The procedure says `/import` is TUI-only (A1) |
  | `DRIFT-05` | The `migrate-to-codex` skill is present at the documented cache path, and its `Docs last checked` date is reported | A2 names that path; a moved cache breaks the inspection flow |
  | `DRIFT-06` | The converter's `--dry-run` still reports `symlinked: AGENTS.md` | D3's warning exists only because of this behaviour; if it stops, the warning is stale |

- **G4 — Revalidation trigger.** The documentation states: when the drift check warns, re-run `quickstart.md` Steps 4–5 and update the stamped claims. A warning is a prompt to re-measure, not a defect to suppress.

## Verification

`quickstart.md` walks A1–F2. The mechanically checkable subset (A4, B1, and the presence of the C table) is covered by `tests/run-codex-references.sh` RULE-06, RULE-07 and RULE-08; the rest is confirmed by human review recorded against SC-001.
