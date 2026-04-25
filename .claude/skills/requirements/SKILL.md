---
name: requirements
description: Turn ambiguous requests into testable requirements and acceptance criteria. Use when scope, constraints, or success conditions are unclear.
when_to_use: requirements, acceptance criteria, clarify scope, ambiguous request, user story, spec quality, testable criteria, elicitation
---

# Requirements Skill

Use this skill when clarification needs formal structure.

## Primary objective

Turn ambiguous requests into testable, bounded, and decision-ready requirements.

## Core process

1. Capture intent, scope, and constraints.
2. Surface ambiguity patterns and blocking gaps.
3. Propose defaults with alternatives.
4. Convert to acceptance criteria the team can test.
5. Confirm assumptions and unresolved risks.

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
