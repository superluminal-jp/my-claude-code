---
status: Superseded by 0010
date: 2026-08-10
deciders: repository maintainer
---

# 0004. Replace the hand-maintained Codex port with OpenAI's official import flow

## Context and problem statement

This repository has carried a hand-written Codex CLI port since features 012–014:
`.codex/AGENTS.md`, four hook adapters, a Rules file, a prompt, eight
`.agents/skills/` symlinks, ~71 lines of `install.sh` deployment logic, two
consistency suites (`SYNC-01`…`SYNC-12`), and a 32-row deployment map. ADR-0002
established that this configuration deploys at **user scope**.

OpenAI now ships its own migration path — the `/import` command in Codex CLI and
the `migrate-to-codex` curated skill — which covers instructions, skills, MCP
servers, hooks, and subagents. Maintaining a parallel port means tracking a
moving target by hand.

Three measurements taken on 2026-08-10 (Codex 0.147.0) forced the question:

- The port's own deployment map already carried a stale claim (that Codex has no
  subagents — it does).
- Running `/import` alongside the installed port produces a **live
  misconfiguration**: the same guard is registered in three config layers, fires
  three times per turn, and Codex prints
  `warning: loading hooks from both … prefer a single representation for this layer`.
- Of the four guardrails the port provided, two work in Codex and two are
  structurally impossible there — Codex fires `PreToolUse`/`PostToolUse` for
  shell commands only, so hooks matching `Edit|Write|Delete` never run.

## Decision drivers

- Maintenance cost of hand-porting software that changes underneath us.
- Accuracy: a port that silently goes stale is worse than no port.
- The duplicate hook registration is an active defect, not a latent one.
- Claude-side safety must not be reduced to achieve symmetry with Codex.

## Considered options

- **A. Keep the hand-maintained port.**
- **B. Delete it; adopt the official import flow.**
- **C. Hybrid: delete the instructions and skills, keep the hook adapters and Rules.**

## Decision outcome

**We will take option B.** The repository ships no Codex artifacts. Developers
run `/import` themselves; generated `.codex/` and `.agents/` content is
git-ignored. The `migrate-to-codex` skill is documented for its **read-only**
modes only (`--scan-only`, `--plan`, `--doctor`, `--dry-run`,
`--validate-target`) — its write modes symlink the root `AGENTS.md` to
`CLAUDE.md` and replace every skill with a copy, which would destroy this
repository's instructions.

Instructions move to the **repo-root `AGENTS.md`**, which Codex reads natively by
directory-walk composition. It must stay flat: Codex does not expand `@` imports
(`openai/codex` issue #17401, open).

Option C was rejected because it preserves the very thing that caused the
three-layer collision, while keeping only the guardrails that `/import` already
delivers on its own.

### Consequences

- Positive: no parallel port to maintain; upstream improvements arrive without
  work here; the duplicate hook registration and Codex's warning disappear; the
  instruction file becomes a conventional `AGENTS.md` rather than a ported
  artifact needing a sync test; two suites and ~71 lines of installer logic go away.
- Negative — **Codex configuration is no longer reproducible from this repository
  alone**. Two developers on the same commit can end up with different Codex
  setups. This is the substantive cost of the decision.
- Negative — edit protection (`.git/`, `main`/`master`) and the allow/prompt
  command policy are **not available in Codex** and are documented as absent.
  Claude Code keeps both, unchanged.
- Negative — skills arrive as copies rather than symlinks, so they drift from
  `.claude/skills/` until re-imported, with nothing detecting the gap.
- Negative — the deployment map's accumulated knowledge is retired; it survives
  only as the historical record in `specs/012`–`014` and `specs/021`.

## Confirmation

- `tests/run-codex-references.sh` (`RULE-01`…`RULE-10`) — no dangling references,
  root `AGENTS.md` is a flat regular file, generated paths are ignored.
- `tests/run-codex-drift.sh` (`DRIFT-01`…`DRIFT-06`) — re-derives the upstream
  facts the documentation rests on; skips when `codex` is absent.
- `quickstart.md` Steps 1–6, including a live Codex session for the guardrail
  coverage table.

## More information

- Supersedes **ADR-0002** (deploy Codex configuration at user scope).
- Feature: `specs/021-codex-official-import/` — `spec.md`, `plan.md` (design
  decisions D1–D6), `research.md` (§§ R-01–R-09, the measurements above).
- Retires the arrangement built by `specs/012`, `specs/013`, `specs/014`.
- Related: **ADR-0001** (spec-kit skills are per-project artifacts, not vendored)
  — the same "generated, not tracked" principle now applies to Codex config.
