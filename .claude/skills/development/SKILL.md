---
name: development
description: Development methodology — Test-Driven Development (Red → Green → Refactor), Spec-Driven Development (spec as source of truth), and documentation-sync discipline. Use when writing new code, adding features, fixing bugs, refactoring, changing public interfaces, or touching README / docs/.
when_to_use: Invoke for any code change that adds or modifies behavior. Trigger phrases — "write a test", "implement X", "fix this bug", "refactor", "add feature", "TDD", "SDD", "spec", "update the docs".
---

# Test-Driven Development (TDD)

Red → Green → Refactor, strict. No implementation code without a failing test first.

- Tests define the contract; implementation satisfies it. Not complete until all tests pass.
- Hard-to-write test ⇒ design signal; fix the interface, not the test.
- Test names describe behavior (`user_cannot_login_with_invalid_password`), not implementation.
- One assertion per test where practical; multiple only for one logical outcome.
- Deterministic only — mock randomness and time.
- Never delete or disable failing tests to pass the suite; fix the root cause.

# Spec-Driven Development (SDD)

Specs are the single source of truth for *what* a feature does and *why*. Code satisfies the spec; docs describe current code.

- No implementation work without a spec when the change adds or alters observable behavior. For trivial internal refactors, TDD alone is sufficient.
- Spec defines **what** and **why** only — keep technology and framework choices out of the spec.
- Acceptance criteria must be verifiable (Given/When/Then or measurable `SC-001…`). If you cannot write a failing test from the spec, the spec is still ambiguous — clarify before coding.
- On divergence, fix the implementation — unless the spec itself is wrong, in which case stop and surface it to the user. Never silently edit a spec to match broken code.
- Implementation reveals a gap in the spec → document the gap and ask before filling.

SDD and TDD compose: the spec names the behavior; the test enforces it; the implementation satisfies both.

For projects using [github/spec-kit](https://github.com/github/spec-kit) (files under `.specify/` or `specs/{N}-{name}/`), `specify init` installs slash commands that carry their own playbooks: `/speckit.constitution`, `/speckit.specify`, `/speckit.clarify`, `/speckit.plan`, `/speckit.tasks`, `/speckit.implement`, `/speckit.analyze`. Invoke them explicitly — do not improvise the workflow.

# Documentation Sync

README and `docs/` must reflect current code. Update docs in the **same change** that alters public interface, behavior, configuration, or usage.

- Describe what the code does **now**, not plans or history. Examples must run against the current codebase.
- No TODO comments as substitutes for doc updates.
- Before reporting done, verify README and `docs/` are consistent. If a stale doc is out of scope, flag it explicitly — do not leave it silently wrong.

## Triggers

| Code change | Doc to update |
|---|---|
| New/removed CLI flag or env var | README usage, `docs/configuration` |
| New/changed API endpoint or signature | `docs/api` or inline docstring |
| Changed default behavior | README, migration/changelog |
| New dependency or install step | README prerequisites / setup |
| Deprecated feature | README + inline deprecation notice |
