# Data Model: Codex configuration artifacts

**Feature**: 021-codex-official-import | **Date**: 2026-08-10

This feature has no runtime data. Its "entities" are configuration artifacts, and its "state transitions" are what happens to each one. Modelling them explicitly is what makes the removal checkable — `tests/run-codex-references.sh` and `quickstart.md` both validate against this table.

## Entity: Configuration Artifact

| Field | Meaning |
|---|---|
| `path` | Repository-relative location |
| `origin` | `hand-ported` (written by a human for Codex), `claude-native` (Claude's own), or `tool-generated` (produced by `/import` or `migrate-to-codex`) |
| `end_state` | `deleted`, `relocated`, `rewritten`, `generated-untracked`, or `unchanged` |
| `tracked` | Whether git tracks it after the change |
| `validation` | The assertion that must hold when the change is done |

## Lifecycle states

```
hand-ported ──┬──> deleted              (no replacement; absence documented)
              ├──> relocated            (content moves to a path Codex reads natively)
              └──> rewritten            (file survives, content replaced)

tool-generated ──> generated-untracked  (exists on a developer machine, never in git)

claude-native ───> unchanged            (NFR-002)
```

## Instances

### Deleted

| path | origin | validation |
|---|---|---|
| `.agents/skills/{adr,clarifier,coder,digital-agency-frontend,minto-builder,minto-reviewer,minto-rewriter,scrum-master}` | hand-ported | Path absent; `git ls-files .agents` empty |
| `.codex/hooks/*.sh` (4) | hand-ported | Path absent; absence of edit protection documented per FR-006 |
| `.codex/rules/guardrails.rules` | hand-ported | Path absent; absence documented per FR-006 |
| `.codex/prompts/verify-config.md` | hand-ported | Path absent |
| `.codex/README.md` | hand-ported | Path absent; no live doc links to it |
| `tests/run-codex-sync.sh`, `tests/run-codex-sync-drift.sh` | hand-ported | Paths absent; no `SYNC-\d+` token anywhere in `tests/` |

### Relocated

| from → to | origin | validation |
|---|---|---|
| `.codex/AGENTS.md` → `AGENTS.md` (repo root) | hand-ported | Root `AGENTS.md` is a **regular file** (not a symlink), > 1 KiB, ≤ 32 KiB, contains no line matching `^@`, and names the repository's skill routing and clarification rules |

**Why the size band**: > 1 KiB rules out the current one-sentence pointer and the converter's symlink-to-`CLAUDE.md` outcome; ≤ 32 KiB is Codex's instruction budget, the constraint spec 014 already designed `.codex/AGENTS.md` against.

### Rewritten

| path | origin | validation |
|---|---|---|
| `README.md` § "Codex CLI support" | hand-ported | Satisfies every assertion in `contracts/codex-setup-procedure.md` |
| `README.ja.md` (Codex section) | hand-ported | Same assertions, Japanese |
| `install.sh` | hand-ported | Zero Codex/agents deployment logic; Claude-side behaviour byte-identical in effect |
| `.gitignore` | claude-native | Contains `.codex/` and `.agents/` entries |

### Generated-untracked

| path | origin | validation |
|---|---|---|
| `.codex/config.toml`, `.codex/hooks.json`, `.codex/agents/*.toml` | tool-generated | `git status --porcelain` is clean after a developer runs the procedure |
| `.agents/skills/**` | tool-generated | Same |
| `~/.codex/**` | tool-generated | Out of repository scope; not asserted |

### Unchanged (NFR-002 — asserted, not assumed)

| path | validation |
|---|---|
| `.claude/hooks/*.sh` | `git diff` touches nothing under `.claude/hooks/` |
| `.claude/settings.json` | `permissions` retains allow 25 / ask 5 / deny 9; `hooks` retains all five registrations |
| `scripts/guardrails/*.sh` | Unmodified; `tests/run-{pre-edit,destructive-command,post-edit-format,prompt-secret}-guard.sh` still pass |
| `.claude/rules/*.md`, `.claude/skills/**` | Unmodified |

## Cross-cutting rules

1. **Immutability** (NFR-001): nothing under `specs/0*/` or `docs/adr/000{1,2,3}-*` is edited. The new ADR supersedes; it does not rewrite.
2. **No dangling reference** (SC-002): for every `deleted` instance, no file outside `specs/` and `docs/adr/` may contain its path.
3. **Official sources only** (FR-012): every Codex documentation URL must be on `developers.openai.com` or `learn.chatgpt.com`. No third-party documentation mirror may be cited anywhere.
4. **Symlink hazard** (plan D1): root `AGENTS.md` must never become a symlink. A `migrate-to-codex` run will try; the procedure warns, the test catches.
