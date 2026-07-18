---
name: clarifier
description: Turn ambiguous requests into testable, bounded, decision-ready requirements with verifiable acceptance criteria. Use when scope, constraints, success conditions, or non-functional requirements are unclear, when user stories need INVEST/Gherkin shape, when scope needs MoSCoW prioritization, or when NFR coverage (FURPS+) is missing — i.e. before estimation, planning, or implementation can safely start. Surfaces blocking gaps in batch with defaults and alternatives, converts the agreed answer into Given/When/Then or measurable SC-### criteria, and labels assumptions with confidence so the team can test, estimate, and commit.
when_to_use: clarify requirements, define acceptance criteria, ambiguous request, vague request, missing success criteria, scope unclear, draft user story, INVEST check, write Given/When/Then scenarios, prioritize backlog, MoSCoW, define non-functional requirements, FURPS+, elicit constraints, formal requirement quality check, spec quality review, before estimation, before implementation kickoff
---

# Requirements Skill

Purpose: the formal-elicitation extension of the clarification gate. `rules/clarifier.md` is the canonical source for *when* to ask vs proceed; this skill supplies the *how* — structured toolboxes for turning ambiguity into testable, bounded requirements. Applies when clarification needs formal structure (user stories, acceptance criteria, NFR coverage). Grounded in ISO/IEC/IEEE 29148:2018, INVEST, Gherkin, MoSCoW, FURPS+, and SMART (see [References](#references)).

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

## References

- ISO/IEC/IEEE 29148:2018, *Systems and software engineering — Life cycle processes — Requirements engineering* — <https://www.iso.org/standard/72089.html>
- Bill Wake, "INVEST in Good Stories, and SMART Tasks," 2003 — <https://xp123.com/invest-in-good-stories-and-smart-tasks/>
- George T. Doran, "There's a S.M.A.R.T. Way to Write Management's Goals and Objectives," *Management Review* 70(11): 35–36, 1981.
- Cucumber, Gherkin reference (Given/When/Then) — <https://cucumber.io/docs/gherkin/>
- Dai Clegg & Richard Barker, *Case Method Fast-Track: A RAD Approach*, 1994 (origin of MoSCoW); DSDM / Agile Business Consortium.
- Robert B. Grady, *Practical Software Metrics for Project Management and Process Improvement*, Prentice Hall, 1992 (FURPS/FURPS+; originally Grady & Caswell, 1987).
- IIBA, *A Guide to the Business Analysis Body of Knowledge (BABOK Guide)*, v3, 2015 — <https://www.iiba.org/>
