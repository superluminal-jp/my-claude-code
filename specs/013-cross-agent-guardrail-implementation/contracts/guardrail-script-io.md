# Contract: Shared Guardrail Script I/O

This is the interface each of the three shared scripts under `scripts/guardrails/` exposes to its two callers (a Claude Code hook wrapper and a Codex CLI adapter — see `data-model.md`'s Shared Guardrail Script / Codex CLI Adapter entities). It is deliberately tool-agnostic: neither caller's own hook event names, matcher syntax, or response format appear here — each adapter is responsible for translating to and from this contract (per FR-006/FR-016/FR-019 and R6).

## Common conventions

- **Input**: JSON on stdin.
- **Output**: JSON on stdout, exactly one object, no trailing content.
- **Exit code**: `0` on successful execution *regardless of the decision reached* (the decision is carried in the JSON body, not the exit code — this is what lets one script serve two callers with different exit-code conventions). Non-zero exit means the script itself failed (malformed input, missing `jq`, unexpected internal error) — **every caller MUST treat a non-zero exit or unparseable stdout the same way it treats a `deny` decision, never as `allow`** (spec Edge Cases: "a broken guardrail must fail closed, not fail open").
- **No side effects on decision**: `destructive-command` and `pre-edit-block` never modify the filesystem; `post-edit-format` is the one script that does (it is automation, not a gate).

## `destructive-command.sh` (Q6 / FR-006)

**Input**:

```json
{ "command": "rm -rf /tmp/foo" }
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `command` | string | yes | The literal shell command string about to run |

**Output**:

```json
{ "decision": "deny", "reason": "rm -rf targeting root, home, or current directory is permanently blocked by policy." }
```

| Field | Type | Notes |
|---|---|---|
| `decision` | `"allow"` \| `"deny"` \| `"ask"` | Matches `.claude/hooks/pre-bash.sh`'s existing three-way outcome (hard block / allow / route to confirmation) |
| `reason` | string | Empty string when `decision` is `"allow"`; human-readable otherwise, reusing `pre-bash.sh`'s existing message text verbatim (FR-009 requires identical behavior, which includes identical messages) |

Category coverage (must match `.claude/hooks/pre-bash.sh` exactly, per FR-009): force push, `git reset --hard`, `git clean -f`, `rm -rf` against root/home/cwd (→ `deny`), other `rm -rf` (→ `ask`), `mkfs`/`dd`/fork-bomb, `curl\|bash`, non-HTTPS request, credential-path read/write, global package installs (→ `deny`), `sudo` (→ `ask`).

**Caller-side `ask` handling**: A caller whose host tool has no three-way primitive MUST treat `ask` as `deny` (FR-008), never `allow`.

## `pre-edit-block.sh` (Q9/Q10 / FR-016)

**Input**:

```json
{ "tool_name": "Edit", "path": ".git/config", "project_dir": "/Users/example/repo" }
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `tool_name` | string | no | Used only for the denial message text (e.g. "Cannot Edit on main branch"); logic does not branch on it |
| `path` | string | yes | The file path the edit/write/delete targets |
| `project_dir` | string | no | Repository root to resolve the current branch against; if absent, the branch check is skipped (matches `.claude/hooks/pre-edit.sh`'s existing `${CLAUDE_PROJECT_DIR:-}` fallback behavior — no false positives when the project directory is unknown) |

**Output**:

```json
{ "decision": "deny", "reason": "Direct modification of .git/ is not allowed." }
```

| Field | Type | Notes |
|---|---|---|
| `decision` | `"allow"` \| `"deny"` | Two-way only — `pre-edit.sh` has no "ask" tier today, so none is added here |
| `reason` | string | Empty when `allow`; otherwise reuses `pre-edit.sh`'s existing message text (FR-018) |

Category coverage (must match `.claude/hooks/pre-edit.sh` exactly, per FR-018): path under `.git/` → `deny`; current branch (resolved from `project_dir`) is `main`/`master` → `deny`; everything else → `allow`. (`pre-edit.sh`'s CI/settings/production-path *warnings* are Q1, not part of this script — they are `AGENTS.md` prose only, per spec FR-001, never a blocking decision even in the original hook.)

## `post-edit-format.sh` (Q7 / FR-019)

**Input**:

```json
{ "path": "scripts/guardrails/destructive-command.sh" }
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `path` | string | yes | The file path just written |

**Output**:

```json
{ "warnings": [] }
```

| Field | Type | Notes |
|---|---|---|
| `warnings` | array of string | Empty array when nothing to report. Never a `decision` field — this script never blocks (matches `.claude/hooks/post-edit-format.sh`'s current `exit 0` always behavior, per FR-021) |

Category coverage (must match `.claude/hooks/post-edit-format.sh` exactly, per FR-021): `*.sh` → `shfmt -w -i 2` then `shellcheck` (warnings surfaced, file reformatted in place); `*.yaml`/`*.yml` → `yamllint` (warnings only); `*.json` → `jq empty` syntax check (warning only); `*/CLAUDE.md` → verify every `@import` line resolves (warning only). Missing tools are silently skipped, matching current behavior.

## Caller responsibilities (not part of this contract, listed for cross-reference)

| Caller | Translates this contract to/from |
|---|---|
| `.claude/hooks/pre-bash.sh` (refactored) | Claude Code's `PreToolUse` JSON stdin/stdout, `exit 2` for hard block, `hookSpecificOutput.permissionDecision: "ask"` for the ask tier — unchanged from today's behavior (FR-009) |
| `.claude/hooks/pre-edit.sh` (refactored) | Claude Code's `PreToolUse` JSON stdin/stdout, `exit 2` for block — unchanged (FR-018) |
| `.claude/hooks/post-edit-format.sh` (refactored) | Claude Code's `PostToolUse` JSON stdin — unchanged (FR-021) |
| `.codex/hooks/destructive-command-adapter.sh` | Codex CLI's `PreToolUse` (matcher `Bash`) JSON stdin/stdout (R1) — new, FR-007 |
| `.codex/hooks/pre-edit-adapter.sh` | Codex CLI's `PreToolUse` (matcher `apply_patch\|Edit\|Write`) JSON stdin/stdout (R1) — new, FR-017 |
| `.codex/hooks/post-edit-adapter.sh` | Codex CLI's `PostToolUse` (matcher `apply_patch\|Edit\|Write`) JSON stdin/stdout (R1) — new, FR-020 |

No Cursor caller exists (spec FR-015).
