---
name: decision-support
description: Decision support—issue trees, trade-off matrices, pre-mortem, second-order thinking, reversibility, opportunity cost. Use proactively for strategy, prioritization, risk-heavy commits, or explicit option comparison.
allowed-tools: Read, Grep, Glob, WebFetch, WebSearch
user-invocable: true
model: opus
effort: high
---

# Decision Support

**Auto-activates for**: Strategic decisions, option evaluation, problem decomposition, risk assessment, planning.

---

## Quick Decision

```
User needs help with a decision or problem?
|
+-- Problem is unclear or complex?
|   +-- YES --> Issue tree / logic tree to decompose
|   +-- NO  --> Skip to evaluation
|
+-- Multiple options to evaluate?
|   +-- YES --> Trade-off matrix with criteria
|   +-- NO  --> Single option: Pre-mortem + Second-order analysis
|
+-- Decision involves risk or uncertainty?
    +-- Irreversible? --> Deep analysis (One-way door)
    +-- Reversible?   --> Bias toward speed (Two-way door)
```

---

## Frameworks

### 1. Problem Decomposition

**Issue Tree / Logic Tree**

Break a problem into **non-overlapping** sub-problems that **together cover** the whole issue. Each branch is testable independently.

```
Root problem
+-- Sub-problem A (distinct from B, C; together with B, C cover the root)
|   +-- Hypothesis A1
|   +-- Hypothesis A2
+-- Sub-problem B
|   +-- Hypothesis B1
+-- Sub-problem C
    +-- Hypothesis C1
    +-- Hypothesis C2
```

**When to use**: The problem is large, vague, or has many potential causes. Decomposition prevents gaps in analysis and reveals which sub-problems matter most (apply Pareto principle to prioritize branches).

### 2. Second-Order Thinking

Consider not just the direct effects of a decision, but the consequences of the consequences.

**Process**:
1. **First order**: What happens immediately if we do X?
2. **Second order**: What happens as a result of that?
3. **Third order**: What are the downstream effects on other stakeholders, systems, or timelines?

**When to use**: Any significant decision. Especially important for policy changes, pricing decisions, organizational restructuring, and market entry.

**Anti-pattern**: Evaluating only the intended effect and ignoring side effects, feedback loops, and behavioral responses by other actors.

### 3. Reversibility Assessment (One-way / Two-way Door)

From Bezos: classify every decision by reversibility before choosing how much rigor to apply.

| Type | Characteristics | Approach |
|------|----------------|----------|
| **One-way door** | Irreversible or very costly to reverse | Deep analysis, broad input, deliberate pace |
| **Two-way door** | Easily reversible, low switching cost | Decide quickly, iterate, gather data from action |

**When to use**: Before deciding how much analysis a decision warrants. Prevents over-analyzing trivial choices and under-analyzing critical ones.

### 4. Pre-Mortem

Assume the plan has already failed. Work backward to identify what caused the failure.

**Process**:
1. State the plan or decision clearly.
2. Imagine it is 6 months later and the plan has failed badly.
3. Each participant independently lists plausible causes of failure.
4. Aggregate, prioritize, and build mitigations into the plan.

**When to use**: Before committing to any significant plan. More effective than standard risk assessment because it overcomes optimism bias by accepting failure as a premise.

### 5. Opportunity Cost

Every choice has a cost: the value of the best alternative foregone.

**Rules**:
- Always include "do nothing" as an explicit option to evaluate.
- Compare the chosen option not against zero, but against the next-best alternative.
- Ask: "What else could we do with the same time, money, and attention?"

**When to use**: Resource allocation, prioritization, go/no-go decisions.

---

## Trade-Off Matrix

When comparing multiple options against multiple criteria:

```markdown
| Criteria (weight)       | Option A | Option B | Option C |
|------------------------|----------|----------|----------|
| Revenue impact (30%)   | High     | Medium   | Low      |
| Implementation cost (25%) | Low   | Medium   | High     |
| Time to value (20%)    | 3 months | 6 months | 1 month  |
| Risk level (15%)       | Medium   | Low      | High     |
| Strategic alignment (10%) | High  | High     | Low      |
```

**Rules**:
- Criteria should be **non-overlapping** and **collectively cover** the decision (no double-counting, no blind spots).
- Weights must sum to 100% and reflect stated priorities.
- Score each cell with specific data, not just "high/medium/low" when data is available.
- Sensitivity test: check if the conclusion changes when weights shift.

---

## Output Format

When providing decision support:

1. **Frame the decision**: What is being decided, by whom, by when?
2. **Decompose**: Issue tree if the problem is complex.
3. **Analyze options**: Trade-off matrix or structured comparison.
4. **Assess risks**: Pre-mortem for the leading option.
5. **Consider ripple effects**: Second-order thinking.
6. **Recommend**: State a clear recommendation with reasoning.
7. **Next action**: One concrete step to take now.

---

**Applied Rule**: `rules/output-standards.md` (analytical reasoning, epistemic standards, response priorities)

**Last Updated**: 2026-03-28
