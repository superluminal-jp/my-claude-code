# Code Review Rules

Purpose: give code review a consistent house standard — what to look for, in what order — so reviews catch what matters and stay actionable. Applies when reviewing a diff, commit, or PR (whether invoked directly or via the built-in `/code-review` and `/security-review` commands). Grounded in OWASP Top 10 / ASVS (security) and this repo's `live-documentation.md`. Composes with `coder` (TDD/SDD/secure-coding standards being reviewed against).

## Review order (first match = highest priority)

1. **Correctness** — does it do what the spec/issue says? Logic errors, off-by-one, null/empty/boundary cases, race conditions, error-path handling at system boundaries.
2. **Security** — OWASP Top 10–class flaws (injection, XSS, auth/access, secrets in code, unsafe deserialization). Validate/encode at boundaries. Flag any credential exposure per `permissions.md`.
3. **Live Documentation drift** — for every changed public contract (exported function, API endpoint, CLI flag, schema field), confirm its Documentation Artifact is updated in the **same** diff. If not, raise a **Live Documentation violation (Drift)** per `live-documentation.md` and name the stale artifact by path.
4. **Tests** — does a test cover the new behavior? Was a failing test written first (TDD)? No disabled/deleted tests to make the suite pass.
5. **Reuse / simplification / efficiency** — duplicate logic, dead code, needless complexity, obvious performance traps. Lower priority; do not let style swamp the substantive findings.

## How to report

- **Severity-tag** each finding: `blocking` / `should-fix` / `nit`. Lead with blocking.
- Reference each finding by `file_path:line_number`.
- Give the *why* and a concrete fix, not just a complaint.
- Distinguish **facts** (this is a bug) from **opinion** (I'd prefer X); label opinion as such.
- No drive-by scope expansion — flag out-of-scope issues separately, do not demand them.

## Posting on PRs

Be frugal with PR comments (see harness rules): comment only when a reply is genuinely necessary. Batch findings into one review rather than dripping comments.
