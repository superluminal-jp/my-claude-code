---
status: Accepted
date: 2026-08-15
deciders: Taiki Ogihara
---

# 0005. Remove .claude/hooks/ entirely, with no replacement

## Context and problem statement

`.claude/hooks/` held seven scripts wired via `.claude/settings.json` into
four Claude Code hook events (`PreToolUse`, `PostToolUse`, `UserPromptSubmit`,
`UserPromptExpansion`) plus the `statusLine` command. Four of the seven were
thin wrappers around shared logic in `scripts/guardrails/*.sh`, designed
(spec-013) so Claude Code and a hand-authored Codex CLI port could enforce
identical guardrails from one source of truth: destructive-command blocking,
`.git/`/`main`-branch edit protection, post-edit auto-formatting, and
prompt-secret scanning. The other three (`speckit-expand-update.sh`,
`statusline.sh`, and the mechanics README) had no shared-script counterpart.

Two things changed since spec-013: (1) this repository stopped hand-porting
a Codex configuration and moved to Codex's own official `/import` flow
(ADR-0004-adopt-official-codex-import) — the cross-agent sharing rationale no
longer has a maintained Codex-side consumer in this repo; and (2) the
maintainer judged the resulting three-layer indirection
(`settings.json` → wrapper → shared script, each wrapper repeating a
three-branch path-resolution fallback) to be more complexity than the
guardrails were worth keeping, and decided — explicitly, after being shown
the security consequence in detail — to remove the mechanism entirely rather
than simplify it.

## Decision drivers

- Reduce the layers a reader has to trace to understand what a Claude Code
  session in this repository will and won't do automatically.
- The cross-agent code-sharing rationale (spec-013) lost its Codex-side
  consumer once this repo adopted Codex's official import flow.
- Maintainer explicitly no longer wants to treat Codex-side parity as a
  constraint on how `.claude/` is organized (confirmed in the driving
  conversation).

## Considered options

- Keep all seven hooks as-is.
- Keep only the three security-blocking hooks (destructive-command, edit
  protection, prompt-secret scanning); drop the three convenience ones
  (post-edit formatting, Spec Kit auto-update, status line).
- Keep the wrapper/shared-script split but simplify its three-branch
  path-resolution fallback (identified separately in this session as a real,
  Claude-Code-only correctness gap: the fallback order let test suites
  silently validate a stale globally-installed copy instead of the
  repository's own working-tree code).
- **Remove `.claude/hooks/` entirely, with no replacement.** (chosen)

## Decision outcome

We will remove `.claude/hooks/` entirely, because the maintainer weighed the
security trade-off explicitly (confirmed across two rounds of clarification)
and judged the simplification worth more than the automated enforcement,
having been shown that no other mechanism in Claude Code (subagents included)
can replace a blocking `PreToolUse`/`UserPromptSubmit` guardrail.

### Consequences

- Positive: `.claude/` no longer has a three-layer wrapper/shared-script/
  fallback-resolution indirection to trace through. `scripts/guardrails/*.sh`
  stays available for direct or manual invocation without the wrapper layer
  obscuring it.
- Negative: Claude Code sessions in this repository — and, once `install.sh`
  is next run, every other project on the machine — no longer automatically
  block destructive commands (`git push --force`, `rm -rf`, etc.), edits to
  `.git/` or the `main`/`master` branch, or prompts containing obvious
  secrets. The only remaining automatic Claude Code guardrail is
  `.claude/settings.json`'s `permissions` allow/ask/deny block, which is
  independent of hooks.
- Negative: Codex CLI (via its own, separately maintained `/import`) now
  enforces *more* automatic guardrails for this repository than Claude Code
  does — the comparison this repository's own docs used to make (README.md
  "What Codex enforces, and what it does not") is now inverted from what it
  said before this change.
- Negative: `scripts/guardrails/*.sh` (4 files) lose their only automatic
  caller and become reachable only by direct/manual/test invocation. They
  were not deleted, since the removal request scoped to `.claude/hooks/`
  only, but their practical value going forward is reduced to a reference
  implementation and test fixture.
- Negative: `.claude/rules/permissions.md` continues to state the policy
  these hooks used to enforce automatically; the policy and its enforcement
  are now decoupled — a reader must know this ADR (or `specs/025-*`) exists
  to know the policy is aspirational rather than machine-enforced.

## Confirmation

`tests/run-*.sh` (the remaining behavior suites after this change) verifies
no file still references `.claude/hooks/` or a deleted hook filename as if it
were live, and that the four former guardrail suites still test
`scripts/guardrails/*.sh` directly. See
`specs/025-remove-claude-hooks/quickstart.md` for the exact verification
commands.

## More information

- `specs/025-remove-claude-hooks/spec.md`, `research.md` — full requirements,
  exact edit locations, and the comparison-table rewrite content.
- `specs/013-cross-agent-guardrail-implementation/` — the design record this
  ADR's removal reverses the Claude-side half of (left unmodified, per this
  repository's append-only convention for historical specs).
- `docs/adr/0004-adopt-official-codex-import.md` — the prior decision that
  removed this repository's Codex-side hook port, eliminating the
  cross-agent sharing rationale spec-013 was originally built for.
