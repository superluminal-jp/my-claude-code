# Shapes by document type

Each shape is the same tree - answer first, support under it - laid out in the order readers of that type expect. Omit a part that has no content.

## Contents

- Report or analysis
- Proposal or decision request
- Design document
- README
- Email or chat message
- Pull-request body
- Issue or bug report
- Slide outline

## Report or analysis

1. Summary: the answer and its main supports in one paragraph.
2. Background: the situation, the question, and the terms a reader needs.
3. Method: sources, procedure, and assumptions, so the reader can judge how far to trust the results.
4. Results: the support, grouped by the points that answer the question.
5. Discussion: what the results mean, where they stop holding, what was not ruled out.
6. Conclusion: what the reader should decide or do next. It is not a repeat of the summary.

## Proposal or decision request

1. The decision asked for, by whom, and by when.
2. The recommendation and its expected effect.
3. The reasons, each with its evidence.
4. The alternatives considered and why each was not chosen.
5. Cost, risk, and what would reverse the decision.
6. The next step once approved.

## Design document

1. What is being built and the problem it solves, in one paragraph.
2. Goals and non-goals.
3. The design: the parts, what each is responsible for, how they interact. A diagram where the structure is the point.
4. The decisions that were not obvious, each with the alternatives and the reason.
5. How it will be tested, rolled out, and observed.
6. Open questions.

## README

1. What the project is and who it is for, in one or two sentences.
2. The quickest path to using it: requirements, install, one working example.
3. Common tasks and configuration.
4. How to develop and test it.
5. Where to find more: deeper documents, how to get help, license.

A reader who stops after part 2 should be able to run it.

## Email or chat message

- First line: what you need from the reader, or the one thing they should know.
- Then only the context they need to act.
- One message, one subject. Put a deadline or a question where it cannot be missed, not in the last line of a long paragraph.

## Pull-request body

1. What the change does and why, in one or two sentences.
2. How it was verified: the commands run and their results.
3. What reviewers should look at closely, and known limits.
4. Links: the issue, specification, or decision record.

## Issue or bug report

1. What is wrong, in one sentence: expected versus actual.
2. How to reproduce it: the smallest steps, the input, the environment and versions.
3. Evidence: the exact error text or output.
4. Impact: who is affected and how badly.
5. What has been tried or ruled out.

## Slide outline

- One message per slide, written as the slide's title in a full sentence.
- The titles read in order form the whole argument; check this before making any slide body.
- The first content slide states the answer; the last states what the audience should do.
