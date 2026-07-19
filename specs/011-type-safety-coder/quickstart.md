# Quickstart: Validating Type Safety Enforcement in Coder Skill

This guide validates that the "Type Safety" instruction block added to `~/.claude/skills/coder/SKILL.md` produces the observable behavior defined in [contracts/type-safety-behavior.md](./contracts/type-safety-behavior.md).

## Prerequisites

- Claude Code CLI installed and on `PATH` (`claude` command available).
- This repo checked out with the `011-type-safety-coder` branch active.
- The `coder` skill at `~/.claude/skills/coder/SKILL.md` updated with the new "Type Safety" section (produced by `/speckit-implement`).

## Setup

No additional setup — the test runner drives `claude -p` in headless mode per scenario; no server or build step is required.

## Run the validation suite

```bash
bash tests/run-type-safety-coder.sh
```

Expected outcome: all four scenarios (`001`–`004` under `tests/type-safety-coder/`) report **PASS**, matching the pattern of `bash tests/run-live-documentation.sh`.

## Manual spot-check (optional)

To confirm behavior interactively rather than via the headless runner:

1. **Public interface annotation** (Contract 1): ask Claude to add a new exported function to a TypeScript or type-hinted Python file in a scratch repo. Confirm the generated signature carries parameter and return types matching the file's existing convention.
2. **No unsafe escape** (Contract 2): introduce a type error (e.g., pass a `string` where a `number` is expected) and ask Claude to fix it. Confirm the fix corrects the type rather than adding `as any` / `# type: ignore` without explanation.
3. **Type checker run** (Contract 3): in a project with `tsc`/`mypy` configured, ask Claude to complete a small change, then check its final response — it should mention running the type checker alongside other verification steps.
4. **Boundary validation** (Contract 4): ask Claude to handle a parsed JSON response from an external API. Confirm the resulting code validates/narrows the payload shape before treating it as a typed value, rather than casting it directly.

## Expected artifacts after `/speckit-implement`

- `~/.claude/skills/coder/SKILL.md` — new "Type Safety" section added, existing sections unchanged.
- `tests/type-safety-coder/001-typed-public-interface.md` … `004-boundary-validation.md` — new scenario files.
- `tests/run-type-safety-coder.sh` — new runner, executable, mirroring `tests/run-live-documentation.sh`.
- `CLAUDE.md` (repo root) — plan reference updated to `specs/011-type-safety-coder/plan.md` (per existing convention, see `specs/009-live-doc-enforcement/plan.md` T009).
