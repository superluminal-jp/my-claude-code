---
name: meta-spec
description: "Decompose one complex initiative into independently specifiable feature slices and record them as a single meta-spec — each slice's purpose, observable end state, dependency order, exposed contracts, and priority — so a spec-driven workflow such as Speckit can then specify, plan, and implement one slice at a time. Also owns re-decomposition when implementation shows a slice boundary was wrong. Use when one request would otherwise produce a single oversized specification, when several specifications must be sequenced, or when an existing decomposition must be revised. Out of scope, each a separate capability's job: writing a slice's own specification, plan, tasks, or code; framing the underlying problem as a gap between current and ideal state; setting product direction, target users, or success metrics; and confirming the acceptance criteria of a single already-agreed feature. When another capability independently matches, this skill owns only the decomposition phase and hands each slice to that capability."
---

# Meta-Spec

For an initiative too large for one specification, produce a **meta-spec**: one document that states what each downstream specification will cover, in what order, and what each hands the next. The meta-spec is the input a spec-driven workflow consumes one slice at a time. It is not itself a specification, and it never contains implementation steps.

## Scope

**Covers**: slicing an initiative into feature-sized units, their dependency order, the contracts they exchange, their priority, and the maintenance of that decomposition over time.

**Out of scope** (a separate concern, not this skill's job):

- Writing any slice's specification, plan, task list, or code. This skill stops at the meta-spec and hands each slice over.
- Running the spec-driven workflow's own commands. It never invokes them and never creates a slice's directory.
- Framing the underlying problem — the gap between the current and the ideal state. That precedes decomposition and belongs to a separate capability.
- Product direction, target users, value proposition, or success metrics. Those precede decomposition too.
- Confirming the scope or acceptance criteria of a single, already-agreed feature. That is a separate requirements capability's job; this skill decides what the features *are*, not what one feature must satisfy.
- Architecture and technology-stack decisions. A slice boundary is not a module boundary, and stating one does not settle the other.

If the initiative fits in a single specification, say so and do not produce a meta-spec. A decomposition of one slice is overhead, not structure.

## How it works

1. **Check for an existing meta-spec** ([Re-decomposition](#re-decomposition)). If one exists for this initiative, that path governs and the steps below apply as a diff.
2. **Cut the slices** against the decomposition criterion ([Where to cut](#where-to-cut)).
3. **Order them and expose the contracts** ([Ordering and contracts](#ordering-and-contracts)).
4. **Test the set before writing** ([Completeness gate](#completeness-gate)).
5. **Write the meta-spec** ([Output shape](#output-shape)). If the session ends early, follow [Handling interruption](#handling-interruption).

## Where to cut

A candidate is one slice only when all three hold. State each slice so that a reader can refute it.

1. **Independently specifiable** — its specification can be written without reading a sibling's specification.
2. **Independently verifiable** — it has an observable end state that can be judged without waiting for a sibling.
3. **Dependency closed by contract** — whatever it needs from a sibling is named as an explicit contract (an interface, a data shape, a configuration key, a file format), not as shared understanding.

Conditions 1 and 2 are **INVEST** applied at feature scale (Bill Wake, "INVEST in Good Stories, and SMART Tasks," XP123, 2003). Condition 3 is **information hiding** (David L. Parnas, "On the Criteria To Be Used in Decomposing Systems into Modules," *Communications of the ACM* 15(12), 1972, pp. 1053–1058): cut where a design decision that is likely to change can be hidden behind a stated contract, not along the steps of the process the system performs.

When a candidate fails a condition, apply the split patterns in Richard Lawrence, "Patterns for Splitting User Stories," Humanizing Work, 2009 — by workflow step, business rule, data variation, interface, or effort — rather than inventing an ad-hoc cut. A slice that resists every pattern is usually a contract that has not been named yet.

**Do not slice by layer.** "Database", "API", "UI" fails condition 2: none has an end state a user can observe alone.

## Ordering and contracts

- **Record dependencies as a matrix, not a list.** Build the slice-by-slice dependency matrix and read the order off it — Design Structure Matrix (Donald V. Steward, "The Design Structure System: A Method for Managing the Design of Complex Systems," *IEEE Transactions on Engineering Management* EM-28(3), 1981, pp. 71–74).
- **A cycle is a defect in the cut, not a scheduling problem.** When slices depend on each other in both directions, either merge them into one slice, or extract the shared decision into a third slice both depend on.
- **The first slice is a walking skeleton** — the thinnest end-to-end path that exercises every contract at least once (Alistair Cockburn, *Crystal Clear*, Addison-Wesley, 2004). It retires integration risk before the slices that carry the volume.
- **Priority is MoSCoW** (Dai Clegg & Richard Barker, *Case Method Fast-Track: A RAD Approach*, Addison-Wesley, 1994), applied to slices, and it never contradicts the dependency order: a Must slice that depends on a Could slice means one of the two is misclassified.

## Completeness gate

Before writing, test the set as a whole:

- **100% rule** (Project Management Institute, *Practice Standard for Work Breakdown Structures*, 3rd ed., 2019): the slices together cover the initiative's stated scope and nothing beyond it. Work that appears in no slice is either out of scope — say so explicitly — or a missing slice.
- **No overlap**: two slices must not both claim the same observable outcome. If they do, the boundary between them is the thing to state, not the outcome.
- **Size**: keep the set small enough to hold in one reading. Above roughly nine slices, group them into a two-level decomposition and say which level each downstream specification maps to, rather than emitting a flat list.

## What each slice records

Per slice, state **purpose and end state, not procedure** — Commander's Intent (US Army ADP 6-0, *Mission Command: Command and Control of Army Forces*, July 2019). How the slice is built is decided later, by the planning step that reads its specification. A meta-spec that names files, functions, or libraries has taken that decision early and on worse information.

## Output shape

Write exactly one file. Inside a project that uses the numbered `specs/<N>-*` convention, write `specs/<NNN>-<slug>/meta-spec.md`, where `<NNN>` is the highest existing numeric prefix plus one, zero-padded to three digits. Otherwise use a project-appropriate default such as `docs/meta-spec/<slug>.md`. Create no other file, and **never write into or modify a file this skill did not create**.

Each slice later receives its own numbered directory from the spec-driven workflow. Record that number in the `Feature` column once it exists, so the meta-spec stays traceable to what was actually built.

Write the meta-spec in the language of the conversation. Keep framework names and sources in their original language.

```markdown
# Meta-Spec: <initiative>

**Status**: Complete | Draft (incomplete)
**Generated**: <YYYY-MM-DD>
**Slices**: <n>

## Purpose and end state

<what the whole initiative is for, and the observable condition under which it is done>

## Out of scope

<work deliberately excluded, so the 100% rule is checkable>

## Slices

| ID | Name | Purpose | End state (observable) | Depends on | Exposes | Priority | Feature |
|----|------|---------|------------------------|------------|---------|----------|---------|
| S1 | ...  | ...     | ...                    | —          | C1      | Must     | 041-... |

## Contracts

**C1 — <name>**: <the interface, data shape, or key; who produces it and who consumes it>

## Sequence

<the order read off the dependency matrix, and why the first slice is the walking skeleton>

## Open points

**Open point**: <what is unresolved>
**Default**: <the recommended answer>
**Alternative**: <another realistic option>
**Impact**: <which slice or boundary changes with the choice>

## Change log

| Date | Change | Reason |
|------|--------|--------|
```

## Re-decomposition

Implementation is the strongest test of a cut, so a boundary that fails during implementation is expected output, not failure. This skill owns the revision.

Detect an existing meta-spec **by path**, never by how similar the content looks — any similarity threshold is arbitrary and cannot be checked. When one exists, ask whether to revise it in place or save a new version; never decide silently.

On revision:

- Apply the change as a diff — add, merge, split, drop, or reorder slices — and leave untouched slices untouched.
- Re-run [Ordering and contracts](#ordering-and-contracts) and [Completeness gate](#completeness-gate) on the whole set; a local change can create a cycle or a gap elsewhere.
- Append one `Change log` row per revision, stating the change and the reason it was needed. Do not rewrite history that was already acted on.
- A slice already specified downstream may be superseded but is not silently deleted: mark it and say what replaced it.

## Handling interruption

If the session ends before the set is complete, save what was cut so far with `**Status**: Draft (incomplete)` and a list of the parts of the scope not yet assigned to a slice. Do not discard it, and do not present a partial set as a decomposition.

## Edge cases

| Situation | Response |
|---|---|
| The initiative fits one specification | Say so; produce no meta-spec |
| Two slices depend on each other | Merge them, or extract the shared decision into a third slice |
| A slice has no observable end state of its own | It is a layer or a task, not a slice; re-cut by workflow step, rule, or data variation |
| More than roughly nine slices | Group into two levels; state which level maps to a downstream specification |
| Scope that fits no slice | Either a missing slice or explicitly out of scope — never left unstated |
| A meta-spec already exists at the path | Ask: revise in place, or new version |
| The user asks for the slice's specification too | Produce the meta-spec, then hand the first slice to the spec-driven workflow; do not write the specification here |
