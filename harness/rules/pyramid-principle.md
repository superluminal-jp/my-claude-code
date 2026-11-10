# Reader-Facing Structure

Make every substantive output communicate one central answer whose support a reader new to the subject can follow. Apply the structure silently; expose labels or formal scaffolding only when they improve the reader's understanding.

## Scope

Apply this rule when an output makes multiple substantive points, including a recommendation, explanation, analysis, plan, or review. A single fact, a short direct answer, or raw machine output needs no artificial hierarchy. Premises and terms apply to every reader-facing output that uses specialised content, however short.

## Central answer

- State the answer, conclusion, or recommendation before its supporting detail.
- If the answer would be unintelligible without shared context, give only the minimum context needed to interpret it and then state the answer immediately. Do not delay the answer merely to narrate how it was reached.
- Keep every lower section relevant to that central answer; omit parallel commentary that does not change, justify, explain, or operationalize it.

## Premises and terms

Assume the reader is new to the subject unless the user's own messages show otherwise, and has seen none of the conversation, code, or documents behind the output.

- State the premises the answer depends on — the prerequisite concept, the condition under which it holds, and its scope — before the answer when it is unintelligible without them, otherwise directly after it.
- Define each term, abbreviation, or symbol a newcomer would not know at its first use, in plain words, by what it is and what it does in this context.
- Name what each reference points to: which one a word with several referents means (which environment, which account), and what a pointer into that unseen context stands for (that file, option B, the earlier fix).
- Write each term in the form practitioners of its field use in the output language; if that form is unclear, keep the original term. Never coin a translation: a term must match its field's literature, code, and tools. Make a term plain by defining it, not by replacing it.
- Never explain by metaphor or analogy: a comparison with something else carries only some of the subject's properties, and the reader infers the rest wrongly. Explain the thing itself — its definition, its parts, and how they relate — and illustrate with a concrete instance of the subject, which is an example, not a comparison.

## Parts

Lay out a full answer in the order of a research paper, keeping the answer first: summary, premises, method, results, discussion, conclusion.

1. Summary — the answer and its main supports in one paragraph, with whatever context it cannot be read without.
2. Premises — the background, the problem, the question, and the terms, as above.
3. Method — how the support was obtained: sources, procedure, and assumptions, so the reader can judge how far to trust it. If the answer rests only on reasoning from the request, say so.
4. Results — the support, grouped by the points that answer the question.
5. Discussion — what the results mean, where they stop holding, and alternative explanations not ruled out.
6. Conclusion — what follows for the reader: the decision, action, or next step, not a repeat of the summary.

- Omit a part with no content. In a short answer, keep the order and compress the parts into a few sentences.
- Show the parts as headings only in long-form writing such as a report, an analysis, or a document, numbered by their place in the tree (1, 1.1) and phrased as claims; in an ordinary answer keep the order without headings.
- Make each supporting point visible: lead with its claim in bold and nest its evidence beneath it. Use a numbered list for a sequence or rank, and a table for items compared on the same criteria.
- Open each paragraph with its claim in the first sentence; the sentences after it support that claim.

## Vertical support

- Every child point must answer the question naturally raised by its parent and must support—not merely relate to—the parent's claim.
- Distinguish the role of each point. Reasons justify a claim, evidence substantiates a reason, examples illustrate rather than prove a general claim, and actions operationalize a decision.
- Do not present reasons, evidence, examples, and actions as though they were comparable siblings. Nest or separate them according to the claim each one supports.

## Horizontal grouping

- Make siblings comparable in kind and abstraction level, mutually exclusive enough to avoid double-counting, and collectively sufficient for the parent claim within the stated scope.
- State the boundary when available evidence or scope does not support an exhaustive group; do not claim MECE by assertion alone.
- Use one reasoning mode within a group. A deductive group leads from compatible premises to a necessary conclusion; an inductive group synthesizes comparable observations into a supported generalization.

## Order

- Order sibling points by one consistent logic that helps the reader follow the claim: dependency or chronology for a sequence, causal order for an explanation, rank for priorities, or a stable category order for a partition.
- In deductive support, preserve the premise-to-conclusion relationship. In inductive support, use the same comparison basis for every member and place the most decision-relevant point first when no natural sequence governs.
