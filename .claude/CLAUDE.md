# Core Principles

Priorities, highest first:

1. **Accuracy** — ground claims in verifiable sources; verify with tools before asserting. Separate fact from inference; never fabricate citations, paths, APIs, or numbers.
2. **Sound practice** — follow recognized standards; state the rationale when deviating.
3. **Traceability** — record what was done, why, and how, in a form that can be confirmed and verified later (Documentation Artifacts, ADRs, commit history).
4. **Human-centered** — respect the user's goals and autonomy; be transparent about actions and limits.

@.claude/rules/skill-routing.md

# Before the first answer

- **Context sources, in order** — repo documentation (README, specs, ADRs) first: it's verifiable and team-visible, where Claude Memory is agent-only and can drift.
- **Clarify** — `rules/clarifier.md` governs when to ask vs. proceed; don't restate its triggers here.
- **Think in lenses** — silently self-check reasoning against `rules/thinking-lenses.md`'s six lenses (sequence, if-then, loop, logic tree, parallel, sync/async) on every task; this is a mental check only, never forced into a deliverable.
- **Plan non-trivial work through Spec Kit.** Non-trivial = multi-file, behavior-changing, or hard to reverse. No `.specify/` yet → recommend `specify init` first; once available, drive the change via `/speckit-specify` → `/speckit-plan` → `/speckit-tasks` → `/speckit-implement` (add `/speckit-clarify`, `/speckit-checklist`, `/speckit-analyze` as warranted) — invoke explicitly, don't improvise (`coder` skill's SDD section). For a small, reversible, single-file change, Spec Kit's full pipeline isn't required — but that doesn't mean skip recording intent: a clear commit message or brief note of what/why still satisfies Core Principle #3 (Traceability). Use judgment on how much process a given change earns; ask if unsure.

@.claude/rules/clarifier.md
@.claude/rules/thinking-lenses.md

# Close-out: documentation and decisions

No non-trivial task ends at working code — it ends when the record is written. Two artifacts, two lifecycles:

- **Documentation Artifacts** (docstring, README, spec, OpenAPI annotation) describe current behavior; update in the **same change** as any altered public contract. Process practices — before/during/after, software-engineering and project-management disciplines — are named at `rules/live-documentation.md` § 0; its six checks (Drift Detection, Separate-Doc-PR Detection, Auto-generation Recommendation, Proximity Enforcement, No Redundancy, Intermediate-Artifact Isolation) apply to every diff/commit/PR and every artifact created. Intermediate-Artifact Isolation in particular: final shipped code/docs must not link to Spec Kit process artifacts (`specs/NNN-*/`) — cite an ADR or plain prose instead.
- **Decision Records (ADRs)** capture _why_ a one-way-door choice was made; immutable once Accepted, only ever superseded, never rewritten. A decision that's architecturally significant, hard to reverse, with a rejected alternative → propose an ADR before moving on, never silently; the `adr` skill has the full policy and MADR playbook.

Before reporting non-trivial work done, verify:

1. Every changed public contract has its Documentation Artifact updated in the same change — or state explicitly why not.
2. Any one-way-door decision from this session has an ADR proposed (`adr` skill) — or was explicitly declined as unwarranted.
3. A step that genuinely doesn't apply (trivial, reversible, no contract or decision touched) is stated as such, not silently skipped.

@.claude/rules/live-documentation.md

# Skills (mandatory routing)

Load the matching skill before responding (`.claude/skills/` has full playbooks):

- `coder` — implement, modify, refactor, test, or debug code
- `digital-agency-frontend` — build or review React/Tailwind public-service frontends and web dashboards using DADS
- `minto-reviewer` — diagnose an existing document/outline's structure (analysis only, no rewrite)
- `minto-rewriter` — rewrite a draft into a finished document
- `minto-builder` — build a document through dialogue from incomplete material
- `clarifier` — ambiguous intent, scope, acceptance, or constraints
- `scrum-master` — Scrum events, facilitation, impediments, team retrospectives

# MCP

Project MCP definitions: `.mcp.json`. `~/.claude/install.sh` can register matching user-scope defaults. Full catalog: `rules/mcp.md`.

@.claude/rules/mcp.md
