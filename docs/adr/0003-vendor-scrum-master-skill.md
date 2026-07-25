---
status: Accepted
date: 2026-07-25
deciders: repository maintainer
---

# 0003. Vendor the scrum-master skill; this repository becomes its sole source of truth

## Context and problem statement

The `scrum-master` skill was authored in a separate working directory,
`/Users/taikiogihara/work/scrum-master-skill/scrum-master/`, as a
standalone Scrum/agile-facilitation playbook: one `SKILL.md`, nine
on-demand `references/*.md` documents, and one Python helper
(`scripts/flow_metrics.py`) that computes cycle time, throughput, and WIP
from a CSV of completed tickets.

The request was to take it in as one of this repository's shared skills —
treated like `adr`, `clarifier`, `coder`, and the Minto suite: discovered
and routed by both Claude Code and Codex CLI, distributed to user scope by
`install.sh`, documented in the READMEs and routing rules, and guarded by
the routing regression suite.

Taking a copy raises a question the copy itself cannot answer: **which
copy is authoritative afterwards?** Two readings were both defensible:

1. This repository becomes the single source of truth; the external
   directory is a one-time import source and stops being maintained.
2. The external directory stays upstream and this repository holds a
   vendored snapshot, with tooling to detect and reconcile drift between
   the two.

The difference is not cosmetic. Reading 2 pulls a synchronisation script
and a drift-detection suite into scope — this repository already has that
shape of machinery in `tests/run-codex-sync.sh`, so it would have been a
consistent thing to build. Reading 1 adds nothing.

A related question surfaced during research: the skill's frontmatter
declared `allowed-tools: Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/flow_metrics.py *)`.
Verified against the official Claude Code skills reference, `allowed-tools`
on a skill is a **restriction over bare tool names** (`Read, Grep, Glob`),
not a permission grant accepting path specifiers, and `${CLAUDE_SKILL_DIR}`
is not an established variable — the documented plugin variable is
`${CLAUDE_PLUGIN_ROOT}`, which does not apply to a vendored user skill.
The declaration was therefore inert at best, and tool-blocking at worst.

## Decision

**This repository is the sole source of truth for the `scrum-master`
skill.** The external `scrum-master-skill` working directory is recorded
here as the one-time import source and is not an upstream.

Consequently:

- The eleven files are vendored to `.claude/skills/scrum-master/` and
  maintained here from now on.
- **No synchronisation mechanism is built** — no sync script, no drift
  test, no scheduled reconciliation against the external directory.
  Recording where something came from is not the same as maintaining a
  link to it.
- The skill joins the shared set on equal footing: the mandatory-routing
  list in `.claude/CLAUDE.md`, the category map in
  `.claude/rules/skill-routing.md`, the Codex routing list in
  `.codex/AGENTS.md`, the `CUSTOM_SKILLS` distribution list in
  `install.sh`, the `.agents/skills/` mirror, all three README
  inventories, and the `SYNC-03` and routing regression suites.
- The inert `allowed-tools` line is **dropped**, and the narrowly-scoped
  permission moves to `.claude/settings.json` `permissions.allow` — the
  mechanism this repository already uses for `Bash(tests/run-*.sh)` and
  friends, and the only one actually enforced. Two anchored entries cover
  the two locations the skill can be loaded from. The skill's declared
  identity (`name`, `description`, `when_to_use`) is preserved
  byte-for-byte.

Deleting or archiving the external directory is the maintainer's call and
happens outside this repository.

### Alternatives considered

**Keep the external directory upstream and build drift detection.**
Rejected. It buys the ability to develop the skill in a dedicated repo,
but the cost is a permanent second place for the skill to be wrong, plus
the tooling to notice. This repository's whole premise is that one tree is
copied to user scope and every agent reads the same files; a skill with an
authoritative copy living elsewhere contradicts that. The precedent in
[ADR 0001](0001-remove-vendored-speckit-skills.md) points the same way —
duplicated copies drifting between this repo and `~/.claude` was exactly
the failure mode that motivated removing vendored `speckit-*` skills. The
difference is that Spec Kit's skills have a real generator upstream
(`specify init`); this skill has no generator and no release process, so
there is nothing for an upstream to provide.

**Reference the external directory by symlink or submodule.** Rejected as
strictly worse than either alternative: it makes the installed
configuration depend on a path outside the repository, breaking the
guarantee that `install.sh` produces a working setup from a clone alone.

**Keep the `allowed-tools` line verbatim.** Rejected. Preserving a
declaration that is inert — and that, if honoured as a restriction, would
block `Read` and break the playbook's own instruction to load its nine
reference files — would mean shipping documentation that lies about how
the skill is permitted to run.

## Consequences

- Positive: the skill is self-contained; a clone plus `install.sh` yields a
  working setup with no external path dependency. No drift surface, no
  reconciliation tooling to maintain.
- Positive: the permission is declared where it is enforced and scoped to a
  single script, satisfying least privilege per
  `.claude/rules/permissions.md`.
- Negative: the skill can no longer be developed independently in its own
  repository with its own history — edits happen here, mixed into this
  repository's commit stream.
- Negative: this is the first skill in the set carrying `references/` and
  `scripts/` subdirectories and an executable, so the directory-shape
  assumption "a skill is one `SKILL.md`" no longer holds. `install.sh`
  already handles it (`sync_path` is a recursive copy), but documentation
  that renders the tree had to change.
- Neutral: the playbook body is Japanese while the other skills' bodies are
  English. Translation was explicitly out of scope; the English
  `when_to_use` field carries the routing triggers.

## Confirmation

- `diff` of the frontmatter against the import source shows exactly one
  difference: the removed `allowed-tools` line.
- No file in the repository references
  `/Users/taikiogihara/work/scrum-master-skill/` as a runtime or build
  input; the only mentions are in this ADR and in
  `specs/016-scrum-master-skill/`.
- `tests/run-codex-sync.sh` `SYNC-03` asserts `scrum-master` is referenced
  in `.codex/AGENTS.md`; `SYNC-01/02` assert its symlinks resolve.
- `tests/skill-routing/007-scrum-facilitation.md` guards the routing.

## More information

Full analysis in `specs/016-scrum-master-skill/` — the source-of-truth
question is FR-021/FR-022 and was put to the maintainer as an explicit
choice during `/speckit-specify`; the `allowed-tools` finding is
`research.md` R0, and the generalised rule it produced is clause C7 of
`contracts/skill-integration.md`.
