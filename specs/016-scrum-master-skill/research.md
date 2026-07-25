# Phase 0 Research: Integrate the `scrum-master` skill

**Feature**: 016-scrum-master-skill | **Date**: 2026-07-25 | **Spec**: [spec.md](./spec.md)

All findings below were established by reading or executing the actual artifacts in this repository and on this machine, not from recollection. Each records what was checked and how.

---

## R0 — `allowed-tools` in the source skill does not do what it looks like it does

**Decision**: Drop the `allowed-tools` line from the vendored `SKILL.md`, and move the narrowly-scoped permission into `.claude/settings.json` `permissions.allow`.

**Rationale**:

The source skill declares:

```yaml
allowed-tools: Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/flow_metrics.py *)
```

Two independent problems, both verified:

1. **`allowed-tools` on a skill is a *restriction*, not a grant.** The official Claude Code skills reference bundled on this machine (`~/.claude/plugins/marketplaces/claude-plugins-official/plugins/claude-code-setup/skills/claude-automation-recommender/references/skills-reference.md:89`) documents it as `allowed-tools: Read, Grep, Glob # Restrict tool access` — a plain comma-separated list of **tool names**. The `Tool(specifier)` form is a slash-command convention; every skill example in that reference and in the bundled official skill `deploy-on-aws/…/aws-architecture-diagram/SKILL.md` uses bare names. A value of `Bash(python3 …)` therefore names no tool that exists. It cannot grant a permission, and if it is honoured as a restriction it would leave the skill with an empty tool set — which would also block `Read`, breaking the playbook's own instruction to read its nine `references/*.md` files on demand.
2. **`${CLAUDE_SKILL_DIR}` is not an established variable.** Searching the entire plugin tree on this machine returns `${CLAUDE_PLUGIN_ROOT}` (used by the `openai-codex` plugin's hooks, commands, and agents) and zero occurrences of `CLAUDE_SKILL_DIR`. This skill is being vendored as a user/project skill, not as a plugin, so `CLAUDE_PLUGIN_ROOT` does not apply either. The documented invocation in the playbook body would expand to `python3 /scripts/flow_metrics.py`.

Moving the scoping to `.claude/settings.json` satisfies both FR-014 (no ad-hoc prompt) and FR-015 (scoped to the one script) through the mechanism this repository already uses for exactly this purpose — `permissions.md` § "`.claude/settings.json` permissions" allow-lists `Bash(tests/run-*.sh)`, `Bash(scripts/guardrails/*.sh)` and friends "to avoid prompt friction". Enforcement in `settings.json` is also strictly stronger than a frontmatter field of uncertain semantics.

This does not conflict with FR-002, which pins the skill's *identity* — `name`, `description`, `when_to_use` — not its tool declaration.

**Alternatives considered**:

- *Keep the line verbatim.* Rejected: preserves a declaration that is inert at best and tool-blocking at worst, and leaves the user with a permission prompt on every metrics run (fails FR-014).
- *Rewrite it as `allowed-tools: Bash, Read, Glob, Write`.* Rejected as unnecessary: the skill needs no narrowing, and enumerating tools invites silent breakage the next time the playbook reaches for one not on the list. Omitting the field inherits the session's tools, which is the correct default here.
- *Add a broad `Bash(python3 *)` allow entry.* Rejected outright — directly violates FR-015 and the least-privilege principle in `permissions.md`.

---

## R1 — The playbook's documented invocation must be made resolvable

**Decision**: Replace the `${CLAUDE_SKILL_DIR}` invocation in the playbook body with a path relative to the skill directory, and add two matching `permissions.allow` entries covering the two locations the skill can be loaded from.

**Rationale**: Following R0, the body's example command is broken as written. The skill legitimately lives in two places — `<repo>/.claude/skills/scrum-master/` when working inside a project, and `~/.claude/skills/scrum-master/` after `install.sh` runs. Claude Code's Bash permission patterns are prefix-shaped (every existing entry in `.claude/settings.json` — `Bash(tests/run-*.sh)`, `Bash(git diff *)` — anchors at the start), so a single leading-wildcard pattern is not reliable. Two explicit entries, one per location, keep the grant narrow and anchored:

```text
Bash(python3 .claude/skills/scrum-master/scripts/flow_metrics.py *)
Bash(python3 ~/.claude/skills/scrum-master/scripts/flow_metrics.py *)
```

The exact pattern must be confirmed by observation during implementation rather than assumed — see the verification step in [quickstart.md](./quickstart.md). If neither pattern matches, the fallback is a single prompt on first use, which degrades FR-014 but breaks nothing.

**Alternatives considered**:

- *Leave the body untouched and document the caveat.* Rejected: the spec's own SC-007 requires the helper to work on the first attempt, and a knowingly broken command in a playbook is precisely the "documentation must never lie" failure `live-documentation.md` exists to prevent.
- *Wrap the script in a shell launcher on `PATH`.* Rejected as disproportionate — it adds an installed executable to solve a path-interpolation problem.

---

## R2 — The guardrail does not block the helper

**Decision**: No guardrail change is needed.

**Rationale**: Executed directly against the shared matcher:

```bash
echo '{"command":"python3 /Users/taikiogihara/.claude/skills/scrum-master/scripts/flow_metrics.py tickets.csv"}' \
  | bash scripts/guardrails/destructive-command.sh
```

Returned `{"decision": "allow", "reason": ""}`, exit 0. `.claude/hooks/pre-bash.sh` is a thin wrapper over that same script, so the PreToolUse path agrees. FR-014's "no guardrail block" clause is satisfied as-is. The helper itself is executable (`-rwxr-xr-x`) with a `#!/usr/bin/env python3` shebang, and `python3` on this machine is 3.14.3.

---

## R3 — The routing regression harness has a hardcoded rule list that must be extended

**Decision**: Extend the embedded routing prompt in `tests/run-skill-routing.sh` with a `scrum-master` rule and add it to the output enum, then add a new case file.

**Rationale**: `tests/run-skill-routing.sh:63-88` does **not** read `.claude/rules/skill-routing.md`. It builds a self-contained evaluation prompt with its own inline rule list and closes with `Output exactly one of: coder | minto-reviewer | minto-rewriter | minto-builder | clarifier | advisor | coder→minto-rewriter`. A new case expecting `scrum-master` would fail no matter how the real routing rules are written, because the model is instructed to answer from that enum. Both the rule list and the enum need the new entry, or FR-019 cannot pass.

Case files follow a fixed shape (`tests/skill-routing/001-code-implement.md`): `# Test:` title, `**Category**`, `**ID**`, `## Input Prompt` fenced block, `## Expected Skill`, `## Expected Behavior`, `## Pass Criteria`, `## Baseline`. The runner parses the first two by heading and rewrites `___` placeholders in the baseline block after a run.

**Observed but out of scope**: that same enum lists `advisor`, and `tests/skill-routing/006-advisor-tradeoff.md` expects it — but no `advisor` skill exists in `.claude/skills/`; `install.sh:112-117` records it as intentionally removed in commit `33c82eb`. This is pre-existing drift. FR-020 requires existing suites to keep passing, so this feature leaves it exactly as it is.

**Alternatives considered**:

- *Make the runner read `skill-routing.md` instead of embedding rules.* The right long-term fix, and it would remove the drift above — but it is a rewrite of the harness, well outside "take in one skill", and it would put FR-020 at risk. Rejected for this feature.

---

## R4 — Distribution needs one line changed, not a new mechanism

**Decision**: Add `scrum-master` to the `CUSTOM_SKILLS` list in `install.sh`.

**Rationale**: `install.sh:27-39` defines `sync_path()` as `rm -rf "$dst"` followed by `cp -R "$src" "$dst"` — a whole-directory recursive copy. `sync_path "skills"` therefore already carries nested `references/` and `scripts/` with no change, satisfying FR-010, and the `rm -rf` before the copy makes it idempotent, satisfying FR-012. The `speckit-*` strip on the next line is a separate `rm -rf` on a glob that does not match `scrum-master`, so FR-013 holds untouched.

The only gap is `install.sh:117`, where `CUSTOM_SKILLS="adr clarifier coder minto-builder minto-reviewer minto-rewriter"` drives the Codex symlink loop. Without the new name there, FR-011 fails. The loop uses `ln -sfn` pointing at `$TARGET_DIR/skills/$skill` — the installed copy, not the working tree — which is what FR-011 requires.

The repo-local mirror `.agents/skills/` holds relative symlinks (`adr -> ../../.claude/skills/adr`); a matching one is needed for `scrum-master`.

---

## R5 — Two suites assert on the skill catalog and one of them is name-by-name

**Decision**: Add `scrum-master` to the `SYNC-03` skill list in `tests/run-codex-sync.sh`; no change needed for `SYNC-08`.

**Rationale**:

- **SYNC-03** (`tests/run-codex-sync.sh:95-100`) iterates a hardcoded `for skill_name in adr clarifier coder minto-builder minto-reviewer minto-rewriter` and asserts each has an `@.agents/skills/<name>/SKILL.md` reference in `.codex/AGENTS.md`. Adding the name here is what turns FR-009 into an enforced invariant rather than a hope.
- **SYNC-08** (`tests/run-codex-sync.sh:193-214`) walks every file under `.claude/` and, for anything matching `.claude/skills/*`, only checks that the literal wildcard string `.claude/skills/*` appears in `.codex/README.md`. The eleven new files are absorbed with no change required.
- **SYNC-01** checks that no symlink under `.agents/skills/` is broken — the new link must therefore resolve, which it will if it is created relative like its siblings.
- **SYNC-03** also enforces a 32 KiB budget on `.codex/AGENTS.md` (warn at 28 KiB). The file is currently far below it and one routing bullet will not approach it, but the suite reports the number on every run.

---

## R6 — Documentation touchpoints are enumerable, and two carry stale counts

**Decision**: Update six documentation locations, two of which contain a literal skill count that becomes wrong.

**Rationale**: Grepping the tracked docs for the existing skill names locates every place the inventory is stated:

| File | What is there | Change |
|---|---|---|
| `.claude/CLAUDE.md` | "Skills (mandatory routing)" bullet list | Add `scrum-master` (per the answered FR-007) |
| `.claude/rules/skill-routing.md` | Category → skill mapping | Add the Scrum category and the FR-007a boundary |
| `.codex/AGENTS.md` | "Skill routing" bullet list with `@.agents/skills/…` paths | Add the matching bullet (FR-009) |
| `README.md:33-35, 85, 188-190` | Prose inventory, deployment table, directory tree | Add the skill; the tree entry must show `references/` + `scripts/` (FR-018) |
| `README.ja.md:9, 18-23, 47, 79-85` | Same three shapes in Japanese | Same; **line 9 says「6 個のスキルリンク」→ 7** |
| `.codex/README.md:25-26` | Deployment map rows | Both rows say「手書き 6 件」→ 7 |

`CLAUDE.md` at the repo root is a one-line `@.claude/CLAUDE.md` include, and `~/.claude/CLAUDE.md` is produced by `install.sh`, so the repo copy is the only file to edit.

---

## R7 — Nothing excludes the skill from version control

**Decision**: No `.gitignore` change.

**Rationale**: The only skill-related ignore rules are `.claude/skills/speckit-*/`, `.agents/skills/speckit-*/`, and `.cursor/skills/speckit-*/`. `scrum-master` matches none of them, satisfying FR-004. Confirmed by reading `.gitignore` in full.

---

## R8 — Cursor stays out

**Decision**: No `.cursor/skills/` entry.

**Rationale**: `.cursor/skills/` contains only the fifteen generated `speckit-*` directories and no link to any hand-written skill — there is no existing pattern to follow, and `.specify/init-options.json` sets `"integration": "cursor-agent"` purely for Spec Kit generation. Adding one would invent a distribution channel this feature was not asked for. Matches the spec's stated assumption.

---

## Summary of resulting scope

| Area | Files touched |
|---|---|
| Skill payload | `.claude/skills/scrum-master/` (SKILL.md + 9 references + 1 script) |
| Permission | `.claude/settings.json` |
| Repo-local Codex mirror | `.agents/skills/scrum-master` (symlink) |
| Routing | `.claude/CLAUDE.md`, `.claude/rules/skill-routing.md`, `.codex/AGENTS.md` |
| Distribution | `install.sh` |
| Docs | `README.md`, `README.ja.md`, `.codex/README.md` |
| Tests | `tests/run-skill-routing.sh`, `tests/skill-routing/007-*.md`, `tests/run-codex-sync.sh` |

No unresolved NEEDS CLARIFICATION remain.
