# Live Documentation Rules

Purpose: documentation must never lie, and must sit close to what it describes. Applies to every diff/commit/PR reviewed and every Documentation Artifact created (docstring, README, spec, OpenAPI annotation).

Rationale, the lifecycle standards these operationalize, and citations: `docs/live-documentation-standards.md` (not auto-loaded — read it for the *why*).

## 1. Drift Detection

For every changed file with a public contract (exported function, public method, API endpoint, CLI argument, schema field), check whether an artifact covering that contract changed in the **same** diff. If not: flag a **violation (Drift)**, name the stale artifact by path, and do not pass the review until it is updated in that change or an Override is stated.

An artifact is stale at whatever layer it sits (§ 7); L2–L5 being recommended never exempts one that already exists. Do NOT flag internal-only changes — private renames, formatting, implementation refactors.

## 2. Separate Documentation PR Detection

On a docs-only diff, ask whether it describes code already shipped. If yes, flag it and recommend amending the original commit. Accept an Override for deliberate separation. Do NOT flag standalone ADRs or onboarding guides that are not code-derivative.

## 3. Auto-generation Recommendation

Before hand-writing an API reference, parameter list, schema description, or type docs, determine whether it can be generated from the code (signatures, annotations, docstrings, OpenAPI decorators). If so, name the tool and decline to hand-write. Otherwise hand-write and apply § 4.

## 4. Proximity Enforcement

Place each artifact closest to what it describes: inline docstring where the language allows, else a `README.md` in the **same** directory, else a co-located spec or contract file. Warn when a remote location is proposed (top-level `docs/`, a wiki, another repo) and offer the nearest co-located alternative. "Closest" is settled by § 7, not taste.

## 5. No Redundancy

If the information already exists in the repo, point at it and decline the duplicate; offer a cross-reference instead.

**Compression exception**: a summary of a lower layer written at a higher one is not a duplicate — § 7 requires it. Permitted when it (a) links to the canonical source, (b) does not contradict it, and (c) adds no fact absent from it. Breaking (b) is also a Drift violation.

## 6. Intermediate-Artifact Isolation

Shipped artifacts (README, docstring, public spec, OpenAPI annotation, code comment) must not cite Spec Kit process artifacts — `specs/NNN-*/spec.md`, `plan.md`, `tasks.md`, `research.md`, `quickstart.md`, `checklists/`. Those are ephemeral and their paths are not stable references. Put rationale in an ADR (`docs/adr/`) and link that, or state it in prose. An existing such link is a **violation (Intermediate-Artifact Leakage)** — replace or remove it. Artifacts inside `specs/` may link to each other; this check governs only what ships.

## 7. Granularity Layers

A fact's canonical source belongs at the **smallest** layer at which it is true; larger layers may compress it (§ 5). This is § 4 made discrete.

| Layer | Canonical artifact |
|---|---|
| L1 `repository` — the whole repository | root `README.md` |
| L2 `subtree` — a subsystem spanning several directories, addressed from outside through one entry point | `README.md` at the subtree root |
| L3 `directory` — the files directly inside one directory | `README.md` in that directory |
| L4 `file` — one file | leading docstring or module comment |
| L5 `block` — a passage inside a function; a non-obvious branch or invariant | inline comment |

L1 is MUST. L2–L5 are SHOULD; their absence is not itself a violation. **Any artifact that exists MUST conform to § 7.1–7.2.** § 1 applies independently, so a changed contract whose existing docstring or README went stale is still a violation.

### 7.1 Every artifact is a pyramid

1. **Shared ground first** — open with what the reader already knows and what this covers, defining its terms. Never open in undefined jargon.
2. **Answer before support** — state what the thing is or does before the detail behind it.
3. **Siblings MECE** — items at one level neither overlap nor leave a gap at that level.
4. **One logic per group** — a group either argues deductively (premise → premise → conclusion) or lists inductively (like kinds of fact). Never both at one level.

Failing any of the four is a **structure violation**.

### 7.2 Expertise rises by descending

Each layer addresses a reader who finished the layer above; L1 assumes no prior knowledge. Dependency runs one way: an artifact may rely on terms introduced at a **higher** layer, never on terms defined only at a **lower** one. A README leaning on a term defined solely in a docstring is a violation, as is any inversion of this direction.

A summary breaking one of § 5's three conditions is a **compression violation**; one that contradicts its canonical source is also Drift — one fact, told two ways.

**Not retroactive** — § 7 governs artifacts created from now on, and existing ones whenever a diff touches them. It is not a mandate to restructure what is already here.

## Override Handling

Accept an Override **only if** a reason is stated inline ("Override: emergency hotfix, docs follow in #123"), and record it — respond "Override accepted: [reason]" before proceeding. Reject silent overrides ("just skip the doc check") with: "Please state a reason for this override so it is on record."

## Out of Scope

Internal refactors with no contract change; generated files (migrations, build artifacts, lock files); new standalone ADRs, onboarding docs, or design documents not derived from existing code; test files describing expected behavior (§ 1 applies only when the tested interface changes); documentation predating § 7 and untouched by the current diff.
