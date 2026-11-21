---
name: record-decision
description: Writes an architecture decision record (ADR) - the context, the decision, the alternatives considered, and the consequences - so that later readers can see why a choice was made. Use when a change settles a question that would be expensive to reverse or that someone will later ask "why" about - a technology or library choice, a structural or interface decision, a policy, a deliberate trade-off - or when asked to write, supersede, or review an ADR. Not for routine changes whose reason is clear from the diff.
---

# Record a decision

Code shows what was chosen. A decision record keeps what the code cannot show: what else was possible and why it was not chosen.

## Steps

1. **Check that it is a decision.** There were at least two workable options, and the choice constrains later work. If the person has not made the choice yet, lay out the options and a recommendation, and write the record as `Proposed`.

2. **Follow the project's convention.** Look for existing records (`docs/adr/`, `docs/decisions/`, `adr/`) and match their location, numbering, file naming, front matter, headings, and language. Where the project has none, propose `docs/adr/NNNN-<kebab-title>.md` with four-digit numbers and use `assets/adr-template.md`.

3. **Write the record.**
   - **Title:** the decision itself as a short phrase ("Store sessions in Redis"), not the topic.
   - **Status:** `Proposed` until the person accepts it, then `Accepted`.
   - **Context:** the situation and the forces at play - requirements, constraints, what made a decision necessary - as facts a reader can check. Leave the decision out of this part.
   - **Decision:** what is chosen, in the active voice, specific enough that a reader can tell whether code complies.
   - **Alternatives:** each real option, with the reason it was not chosen. Include "do nothing" when it was viable.
   - **Consequences:** what becomes easier, what becomes harder, what must now be maintained, and what would make the decision worth revisiting.

4. **Keep it to one decision** and to about one page. A second decision gets a second record.

5. **Link it** from the place a reader would start: the records index if there is one, and the document or code the decision governs.

## Changing a decision

An accepted record is history. To change the decision, write a new record that states what it replaces, and change only the status line of the old one to `Superseded by NNNN`. Edit the body of an accepted record only to fix a typo or a broken link.

## Done when

- The record states one decision, the alternatives with reasons, and the consequences, including the unfavorable ones.
- It follows the project's existing convention, or the proposed one was agreed.
- Its status reflects what the person actually decided, and it is linked from where readers will look.
