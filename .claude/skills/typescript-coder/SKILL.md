---
name: typescript-coder
description: Implement and modify TypeScript and JavaScript code with strict typing, ESLint/Prettier, modern ES modules, and framework-aware patterns (React, Next.js, Node). Use when writing or changing .ts, .tsx, .js, .jsx files, package.json scripts, tsconfig, Vitest/Jest tests, or Node/browser tooling. Composes with the coder skill for TDD/SDD, docs sync, and OWASP-aware boundaries.
when_to_use: TypeScript, JavaScript, .ts, .tsx, .js, .jsx, tsconfig, eslint, prettier, npm, pnpm, yarn, React, Next.js, Node.js, Vitest, Jest, Vite, tsc, strict mode
---

Purpose: TypeScript/JavaScript-specific implementation discipline. Applies when the primary language is TS/JS. Composes with `coder` — load both; this skill adds stack conventions on top of TDD/SDD/docs/security.

# Type system

- **`strict`: true** in `tsconfig` — no new `any` without a documented escape hatch. Prefer `unknown` at boundaries, then narrow.
- **Explicit types** on public function signatures and exported APIs. Let inference work inside function bodies.
- Prefer **`interface`** for object shapes that may be extended; **`type`** for unions, intersections, and mapped types.
- Use **`satisfies`** and `as const` where they preserve literal types without widening. Avoid type assertions (`as`) unless unavoidable — comment why.
- **Discriminated unions** for state machines and result types (`{ ok: true, value } | { ok: false, error }`).

# Style and modules

- **ES modules** (`import`/`export`); no CommonJS in new code unless the repo requires it.
- **ESLint + Prettier** — match existing config. No disabled rules on touched lines without justification.
- **async/await** over raw `.then()` chains. Always handle rejection paths.
- **Named exports** for libraries; default exports only when the framework convention requires (e.g., Next.js pages).
- **JSDoc** on exported functions and complex types when behavior is not obvious from signatures alone.

# React / Next.js

- **Functional components** and hooks only — no new class components.
- **Props and state fully typed**; destructure props in the signature.
- **Error boundaries** around route- or feature-level trees where the project uses them.
- Stable **`key`** props on lists. Memoize (`useMemo`, `useCallback`) only when profiling or referential equality matters — not by default.
- **Next.js App Router**: server components by default; `"use client"` only when interactivity or browser APIs are required. Co-locate data fetching with the layer the framework prescribes.
- **Accessibility**: semantic HTML, ARIA where needed, keyboard focus management for interactive widgets.

# Node and I/O

- **Project-scoped dependencies**: add packages to `package.json` (`dependencies`/`devDependencies`); never `npm install -g` / `pnpm add -g` / `yarn global add` for project work. One-off CLI tools run via `npx`/`pnpm dlx` instead of a global install. (Enforced for Claude's own commands by `.claude/hooks/pre-bash.sh`.)
- Validate **env vars and request payloads** at boundaries (Zod, Valibot, or project schema library).
- **Never** concatenate user input into shell commands or raw SQL. Use parameterized queries and safe APIs.
- Set **timeouts** on `fetch` and HTTP clients. Prefer the project's HTTP client over ad-hoc `fetch` wrappers.
- **Structured logging** (pino, winston, or project standard) — no secrets or tokens in log fields.

# Testing

- **Vitest** or **Jest** per repo convention. Test behavior, not implementation details.
- Use **Testing Library** for React — query by role/label, not by class or test IDs unless necessary.
- Mock **network and I/O** at module boundaries; avoid mocking React internals.
- For async UI, use `findBy*` / `waitFor` — no arbitrary `setTimeout` in tests.

# Security

- Encode output for context (React escapes by default; beware `dangerouslySetInnerHTML`).
- **CSP**, **CSRF**, and **auth** patterns follow framework and project docs — do not roll custom crypto.
- Dependencies: prefer maintained packages; run audit when adding security-sensitive libs.

# Before reporting done

- [ ] `tsc --noEmit` / project typecheck passes
- [ ] ESLint passes on touched files
- [ ] Tests added or updated; suite green for affected scope
- [ ] Public API or env var changes reflected in README or `.env.example`

# Related skills

- **Always** → `coder` (TDD, SDD, docs sync, security baseline)
- **AWS CDK in TypeScript** → `aws-cdk-coder` when infrastructure code is in scope
