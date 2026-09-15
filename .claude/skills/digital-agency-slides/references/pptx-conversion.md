# HTML to PowerPoint

Load this when running the conversion, reading its findings, or explaining why
something did not survive it.

## How it works

1. Chromium loads the deck and lays it out. Nothing is inferred from the CSS —
   every position, size, colour and font is a measured value.
2. `extract_slides.js` walks each slide's DOM and emits an intermediate
   representation: shapes in document order, each with a rectangle in CSS
   pixels, plus the findings the linter reports.
3. `deck.py` builds the `.pptx` with python-pptx, converting pixels to EMU with
   the exact factor below, and rewrites the deck theme from the DADS tokens.

```
1 CSS px = 0.75 pt = 9525 EMU
1280 x 720 px = 12192000 x 6858000 EMU = 13.333 x 7.5 in
```

Both conversions are exact integers. A slide authored at the canvas size needs
no scaling at any stage, which is why the pipeline has none.

## What each thing becomes

| In the deck | In the .pptx |
|---|---|
| The slide's governing message | The slide's **title placeholder** — the shape is promoted, not duplicated, so PowerPoint's outline, the reading-order pane and every screen reader can see it |
| Text block | A text box with per-run size, weight, colour, underline, strikethrough, font and letter spacing, and per-paragraph alignment, line spacing and space before/after |
| `<ul>` / `<ol>` | One text box with real PowerPoint bullets or auto-numbering, hanging indent taken from the measured marker strip |
| Background, border, radius | A rectangle or rounded rectangle, marked decorative; a one-sided border becomes its own filled bar. A translucent CSS colour keeps its transparency |
| `<table>` | A native table with `firstRow` set when the markup declares `<th>`: merged cells, column widths, row heights, per-cell fill, borders and padding |
| `<img>` | An embedded picture with the `alt` text as its description. `alt=""` marks it decorative rather than letting the filename be announced |
| `data-pptx="raster"` | A picture captured at 2x from the rendered element, with its text alternative as the description |
| Speaker notes | The notes pane |
| The document's `lang` | Every run's `lang`, plus the master, layouts and presentation defaults, so text typed later is tagged too |
| The deck's design tokens | The theme's colour and font scheme, named for what it is — a theme derived from the tokens, not the design system itself |

Nothing about the palette is written into the converter. Every theme colour is
read from the deck at conversion time; if a token does not resolve, the theme is
left at PowerPoint's default and the run says which token was missing.

Shapes are emitted in document order, which is the order PowerPoint uses for
the accessibility reading order and for tab order.

## Commands

```sh
deck.py lint    deck.html                    # findings only, non-zero exit on errors
deck.py preview deck.html -o preview         # one PNG per slide
deck.py pptx    deck.html -o deck.pptx       # convert
deck.py ir      deck.html -o ir.json         # dump the IR, for debugging a bad conversion
```

| Option | Default | Use |
|---|---|---|
| `--selector` | `.sld-slide, [data-slide]` | A project whose slides use different markup |
| `--font FROM=TO` | none | Remap a font for the file; a bare name remaps every font |
| `--safe-area` | 32 px | Tighter or looser edge band |
| `--min-font` / `--body-font` | 14 / 18 px | The legibility floor and the body-copy warning |
| `--secondary-selector` | footers, captions, labels | What is exempt from the body-copy warning |
| `--max-list-items` | 5 | Items in any one list |
| `--max-slide-items` | 10 | List items on a slide, pooled |
| `--text-contrast` | 4.5 | Minimum ratio for text, at every size |
| `--nontext-contrast` | 3 | Minimum ratio for a border or rule |
| `--slack` | 6 px | Extra width for wrapping text boxes, to absorb font-metric differences |
| `--wrap` | `preserve` | `preserve` keeps the browser's line breaking; `reflow` lets every box wrap. See below |
| `--chromium PATH` | Playwright's own | A preinstalled browser (also `DECK_CHROMIUM`) |
| `--allow-findings` | off | Convert despite errors. Say so in the hand-off when used. |

## Findings

| Code | Level | Means |
|---|---|---|
| `off-slide` | error | Content extends past the slide edge and will be cut off |
| `clipped` | error | Text does not fit its box; the overflow is lost |
| `contrast` | error | Below 4.5:1, or 3:1 for large text |
| `font-too-small` | error | Below the 14 px floor |
| `no-alt` | error | An image with no `alt`, or rasterized content with no text alternative |
| `no-message` | error | The slide states no governing message, so the converted slide has no title |
| `table-no-header` | error | A table with no `<th>`, so no header row can be marked |
| `color-unreadable` | error | A text colour the browser reported in a form the converter cannot resolve |
| `slide-transformed` | error | A `transform` or `zoom` scales geometry but not type, voiding the px/pt invariant |
| `size-mismatch` | error | A slide is not the same size as slide 1 |
| `no-slides` | error | The selector matched nothing |
| `safe-area` | warn | Content inside the edge band |
| `font-small` | warn | Body copy below the comfortable projected size |
| `nontext-contrast` | warn | A border or rule below 3:1 against its background |
| `contrast-unknown` | warn | Text on a gradient or image, where contrast has no single answer |
| `pseudo-decoration` | warn | `::before`/`::after` paints something the converter cannot reach |
| `dense` | warn | More list items than the per-list or per-slide threshold |
| `dropped` | warn | An element produced no convertible content |

Text is checked everywhere it appears — in text blocks, in table cells, and
inside a rasterized SVG, which no other check can see once it becomes a
picture.

Errors block conversion. Warnings do not, but each one should be a decision.

## How editable the delivered file is

Every element is a real PowerPoint object: text boxes you can retype, autoshapes
you can restyle, a native table, and a theme whose colour picker offers the
deck's own palette. What does *not* survive is the layout relationship. The
converter reads a laid-out document and writes absolute geometry, so nothing in
the file knows that the takeaway band sits below the list — each is a shape at
its own measured position.

That makes three kinds of edit behave differently:

| Edit | What happens |
|---|---|
| Retyping a value in place | Fine. The box does not grow, so a much longer value eventually overflows it |
| Adding a list item | Fine while there is room. The band below does not move down |
| Lengthening a line | Under `--wrap preserve`, the text runs off the slide instead of wrapping |

The default exists for delivery. `preserve` keeps the line breaks the browser
chose, so PowerPoint's own font metrics cannot re-wrap a label and shift a
layout that was correct in the preview. The cost is that a line edited to be
longer has nowhere to go.

**Convert with `--wrap reflow` when somebody will edit the file.** Every box
then wraps, so edited text stays inside it. The trade goes the other way: a
label that fitted on one line in the browser may wrap in PowerPoint if the deck
font is missing.

Neither mode makes the deck reflow as a whole. If the content changes enough to
move things, change it in the HTML and convert again — that is where the layout
actually lives.

## Fidelity: what is exact, what is close, what differs

**Exact.** Position and size of every shape, every fill and border colour, font
size in points, line spacing, table geometry, slide dimensions.

**Close.** Where a line breaks inside a wrapping text box, and therefore how
tall a paragraph is. The browser and PowerPoint resolve the same font family
slightly differently. Single-line text is protected by switching wrapping off;
wrapping text gets a few pixels of slack.

**Different, by design.**

- **Fonts must exist on both machines.** The deck is measured against the font
  the browser resolved. If PowerPoint substitutes a different one, widths move.
  Install the deck's font where the file will be opened, or pass `--font` to
  remap it to one that is there.
- **PowerPoint adds spacing between Japanese and Latin runs.** Renderers apply
  their own East Asian typography rules, so `12.4日` can show a little more air
  than the browser gave it. This is the viewer's typography, not a conversion
  error.
- **Rasterized elements are pictures.** They do not reflow, restyle, or respond
  to a theme change.
- **Nothing is animated.** Transitions and builds are a PowerPoint authoring
  step after conversion, if they are wanted at all.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| A label wrapped in PowerPoint but not in the browser | Font substitution | Install the deck font, or `--font "<installed font>"` |
| Many shapes reported as rasterized | SVG or canvas used where markup would do | Rebuild the block as elements; keep `raster` for real diagrams |
| A rule, badge or flourish is missing | Drawn in `::before`/`::after` | Make it a real element; check the `pseudo-decoration` warnings |
| Text is cut off in the file | It was already clipped in the browser | Fix the `clipped` error; do not enlarge the box in PowerPoint |
| Bullets sit on top of their text | The list's left padding was reset away | Leave a list's `padding-left` alone — it is the marker strip the converter measures |
| A pale tile came through solid | Fixed: a translucent fill now converts to real DrawingML transparency | Re-run the conversion |
| Centred text sits too far right | Fixed: the paragraph margin is the box offset, not the glyph offset | Re-run the conversion |
| A table came through as a picture | It is inside a `data-pptx="raster"` subtree | Move the override down to the element that needs it |
| Chromium will not launch | Playwright's browser build does not match | `--chromium PATH`, or re-run `scripts/setup.sh` |

Use `deck.py ir` when a shape lands somewhere unexpected: the IR shows exactly
what was measured, which separates a layout problem from a conversion problem.

## Dependencies

`scripts/setup.sh` installs python-pptx and Playwright into a project-local
virtual environment, and Chromium unless `PLAYWRIGHT_BROWSERS_PATH` already
points at a browser set. Versions resolve at install time; pin them in the
consuming project's lockfile if it needs reproducible builds.
