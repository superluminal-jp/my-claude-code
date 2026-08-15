---
status: Accepted
date: 2026-08-16
deciders: Taiki Ogihara
---

# 0006. Remove the permissions block entirely, with no replacement

## Context and problem statement

`.claude/settings.json` and `.claude/settings.local.json` each carried a
`permissions` block (`allow`/`ask`/`deny` arrays) governing which tool calls
run automatically, which require confirmation, and which are blocked
outright — including the `deny` list that stopped `Read` on `.env`,
`.ssh/`, `.aws/`, and private-key files. ADR-0005
(`docs/adr/0005-remove-claude-hooks.md`, Accepted) removed all of
`.claude/hooks/`, the mechanism that used to enforce destructive-command
blocking, edit protection, and prompt-secret scanning, and named this
`permissions` block "the only remaining automatic Claude Code guardrail."

The maintainer decided, immediately after that removal, to remove this
block too — confirmed explicitly via `AskUserQuestion`, with the
consequence (Claude Code left with zero automated enforcement of any kind
for this repository) stated plainly before the decision was made.

Because ADR-0005 is Accepted and its substance is immutable, the fact it
asserted — that the permissions block is what remains — needed a new
record rather than an edit, once that fact stopped being true.

## Decision drivers

- Continuation of the same simplification judgment behind ADR-0005: fewer
  automated layers to reason about, even at the cost of automated
  enforcement.
- ADR policy: an Accepted record's substance is never rewritten, only
  superseded or extended by a later record.

## Considered options

- Keep the `permissions` block as the one remaining automated guardrail
  (the state ADR-0005 left things in).
- Keep only the credential-safety `deny` entries (the highest-severity
  protection) and drop `allow`/`ask`.
- **Remove the `permissions` block entirely, with no replacement.** (chosen)

## Decision outcome

We will remove the `permissions` block entirely from both settings files,
because the maintainer weighed the consequence explicitly and chose full
removal over a partial one, consistent with the same reasoning applied in
ADR-0005.

### Consequences

- Positive: `.claude/settings.json` and `.claude/settings.local.json` no
  longer need to be read alongside `.claude/hooks/` (now absent) to
  understand what, if anything, this repository automates or restricts —
  the answer is now uniformly "nothing."
- Negative: Claude Code sessions in this repository — and every other
  project once `install.sh` next syncs `settings.json` — no longer
  automatically deny reads of `.env`, `.ssh/`, `.aws/`, or private-key
  files, no longer auto-allow the previously allow-listed read-only
  commands (now prompting for each instead), and no longer route
  destructive-leaning git operations to a confirmation tier distinct from
  ordinary prompting.
- Negative: `.claude/rules/permissions.md` now states policy with no
  automated enforcement backing any of it — every rule in that document is
  now purely a matter of the assistant's own judgment and the operator's
  vigilance.
- Negative: Codex CLI (via its own, independently maintained `/import`)
  retains its guardrails regardless of this change, widening further the
  gap this repository's own README now documents: Codex enforces more for
  this repository than Claude Code does.

## Confirmation

`tests/run-*.sh` (all remaining suites) verifies no file claims the
permissions block, or any hook, is still automatically enforced. See
`specs/026-remove-permissions-config/quickstart.md` for the exact commands.

## More information

- `specs/026-remove-permissions-config/spec.md`, `research.md` — full
  requirements and exact edit locations.
- `docs/adr/0005-remove-claude-hooks.md` — the prior, related decision this
  one extends; left unmodified per ADR immutability.
- `.claude/rules/permissions.md` — the policy document this decision
  decouples from automated enforcement.
