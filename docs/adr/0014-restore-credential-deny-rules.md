---
status: Accepted
date: 2026-08-30
deciders: Taiki Ogihara
---

# 0014. Restore credential-safety deny rules as enforced configuration

## Context and problem statement

ADR-0006 (`docs/adr/0006-remove-permissions-config.md`, Accepted) removed the
`permissions` block from `.claude/settings.json` entirely, with no
replacement. It considered — and rejected — the exact option this record now
adopts: "Keep only the credential-safety `deny` entries (the highest-severity
protection) and drop `allow`/`ask`." Full removal was chosen instead,
continuing the simplification of ADR-0005.

What ADR-0006 left behind is a safety policy that enforces nothing.
`.claude/rules/permissions.md` still lists `.env`, `secrets/`, `.ssh/`,
`.aws/`, and private-key files under "never read, display, log, or commit",
while its own text states that "nothing in Claude Code enforces it
automatically." The rule is advisory: it holds only for as long as the
assistant's judgement holds.

Three things have changed since that decision, and together they are why the
same option is now the right one:

1. **The enforcement boundary is now documented explicitly.** Claude Code's
   documentation states that settings rules are enforced by the client
   regardless of what Claude decides, while `CLAUDE.md` and `.claude/rules/`
   are context with no enforcement guarantee. The distinction between a
   configured control and a written one is not a matter of degree.
2. **A `Read` deny rule buys more than it did.** It now also blocks the Edit
   and Write tools on the same path, including creating a new file there
   (Claude Code v2.1.208 for edits, v2.1.228 for writes).
3. **The cost of the prose was measured.** The advisory text occupies 3,754
   bytes of every session's context and enforces nothing; the whole
   `.claude/rules/` set was measured at 36,165 bytes, roughly 9,000 tokens
   loaded into every session of every project.

## Decision drivers

- Least privilege and fail-safe defaults (Saltzer & Schroeder, 1975) — the
  citation that previously sat in `.claude/rules/permissions.md`.
- For the highest-severity control, prefer client-enforced configuration over
  prose that depends on model judgement.
- Preserve the simplification intent of ADR-0005 and ADR-0006 by restoring
  only the minimum that actually enforces, not the full allow/ask/deny
  apparatus.

## Considered options

- Leave everything as prose in `.claude/rules/permissions.md` (the ADR-0006
  status quo).
- Restore the full `permissions` block (`allow` + `ask` + `deny`).
- **Restore only the credential-safety `deny` entries.** (chosen)
- Enable the OS-level sandbox for true all-process enforcement.

## Decision outcome

We will restore only the credential-safety `deny` entries, because they are
the one control whose failure mode is severe and irreversible, while `allow`
shortcuts and `ask` tiers are convenience features whose removal ADR-0005 and
ADR-0006 deliberately chose.

The adopted list is eleven `Read` rules: `**/.env`, `**/.env.*`, `**/*.pem`,
`**/*.p12`, `**/*.pfx`, `**/secrets/**`, `**/credentials/**`, `**/.ssh/**`,
`**/.aws/**`, `~/.ssh/**`, `~/.aws/**`.

Two constraints shaped those patterns and are recorded here because neither is
obvious from the list itself:

- **No single-leading-slash `/path` patterns.** That form anchors at the
  settings source, so one file resolves two ways: read as project settings at
  `.claude/settings.json` it means `<primary working directory>/path`, but
  once `install.sh` copies it to `~/.claude/settings.json` it means
  `~/.claude/path`. Only the `~/` and `**/` forms behave identically in both
  roles, and this repository's settings file occupies both.
- **The "filenames containing `secret` / `credential` / `token` / `key`"
  clause is deliberately not translated into a glob.** `Read(**/*key*)` would
  match `.claude/keybindings.json` and similar innocent files, and a deny rule
  cannot carry allowlist exceptions — a matching deny beats any narrower
  allow — so over-blocking could not be relaxed afterwards. That clause stays
  as prose in `.claude/rules/permissions.md`.

Rejected: leaving it as prose, because a safety rule with zero enforcement is
advisory only. Rejected: the full `permissions` block, because it reintroduces
the complexity ADR-0005 and ADR-0006 removed on purpose. Rejected as out of
scope: the OS-level sandbox, which would reverse the ADR-0005/0007
simplification direction far more broadly and deserves its own decision.

### Consequences

- Positive: the highest-severity protection is enforced by the client rather
  than depending on the assistant's judgement, and it covers both the built-in
  file tools and the file commands Claude Code recognises in Bash (`cat`,
  `head`, `tail`, `sed`).
- Positive: `.claude/rules/permissions.md` shrinks to only what genuinely
  cannot be expressed as configuration.
- Negative: Claude can no longer create or edit `.env` files either, not just
  read them, because a `Read` deny also covers Edit and Write. Generating a
  `.env` from a `.env.example` template becomes the user's own task.
- Negative: `.env.example` and `.env.sample` become unreadable too, since they
  match `**/.env.*`. These are usually harmless templates, so real convenience
  is lost. Deny rules admit no exceptions, so the only way to exempt them
  would be to drop `**/.env.*` entirely. Fidelity to the repository's stated
  policy, which names `.env.*`, was chosen over template convenience.
- Negative: the deny propagates to every other project on the machine, because
  `install.sh` syncs `settings.json` to user scope. This is the same
  propagation path ADR-0006 recorded as a negative consequence of removal,
  now running in the opposite direction.

**Enforcement boundary.** Deny rules do not apply to arbitrary subprocesses
that open files themselves, such as a Python or Node script, and they are not
OS-level. Anything stronger requires the sandbox, which this decision does not
adopt. `.claude/rules/permissions.md` states this boundary, so the restored
configuration is never mistaken for more protection than it provides.

## Confirmation

No automated test exists: ADR-0005 and ADR-0007 removed all hooks and scripts,
and this decision does not restore them. Compliance is verified manually, by a
procedure repeatable in any new session:

1. Attempt to read a scratch `.env` through the file tools and through `cat`;
   both must be refused.
2. Read `.claude/keybindings.json` and `.claude/settings.json`; both must
   succeed, demonstrating the patterns are not over-broad.
3. Attempt to read `.env.example` and to create a `.env`; both must be
   refused, confirming the two accepted side effects above are real rather
   than theoretical.

A result that contradicts step 3 means this record is wrong and must be
corrected by a superseding one.

## More information

- `docs/adr/0006-remove-permissions-config.md` — the decision this partially
  supersedes, left unmodified per ADR immutability.
- `docs/adr/0005-remove-claude-hooks.md` — the removal of the enforcement
  mechanism that preceded it.
- `docs/adr/0009-adopt-deploy-on-aws-plugin.md` — the AWS confirmation
  requirement that remains prose in `.claude/rules/permissions.md`, because it
  cannot be expressed as a permission rule.
- `.claude/rules/permissions.md` — the policy document this decision
  re-couples to enforcement.
- Jerome H. Saltzer & Michael D. Schroeder, "The Protection of Information in
  Computer Systems," *Proceedings of the IEEE* 63(9): 1278–1308, 1975 —
  <https://www.cs.virginia.edu/~evans/cs551/saltzer/>
