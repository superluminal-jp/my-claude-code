---
name: clarifier
description: Formalize material ambiguity into testable, bounded, decision-ready requirements. Use when unresolved scope, constraints, success conditions, non-functional requirements, prioritization, or acceptance criteria prevent safe commitment, or when the user explicitly requests formal requirement elicitation, user stories, Given/When/Then scenarios, INVEST, MoSCoW, or FURPS+ coverage. Do not use merely because a request is brief when it clearly names a recognizable artifact or workflow and provides enough information to start, nor for ordinary context gathering within that work. When another capability independently matches, apply this first only to resolve blocking requirements, then continue with the independently matched work.
---

# Formal Requirements

Purpose: turn material ambiguity into testable, bounded requirements through structured elicitation. Apply formal techniques only when an unresolved choice prevents safe commitment or the user requests a requirements artifact. A short request that clearly names a recognizable artifact or workflow is not ambiguous by brevity alone. Grounded in ISO/IEC/IEEE 29148:2018, INVEST, Gherkin, MoSCoW, FURPS+, and SMART (see [References](#references)).

## Primary objective

Turn ambiguous requests into testable, bounded, and decision-ready requirements.

## Core process

1. Capture intent, scope, and constraints.
2. Separate material blocking gaps from details that can be resolved during the requested work.
3. Propose defaults with alternatives.
4. Convert to acceptance criteria the team can test.
5. Confirm assumptions and unresolved risks.

When another capability independently matches, complete only the blocking requirements work first, then continue with that work. Do not replace its operation-specific context gathering or deliverable procedure.

## Ambiguity patterns to flag

- **Vague quantifiers**: "fast", "a lot", "many", "soon", "robust", "scalable", "user-friendly" -> demand a number + unit.
- **Undefined pronouns / scope**: "it", "the system", "everything" -> name the target.
- **Hidden compound**: statements with "and/or" that bundle multiple requirements -> split.
- **Implicit actor / trigger**: "when needed", "automatically" -> specify actor, event, precondition.
- **Implementation leakage in a requirement**: solution dictated before problem agreed -> separate *what* from *how*.
- **Negation without positive**: "should not be slow" -> restate as measurable positive ("p95 < 200ms").

## Elicitation toolbox (use selectively)

- 5W2H for missing dimensions.
- SMART for measurable goals.
- INVEST for user-story quality.
- Given/When/Then for test scenarios.
- MoSCoW for scope prioritization.
- FURPS+ for non-functional requirements.

## Quality gate

Before moving to implementation, each requirement should be:

- unambiguous,
- feasible,
- verifiable,
- non-conflicting,
- scoped enough to estimate.

## Anti-patterns

- Silently picking one interpretation when multiple are plausible.
- Asking after the work is done ("I built X, is that what you wanted?").
- Stacking clarifications turn-by-turn instead of batching.
- Treating a materially ambiguous request such as "make it better" as actionable without an agreed fit criterion.
- Redirecting a sufficiently defined artifact request into a generic requirements interview.
- Inventing acceptance criteria the user never agreed to.

## Clarification template

```text
Blocking gaps:
1) <dimension>: <question>
   Default: <X>
   Alternative: <Y>
   Impact: <reversible/irreversible, scope>

Assumptions if proceeding:
- <assumption> (confidence: high/medium/low)
```

## References

- ISO/IEC/IEEE 29148:2018, *Systems and software engineering — Life cycle processes — Requirements engineering* (2nd ed.) — <https://www.iso.org/standard/72089.html>
- Bill Wake, "INVEST in Good Stories, and SMART Tasks," 2003 (origin of INVEST) — <https://xp123.com/invest-in-good-stories-and-smart-tasks/>
- George T. Doran, "There's a S.M.A.R.T. Way to Write Management's Goals and Objectives," *Management Review* 70(11): 35–36, 1981 (origin of SMART).
- Cucumber, Gherkin reference (Given/When/Then) — <https://cucumber.io/docs/gherkin/>
- Dai Clegg & Richard Barker, *Case Method Fast-Track: A RAD Approach*, Addison-Wesley, 1994 (origin of MoSCoW); stewarded by the DSDM / Agile Business Consortium.
- IIBA, *A Guide to the Business Analysis Body of Knowledge (BABOK Guide)*, v3, 2015 — <https://www.iiba.org/>
- Robert B. Grady, *Practical Software Metrics for Project Management and Process Improvement*, Prentice Hall, 1992 (FURPS/FURPS+; originally Grady & Caswell, 1987).
