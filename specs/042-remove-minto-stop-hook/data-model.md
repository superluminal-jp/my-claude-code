# Data Model: Remove the Minto Pyramid Stop Hook

There is no runtime data. The "entities" are the configuration artifacts whose
state this feature changes. Decisions are referenced by their IDs in
[research.md](research.md).

## Minto package (repository source)

Path: `.claude/skills/minto-pyramid/`

| Field | Before | After | Rule |
|-------|--------|-------|------|
| `hooks/hooks.json` | present; one `Stop` handler, `type: prompt`, `timeout: 30` | absent | FR-001; R1 |
| manifest `hooks` key | absent | absent | FR-001; a manifest key would merge with the default file [S2] |
| manifest `version` | `0.3.0` | `0.3.0+local.no-stop-hook` | R5; [S4] §10 |
| `SKILL.md`, `rules/`, `templates/`, `references/`, `evals/` | present | unchanged (byte-identical), except the row below | FR-003 |
| `references/anthropic-guidance.md` line 24 | "This plugin uses a `Stop` hook only for observable-output compliance." | states that the plugin declares no hooks and relies on the skill's completion check | FR-003 exception; plan D11 (analysis A1) |
| `tests/test_package.py` | 5 tests incl. `test_stop_hook` | 5 tests; `test_stop_hook` replaced by `test_declares_no_hooks` | FR-004; R7 |
| `README.md` | describes Stop hook as enforcement | describes self-applied completion check, no hooks, local divergence | FR-005 |

**Validation rules**

- Declared hooks = (`hooks/hooks.json` if present) ∪ (manifest `hooks` if present) [S2]. Both are empty after the change, so the count is 0 (SC-001).
- `claude plugin validate --strict .` passes. A missing `hooks/` directory is not an error, because that path is only a default [S2].

## Installed copy

Path: `~/.claude/skills/minto-pyramid/`

| State | Condition | Hooks declared |
|-------|-----------|----------------|
| Stale | `install.sh` not re-run after the change | 1 (`Stop`) **[observed today]** |
| Current | `install.sh` re-run | 0 |

**Transition**: Stale → Current, only by running `install.sh`, which replaces the directory exactly (R2). There is no reverse transition except reinstalling from an older commit.

**Effect timing**: A running session keeps the hooks it snapshotted at start. The new state applies from the next session [S1] (R3).

## Repository documentation

| Document | Field changed | After |
|----------|---------------|-------|
| `README.md` §managed paths (lines 56–60) and tree (line 153) | `minto-pyramid` description | no "Stop-hook check"; marked as locally modified (Stop hook removed) |
| `README.ja.md` (lines ~47–48) | same | same facts, in Japanese |
| `docs/claude-config-design.md` line 87 | "上流のまま取り込んだ2つのプラグイン" | `minto-pyramid` noted as locally modified |
| `tests/run-config-pyramid.sh` lines 132–134 | comment "kept verbatim" | comment notes the local hook removal |

Sources: [S1] <https://code.claude.com/docs/en/hooks>, [S2] <https://code.claude.com/docs/en/plugins-reference>, [S4] <https://semver.org/spec/v2.0.0.html>.
