---
name: advisor
description: Analyze options and recommend a defensible path for non-coding decisions. Use when the user wants high-quality thinking and a clear recommendation rather than code changes — strategy calls, build/buy/migrate decisions, architecture trade-offs, risk assessment, executive briefs, pre-mortems, and open-ended "what should we do" framing. Produces BLUF + 2–4 realistic options with trade-offs + recommended path with rationale + downside risks/mitigations + concrete next actions, with confidence levels and unknowns labeled.
when_to_use: strategy decision, technical direction, build vs buy, vendor selection, architecture trade-off, options comparison, alternatives analysis, risk analysis, pre-mortem, executive brief, recommendation memo, decision support, one-way vs two-way door call, open-ended framing, "what should we do", "which option", "should we"
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
