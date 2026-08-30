---
name: coder
description: Implement and modify code, configuration, tests, scripts, interfaces, or observable behavior safely through spec-driven development, automatable red → green → refactor, boundary validation, secure coding, and factual contract synchronization. Use for every such change, including features, fixes, refactors, review feedback, and documentation that must change with a public contract. Do not use for standalone prose creation, structural review, or research that changes no code, configuration, test, interface, or observable behavior. When another capability independently matches the same request, apply both; this capability retains ownership of implementation, verification, and changed-contract documentation.
---

Purpose: change code, configuration, tests, scripts, interfaces, and observable behavior safely. Define what and why before implementation, establish a failing automated check for an automatable contract or a concrete pre-change observation otherwise, synchronize factual contract documentation, and keep system boundaries secure. These obligations remain when another independently applicable capability supplies domain or artifact-specific guidance. Security is grounded in OWASP Top 10 / OWASP ASVS and CWE-aware defect handling.

# Test-Driven Development (TDD)

Use Red → Green → Refactor whenever the changed contract can be checked automatically. Before implementation, add or identify a deterministic check and run it to observe the expected failure. For a non-automatable change, record the concrete current behavior or structure and define how the intended change will be verified before editing.

- Tests define automatable contracts; implementation satisfies them. Not complete until relevant checks pass.
- Hard-to-write test ⇒ design signal; fix the interface, not the test.
- Test names describe behavior (`user_cannot_login_with_invalid_password`), not implementation.
- One assertion per test where practical; multiple only for one logical outcome.
- Deterministic only — mock randomness and time.
- Never delete or disable failing tests to pass the suite; fix the root cause.
- For prose, policy, or structure that cannot be asserted meaningfully, compare the result with the recorded pre-change observation and perform the stated review; do not create a brittle token-presence test merely to claim TDD.

# Spec-Driven Development (SDD)

Specs are the single source of truth for *what* a feature does and *why*. Code satisfies the spec; docs describe current code.

- No implementation work without a spec when the change adds or alters observable behavior. For trivial internal refactors, TDD alone is sufficient.
- Spec defines **what** and **why** only — keep technology and framework choices out of the spec.
- Acceptance criteria must be verifiable (Given/When/Then or measurable `SC-001…`). If you cannot write a failing test from the spec, the spec is still ambiguous — clarify before coding.
- On divergence, fix the implementation — unless the spec itself is wrong, in which case stop and surface it to the user. Never silently edit a spec to match broken code.
- Implementation reveals a gap in the spec → document the gap and ask before filling.

SDD and TDD compose: the spec names the behavior; the test enforces it; the implementation satisfies both.

When a project already uses [github/spec-kit](https://github.com/github/spec-kit), follow its installed specification, planning, task, consistency-analysis, and implementation lifecycle explicitly rather than improvising an abbreviated substitute.

# Documentation Sync

Identify the canonical explanation of each changed public interface, behavior, configuration field, schema, or usage contract and update it in the **same change**.

- Describe what the code does **now**, not plans or history. Examples must run against the current codebase.
- No TODO comments as substitutes for doc updates.
- Before reporting done, verify affected contract documentation is factually consistent. If a stale artifact cannot be updated within the authorized scope, flag it explicitly — do not leave it silently wrong.

## Triggers

| Code change | Doc to update |
|---|---|
| New/removed CLI flag or env var | README usage, `docs/configuration` |
| New/changed API endpoint or signature | `docs/api` or inline docstring |
| Changed default behavior | README, migration/changelog |
| New dependency or install step | README prerequisites / setup |
| Deprecated feature | README + inline deprecation notice |

# Type Safety

Applies whenever the active language supports static or gradual typing (e.g., TypeScript, Python with type hints, Go, Rust, Swift, Kotlin, Java, C#). Composes with "Language and stack conventions" below — match the repo's existing typing convention; do not introduce a new typing system, annotate untouched code, or perform unrelated typing refactors beyond the agreed task.

- **Annotate public interfaces**: new or changed public functions, exported values, and class members carry explicit type annotations consistent with the project's existing convention. When a change alters a typed interface's inputs or outputs, update its annotations in the same change — not just the implementation.
- **No unsafe escapes by default**: when a type-checking error occurs, fix the underlying type mismatch (narrowing, correct typing, or a small refactor) rather than reaching for `any`, a blanket cast, a suppression comment (`# type: ignore`, `@ts-ignore`), or a non-null assertion. If an escape is genuinely unavoidable (e.g., an untyped third-party library), add a one-line comment stating why and surface the trade-off to the user.
- **Verify, don't just annotate**: when the project has a configured type checker (`tsc`, `mypy`, `pyright`, etc.), run it as part of pre-completion verification alongside the test/lint/format checks in "Language and stack conventions," and resolve any type error the change introduced before reporting done. Projects with no type checker configured are unaffected — do not fabricate this step.
- **Validate at boundaries**: data crossing into typed code from outside the type system's guarantee (user input, external API responses, deserialized payloads, environment/config values) is validated or narrowed into the expected type at the boundary, not trusted or cast without verification. Do not add redundant validation for already-typed internal data with no boundary crossing.

# Code quality and security

Applies to implementation work in the repo. Composes with TDD/SDD/docs above.

## Code quality

- **Adopt** established best practices in everything you **do** change (logging, comments, errors, structure) — match the stack and the repo; no deliberate sloppiness.
- Write no speculative abstractions: complexity should match the task, not hypothetical future needs.
- **Logging**: follow the project’s conventions (levels, format, structured vs plain). Log what operators need to debug and audit; **never** log secrets, tokens, or unredacted PII. At I/O and request boundaries, include correlation identifiers when the codebase already does so. Avoid log noise in hot paths unless diagnosing an issue.
- **Comments and docstrings on edited code**: prefer **why** and non-obvious invariants, not narration of the next line. For **public** or **tricky** surfaces, document contracts where the project expects it (TDD/SDD sections above). Do **not** add docstrings, comments, or type annotations to **untouched** code.
- **Error handling**: at **system boundaries** (user input, file/network/DB, external APIs, user-visible failures), use clear validation, **typed or narrow** error paths, and user-safe messages; fail fast on programmer mistakes where that’s idiomatic. **Do not** add catch-all handling for “impossible” internal states — trust the framework. Do **not** hide failures without a documented reason. If insecure or misleading error behavior appears, **fix** it before finishing (same as Security).
- **Suggest to the user** when a best practice would clearly help but is **out of scope** (e.g. missing structured logs for a new integration, missing timeout on a new client): state the gap, why it matters, and a **minimal** follow-up — **do not** implement large or unrelated work without alignment.
- Add no unsolicited **code** improvements: no drive-by refactors, cleanup, or feature creep beyond the agreed task — telling the user is allowed; changing arbitrary files is not.

## Security

Aim for **secure and safe** outcomes in both **code** and how the **environment** is used. Prefer **established** secure-coding practice and, where it applies, **recognised international and industry baselines** (e.g. OWASP guides and ASVS-style controls, **CWE**-aware handling of common defect classes, and language or platform **security advisories**). Favour current recommendations over deprecated patterns.

- **In code**: never introduce command injection, XSS, SQL injection, or other **OWASP Top 10**–class flaws; apply least privilege for secrets and capabilities; use vetted crypto and dependency hygiene when touching those layers; validate and encode at **system boundaries** (user input, external APIs) and avoid leaking stack traces or internal detail to end users. If insecure or unsafe code is written, **fix it before** claiming done.
- **In the dev environment** (shell, repository, tool use): do not expose credentials, surprise the user with destructive actions, or execute unreviewed remote content; use official sources and **HTTPS**, keep secrets in designated stores, and obtain explicit authorization for destructive, machine-wide, credential-bearing, or externally consequential effects whose authority is not already clear. When suggesting commands or integrations, default to the safer option and call out material risk.
- When standards or the project’s own **security** docs conflict with a shortcut, follow the stricter or project-mandated rule. If a requirement is **unclear** (e.g. data classification, crypto choice), **ask** before implementing.

# Language and stack conventions

This is the single coding skill; it is language-agnostic. For the active language and stack, follow the repository's configured linter, formatter, type-checker, and test runner, and run them before reporting done. Match existing repo conventions rather than importing external defaults.

# References

- Kent Beck, *Test-Driven Development: By Example*, Addison-Wesley, 2002 (TDD).
- OWASP Top 10 (2025) — <https://owasp.org/www-project-top-ten/>
- OWASP Application Security Verification Standard (ASVS), v5.0 (2025) — <https://owasp.org/www-project-application-security-verification-standard/>
- CWE — Common Weakness Enumeration (MITRE) — <https://cwe.mitre.org/>
- Spec-driven development via GitHub Spec Kit — <https://github.com/github/spec-kit>
