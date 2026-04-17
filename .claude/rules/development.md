# Development Methodology

## Test-Driven Development

Red → Green → Refactor, strict. No implementation code without a failing test first.

- Tests define the contract; implementation satisfies it. Not complete until all tests pass.
- Hard-to-write test ⇒ design signal; fix the interface.
- Test names describe behavior (`user_cannot_login_with_invalid_password`), not implementation.
- One assertion per test where practical; multiple only for one logical outcome.
- Deterministic only — mock randomness and time.
- Never delete / disable failing tests to pass the suite; fix the root cause.

## Documentation Sync

README and `docs/` must reflect current code. Update docs in the **same change** that alters public interface, behavior, configuration, or usage.

- Describe what the code does **now**, not plans or history. Examples must run against the current codebase.
- No TODO comments as substitutes for doc updates.
- Before reporting done, verify README and `docs/` are consistent. If a stale doc is out of scope, flag it explicitly — do not leave it silently wrong.

### Triggers

| Code change | Doc to update |
|---|---|
| New/removed CLI flag or env var | README usage, `docs/configuration` |
| New/changed API endpoint or signature | `docs/api` or inline docstring |
| Changed default behavior | README, migration/changelog |
| New dependency or install step | README prerequisites / setup |
| Deprecated feature | README + inline deprecation notice |
