---
status: Accepted
date: 2026-08-16
deciders: repository maintainer
---

# 0010. Remove Codex CLI support entirely

## Context and problem statement

This repository has carried Codex CLI guardrail-parity support across two
prior decisions. ADR-0002 established that a hand-maintained Codex port
(`.codex/`, `.agents/` symlinks, deployment logic in `install.sh`, two
consistency suites) deploys at **user scope**, so a single installation
gives every project the same baseline. ADR-0004 then replaced that
hand-maintained port with OpenAI's official `/import` flow: the repository
stopped shipping ported Codex artifacts and instead documented, in a
`## Codex CLI support` README section and a root `AGENTS.md`, how a
developer brings their own Codex configuration via `/import`. ADR-0004's
frontmatter is still `status: Proposed` — it was never formally moved to
`Accepted` even though it is the decision spec 021 actually implemented,
and even though ADR-0002 already points forward to it as superseding.
ADR-0002 itself is already correctly marked "Superseded by 0004."

Since ADR-0004, this documented-but-not-shipped Codex relationship has
required its own upkeep: `AGENTS.md` at the repository root, the README
`## Codex CLI support` / `## Codex CLI サポート` sections in both English
and Japanese, an `install.sh` disclaimer pointing at that section, two
dedicated test suites (`tests/run-codex-references.sh`,
`tests/run-codex-drift.sh`) that exist solely to keep `AGENTS.md` and the
README section honest against the live Codex CLI, and individual
Codex-specific checks embedded in two otherwise-unrelated test suites
(`tests/run-subagent-delegation.sh`, `tests/run-digital-agency-frontend-skill.sh`).
Codex CLI is not otherwise used, tested against, or depended on anywhere
else in this repository. The question this decision answers is whether to
keep maintaining that documentation surface and its verification harness,
or to remove Codex from the repository's documented scope entirely.

## Decision drivers

- Maintaining documentation and a dedicated drift-verification harness for
  a product this repository does not otherwise use or test against costs
  more, in an ongoing sense, than the documentation is worth to this
  repository's own users.
- The two dedicated test suites (`run-codex-references.sh`,
  `run-codex-drift.sh`) are the only thing keeping the README section
  honest as Codex CLI changes upstream; retiring the documentation without
  retiring that harness would leave dead verification code with nothing
  left to check.
- Simplicity: one fewer supported integration surface to keep current,
  narrowing this repository's actual scope to what it verifies (Claude
  Code) rather than what it merely describes (Codex CLI, by way of a
  third-party `/import` command this repository does not run or test).

## Considered options

- **A. Keep documenting Codex via the ADR-0004 approach** — retain
  `AGENTS.md`, the README sections, and both dedicated test suites,
  continuing to track upstream Codex CLI behavior by hand.
- **B. Remove Codex from the repository's documented scope entirely** —
  delete `AGENTS.md`, the README sections in both languages, the
  `install.sh` disclaimer, both dedicated test suites, and the
  Codex-specific checks inside the two surviving test suites that
  reference `AGENTS.md`.
- **C. Lighter-touch: delete only the two dedicated drift/reference test
  suites, leave the documentation in place undocumented as verified.**

## Decision outcome

**We will take option B.** `AGENTS.md` is deleted; the README
`## Codex CLI support` / `## Codex CLI サポート` sections and every other
Codex mention in `README.md` and `README.ja.md` are removed; the
`install.sh` header comment's Codex disclaimer is dropped; both
`tests/run-codex-references.sh` and `tests/run-codex-drift.sh` are
deleted outright; and the Codex-specific checks inside
`tests/run-subagent-delegation.sh` and
`tests/run-digital-agency-frontend-skill.sh` are removed, leaving each
suite's other assertions intact. One comment in
`tests/run-mcp-startup.sh` that used Codex only as an illustrative example
is reworded to make the same point without naming Codex, and
`.gitignore`'s explanatory comment above its `.codex/`/`.agents/`
directory-ignore lines is reworded to describe the directories generically
— the ignore rules themselves are kept, since a developer can still run
`/import` on their own initiative independent of whether this repository
documents that workflow.

Option A was rejected as the status quo this decision reverses: it keeps
paying the upkeep cost identified in the decision drivers for a
documentation surface with no other stake in this repository. Option C
was rejected because leaving undocumented, unverified Codex claims in the
README would be worse than removing them outright — an unverified claim
about third-party CLI behavior is a stale-documentation risk in its own
right, not a lesser version of option B.

### Consequences

- Positive: no README section, `AGENTS.md`, or dedicated test harness to
  keep current against a product this repository does not otherwise use.
- Positive: no risk of the README silently going stale relative to a live
  Codex CLI this repository no longer re-verifies against.
- Positive: one fewer supported integration surface, narrowing this
  repository's actual scope to what it tests.
- Negative: a developer who does want Codex CLI guardrail parity with this
  repository's Claude Code configuration gets no guidance here at all —
  not even the "bring your own `/import`" pointer ADR-0004 provided. They
  must rediscover OpenAI's `/import` flow and work out parity on their
  own, with no starting point in this repository.
- Negative: this closes out the ADR-0002 → ADR-0004 → ADR-0010 chain
  entirely; any future reintroduction of Codex support starts from
  nothing, not from the documented baseline ADR-0004 established.

## Confirmation

Verification covers three things: a repository-wide case-insensitive
search for "codex" outside the historical `specs/` tree, every permanent
ADR body under `docs/adr/` (several beyond 0002/0004/0010 cite Codex as
part of their own immutable historical rationale), Spec Kit's own
unrelated `codex`-integration bookkeeping
(`.specify/integrations/codex.manifest.json`,
`.specify/extensions/.registry`), and `.gitignore`'s literal `.codex/`
directory-ignore line returns no matches; `AGENTS.md`,
`tests/run-codex-references.sh`, and `tests/run-codex-drift.sh` no longer
exist in the repository; and the full `tests/run-*.sh` suite set runs
with no new failure caused by this change — in particular, the three
suites edited directly (`tests/run-subagent-delegation.sh`,
`tests/run-digital-agency-frontend-skill.sh`, `tests/run-mcp-startup.sh`)
pass and contain no remaining Codex-specific check, comment, or string.

## More information

- Supersedes [ADR-0004](0004-adopt-official-codex-import.md) (replace the
  hand-maintained Codex port with OpenAI's official import flow).
- [ADR-0002](0002-deploy-codex-configuration-at-user-scope.md) (deploy
  Codex configuration at user scope) was already marked "Superseded by
  0004" before this decision; that chain is now fully closed out through
  this ADR.
