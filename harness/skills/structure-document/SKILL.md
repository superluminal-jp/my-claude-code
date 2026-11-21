---
name: structure-document
description: Structures a document as one claim tree (Minto pyramid) so that a reader finds its single answer first and can check the support under it. Use when drafting, revising, reviewing, or restructuring a report, proposal, design document, README, email, slide outline, or pull-request or issue body. Not for a short conversational answer, a commit message, or raw command output.
---

# Structure a document

A reader should be able to stop after the first paragraph and still have the answer, and to check any claim by reading only what sits under it. Build the tree first, then write the prose from it.

## Steps

1. **Name the reader and their question.** Who reads this, what do they already know, and what will they decide or do with it? Write the question in one sentence.

2. **Write the answer in one sentence.** It answers that question and is a claim someone could disagree with, not a topic ("Move the batch job to a queue", not "About the batch job"). If it cannot be written, the thinking is not finished; work that out before structuring.

3. **Build the tree under the answer.**
   - Each point answers the question its parent raises: why, how, or which ones.
   - Siblings are the same kind of thing, do not overlap, and together are enough for the parent. Where they are not exhaustive, state the boundary.
   - Each group reasons in one way: an argument in which each point leads to the next, or a set of parallel points supporting the parent.
   - Order siblings by one logic: time, structure, or importance.
   - Aim for two to five children per parent. One child means the level is not needed; many more usually means a missing level.

4. **Open with only the context the answer needs:** the situation the reader already accepts, what changed or went wrong, and the question that raises. Then the answer immediately.

5. **Write from the tree.** Headings are claims, not labels ("Retries double the load", not "Retries"). Each paragraph opens with its point. Read `references/genres.md` for the usual shape of the document type at hand.

6. **Test it.**
   - Read only the answer and the headings: do they carry the whole argument?
   - For each heading, does everything under it support that claim? Move or cut what does not.
   - Read it as someone who has seen none of the surrounding conversation or code: is every term defined and every reference ("the earlier fix", "option B") spelled out?

## Reviewing an existing document

Extract its tree as it stands - the answer and the points under each - before judging the prose. Report, in order: whether there is a single answer and where it sits; points that do not support their parent; groups that overlap or have gaps; then wording. Propose the restructured tree before rewriting anything.

## Done when

- The first paragraph states the answer, and the answer and headings alone carry the argument.
- Every point supports its parent, and siblings are parallel, non-overlapping, and in a deliberate order.
- A reader new to the subject can follow it without access to the conversation.
