# Contract: Custom skill integration

**Feature**: 016-scrum-master-skill | **Date**: 2026-07-25

## Purpose

This repository exposes one externally-visible interface to its users: **the set of skills an agent can reach**, and the guarantee that the set is the same whichever supported agent asks and whichever directory the user is in. That set is not declared in one place — it is the agreement between eleven locations across the tree. This contract states what "a skill is integrated" means, so the condition can be checked rather than assumed.

It generalises beyond this feature: any future custom skill added to this repository must satisfy every clause below. `scrum-master` is the first skill to exercise clauses C3 and C7, because it is the first with subdirectories and the first with an executable.

---

## C1 — Payload

The skill directory `.claude/skills/<name>/` MUST exist and contain `SKILL.md` with frontmatter declaring `name: <name>` identical to the directory name.

**Check**: `test -f .claude/skills/<name>/SKILL.md` and the frontmatter `name` matches the directory.

---

## C2 — Link integrity

Every relative link in `SKILL.md` and in any `references/*.md` MUST resolve to a file that exists inside the skill directory.

**Check**: extract each `](...)` target that is not a URL, resolve it against the containing file's directory, and assert the file exists. Zero unresolved (SC-005).

---

## C3 — Supporting assets

A skill MAY carry `references/` and `scripts/` subdirectories. If it does:

- Reference files MUST be plain Markdown reachable from the playbook per C2.
- Scripts MUST carry an executable bit and a shebang naming an interpreter available on the target platform.
- Scripts MUST NOT require network access, credentials, or write access outside the working directory.

**Check**: `test -x` on each script; the first line matches `^#!`; the guardrail returns `allow` for its documented invocation.

---

## C4 — Declared identity is preserved

`name`, `description`, and `when_to_use` MUST be byte-identical to the skill's authored source. These three fields determine when the skill is selected; editing them silently changes behaviour the source specified (FR-002).

Other frontmatter fields are **not** covered by this clause and MAY be adjusted to match the host's actual semantics — see C7.

**Check**: field-by-field diff against the source for exactly those three keys.

---

## C5 — Routing agreement

The skill MUST be named in all three routing surfaces, and they MUST agree:

| Surface | Form |
|---|---|
| `.claude/CLAUDE.md` | entry in the mandatory-routing list |
| `.claude/rules/skill-routing.md` | category → skill mapping, including how compound requests are resolved |
| `.codex/AGENTS.md` | bullet ending in the literal `@.agents/skills/<name>/SKILL.md` |

A skill named in one surface and absent from another is a contract violation, not a cosmetic gap: the agents disagree about what exists.

**Check**: `tests/run-codex-sync.sh` SYNC-03 asserts the `.codex/AGENTS.md` clause name-by-name. The other two are checked by review.

---

## C6 — Distribution

After one `install.sh` run — on an existing profile is sufficient, since each managed path is replaced outright rather than merged:

| Target | Required state |
|---|---|
| `~/.claude/skills/<name>/` | full recursive copy, subdirectories and executable bits intact |
| `~/.agents/skills/<name>` | symlink resolving to `~/.claude/skills/<name>` |
| `.agents/skills/<name>` (tracked) | relative symlink resolving to `../../.claude/skills/<name>` |

Symlinks MUST point at the installed copy, never at a repository working tree, so they survive the clone being moved or deleted.

A second run MUST leave an identical end state — no duplicates, no dangling links, no leftovers (SC-004).

**Check**: `tests/run-codex-sync.sh` SYNC-01/02 assert no dangling links. Idempotence is checked by running the installer twice and comparing.

---

## C7 — Permission scope

If a skill ships an executable, the permission that lets it run without an ad-hoc prompt MUST be declared in `.claude/settings.json` `permissions.allow`, scoped to that script's path.

It MUST NOT be declared only in `SKILL.md` frontmatter: `allowed-tools` on a skill is a *restriction over tool names*, not a permission grant with path specifiers (research R0). A `Tool(specifier)` value there names no tool that exists.

The grant MUST NOT widen general command execution. `Bash(python3 <scoped path> *)` satisfies this; `Bash(python3 *)` does not.

**The granted pattern and the command the playbook documents MUST agree character-for-character up to the argument.** A grant scoped to a repo-root-relative path does not cover a skill-directory-relative invocation, and a mismatch surfaces only as a permission prompt at run time — long after both halves look individually correct. Where a skill is reachable from more than one location, every location needs its own entry and its own documented form.

**Check**: the entry exists, is anchored at a path prefix, and contains no bare interpreter wildcard; every command in the playbook has a matching entry. Effectiveness confirmed by running the documented command and observing no prompt, and by feeding that exact command to the destructive-command guardrail and observing `allow`.

---

## C8 — Documentation inventory

Every human-facing inventory MUST list the skill: `README.md`, `README.ja.md`, `.codex/README.md`. Where an inventory states a count of hand-written skills, that count MUST equal the actual number. Where an inventory renders a directory tree, the rendering MUST reflect the skill's real shape — a skill with `references/` and `scripts/` must not be drawn as a bare `SKILL.md` (FR-018).

**Check**: each file names the skill; every stated count matches `ls .claude/skills | grep -vc '^speckit-'`.

---

## C9 — Regression coverage

At least one case under `tests/skill-routing/` MUST expect the skill, in the established case-file format.

Because `tests/run-skill-routing.sh` builds a **self-contained** evaluation prompt with its own inline rule list and a closed output enum, adding a case is not sufficient on its own: the runner's rule list and enum MUST both carry the skill name, or the case can never pass regardless of what the real routing rules say (research R3).

**Check**: the case file exists and parses; `grep` confirms the name appears in both the inline rules and the enum; the suite passes where a live `claude` CLI is available.

---

## C10 — Additive guarantee

Integrating a skill MUST NOT change the routing outcome of any pre-existing category, alter any pre-existing permission, or change the result of any pre-existing suite (FR-008, FR-020).

**Check**: all `tests/run-*.sh` pass, and every pre-existing routing case resolves to its recorded skill (SC-002).

---

## Non-goals

- **No upstream reconciliation.** Once vendored, this repository is the sole source of truth. No sync script, drift test, or scheduled reconciliation against an external source directory (FR-021, FR-022). The *provenance* must still be recorded durably — an ADR is this repository's established mechanism — so a later reader can tell where the files came from and that nothing is being tracked upstream. Recording where something came from is not the same as maintaining a link to it.
- **No content editing.** Integration does not translate, rewrite, or restructure a skill's playbook.
- **No Cursor distribution.** `.cursor/skills/` holds only Spec Kit's generated artifacts; hand-written skills are not distributed there (research R8).
