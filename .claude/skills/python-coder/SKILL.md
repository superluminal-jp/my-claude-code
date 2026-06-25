---
name: python-coder
description: Implement and modify Python code following PEP 8, Black, strict typing, pytest, and secure-by-default patterns. Use when writing or changing Python source, tests, packaging (pyproject.toml), or Python tooling — .py files, pytest/unittest, FastAPI/Django/Flask, scripts, Lambda handlers, or data/CLI utilities in Python. Composes with the coder skill for TDD/SDD, docs sync, and OWASP-aware boundaries.
when_to_use: Python, .py file, pytest, unittest, pyproject.toml, requirements.txt, poetry, pip, FastAPI, Django, Flask, boto3 Python, Lambda Python, type hints, mypy, ruff, black, virtualenv, venv
---

Purpose: Python-specific implementation discipline. Applies when the primary language is Python. Composes with `coder` — load both; this skill adds stack conventions on top of TDD/SDD/docs/security.

# Style and structure

- **PEP 8** with **Black** (88-char lines). Match the repo's formatter/linter config (`ruff`, `flake8`, etc.) when present.
- **Type hints** on all function and method signatures; use `typing` / `collections.abc` for generics. Prefer `X | None` over `Optional[X]` on 3.10+.
- **Docstrings** (Google or NumPy style) on public modules, classes, and functions — purpose, parameters, returns, raised exceptions. Do not docstring private helpers unless non-obvious.
- **f-strings** for formatting; no `*` imports; explicit imports grouped stdlib → third-party → local.
- Functions ideally **≤20 lines**, one cohesive responsibility. Extract when logic branches multiply.
- **Double quotes** for strings unless the file already standardizes on single quotes.

# Project layout and dependencies

- Prefer **`pyproject.toml`** as the single source for build, deps, and tool config. Pin versions in lock files when the project uses them.
- Use a **virtual environment** (`venv`, `poetry`, `uv`) — never install packages globally for project work.
- Entry points and scripts belong in documented locations (`src/` layout or repo convention); avoid ad-hoc `sys.path` hacks.

# Testing

- **pytest** as default unless the repo uses unittest. Test names describe behavior (`test_user_cannot_login_with_invalid_password`).
- Use **fixtures** for shared setup; **parametrize** for input matrices. Mock **I/O boundaries** (HTTP, DB, filesystem, clock) — not internal private methods.
- **`pytest.raises`** / `match=` for expected exceptions. No `sleep` in tests; use freezegun or injected clocks.
- Run the narrowest failing test first, then the relevant suite before reporting done.

# Error handling and logging

- **Structured logging** (`logging` or project wrapper) with correlation/request IDs at boundaries when the codebase already uses them.
- Custom **domain exceptions** for recoverable business errors; let programmer errors propagate. Validate at **system boundaries** (HTTP handlers, CLI args, env vars, file/DB/API I/O).
- **Never** log secrets, tokens, or unredacted PII. Redact or omit sensitive fields.
- Use **context managers** (`with`) for resources; `try/finally` only when a context manager is unavailable.

# Security and I/O

- **No** `eval`, `exec`, or `pickle` on untrusted data. Use `subprocess` with argument lists, never `shell=True` with user input.
- Parameterized queries or ORM — **no** string-built SQL. Encode/escape output for the target context (HTML, JSON, etc.).
- **Secrets** from env, secret managers, or `.env` excluded from VCS — never hard-coded. Use **boto3** session/profile patterns for AWS.
- Set **timeouts** on HTTP and socket clients. Prefer **httpx** / **requests** with explicit `timeout=`.

# Async and performance

- Use **`async`/`await`** consistently in async codebases — no blocking calls inside the event loop without `asyncio.to_thread` or equivalent.
- Lazy iterators (`yield`, generators) for large sequences. Profile before micro-optimizing.

# Before reporting done

- [ ] `ruff check` / `mypy` / project linters pass on touched files
- [ ] Tests added or updated; suite green for affected scope
- [ ] Public API changes reflected in README or module docstring
- [ ] No new dependencies without justification and lockfile update

# Related skills

- **Always** → `coder` (TDD, SDD, docs sync, security baseline)
- **Unknown root cause** → `debugger`
- **AWS infrastructure as code** → `aws-cdk-coder` or `aws-cli-coder` when those layers are in scope
