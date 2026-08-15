# Research: Skill Bodies Independent of Sibling Skills

## R1 — `digital-agency-frontend/SKILL.md` (4 instructions, largest change)

### "## Compose the workflow" section (currently lines 10–15)
Currently:
```
1. Load `coder` before changing code; keep TDD, type safety, security, and documentation sync there.
2. Use this skill for DADS-specific design, source, dashboard, and accessibility decisions.
3. Load `clarifier` when the users, task, decision, data meaning, constraints, or success criteria are materially ambiguous.
4. Preserve the target repository's architecture and instructions. Do not introduce React or Tailwind CSS solely to make this skill applicable.
```
→ new (renamed "## Scope of this skill" — "compose" implied a sibling to compose with):
```
1. Use this skill for DADS-specific design, source, dashboard, and accessibility decisions.
2. Preserve the target repository's architecture and instructions. Do not introduce React or Tailwind CSS solely to make this skill applicable.
3. Resolve material ambiguity in users, task or decision, use context, content or data, constraints, and success criterion before implementation (step 1 below) rather than inventing intent.
4. Treat implementation as test-first and boundary-safe: write or update a failing behavior or accessibility test before implementing, keep the change type-safe, validate external data at its boundary, and keep documentation synchronized with any changed contract in the same change (steps 4–6 below).
```
Items 1 and 4 (old numbering) named sibling skills; items 2 and 3 (old numbering) already were self-contained and are kept, renumbered. New items 3 and 4 restate what naming `clarifier`/`coder` was standing in for, in the skill's own terms, so no behavior is lost — this is the substantive content preserved per FR-001.

### "### 4. Implement through `coder`" heading (currently line 46)
→ new: "### 4. Implement test-first and type-safe"
The five bullets under this heading (lines 47–51) already describe self-contained DADS-specific behavior (failing test first, adapt official examples, theme plugin caution, boundary validation) and need no wording change — only the heading named `coder`. Add one bullet after the first to state the type-safety requirement explicitly, since old item 1 of "Compose the workflow" named it and nothing else in the file did:
```
- Keep the change type-safe; do not weaken or bypass the project's type checker to make code compile.
```

### "### 6. Close out with traceability" section (currently lines 60–65)
Currently the second bullet: "Run the project test, type-check, lint, format, and build commands required by `coder` and the repository."
→ new: "Run the project's test, type-check, lint, format, and build commands."
Add one new bullet (documentation-sync was previously implied by "keep... documentation sync" in the removed `coder` line, and nothing else in the file states it): "Update the documentation artifact (README, component/prop reference, story) for any changed public component contract in the same change."

## R2 — `coder/SKILL.md` (1 instruction)

Currently (line 92, under "# Related rules"):
```
- **A significant, hard-to-reverse decision is settled** → load the `adr` skill to record it.
```
→ Remove this line entirely. The "Related rules" section's remaining bullet (git-workflow.md) is unaffected — it points to a *rule file*, not a skill, and is out of scope per FR-002. No replacement text is needed: `coder`'s own scope is implementing code, not deciding whether a decision needs a permanent record; that judgment call belongs wherever the decision surfaces (already covered at the router layer — `.claude/CLAUDE.md`'s Close-out section already instructs proposing an ADR for one-way-door decisions, so removing this line from `coder` drops no coverage).

## R3 — `adr/SKILL.md` (1 mention)

Currently (line 9):
```
Purpose: author and maintain Architecture Decision Records — policy and playbook in one place. Complements `coder` (SDD captures *what/why* of a feature) by recording the *decision* itself. Template follows Nygard's original structure extended with the MADR 4.0.0 optional sections; rationale content follows ISO/IEC/IEEE 42010:2022 (see [References](#references)).
```
→ new:
```
Purpose: author and maintain Architecture Decision Records — policy and playbook in one place. An ADR captures a decision's context, choice, consequences, and rejected alternatives, distinct from a feature's day-to-day *what/why*. Template follows Nygard's original structure extended with the MADR 4.0.0 optional sections; rationale content follows ISO/IEC/IEEE 42010:2022 (see [References](#references)).
```

## R4 — `minto-builder/SKILL.md` (2 sentences)

Currently (lines 48–50, between the "Do not use this skill when" list and "## Interaction contract"):
```
Route diagnosis to `minto-reviewer`.

Route direct rewriting to `minto-rewriter`.
```
→ Remove both lines and the blank line between them. The preceding "Do not use this skill when" list (lines 41–46: structural diagnosis, direct final rewrite, proofreading, factual research) already states the boundary in the skill's own terms without naming which sibling handles it; "## Interaction contract" follows directly.

## R5 — `minto-reviewer/SKILL.md` (2 sentences)

Currently (between its own "Do not use this skill when" list and "## Input assumptions"):
```
Route finished-document rewriting to `minto-rewriter`.

Route collaborative document development to `minto-builder`.
```
→ Remove both lines and the intervening blank line, same rationale as R4.

## R6 — `minto-rewriter/SKILL.md` (2 sentences)

Currently (between its own "Do not use this skill when" list and "## Output contract"):
```
Route structural diagnosis to `minto-reviewer`.

Route collaborative development to `minto-builder`.
```
→ Remove both lines and the intervening blank line, same rationale as R4.

## R7 — `specs/015-digital-agency-frontend/spec.md` FR-004 (supersession)

Currently:
```
- **FR-004**: The skill MUST compose with the repository's existing clarification and coding workflows rather than duplicate their generic requirements, test-driven development, security, or documentation rules.
```
→ new (rewritten in place, per this repository's precedent of correcting a prior spec's specific invalidated line — see how spec-026 corrected `permissions.md`'s claims — rather than leaving it to silently contradict the shipped skill):
```
- **FR-004**: The skill's own body MUST be self-contained: it MUST NOT instruct loading, routing to, or implementing through another named skill (`coder`, `clarifier`, or any other). It MUST state, in its own terms, the test-driven, type-safety, security, documentation-sync, and ambiguity-resolution behavior the DADS/dashboard workflow requires. *(Supersedes the original FR-004, which required composing with `coder`/`clarifier` instead of duplicating their rules — superseded by `specs/028-independent-skills/` to keep skill bodies independent of sibling skills; sequencing which skills a request needs remains the router's job in `.claude/CLAUDE.md`/`.claude/rules/skill-routing.md`, unaffected by this change.)*
```
Also update the Assumptions section's line "The existing `clarifier` and `coder` skills remain responsible for generic requirements elicitation, test-driven implementation, security, and documentation synchronization." → this becomes false for `digital-agency-frontend` specifically; rewrite to: "Generic requirements elicitation, test-driven implementation, security, and documentation synchronization are now stated within `digital-agency-frontend`'s own body (see FR-004, superseded by `specs/028-independent-skills/`); the `clarifier` and `coder` skills remain available for other work but are no longer a dependency of this skill."

## R8 — `tests/run-digital-agency-frontend-skill.sh` DADS-06/DADS-07

Currently:
```sh
check_contains "DADS-06: workflow composes with coder" "$SKILL_FILE" '`coder`'
check_contains "DADS-07: workflow composes with clarifier" "$SKILL_FILE" '`clarifier`'
```
→ new (assert the new contract — self-contained coverage, and absence of the removed instructions — rather than deleting the checks outright, so the file keeps guarding *something* about completeness):
```sh
check "DADS-06: skill body does not name coder or clarifier as a dependency" "$([ -f "$SKILL_FILE" ] && ! grep -Eq '(Load|Implement through) .(coder|clarifier).' "$SKILL_FILE" && echo 1 || echo 0)"
check_contains "DADS-07: workflow requires test-first, type-safe, documented implementation in its own terms" "$SKILL_FILE" '(failing (behavior|accessibility) test|type-safe).*(before implement|type checker)'
```
Exact grep syntax to be finalized during implementation against the actual rewritten file text (R1) — the check must fail before R1's edit and pass after, verified by running the suite both ways.

SYNC-SKILL-05A (asserts `.claude/rules/skill-routing.md` composes `coder` + `digital-agency-frontend`) is unmodified and expected to keep passing — verified directly:
```sh
grep -nE 'coder.*digital-agency-frontend|digital-agency-frontend.*coder' /Users/taikiogihara/work/my-claude-code/.claude/rules/skill-routing.md
```
confirms this line still exists at skill-routing.md and is untouched by this feature (out of scope per FR-007).

## R9 — No other test files affected

Direct grep against `tests/run-codex-drift.sh`, `tests/run-codex-references.sh`, and `tests/run-install.sh` for the patterns being removed/reworded (`` `coder` ``, `` `clarifier` ``, `` `adr` ``, `` `minto-reviewer` ``, `` `minto-rewriter` ``, `` `minto-builder` ``, "Route diagnosis", "Route finished-document", "Route structural diagnosis", "Route collaborative", "Complements", "Implement through") returns zero hits in all three files. No other test file needs edits.

## R10 — No `contracts/` artifact needed

No external interface (API, CLI, schema) is exposed or changed by this feature — it edits instructional skill content and one guarding test file. Same rationale as spec-024/025/026.

## R11 — No new ADR

Per the spec's Assumptions: the routing/composition *mechanism* (the router decides which skill(s) a request needs and in what sequence) is unchanged by this feature — only where the *instruction to compose* is written down moves from skill body to (already-existing) router documentation. This is not an architecturally significant, hard-to-reverse decision with a rejected alternative in the `adr` skill's sense; it is a duplication cleanup. No ADR is proposed.
