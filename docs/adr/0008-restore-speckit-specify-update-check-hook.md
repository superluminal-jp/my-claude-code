---
status: Accepted
date: 2026-08-16
deciders: Taiki Ogihara
---

# 0008. Restore a narrow specify-cli update-check hook for speckit-specify

## Context and problem statement

ADR-0005 (2026-08-15) removed `.claude/hooks/` entirely with no
replacement, including `speckit-expand-update.sh`, which had auto-updated
Spec Kit before `/speckit-*` commands ran. That removal was explicit and
deliberate, made after weighing the security trade-off of losing the three
guardrail hooks (destructive-command blocking, edit protection,
prompt-secret scanning) that shared `.claude/hooks/`'s wrapper mechanism.

One day later, the maintainer asked to restore *only* the Spec Kit
version-check/update behavior — not the guardrails, and not the
wrapper/shared-script indirection ADR-0005 specifically objected to. The
question is how to reintroduce this one piece of functionality without
re-creating the complexity ADR-0005 removed.

## Decision drivers

- Honor the maintainer's explicit, current request without silently
  re-opening the guardrail question ADR-0005 already settled.
- Avoid recreating the three-layer `settings.json` → wrapper script →
  `scripts/guardrails/*.sh` indirection ADR-0005 named as its own
  complexity driver.
- Keep the check narrowly scoped so it doesn't add latency or a network
  dependency to every `/speckit-*` invocation.

## Considered options

- Recreate `.claude/hooks/speckit-expand-update.sh` and re-wire it via
  `settings.json`, restoring the pre-ADR-0005 file layout.
- Add a single inline `PreToolUse`/`Skill` hook command directly in
  `.claude/settings.json`, gated to only the `speckit-specify` skill, with
  no `.claude/hooks/` directory or wrapper file.
- Do nothing; rely on manually running `uv tool upgrade specify-cli`.

## Decision outcome

We will add a single inline `PreToolUse` hook in `.claude/settings.json`
(matcher `Skill`), gated in-command to only the `speckit-specify` skill
invocation. It queries the GitHub releases API for
`github/spec-kit`'s latest tag, compares it against the `rev=` pinned in
`~/.local/share/uv/tools/specify-cli/uv-receipt.toml`, and — only on a
mismatch — reinstalls via `uv tool install specify-cli --from
git+https://github.com/github/spec-kit.git@<tag> --force`. It fails open:
any network or lookup failure exits 0 without blocking the skill.

This does not reopen ADR-0005's guardrail decision (destructive-command
blocking, edit protection, prompt-secret scanning remain unenforced by
Claude Code, as ADR-0005 accepted) and does not recreate the
`.claude/hooks/` directory or its wrapper/shared-script indirection —
the whole mechanism is one inline command.

### Consequences

- Positive: `specify init`/`specify.md` runs against a current Spec Kit
  release without a separate manual update step, addressing the one part
  of ADR-0005's removal the maintainer wanted back.
- Positive: no `.claude/hooks/` directory, wrapper script, or shared-script
  fallback resolution is reintroduced — avoids the specific complexity
  ADR-0005's decision drivers named.
- Negative: `.claude/settings.json` now carries one non-trivial inline
  shell command, which is harder to unit-test than a standalone script
  file would be (accepted trade-off, given the alternative reintroduces
  the indirection ADR-0005 removed).
- Negative: adds one GitHub API call (network-dependent, fails open) the
  first time `speckit-specify` runs in a session; scoped to that one skill
  only, not all 15 `speckit-*` skills, to bound this cost.
- Neutral: ADR-0005 remains Accepted and in effect for everything except
  this one narrow case — the guardrail hooks it removed are not restored.

## Confirmation

`jq -e '.hooks.PreToolUse[] | select(.matcher == "Skill") | .hooks[] | select(.type == "command") | .command' .claude/settings.json` must
exit 0. The command was pipe-tested directly against synthesized
`Skill`-tool stdin payloads (both a `speckit-specify` match and a
non-matching skill) before being wired into `settings.json`, and the
underlying `uv tool install --force` step was run live against the actual
`specify-cli` install and confirmed to upgrade it.

## More information

- `docs/adr/0005-remove-claude-hooks.md` — the decision this narrows;
  remains Accepted and unedited.
- `specs/025-remove-claude-hooks/` — original removal requirements.
