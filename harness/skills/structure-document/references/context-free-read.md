# Read by someone without the context

Read when the document will be published, committed for others, or sent to people who were not in the conversation. The author cannot see which words depend on the conversation; a reader who was not there can.

This read costs a full pass by a second model. In one measurement, a read of a 490-line document used about 115,000 to 125,000 tokens. Run it once the mechanical check passes, not on every draft.

## Procedure

1. Start a new subagent, not a fork, so that it has seen none of the conversation. If a read-only reviewer type is available, use it. With no subagent tool available, skip this step and say so.
2. Give it the path of the one file and the prompt below. Give it nothing else: no summary, no background, no other path.
3. Fix every item it lists in the document itself. Do not answer an item by explaining it in the conversation; the next reader will not have the conversation either.
4. If the first read listed anything, read once more with a new subagent. Report what the second read still lists. Do not run a third read without asking the person.

## Prompt

```text
You are a first-time reader of one document. Open exactly this one file and
nothing else: <path>

You have seen none of the conversation, code, or documents behind it. Report
what a reader in your position cannot follow. Do not judge whether its
content is right, and do not suggest improvements to the content.

Report two lists with line numbers, in <the document's language>:
1. Words whose referent you cannot identify from the document alone: a word
   used with two meanings, a pointer such as "that file" or "option B", an
   abbreviation or technical term that is never explained, a label that has
   no entry where the document says entries are listed.
2. Sentences whose meaning, or whose connection to the claim they sit under,
   you cannot follow. Say in one line what is missing.

Also check, and report each as OK or with the failing line numbers:
- every reference to a section, table, or source points to one that exists;
- every number derived from other numbers in the document agrees with them.

Rank each list by how much the item blocks understanding, and list at most
15 items per list, giving the total if it is larger. If a list is empty, say
so. No preamble and no summary of the document.
```
