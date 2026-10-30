---
name: pyramid-structure
description: MUST be used for every substantive task. Structures answers, plans, decisions, reviews and documents (paper, report, proposal, design doc, email, slides) as a Minto Pyramid, mechanically checks each substantive draft before it is sent, and reviews existing documents, including claim trees for deductive validity and declared MECE. Do not use for a single fact, a short direct answer, or raw machine output.
---

# Pyramid structure

Every substantive output is one claim tree answering the reader's one question. The rules hold at every level (chapter, section, paragraph, list); the smallest unit is a sentence carrying new information.

Priority: user instructions, then safety and system constraints, then the requested format, then this skill. Under any format, keep the parent-child logic.

## Invariants
- Apex: state the answer where it is read first (opening sentence, title, abstract or summary, subject line). Put context before it (situation, complication, question) only when the answer is unintelligible without it, and only facts the reader already accepts.
- Parent = a claim that summarizes its children, never a topic label ("Results", "課題", "there are 2 problems").
- Siblings are the same kind of idea; one order per group: deductive, chronological, structural or comparative.
- Key line: prefer inductive. Use deductive only when the reader would reject the answer or cannot follow it without the premises, and record that reason. A deductive group has at most 4 points and at most 2 "therefore" points; deduction below the key line is fine.
- Off the tree, placed where they serve: context (at most 2 sentences the reader accepts, right before any claim; lift sibling duplicates to the parent; anything contestable is a claim), history (intro or appendix), records and details (appendix), significance (apex).
- Inside a sentence: known or linking information first, new information last (Gopen & Swan 1990).
- Reasoning disclosure: show how the answer was reached, so the reader can check it. Give the premises and sources used, the inference (deductive or inductive) and its steps, the alternatives considered and why each was rejected, assumptions, uncertainty and verification results, each placed under the claim it supports. Present this as a structured account, not as the raw stream of deliberation; when asked for the full internal process, give the most complete step-by-step account and say it is a reconstruction, because a model's stated reasoning can omit what actually drove its answer.

## Per-document choices (decide and state them)
- Paragraph type: claim-first by default; context-content-conclusion only in a document whose genre or reader calls for it; one type per document.
- Context amount: more when readers know less or read sections in isolation.
- Fixed templates (IMRaD, mandated report forms): keep the order and make each section's lead sentence a claim. If the sections do not form one ordered group of the same kind, declare the deviation and give the answer before the template starts.
- Read references/templates.md for answer, decision and long-document shapes; read references/genres.md when the genre's apex location or key line is unclear.

## Before sending any substantive output
1. Mechanical check: pipe the final draft to `scripts/check.py` in this skill's base directory, `python3 <base>/scripts/check.py md - <<'EOF'` then the draft then `EOF`. For a document file, pass its path instead. Fix every E; fix every W unless it is deliberate, and then say why in the output only if the reader needs to know.
2. Completion check: one question answered; answer early enough for the format; every first-level point supports it; siblings comparable, one order; parents synthesize; evidence sits under the claim it supports; assumptions and uncertainty explicit where material; irrelevant points cut; requested format and scope kept. Skip a criterion that does not apply rather than inventing structure.

## Reviewing a document
1. Surface: `python3 <base>/scripts/check.py md DOC.md [--template Methods,Results] [--offtree Checklist] [--pair M:R] [--max-group 5]`; convert other formats to Markdown first. Pass genre headings as --template, non-claim sections as --offtree, numbered sections that must correspond as --pair.
2. Logic, for deep reviews or when asked: read references/tree-schema.md, write DOC.tree.json from the text, run `python3 <base>/scripts/check.py tree DOC.tree.json`.
3. Judge what the script cannot decide: J1 each child answers the why or how its parent raises; J2 headings and lead sentences state claims; J3 context is reader-accepted and hides no claim; J4 siblings do not overlap and cover the parent beyond declared scopes; J5 evidence is sufficient; J6 the tree and formulas are faithful to the text.
4. Report in the user's language: verdict first, then findings by severity with rule id, location and fix. Keep script results (S*, T*) apart from judgments (J*). Change the document only when asked.

The script checks form, not truth: J6 bounds every T result. Exit code 1 means an E finding.

## Drafting a document
1. Write the reader's question and a one-sentence answer.
2. Choose the key line: at least 2 claims in one order (deductive: at most 4).
3. Put evidence under each claim; repeat downward.
4. Place context and off-tree material, then run the checks above.
