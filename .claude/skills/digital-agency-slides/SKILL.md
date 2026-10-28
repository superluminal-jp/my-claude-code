---
name: digital-agency-slides
description: Build 16:9 presentation slides as one HTML deck on the Digital Agency Design System's official HTML and CSS reference assets, structured top down — shared premises first, then the conclusion, then one slide per supporting point — so the slide count stays bounded. Use for slide decks, briefing material, and presentation documents that must follow DADS and are delivered as HTML (or printed from it). Do not use for web pages, application interfaces, or dashboards that are not slides, and do not use to create or edit PowerPoint (.pptx) files. Apply alongside every independently matching requirements, document-structure, implementation, or review operation; this capability owns the slide authoring surface.
---

# Digital Agency Slides

Author a deck as one HTML document on a fixed 16:9 canvas, styled by the
Digital Agency's own stylesheets. The HTML is the deliverable: it is presented
in a browser, read in a browser, or printed from one. Nothing is converted to
another format, so the deck uses the official components exactly as the design
system publishes them.

## The invariant everything rests on

A slide is **1280 x 720 CSS pixels**, and printing gives one 1280 x 720 page
per slide. Every layout value, every density limit and every check below is
stated against that canvas. Break the canvas size and they stop holding.

## Scope

- Presentation slides delivered as HTML. Browser-resident pages that are not
  slides, application UI, and interactive dashboards are out of scope.
- The deck's own content is the deliverable. Do not restructure the
  surrounding project or introduce a build system it does not already have.
- Resolve material ambiguity before building: who the audience is and what
  they already know, what decision the deck asks for, the governing message,
  and how the deck will be used (projected, read alone, or both). Ask when two
  reasonable readings would produce different decks; otherwise proceed on a
  stated assumption.

## Load references progressively

| Read | When |
|---|---|
| `references/slide-design.md` | Planning the deck's tree, choosing a layout, setting type and colour |
| `references/authoring-contract.md` | Writing or editing slide HTML — the markup contract the checker reads |
| `references/deck-checks.md` | Running `lint` and `preview`, or reading a finding |
| `references/asset-sourcing.md` | Fetching or refreshing official assets, or writing attribution |

Never quote a DADS version, token name, component class, or package API from
memory. Read it from the fetched assets, the installed package, or the live
official source.

## Bundled material

| Path | What it is |
|---|---|
| `assets/slide.css` | This skill's own 16:9 layout layer, built only on DADS token custom properties. Not a DADS component library. |
| `assets/deck-template.html` | A working deck: seven main slides and one appendix slide, covering every slide role and body pattern. Copy it; do not edit it in place. |
| `scripts/setup.sh` | Installs Playwright and Chromium into a project-local virtual environment |
| `scripts/fetch-dads-assets.sh` | Resolves the official DADS stylesheets into a deck workspace at task time |
| `scripts/deck.py` | `lint` and `preview` |
| `scripts/check_slides.js` | Measures the laid-out deck in the browser and returns the findings |

No official Digital Agency code is vendored here. It is fetched when a deck is
built, so a deck always uses the current upstream reference implementation.

## Workflow

### 1. Define the deck before opening an editor

Establish the audience and what they already know, the decision or action
being asked for, the single governing message, and the delivery context.

### 2. Write the tree, then derive the slides from it

Write the deck as a tree before writing any slide: the governing message at
the root, the two to four key-line points that answer the question it raises,
and under each point the evidence that proves it. Then lay it out in this
order — **premise, answer, points**:

1. **Cover** — the governing message as the title.
2. **Premise** — the situation the audience accepts, what has gone wrong, the
   terms a newcomer needs, defined in plain words, and one line on how the
   evidence was gathered. It ends in the question the deck answers. Omit it
   only when the audience already shares all of it.
3. **Answer** — the governing message again, with the key line drawn as a tree,
   and the ask. This slide replaces an agenda and section dividers.
4. **One slide per key-line point** — the point as the headline, its evidence
   in the body.
5. **Closing** — who does what by when, when the deck asks for a decision,
   and one line on where the conclusion stops holding.
6. **Appendix** — detail a reader may look up, after the main deck.

This is the order of a research paper's parts — summary, introduction,
method, results, discussion, conclusion — with the answer first, and with the
method and the discussion folded into existing slides rather than given their
own. A slide is one node of the tree with its direct children, never one leaf.
The main deck is at most k + 4 slides for k key-line points.

Make the structure visible on every slide: a tracker at the top right lists
the main deck's parts and marks the current one, the shoulder text names it,
and the footer counts `n / N`. Each level of the tree has its own visual
treatment — headline, block titles, the evidence inside each block, the
takeaway band. Details, the layout
catalogue and the density limits: `references/slide-design.md`.

### 3. Set up the workspace

```sh
mkdir -p my-deck && cd my-deck
cp "$CLAUDE_SKILL_DIR/assets/deck-template.html" deck.html
cp "$CLAUDE_SKILL_DIR/assets/slide.css" .
bash "$CLAUDE_SKILL_DIR/scripts/fetch-dads-assets.sh" .
bash "$CLAUDE_SKILL_DIR/scripts/setup.sh"
```

Without arguments the fetch script takes the components the template links.
Name more components to add them; the script lists what is available upstream
when a name does not resolve.

### 4. Build the slides

Work from the template rather than inventing layout. Use official `dads-*`
components with their published markup for anything DADS already defines —
headings, lists, description lists, tables, links, chip labels — and this
skill's `sld-*` classes only for slide geometry and the blocks DADS does not
publish. Keep every slide inside the canvas and the safe area. The markup
contract is in `references/authoring-contract.md`.

### 5. Check, then look

```sh
.venv/bin/python "$CLAUDE_SKILL_DIR/scripts/deck.py" lint deck.html
.venv/bin/python "$CLAUDE_SKILL_DIR/scripts/deck.py" preview deck.html -o preview
```

`lint` reports a broken tree order, an over-long deck, a tracker that marks
the wrong part, document-level
accessibility faults, clipped or off-slide content, type below the legibility
floor, insufficient contrast, and missing text alternatives. Drive errors to
zero and account for every warning. Then **look at the preview images** — a
linter cannot tell you a slide is unreadable. Findings and options:
`references/deck-checks.md`.

### 6. Close out

Report: the governing message and the tree that supports it; the main-deck
slide count against its budget; lint findings and what was done about each;
which official assets were fetched and at which commit; and what the reader
needs to see the deck as intended — a current browser and, offline, the Noto
Sans JP font. Apply the attribution rules in `references/asset-sourcing.md`.

## Guardrails

- **Never split a node across slides** to make each slide shorter. A slide
  that cannot hold its children has children that are not one group: regroup
  them into at most four, or move detail to the appendix.
- **Never explain by metaphor or analogy** on a slide. Define a term by what it
  is; illustrate with an instance of the thing itself.
- **Fonts decide line breaks.** The deck is checked with the font the browser
  loaded. A viewer without Noto Sans JP gets a fallback with different widths,
  and a line that fitted may wrap or clip. Say how the font reaches the viewer.
- Never let colour, position, or a graphic alone carry meaning that the text
  does not also state.
- Never claim a deck is a Digital Agency product or is endorsed by the Digital
  Agency.
- Never invent a DADS token, component class, or version number. Label
  everything this skill adds as this skill's own, not as DADS.
- Do not copy the Digital Agency's illustrations, icons, or Figma data into a
  deck. They carry separate terms from the MIT-licensed code.
