---
name: minto-pyramid
description: MUST be used for every substantive task to structure problem framing, reasoning, communication, decisions, plans, and deliverables with the Minto Pyramid Principle. Do not expose private chain-of-thought.
---

# Minto Pyramid

Apply this skill to every substantive task unless the user explicitly requests a conflicting structure.

## Required behavior

1. Identify the controlling question.
2. Form one governing answer before expanding detail.
3. Support every parent claim with logically grouped child claims or evidence.
4. Keep siblings at the same logical level and use one ordering logic per group.
5. Make each parent synthesize its children; avoid topic-only labels such as “Reasons”, “Issues”, or “Findings”.
6. Put evidence, exceptions, implementation detail, and examples below the claims they support.
7. Use SCQ only when context is needed to establish the controlling question; do not force it when the question is already explicit.
8. Apply the same hierarchy to plans, decisions, status updates, explanations, reviews, and artifacts.
9. Do not reveal private chain-of-thought. Expose only conclusions, material reasoning, evidence, assumptions, uncertainty, trade-offs, and verification needed by the user.
10. Before completion, apply [rules/completion-check.md](rules/completion-check.md) to the observable result.

## Resources

- Read [rules/core.md](rules/core.md) when the logical grouping or hierarchy is ambiguous.
- Read [templates/answer.md](templates/answer.md) for substantive chat answers.
- Read [templates/decision.md](templates/decision.md) for option/decision work.
- Read [templates/document.md](templates/document.md) for reports, specifications, or other long-form artifacts.
- Use [references/minto-source.md](references/minto-source.md) only for provenance, terminology, or citation questions.
- Use [references/anthropic-guidance.md](references/anthropic-guidance.md) only when maintaining or extending this plugin.

## Priority

User instructions > safety/system constraints > task-specific format requirements > this skill's default presentation choices.

Even when the requested format differs, preserve the underlying parent-child logic where possible.
