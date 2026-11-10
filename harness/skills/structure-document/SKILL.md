---
name: structure-document
description: Structure a document as one claim tree, so that a reader finds its one answer first and can check the support under it, and check the result with the bundled checker - a report, proposal, design document, specification, README, email, slide outline, or pull-request or issue body. Use when drafting or revising such a document, and when asked to review or restructure an existing one. Do not use for a short conversational answer, a single fact, raw command output, or a commit message; those need no separate procedure.
metadata:
  kind: worker
  permission: workspace_write
  sandbox: inside
  produces: a document whose structure passes the checker, or a review of one
---

# Structure a document

A document answers one question of its reader. Everything in it is one claim tree under that answer, and the same rules hold at every level: chapter, section, paragraph, list. The person's instructions and the requested format come before this skill; under any format, keep the parent-child logic.

## Invariants

- **Answer first.** State the answer where it is read first: the opening sentence, title, summary, or subject line. Put context before it only when the answer is unintelligible without it, and only facts the reader already accepts.
- **A parent is a claim that summarizes its children,** never a topic label such as "Results" or "There are two problems".
- **Siblings are the same kind of idea in one order:** deductive, chronological, structural, or comparative.
- **Prefer an inductive key line.** Use a deductive one only when the reader would reject the answer or could not follow it without the premises, and say why. A deductive group has at most four points and at most two "therefore" points; deduction below the key line is fine.
- **Off the tree, placed where they serve:** context (at most two sentences the reader accepts, directly before a claim; lift what siblings repeat to their parent; anything contestable is a claim), history (introduction or appendix), records and details (appendix), significance (with the answer).
- **Inside a sentence,** known or linking information comes first and new information last.
- **Show how the answer was reached,** under the claim it supports: premises and sources, the inference and its steps, the alternatives rejected and why, assumptions, uncertainty, and verification results. Present a structured account, not the raw stream of deliberation. When asked for the full process, give the most complete step-by-step account and say that it is a reconstruction, because a model's stated reasoning can omit what actually drove its answer.

## Choices to make per document

- Paragraph type: claim-first by default. Use context-content-conclusion only when the genre or the reader calls for it, and use one type per document.
- Context amount: more when readers know less or read sections in isolation.
- Fixed templates (a research paper's parts, a mandated report form): keep the order and make each section's lead sentence a claim. If the sections do not form one ordered group, say so and give the answer before the template starts.
- Read `references/templates.md` for the shapes of an answer, a decision, and a long document. Read `references/genres.md` when it is unclear where a genre puts its answer.

## Drafting

1. Write the reader's question and a one-sentence answer.
2. Choose the key line: at least two claims in one order.
3. Put the evidence under each claim, and repeat downward.
4. Place context and off-tree material, then run the checks.

## Checks before delivering

1. **Mechanical check.** Run `python3 "${CLAUDE_SKILL_DIR}/scripts/check.py" md FILE.md`. Fix every `E`. Fix every `W` unless it is deliberate. Options: `--template Methods,Results` for genre headings, `--offtree Appendix` for non-claim sections, `--pair M:R` for numbered sections that must correspond, `--max-group 5`.
2. **Completion check.** One question answered; the answer early enough for the format; every first-level point supports it; siblings comparable and in one order; parents synthesize; evidence under the claim it supports; assumptions and uncertainty explicit where they matter; requested format and scope kept; a reader who has seen none of the conversation, code, or documents can tell what every word and pointer refers to. Skip a criterion that does not apply rather than inventing structure.
3. **Read by someone without the context, for a document that leaves the conversation.** When the document will be published, committed for others, or sent to people who were not in the conversation, read `references/context-free-read.md` and follow it. Skip it for drafts and working notes, and say that it was skipped.

## Reviewing an existing document

1. Surface: run the checker as above. Convert other formats to Markdown first.
2. Logic, for a deep review or when asked: read `references/tree-schema.md`, write `DOC.tree.json` from the text, and run `python3 "${CLAUDE_SKILL_DIR}/scripts/check.py" tree DOC.tree.json`.
3. Judge what the script cannot decide: each child answers the why or how its parent raises; headings and lead sentences state claims; context is reader-accepted and hides no claim; siblings do not overlap and cover the parent; the evidence is sufficient; the tree is faithful to the text.
4. Report in the person's language: verdict first, then findings by severity with rule id, location, and fix. Keep script results apart from judgments. Change the document only when asked.

The script checks form, not truth. Exit code 1 means an `E` finding remains.

## Done when

- The checker reports no `E`, and every remaining `W` is deliberate.
- The completion check holds for the criteria that apply.
- For a document that leaves the conversation, the read without context ran and what the second read still listed is reported, or the reason it was skipped is stated.
- For a review, the verdict and findings are reported and the document is unchanged unless a change was asked for.

## Bundled files

| File | Read or run when |
|---|---|
| `references/templates.md` | Choosing the shape of an answer, a decision, or a long document |
| `references/genres.md` | The genre's place for its answer, or its key line, is unclear |
| `references/tree-schema.md` | Writing a claim tree for a logic review |
| `references/context-free-read.md` | The document leaves the conversation (check 3) |
| `scripts/check.py` | Checks 1 and review steps 1 and 2. Reads its input only; writes no file |
