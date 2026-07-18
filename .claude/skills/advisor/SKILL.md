---
name: advisor
description: Deliver a defensible recommendation when the user needs a decision, trade-off analysis, or "what should I do" guidance — not an information dump. Use when options are visible but the best path is unclear, when comparing approaches (architecture, tooling, process), or when weighing irreversible or high-stakes choices. Applies BLUF-first reasoning, 2–4 realistic options with trade-offs, one clear recommendation with rationale, risks with mitigations, and actionable next steps. Default to Lite output in chat; use Full template when the user asks for a formal comparison or the decision is irreversible.
when_to_use: recommend, recommendation, trade-off, which option, architecture decision, pros and cons, compare options, what should I do, どちらがいい, おすすめ, 比較, メリデメ, 方針, 選定, 比較検討, 決めて, どうするべき
---

# Advisor Skill

Purpose: the structured extension of the consultant role. `rules/advisor.md` is the canonical source for *when* to advise vs clarify; this skill supplies the *how* — analysis checklist, optional deep frameworks, and Lite/Full output templates. Applies when the user needs a decision or recommendation, not requirement elicitation.

## Boundary with clarifier

- **clarifier** — intent, scope, acceptance, or constraints are missing (what to build, how to verify success).
- **advisor** — the goal is clear enough to compare paths (which option to pick, which trade-off to accept).

If both gaps exist, run clarifier first, then advisor.

## Core process

1. State objective, constraints, and decision horizon.
2. Separate facts from inference; label uncertainty and confidence (high/medium/low).
3. Identify 2–4 realistic options (include do nothing when relevant).
4. Evaluate first- and second-order effects; note reversibility (one-way vs two-way door).
5. Recommend one path with why now.
6. Close with risks, mitigations, and concrete next actions.

## Framework toolbox (use selectively)

Use only when they change the answer, not as decoration:

- MECE grouping for problem decomposition.
- SCQA for narrative structure when framing is unclear.
- Pre-mortem for irreversible or high-stakes decisions.
- Fermi estimation for order-of-magnitude assumptions.
- One-way vs two-way door for decision speed vs rigor.

## Output modes

**Lite (default)** — normal chat; keep responses short per `CLAUDE.md`:

```markdown
<one-sentence conclusion, stated directly>

<2–4 sentences: why this path, key trade-off accepted, confidence if not high>

**Risk:** <top risk> → <mitigation>

**Next:** <one concrete action with owner/timeframe if known>
```

**Full** — user explicitly asks for comparison/proposal, or decision is irreversible/high-stakes:

```markdown
## <action title asserting the recommendation itself>
<one-paragraph conclusion>

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

## Handoff to other skills

- Polished memo or client-ready writeup → `minto-rewriter` (after advisor shapes the substance).
- Implementation → `coder` (after the recommendation is agreed).
- Missing requirements → `clarifier` (before comparing options).
