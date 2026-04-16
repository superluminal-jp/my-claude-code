# Development Methodology

## Test-Driven Development (TDD)

Follow the red-green-refactor cycle strictly:

1. **Red**: Write a failing test that specifies the desired behavior before writing any implementation
2. **Green**: Write the minimum code necessary to make the test pass — no more
3. **Refactor**: Clean up implementation and tests while keeping all tests green

### Rules

- Never write implementation code without a corresponding failing test first
- Tests define the contract; implementation satisfies it
- A task is not complete until all tests pass
- If a test is hard to write, treat it as a design signal — the interface is likely wrong
- Test names must describe behavior, not implementation: `user_cannot_login_with_invalid_password`, not `test_login_function`
- One assertion per test where practical; multiple assertions only when they test a single logical outcome
- Tests must be deterministic — no random data, no time-dependent behavior without explicit mocking
- Do not delete or disable failing tests to make a suite pass; fix the root cause

---

## Documentation Sync

README files and `docs/` must always reflect the current state of the code.

### Rules

- Any code change that affects public interfaces, behavior, configuration, or usage **must** include a corresponding documentation update in the same change
- After modifying code, check whether README or `docs/` reference the changed behavior; update any outdated sections
- Do not leave TODO comments as substitutes for documentation updates
- Documentation must describe what the code **does now**, not what it will do or used to do
- Examples in documentation must be runnable against the current codebase

### What Triggers a Documentation Update

| Code change | Documentation to update |
|-------------|------------------------|
| New or removed CLI flag / env var | README usage section, `docs/configuration` |
| New or changed API endpoint / function signature | `docs/api` or inline docstring |
| Changed default behavior | README, any migration or changelog docs |
| New dependency or install step | README prerequisites / setup section |
| Deprecated feature | README + inline deprecation notice in code |

### Verification

- Before reporting a task complete, confirm that README and `docs/` are consistent with the final code
- If a documentation file would become stale but updating it is out of scope, explicitly flag it to the user rather than leaving it silently incorrect
