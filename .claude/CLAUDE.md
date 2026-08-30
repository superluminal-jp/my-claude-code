# Core Principles

Priorities, highest first:

1. **Accuracy** — ground claims in verifiable sources; verify with tools before asserting. Separate fact from inference; never fabricate citations, paths, APIs, or numbers.
2. **Search and apply best practices in every aspect of the work** — follow recognized standards; state the rationale when deviating.
3. **Traceability** — record what was done, why, and how, in a form that can be confirmed and verified later (Documentation Artifacts, ADRs, commit history).
4. **Human-centered** — respect the user's goals and autonomy; be transparent about actions and limits.

# Before the first answer

- **Context sources, in order** — repo documentation (README, specs, ADRs) first: it's verifiable and team-visible, where Claude Memory is agent-only and can drift.
- **Clarify** — `rules/clarifier.md` governs when to ask vs. proceed; don't restate its triggers here.
- **Think in lenses** — silently self-check reasoning against `rules/thinking-lenses.md`'s six lenses (sequence, if-then, loop, logic tree, parallel, sync/async) on every task; this is a mental check only, never forced into a deliverable.
- **Plan non-trivial work through Spec Kit.** Non-trivial = multi-file, behavior-changing, or hard to reverse. No `.specify/` yet → recommend `specify init` first; once available, drive the change via `/speckit-specify` → `/speckit-plan` → `/speckit-tasks` → `/speckit-implement` (add `/speckit-clarify`, `/speckit-checklist`, `/speckit-analyze` as warranted) — invoke explicitly, don't improvise (`coder` skill's SDD section). For a small, reversible, single-file change, Spec Kit's full pipeline isn't required — but that doesn't mean skip recording intent: a clear commit message or brief note of what/why still satisfies Core Principle #3 (Traceability). Use judgment on how much process a given change earns; ask if unsure.

# Close-out: documentation and decisions

No non-trivial task ends at working code — it ends when the record is written. Two artifacts, two lifecycles:

- **Documentation Artifacts** (docstring, README, spec, OpenAPI annotation) describe current behavior; update in the **same change** as any altered public contract. `rules/live-documentation.md` holds the seven checks that apply to every diff and every artifact created. Two bind hardest at close-out: shipped code and docs must not link to Spec Kit process artifacts (`specs/NNN-*/`) — cite an ADR or plain prose instead; and a fact's canonical source sits at the smallest granularity layer where it is true, with every artifact stating its answer before the supporting detail.
- **Decision Records (ADRs)** capture _why_ a one-way-door choice was made; immutable once Accepted, only ever superseded, never rewritten. A decision that's architecturally significant, hard to reverse, with a rejected alternative → propose an ADR before moving on, never silently; the `adr` skill has the full policy and MADR playbook.

Before reporting non-trivial work done, verify:

1. Every changed public contract has its Documentation Artifact updated in the same change — or state explicitly why not.
2. Any one-way-door decision from this session has an ADR proposed (`adr` skill) — or was explicitly declined as unwarranted.
3. A step that genuinely doesn't apply (trivial, reversible, no contract or decision touched) is stated as such, not silently skipped.

# Skills

Skills load on demand; their names, descriptions and trigger phrases are already in context, so no list is kept here. `rules/skill-routing.md` covers what those descriptions cannot: how skills combine, where they stop, and how to break a tie. Full playbooks live in `.claude/skills/`.

# MCP

Project MCP definitions: `.mcp.json`. `~/.claude/install.sh` can register matching user-scope defaults. Full catalog: `rules/mcp.md`.

