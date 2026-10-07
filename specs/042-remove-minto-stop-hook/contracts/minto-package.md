# Contract: `minto-pyramid` package after hook removal

The package is consumed by Claude Code's plugin loader and by readers of the
repository's documentation. These are the observable guarantees after this
feature. Each clause is tied to a check in [../quickstart.md](../quickstart.md).

## C1. Hook surface (consumer: Claude Code plugin loader)

- C1.1 `hooks/hooks.json` does not exist in the package. → V2
- C1.2 `.claude-plugin/plugin.json` has no `hooks` key. → V2
- C1.3 Consequently the package declares 0 hooks for every event. The two locations above are the only ones Claude Code reads plugin hooks from: the default file plus the manifest key, which merges with it [S2]. → V2, V5
- C1.4 `tests/test_package.py::test_declares_no_hooks` enforces C1.1 and C1.2. → V1, V2

## C2. Manifest and skill (consumer: plugin loader, skill matcher)

- C2.1 `name` stays `minto-pyramid`, and `version` is `0.3.0+local.no-stop-hook` (build metadata marks the local build [S4] §10). → V2
- C2.2 `SKILL.md`, `rules/core.md`, `rules/completion-check.md`, `templates/*`, `references/*`, and `evals/*` are byte-identical to the pre-change commit, except `references/anthropic-guidance.md` line 24, which no longer states that the plugin uses a `Stop` hook (spec FR-003 exception, plan D11, analysis A1). → V3, V4
- C2.3 `claude plugin validate --strict .` reports no error or warning that this change introduced. → V2

## C3. Documentation facts (consumer: maintainers, future re-vendorers)

`README.md` and `README.ja.md` state the same facts:

- C3.1 `minto-pyramid` applies Minto structure as advisory guidance and has no `Stop`-hook check.
- C3.2 The local copy diverges from upstream: its Stop hook was removed. A verbatim re-copy would restore the hook.
- C3.3 `maintaining-living-documentation` remains described as before, including its `Stop`-hook gate.

The package `README.md` states:

- C3.4 Compliance relies on the skill's self-applied completion check (`rules/completion-check.md`), and the package declares no hooks.
- C3.5 The removal rationale separates sourced and observed facts from inference (FR-008).

Checked by V4.

Sources: [S2] <https://code.claude.com/docs/en/plugins-reference>, [S4] <https://semver.org/spec/v2.0.0.html>.
