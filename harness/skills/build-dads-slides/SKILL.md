---
name: build-dads-slides
description: Build 16:9 presentation slides as one HTML deck on the Digital Agency Design System's official HTML and CSS reference assets, structured top down - shared premises, then the conclusion, then the supporting points - with every slide showing where it sits in that structure. Use for slide decks, briefing material, and presentation documents that must follow DADS and are delivered as HTML or printed from it. Do not use for web pages, application interfaces, or dashboards that are not slides, and do not use to create or edit PowerPoint files.
metadata:
  kind: worker
  permission: workspace_write
  sandbox: network
  network-hosts: github.com, pypi.org, files.pythonhosted.org, the Playwright browser download host, fonts.googleapis.com, fonts.gstatic.com
  produces: one HTML deck that passes the bundled lint, with preview images
---

# Build slides on the Digital Agency Design System

Author a deck as one HTML document on a fixed 16:9 canvas, styled by the Digital Agency's own stylesheets. The HTML is the deliverable: it is presented in a browser, read in a browser, or printed from one. Nothing is converted to another format.

A slide is **1280 x 720 CSS pixels**, and printing gives one such page per slide. Every layout value, density limit, and check is stated against that canvas.

## Scope

- Presentation slides delivered as HTML. The deck's own content is the deliverable: do not restructure the surrounding project or add a build system it does not have.
- Resolve material ambiguity before building: who the audience is and what they already know, what decision the deck asks for, the governing message, how the deck will be used (projected, read alone, or both), and the information's classification - its 機密性 (1, 2, or 3) and its 公開範囲. Ask when two reasonable readings would produce different decks; otherwise proceed on a stated assumption.
- Never quote a DADS version, token name, component class, or package API from memory. Read it from the fetched assets, the installed package, or the live official source.

## Steps

1. **Define the deck before opening an editor.** Establish the audience, the decision or action asked for, the single governing message, the delivery context, and the classification marking every slide will carry, as the author or the organisation's security policy sets it.
2. **Write the tree, then derive the slides from it.** Put the governing message at the root, the two to four key-line points that answer the question it raises under it, and under each point the evidence that proves it. Lay the deck out in this order - premise, answer, points:
   1. Cover: the governing message as the title.
   2. Premise: the situation the audience accepts, what has gone wrong, the terms a newcomer needs in plain words, and one line on how the evidence was gathered. It ends in the question the deck answers. Omit it only when the audience already shares all of it.
   3. Answer: the governing message again, with the key line drawn as a tree, and the ask. This slide replaces an agenda and section dividers.
   4. One slide per key-line point: the point as the headline, its evidence in the body. A point whose supports are themselves claims continues onto one further slide per support.
   5. Closing: who does what by when, and one line on where the conclusion stops holding.
   6. Appendix: detail a reader may look up.

   A slide is one node of the tree with its direct children, never one leaf. The slide count follows the tree, not a budget. Make the structure visible on every slide: a tracker at the top right, the shoulder text, and a footer that counts `n / N`. Layouts and density limits: `references/slide-design.md`.
3. **Set up the workspace.**

   ```sh
   mkdir -p my-deck && cd my-deck
   cp "${CLAUDE_SKILL_DIR}/assets/deck-template.html" deck.html
   cp "${CLAUDE_SKILL_DIR}/assets/slide.css" .
   bash "${CLAUDE_SKILL_DIR}/scripts/fetch-dads-assets.sh" .
   bash "${CLAUDE_SKILL_DIR}/scripts/setup.sh"
   ```

   Without arguments the fetch script takes the components the template links. Name more components to add them.
4. **Build the slides.** Work from the template rather than inventing layout. Use the official `dads-*` components with their published markup for anything DADS defines, and this skill's `sld-*` classes only for slide geometry and the blocks DADS does not publish. Keep every slide inside the canvas and the safe area. The markup contract: `references/authoring-contract.md`.
5. **Check, then look.**

   ```sh
   .venv/bin/python "${CLAUDE_SKILL_DIR}/scripts/deck.py" lint deck.html
   .venv/bin/python "${CLAUDE_SKILL_DIR}/scripts/deck.py" preview deck.html -o preview
   ```

   Drive errors to zero and account for every warning. Then look at the preview images: a linter cannot tell that a slide is unreadable. Findings and options: `references/deck-checks.md`.
6. **Report** the governing message and the tree that supports it; the main-deck slide count and the parts the tracker groups it into; the lint findings and what was done about each; which official assets were fetched and at which commit; and what the reader needs to see the deck as intended - a current browser and, offline, the Noto Sans JP font. Apply the attribution rules of `references/asset-sourcing.md`.

## Inside the Bash sandbox

- `fetch-dads-assets.sh` clones the official repository and `setup.sh` installs Playwright and Chromium into a virtual environment in the deck's directory. Both need the hosts this skill declares. When the sandbox blocks a host, report the host and stop at that step; do not work around the sandbox. With assets and the environment already in place, `lint` and `preview` need no network apart from the web font.
- `deck.py` starts Chromium as a single process when it runs inside the sandbox on macOS, because the sandbox refuses the service registration that a multi-process start makes.
- The fetch script keeps its working copy under `$TMPDIR`.

## Guardrails

- **Never guess a classification.** Take the 機密性 level and the 公開範囲 from the author or the organisation's security policy; if neither is given, ask before building. Every slide, the cover and the appendix included, carries the same marking at its top right.
- **Never split a node across slides** to make each slide shorter. A slide that cannot hold its children has children that are not one group: regroup them into at most four, or move detail to the appendix.
- **Never explain by metaphor or analogy** on a slide. Define a term by what it is; illustrate with an instance of the thing itself.
- **Fonts decide line breaks.** The deck is checked with the font the browser loaded. A viewer without Noto Sans JP gets a fallback with different widths, so say how the font reaches the viewer.
- Never let colour, position, or a graphic alone carry meaning that the text does not also state.
- Never claim that a deck is a Digital Agency product or is endorsed by the Digital Agency.
- Never invent a DADS token, component class, or version number. Label everything this skill adds as this skill's own.
- Do not copy the Digital Agency's illustrations, icons, or Figma data into a deck. They carry separate terms from the MIT-licensed code.

## Done when

- `lint` reports no error, and every warning is accounted for in the report.
- The preview images were looked at, and every slide is readable inside the canvas.
- Every slide carries the classification marking the author gave.
- The report names the fetched assets with their commit, and what was not checked.

## Bundled files

| File | Read or run when |
|---|---|
| `references/slide-design.md` | Planning the deck's tree, choosing a layout, setting type and colour |
| `references/authoring-contract.md` | Writing or editing slide HTML: the markup contract the checker reads |
| `references/deck-checks.md` | Running `lint` and `preview`, or reading a finding |
| `references/asset-sourcing.md` | Fetching or refreshing official assets, or writing attribution |
| `assets/slide.css` | This skill's own 16:9 layout layer, built only on DADS token custom properties |
| `assets/deck-template.html` | A working deck that covers every slide role and body pattern. Copy it; do not edit it in place |
| `scripts/fetch-dads-assets.sh` | Step 3: resolves the official stylesheets into the deck workspace |
| `scripts/setup.sh` | Step 3: installs the checker's browser environment in the deck's directory |
| `scripts/deck.py`, `scripts/check_slides.js` | Step 5: `lint` and `preview` |
