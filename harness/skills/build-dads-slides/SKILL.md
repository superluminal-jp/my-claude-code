---
name: build-dads-slides
description: Build 16:9 presentation slides as one HTML deck on the Digital Agency Design System's official HTML and CSS reference assets, structured as a Minto pyramid in the form its audience needs - a research-paper form (summary, premises, method, results, discussion, conclusion), a business-presentation form (introduction, answer, supporting points, next step), or a business deck that borrows parts of the paper form - with every slide showing where it sits in that structure. Use for slide decks, briefing material, and presentation documents that must follow DADS and are delivered as HTML or printed from it. Do not use for web pages, application interfaces, or dashboards that are not slides, and do not use to create or edit PowerPoint files. [Developers / execute]
metadata:
  kind: worker
  role: developers
  branch: execute
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

1. **Define the deck before opening an editor.** Establish the audience, the decision or action asked for, the single governing message, the delivery context, the classification marking every slide will carry, as the author or the organisation's security policy sets it, and the deck's form - paper or business - chosen by what the audience already knows and what it must do (`references/slide-design.md`).
2. **Write the tree, then lay it out in the deck's form.** The Minto pyramid is the same in either form: put the governing message at the root, the two to four key-line points that answer the question it raises under it, and under each point the evidence that proves it; give the answer before its support; make every headline an assertion. The form decides what surrounds the tree.
   - **Paper form** (`data-form="paper"`), for an audience new to the subject or one that must be able to check the evidence. The order of a research paper, keeping the answer first - summary, premises, method, results, discussion, conclusion:
     1. Cover: the governing message as the title.
     2. Summary (要旨), always slide 2: the governing message again, the key line drawn as a tree with one line of evidence per branch, and the ask. Like a paper's abstract it is read before the premises, so it uses no term they have yet to define. It replaces an agenda and section dividers.
     3. Premises (前提), on as many slides as they need: the situation the audience accepts, what has gone wrong, the question this raises - the one the deck answers - and the terms a newcomer needs, in plain words.
     4. Method (方法): how the evidence was gathered - its sources, the period, the procedure, and the assumptions - so the audience can judge how far to trust it; or, when the answer rests on reasoning alone, that it does.
     5. Results: one slide per key-line point, the point as the headline and its evidence in the body. A point whose supports are themselves claims continues onto one further slide per support.
     6. Discussion (考察): what the results mean, where the conclusion stops holding, and the alternative explanations the evidence does not rule out.
     7. Conclusion (結論): the decision asked for, and who does what by when - what follows for the audience, not a repeat of the summary.
     8. Appendix: detail a reader may look up.
   - **Business form** (`data-form="business"`), for an audience that shares the background and must decide or act. Minto's own presentation order - introduction, answer, supporting points, next step:
     1. Cover: the governing message as the title.
     2. Introduction (導入), one slide at most: the situation the audience knows, the complication that changed it, and the question it raises. It reminds the audience; it does not inform them. Leave it out when they are already asking the question.
     3. Answer (結論), slide 2, or slide 3 after the introduction: the governing message, the key line drawn as a tree, and the ask.
     4. Points: one slide per key-line point, as in the paper form.
     5. Next step (次の一手): the decision asked for, and who does what by when.
     6. Appendix: background the introduction could not hold, and detail a reader may look up.

     A business deck borrows a part of the paper form when its audience needs it - a method slide when the figures will be challenged, a discussion slide headed リスク when the answer depends on a condition that may not hold - and puts it where the paper form would: the method before the points, the discussion after them.

   A slide is one node of the tree with its direct children, never one leaf. A part that needs more than one slide continues onto further slides marked `data-continues`, so the tracker still shows it as one part. The slide count follows the tree and its parts, not a budget. Make the structure visible on every slide: a tracker at the top right, the shoulder text, and a footer that counts `n / N`. Layouts and density limits: `references/slide-design.md`.
3. **Set up the workspace.**

   ```sh
   mkdir -p my-deck && cd my-deck
   cp "${CLAUDE_SKILL_DIR}/assets/deck-template.html" deck.html   # paper form
   cp "${CLAUDE_SKILL_DIR}/assets/slide.css" .
   bash "${CLAUDE_SKILL_DIR}/scripts/fetch-dads-assets.sh" .
   bash "${CLAUDE_SKILL_DIR}/scripts/setup.sh"
   ```

   For the business form, copy `deck-template-business.html` to `deck.html` instead. Each template declares its form on `<body>`, and `lint` checks the deck against that form. Without arguments the fetch script takes the components the templates link. Name more components to add them.
4. **Build the slides.** Work from the template rather than inventing layout. Use the official `dads-*` components with their published markup for anything DADS defines, and this skill's `sld-*` classes only for slide geometry and the blocks DADS does not publish. Keep every slide inside the canvas and the safe area. The markup contract: `references/authoring-contract.md`.
5. **Check, then look.**

   ```sh
   .venv/bin/python "${CLAUDE_SKILL_DIR}/scripts/deck.py" lint deck.html
   .venv/bin/python "${CLAUDE_SKILL_DIR}/scripts/deck.py" preview deck.html -o preview
   ```

   Drive errors to zero and account for every warning. Then look at the preview images: a linter cannot tell that a slide is unreadable. Findings and options: `references/deck-checks.md`.
6. **Report** the form chosen and why; the governing message and the tree that supports it; the main-deck slide count and the parts the tracker groups it into; the lint findings and what was done about each; which official assets were fetched and at which commit; and what the reader needs to see the deck as intended - a current browser and, offline, the Noto Sans JP font. Apply the attribution rules of `references/asset-sourcing.md`.

## Inside the Bash sandbox

- `fetch-dads-assets.sh` clones the official repository and `setup.sh` installs Playwright and Chromium into a virtual environment in the deck's directory. Both need the hosts this skill declares. When the sandbox blocks a host, report the host and stop at that step; do not work around the sandbox. With assets and the environment already in place, `lint` and `preview` need no network apart from the web font.
- `deck.py` starts Chromium as a single process when it runs inside the sandbox on macOS, because the sandbox refuses the service registration that a multi-process start makes.
- The fetch script keeps its working copy under `$TMPDIR`.

## Guardrails

- **Never guess a classification.** Take the 機密性 level and the 公開範囲 from the author or the organisation's security policy; if neither is given, ask before building. Every slide, the cover and the appendix included, carries the same marking at its top right.
- **Never compress a part to reach the answer sooner.** In the paper form the summary already gives the answer on slide 2, so the premises, the method, and the discussion each take the slides their content needs; none of them shrinks to one line on another part's slide. The business form's one-slide introduction is not a compressed premise: choose that form only when the audience already shares the background, and when it does not, use the paper form rather than shrinking the premises.
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
| `assets/deck-template.html` | A working paper-form deck that covers every slide role and body pattern. Copy it; do not edit it in place |
| `assets/deck-template-business.html` | A working business-form deck on the same story: an introduction, the answer on slide 3, the points, a borrowed risk slide, and the next step. Copy it; do not edit it in place |
| `scripts/fetch-dads-assets.sh` | Step 3: resolves the official stylesheets into the deck workspace |
| `scripts/setup.sh` | Step 3: installs the checker's browser environment in the deck's directory |
| `scripts/deck.py`, `scripts/check_slides.js` | Step 5: `lint` and `preview` |
