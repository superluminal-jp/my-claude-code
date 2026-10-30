# Claim tree JSON

`{"nodes": [node, ...]}` with exactly one root claim (`"parent": null`). List order = reading order.

| key | on | value |
|---|---|---|
| id, parent, kind, text | every node | kind: claim, context, history, record, significance. text: the document's sentence, condensed but not reworded in meaning |
| order | claim with 2+ claim children | deductive, chronological, structural, comparative |
| reason | root, when order is deductive | why the key line must be deductive |
| therefore | child in a deductive group | true for a "therefore" point |
| prop | every child of a deductive group | propositional formula; the last child is the conclusion and is checked for entailment by the others |
| universe / scope | parent / each child | declared categories; checked for overlap and coverage |

Formulas: atoms `[A-Za-z_][A-Za-z0-9_]*`, operators `! & | -> <->` and parentheses; at most 12 atoms per group. Use one atom per proposition across the group. Formalize only what the text states: if the conclusion needs a premise the text lacks, leave it out and let T8 report the gap, because that gap is the finding.

Example (modus ponens):

```json
{"nodes": [
 {"id": "A", "parent": null, "kind": "claim", "text": "薬Aは血圧を下げる", "order": "deductive", "reason": "skeptical reviewers"},
 {"id": "M", "parent": "A", "kind": "claim", "text": "RCTなので差は薬効とみなせる", "prop": "diff -> effect"},
 {"id": "R", "parent": "A", "kind": "claim", "text": "12週後に差が出た", "prop": "diff"},
 {"id": "D", "parent": "A", "kind": "claim", "text": "よって薬Aは血圧を下げる", "prop": "effect", "therefore": true},
 {"id": "s", "parent": "A", "kind": "significance", "text": "治療選択が広がる"}
]}
```

Rules: T1 schema; T2 single root, parents exist, no cycles; T3 single child claim; T4 group lacks order; T5 deductive group over 4; T6 over 2 therefore points; T7 deductive key line without reason; T8 conclusion not entailed (countermodel given) or unchecked; T9 context over 2 sentences; T10 off-tree node misplaced or not a leaf; T11 declared scopes overlap, leave gaps or fall outside the universe; T12 topic label used as a claim.
