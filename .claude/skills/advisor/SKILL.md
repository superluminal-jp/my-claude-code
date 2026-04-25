---
name: advisor
description: Analyze options and recommend a path for non-coding decisions. Use for strategy, trade-offs, risk assessment, and open-ended exploration.
when_to_use: strategy, trade-off, options comparison, risk analysis, recommendation, decision support, wall session, executive brief
---

# Advisor Skill

Use this skill when the user needs high-quality thinking, not code changes.

## Working style

1. Start with BLUF.
2. Separate facts from inference.
3. Provide 2-4 realistic options with trade-offs.
4. Recommend one path and state why now.
5. End with concrete next actions.

## Analysis checklist

- Define objective, constraints, and decision horizon.
- Identify alternatives (including do nothing).
- Evaluate first-order and second-order effects.
- Include downside risks and mitigation.
- State confidence (high/medium/low) and unknowns.

## Optional deep frameworks

Use only when useful for the user’s request:

- MECE grouping for problem decomposition.
- SCQA for narrative structure.
- Pre-mortem for risk-first planning.
- Fermi estimation for bounded assumptions.
- One-way vs two-way door for decision speed vs rigor.

## Output template

```markdown
## Recommendation
<one-paragraph BLUF>

## Options considered
- Option A: <benefit> / <risk>
- Option B: <benefit> / <risk>

## Why this recommendation
- <reason 1>
- <reason 2>

## Risks and mitigations
- <risk> -> <mitigation>

## Next steps
1. <owner> - <action> - <timeframe>
2. <owner> - <action> - <timeframe>
```
