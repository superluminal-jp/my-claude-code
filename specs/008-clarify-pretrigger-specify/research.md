# Research: Clarify Skill Pre-Trigger on Speckit Specify

**Feature**: 008-clarify-pretrigger-specify  
**Date**: 2026-05-26

## Decision Log

---

### 1. Passthrough Mechanism: How Clarify Output Reaches Specify

**Decision**: Implicit — via Claude Code conversation context. No explicit data plumbing needed.

**Rationale**: Claude Code skills execute inside a running conversation. When a `before_specify` hook invokes the clarifier skill, the entire Q&A exchange becomes part of the conversation history. When speckit-specify resumes after the hook, Claude naturally incorporates the clarified requirements visible in that history. The `$ARGUMENTS` passed to speckit-specify remains unchanged, but Claude synthesises the original description + clarify responses when generating the spec.

**Constraint**: This mechanism is conversational only — it works exclusively when Claude Code is the execution engine. Shell-script hooks (e.g., create-new-feature.sh) do not share this context, which is why they use JSON stdout for passthrough. The clarifier skill does not need a JSON output contract.

**Alternatives considered**:
- Write clarified requirements to a temp file and have speckit-specify read it: adds file I/O complexity with no benefit; rejected.
- Modify the speckit-specify playbook to explicitly consume hook output: out of scope; the playbook already handles conversational context naturally.

---

### 2. Hook Command Name

**Decision**: `command: clarifier`

**Rationale**: The `command` field maps to a slash command invocation. The clarifier skill's frontmatter declares `name: clarifier`, so `/clarifier` is the correct invocation. Existing hooks follow the same pattern (e.g., `command: review` → `/review`, `command: speckit.git.feature` → `/speckit-git-feature` after dot-to-hyphen substitution).

**Alternatives considered**:
- `command: clarify` (short form): does not match any registered skill name; rejected.

---

### 3. Optional vs Mandatory

**Decision**: `optional: true`, `enabled: true` (opt-out, not opt-in)

**Rationale**: Not all feature descriptions need clarification. A mandatory hook would block quick spec creation for already-clear descriptions. `optional: true` presents the hook as a user-prompted choice; `enabled: true` makes it visible and active by default so users discover it, but they can always skip the prompt or set `enabled: false` per-project.

**Alternatives considered**:
- `optional: false` (mandatory): forces clarify on every invoke — too disruptive for experienced users; rejected.
- `optional: true, enabled: false` (opt-in): users may never discover it; rejected.

---

### 4. Hook Position in before_specify List

**Decision**: First position in `before_specify`, before ubiquitous-language and speckit.git.feature.

**Rationale**: Clarification is the earliest-phase activity — it defines *what* to build. Ubiquitous-language validation and branch creation should follow once the requirements are settled. Running clarify first prevents branch names and UL candidates from being derived from an unclear description.

**Ordering**:
```
before_specify:
  1. clarifier          ← new (requirements-gathering, first)
  2. ubiquitous-language ← existing (UL validation, second)
  3. speckit.git.feature ← existing (branch creation, third)
```

**Alternatives considered**:
- Last position: clarify runs after UL and branch are already set up; inconsistent ordering rejected.
- After ubiquitous-language but before git: no meaningful benefit over first position; rejected.

---

### 5. Deliverable Scope

**Decision**: Single YAML entry added to `.specify/extensions.yml` under `before_specify`. No changes to skill files or playbook required.

**Rationale**: The speckit-specify playbook already handles `before_specify` hooks generically. The clarifier skill is already implemented. This feature is purely a configuration wire-up — adding one hook entry is the complete implementation.

**Deliverable**:
```yaml
- extension: clarifier
  command: clarifier
  enabled: true
  optional: true
  prompt: Run clarifier before specifying to sharpen requirements?
  description: Elicit intent, scope, constraints, and acceptance criteria before generating the spec
  condition: null
```
