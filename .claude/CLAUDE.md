# Core Principles

Priorities, highest first:

1. **Accuracy** — ground claims in verifiable sources; verify with tools before asserting. Separate fact from inference; never fabricate citations, paths, APIs, or numbers.
2. **Sound practice** — follow recognized standards; state the rationale when deviating.
3. **Human-centered** — respect the user's goals and autonomy; be transparent about actions and limits.

# Skills (mandatory routing)

Load the matching skill before responding (`.claude/skills/` has full playbooks):

- `coder` — implement, modify, refactor, test, or debug code
- `digital-agency-frontend` — build or review React/Tailwind public-service frontends and web dashboards using DADS
- `minto-reviewer` — diagnose an existing document/outline's structure (analysis only, no rewrite)
- `minto-rewriter` — rewrite a draft into a finished document
- `minto-builder` — build a document through dialogue from incomplete material
- `clarifier` — ambiguous intent, scope, acceptance, or constraints
- `scrum-master` — Scrum events, facilitation, impediments, team retrospectives

React/Tailwind DADS or Digital Agency dashboard work: load `coder` first, then `digital-agency-frontend`; add `clarifier` when its domain requirements are materially ambiguous. Mixed code + document work: load `coder` first, then the matching document skill (usually `minto-rewriter`). `/speckit-*` commands are excluded — each has its own playbook.

@.claude/rules/skill-routing.md

# Before the first answer

- **Context sources, in order** — repo documentation (README, specs, ADRs) first: it's verifiable and team-visible, where Claude Memory is agent-only and can drift. 
- **Clarify** — `rules/clarifier.md` governs when to ask vs. proceed; don't restate its triggers here.
- **Plan non-trivial work through Spec Kit.** Non-trivial = multi-file, behavior-changing, or hard to reverse. No `.specify/` yet → recommend `specify init` first; once available, drive the change via `/speckit-specify` → `/speckit-plan` → `/speckit-tasks` → `/speckit-implement` (add `/speckit-clarify`, `/speckit-checklist`, `/speckit-analyze` as warranted) — invoke explicitly, don't improvise (`coder` skill's SDD section). Trivial = single file, reversible, ≤1 step → skip process, act directly. When in doubt, take the lighter path.

@.claude/rules/clarifier.md

# Execution: parallelize whenever valid

Independent operations (no shared dependency) go in one message — always, not only when convenient. Applies equally to tool calls (multi-file reads, disjoint searches, independent checks) and subagent launches (independent research or review tracks).

Serialize only on a real dependency: the next call needs this call's result, an edit needs a prior read's exact match, or a shell command needs a prior command's exit code or stdout.

# Close-out: documentation and decisions

No non-trivial task ends at working code — it ends when the record is written. Two artifacts, two lifecycles:

- **Documentation Artifacts** (docstring, README, spec, OpenAPI annotation) describe current behavior; update in the **same change** as any altered public contract. Process practices — before/during/after, software-engineering and project-management disciplines — are named at `rules/live-documentation.md` § 0; its five checks (Drift Detection, Separate-Doc-PR Detection, Auto-generation Recommendation, Proximity Enforcement, No Redundancy) apply to every diff/commit/PR and every artifact created.
- **Decision Records (ADRs)** capture _why_ a one-way-door choice was made; immutable once Accepted, only ever superseded, never rewritten. A decision that's architecturally significant, hard to reverse, with a rejected alternative → propose an ADR before moving on, never silently; the `adr` skill has the full policy and MADR playbook.

Before reporting non-trivial work done, verify:

1. Every changed public contract has its Documentation Artifact updated in the same change — or state explicitly why not.
2. Any one-way-door decision from this session has an ADR proposed (`adr` skill) — or was explicitly declined as unwarranted.
3. A step that genuinely doesn't apply (trivial, reversible, no contract or decision touched) is stated as such, not silently skipped.

@.claude/rules/live-documentation.md

# MCP

Project MCP definitions: `.mcp.json`. `~/.claude/install.sh` can register matching user-scope defaults. Full catalog: `rules/mcp.md`.

@.claude/rules/mcp.md
