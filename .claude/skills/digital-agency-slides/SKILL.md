---
name: digital-agency-slides
description: Build 16:9 presentation slides from the Digital Agency Design System's official HTML and CSS reference assets, and convert them into an editable PowerPoint file through the bundled deck tooling. Use for slide decks, briefing material, and presentation documents that must follow DADS and be delivered as .pptx. Do not use for web pages, application interfaces, or dashboards that stay in a browser, and do not use to edit an existing .pptx that was not authored in this deck format. Apply alongside every independently matching requirements, document-structure, implementation, or review operation; this capability owns the slide authoring surface and the HTML-to-PowerPoint conversion.
---

# Digital Agency Slides

Author a deck as one HTML file on a fixed 16:9 canvas, styled by the Digital
Agency's own stylesheets, and convert it to PowerPoint as native, editable
shapes. PowerPoint is the delivery format, so the authoring surface is shaped
by what PowerPoint can represent — not the other way round.

## The invariant everything rests on

A slide is **1280 x 720 CSS pixels**. At 96 px/in that is exactly 13.333 x 7.5
inches, which is PowerPoint's standard 16:9 slide. So:

```
1 CSS px = 0.75 pt = 9525 EMU        exactly, no rounding, no scaling
```

A 32 px heading becomes a 24 pt heading; an element 64 px from the left edge
lands 0.667 in from the left edge. Nothing in the pipeline rescales anything.
Break the canvas size and every guarantee below goes with it.

## Scope

- Presentation slides and their conversion to `.pptx`. Browser-resident pages,
  application UI, and interactive dashboards are out of scope.
- The deck's own content is the deliverable. Do not restructure the
  surrounding project or introduce a build system it does not already have.
- Resolve material ambiguity before building: who the audience is, what
  decision the deck asks for, the governing message, the slide budget, and how
  the file will be presented. Ask when two reasonable readings would produce
  different decks; otherwise proceed on a stated assumption.

## Load references progressively

| Read | When |
|---|---|
| `references/slide-design.md` | Planning the deck's argument, choosing a layout, setting type and colour |
| `references/authoring-contract.md` | Writing or editing slide HTML — the markup contract the converter reads |
| `references/pptx-conversion.md` | Running the conversion, reading its findings, or explaining a fidelity limit |
| `references/asset-sourcing.md` | Fetching or refreshing official assets, or writing attribution |

Never quote a DADS version, token name, component class, or package API from
memory. Read it from the fetched assets, the installed package, or the live
official source.

## Bundled material

| Path | What it is |
|---|---|
| `assets/slide.css` | This skill's own 16:9 layout layer, built only on DADS token custom properties. Not a DADS component library. |
| `assets/deck-template.html` | A working nine-slide deck covering every layout. Copy it; do not edit it in place. |
| `scripts/setup.sh` | Installs the Python dependencies and Chromium into a project-local virtual environment |
| `scripts/fetch-dads-assets.sh` | Resolves the official DADS stylesheets into a deck workspace at task time |
| `scripts/deck.py` | `lint`, `preview`, `pptx`, `ir` — the whole pipeline |
| `scripts/extract_slides.js` | Measures the laid-out deck in the browser and emits the conversion IR |

No official Digital Agency code is vendored here. It is fetched when a deck is
built, so a deck always uses the current upstream reference implementation.

## Workflow

### 1. Define the deck before opening an editor

Establish the audience, the decision or action being asked for, the single
governing message, the slide budget, and the delivery context (projected,
printed, read alone). Confirm that PowerPoint is genuinely required — if the
deck will only ever be read in a browser, the conversion constraints below buy
nothing.

### 2. Write the storyline, not the slides

Give every slide one assertion, written as a full sentence that could stand
alone. Order and group them so each section's slides together support that
section's claim, and the sections together support the deck's governing
message. A slide whose headline is a topic label ("現状について") has no
assertion yet. Details and the layout catalogue: `references/slide-design.md`.

### 3. Set up the workspace

```sh
mkdir -p my-deck && cd my-deck
cp "$CLAUDE_SKILL_DIR/assets/deck-template.html" deck.html
cp "$CLAUDE_SKILL_DIR/assets/slide.css" .
bash "$CLAUDE_SKILL_DIR/scripts/fetch-dads-assets.sh" . table list divider
bash "$CLAUDE_SKILL_DIR/scripts/setup.sh"
```

Add the official component stylesheets the deck actually uses; the fetch script
lists what is available upstream when a name does not resolve.

### 4. Build the slides

Work from the layout catalogue in the template rather than inventing layout.
Use official `dads-*` classes and the DADS type and colour tokens for anything
DADS already defines, and this skill's `sld-*` classes for slide geometry.
Keep every slide inside the canvas and the safe area. The markup contract —
including what converts natively, what is rasterized, and the `data-pptx`
overrides — is in `references/authoring-contract.md`.

### 5. Check before converting

```sh
.venv/bin/python "$CLAUDE_SKILL_DIR/scripts/deck.py" lint deck.html
.venv/bin/python "$CLAUDE_SKILL_DIR/scripts/deck.py" preview deck.html -o preview
```

`lint` reports clipped text, content off the slide or inside the safe-area
band, type below the legibility floor, insufficient contrast, missing text
alternatives, and decoration the converter cannot reach. Drive errors to zero
and account for every warning. Then **look at the preview images** — a linter
cannot tell you a slide is unreadable.

### 6. Convert and inspect the result

```sh
.venv/bin/python "$CLAUDE_SKILL_DIR/scripts/deck.py" pptx deck.html -o deck.pptx
```

The command refuses to convert a deck with errors unless `--allow-findings` is
given, and reports how many shapes were emitted natively versus rasterized.
Add `--wrap reflow` when the recipient will edit the file rather than only
present it: text then wraps inside its box instead of running off the slide. A
deck that is mostly rasterized has lost the point: find out why and fix the
markup. Open the `.pptx` and confirm text is selectable, the table is a real
table, and the speaker notes arrived. `references/pptx-conversion.md` covers
the mapping, the options, and the known limits.

### 7. Close out

Report: the governing message and how the deck supports it; lint findings and
what was done about each; the native-versus-rasterized shape count; which
official assets were fetched and at which commit; and anything a reader must
install — above all the deck's font — to see the file as intended. Apply the
attribution rules in `references/asset-sourcing.md`.

## Guardrails

- **Fonts decide fidelity.** Geometry is measured with the browser's font
  metrics; PowerPoint re-lays the same text with its own. Install the deck's
  font on the machine that opens the file, or remap it with `--font` at
  conversion time, and say which was done.
- **The converted file does not reflow.** Absolute geometry is what makes it
  faithful, and it is also why nothing moves down when something above it grows.
  Layout changes belong in the HTML, followed by another conversion — not in
  PowerPoint.
- **Never rasterize a whole slide** to dodge a conversion problem. A picture of
  a slide cannot be edited, searched, translated, or read aloud. Rasterize the
  smallest element that genuinely needs it, and give it a text alternative.
- **Decoration drawn in `::before` or `::after` does not convert.** Pseudo-
  elements have no DOM node and no measurable box. Use a real element.
- Never let colour, position, or a graphic alone carry meaning that the text
  does not also state.
- Never claim a deck is a Digital Agency product or is endorsed by the Digital
  Agency.
- Never invent a DADS token, component class, or version number. Label
  everything this skill adds as this skill's own, not as DADS.
- Do not copy the Digital Agency's illustrations, icons, or Figma data into a
  deck. They carry separate terms from the MIT-licensed code.
