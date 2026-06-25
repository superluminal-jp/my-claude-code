---
name: editor
description: Produce polished, ready-to-ship work products — memos, proposals, reports, briefing notes, slide decks, charts/dashboards, proofreading edits, and translations. Use when the main output is a finished artifact rather than source code, and the user expects publishable copy (not just an outline or brainstorm). Applies pyramid/MECE structure, BLUF at the section level, action titles on slides, Cleveland–McGill chart selection, Tufte-style data-ink discipline, and plain professional language; quantifies claims, names sources/units/scope, and ships finished copy with frameworks applied implicitly.
when_to_use: write memo, draft report, prepare proposal, create slides, build deck, design chart, build dashboard, proofread text, edit document, translate content, executive summary, one-pager, briefing note, analysis document, client-ready writeup, polish wording, rewrite for clarity
---

# Work Products: Documents, Decks, Research, and Language

Purpose: ship a finished, publishable artifact (not an outline). Applies when the deliverable is a document, deck, chart, proofread, or translation. Grounded in the Pyramid Principle (Minto), Tufte's data-ink discipline, and the Cleveland–McGill graphical-perception ranking.

Use for **produced artifacts** (memos, proposals, analyses, decks) and for **editing, translation, and study designs**. For live conversation and decision support, load **`advisor`** skill (or see `rules/advisor.md`). When the deliverable is a polished writeup of a recommendation, shape with `advisor` first, then finish with `editor`.

## Documents

- **Structure**: Pyramid principle; **MECE** groupings; **SCQA** for problem framing; **BLUF** at section level for executive readers.  
- **“So what?”** on every substantive claim — show insight, not only data.  
- For recommendations: **owner, deadline, expected result, and resources/dependencies** when relevant.  
- **Quantify** where possible. Avoid vague intensifiers without numbers.  
- In **external-facing** or client-ready text: do **not** name frameworks or methodology brands; use plain professional language.  
- Deliver **finished** copy when the user asked for a document (ready to use or light polish), unless they asked for outline only.

## Slides and charts

- **Action titles** (McKinsey style): every slide’s title is a full **conclusion in ~15 words**; reading titles alone should tell the story.  
- **One message per slide**; about **one minute** of spoken content per slide as a guide.  
- **Chart type** (Zelazny / standard practice): parts → pie or stacked bar; **comparison** → bar (often horizontal); **trend** → line or column; **relationship** → scatter.  
- **Semantic color** sparingly: e.g. positive / negative / neutral; cap palette at **3–5** colors for the deck.  
- **Tufte-style**: high **data-ink** ratio; drop chartjunk. Always include **units**, **axis labels**, **source**, and **legend** when needed.  
- **Cleveland & McGill**: prefer position and length over angle, area, or color alone. Keep **lie factor** near 1.  
- **Typography**: at most **two** font families; body **≥ 18pt**, title **~32pt**; consistent **margins** (e.g. 1" feel).

## Quality pipeline (order matters)

1. **Revision** — substance, structure, and logic.  
2. **Edit** — wording, voice, and consistency.  
3. **Proof** — typos, grammar, and formatting.  

- **Citations** (if required): state style up front — e.g. **APA 7** (academic), **IEEE** (engineering), **Chicago 17** (many business / trade contexts).  
- **Source hierarchy** when triangulating: **primary** → peer-reviewed or equivalent → reputable secondary.

## Research and analysis (for deliverables)

- Distinguish **primary vs secondary**; prefer **primary** when practical.  
- For numbers: **source, date, and scope** (population, geography, cohort).  
- In comparisons: name **axes** and keep **assumptions** parallel across options.  
- If exact data are unavailable, use **bounded** estimates and label them as such.

## Language and style

- **Strunk & White** habits: **active** voice, concise, **concrete** verbs.  
- **Plain language**; one main idea per paragraph; prefer measurable statements.  
- On first use of a **technical term**: short **plain-language** gloss.  
- **Tone, depth, and format** flex to **audience and purpose** (e.g. exec summary vs working note).

## Learning and explanation

When asked to teach: **Feynman** style — simple words, **examples**, **analogies** from known to new. **Socratic** prompts (questions that guide) when the user asked for coaching rather than a direct answer. Check **understanding** before adding complexity.

## Proofreading and translation

- **Proofreading**: keep the author’s intent; improve **clarity**, **brevity**, and **logical** flow.  
- **Translation**: not literal if that reads poorly — **natural, professional** target language.

## Output and packaging

- Use **headings**, **lists**, and **tables** to scan.  
- In **shipped** artifacts, no **framework labels**; natural wording only.  
- Match **output format** to the ask (e.g. memo, email, one-pager, report sections).

## Related rules

- **Choosing response vs persisted-artifact language** (which language to write in) → `rules/localization.md`.
