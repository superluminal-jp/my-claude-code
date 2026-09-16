# The deck markup contract

Load this when writing or editing slide HTML. The converter reads the laid-out
document, so this contract is what makes a slide convertible.

## Workspace layout

```
my-deck/
├── deck.html              the deck — one file, one section per slide
├── slide.css              copied from assets/, this skill's layout layer
├── dads/                  fetched official assets, never hand-edited
│   ├── global.css           tokens + the dads-u-* type utilities
│   ├── components/<name>/<name>.css
│   └── SOURCE.md            upstream URL, commit, licence
├── media/                 images the deck references
└── preview/               generated PNGs (regenerated, not edited)
```

## The document

```html
<body class="sld-deck">
  <section class="sld-slide" data-layout="kpi">
    <div class="sld-slide__frame">
      <header class="sld-slide__header">
        <p class="sld-eyebrow" data-role="meta"><span>現状</span><span class="sld-rule"></span></p>
        <h2 class="sld-message dads-u-std-32B-150">…one assertion…</h2>
      </header>
      <div class="sld-slide__body">…</div>
    </div>
    <footer class="sld-slide__footer dads-u-dns-14N-130">…</footer>
    <div class="sld-notes" data-pptx="notes">…speaker notes…</div>
  </section>
</body>
```

- One `.sld-slide` per slide, in presentation order. Override the selector with
  `--selector` if a project uses different markup.
- `data-layout` names the layout for the catalogue and for the converted
  deck's per-slide record. It does not change conversion.
- `.sld-slide__frame` is the safe content area; `.sld-slide__footer` is
  positioned separately so it sits at the foot of the slide.
- Speaker notes live in `[data-pptx="notes"]` or `.sld-notes` (which is
  `display: none`), or in a `data-notes` attribute on the slide.

### Two class families, one namespace each

| Prefix | Owner | Rule |
|---|---|---|
| `dads-*` | Digital Agency | Use as published. Never redefine one; never invent one. |
| `sld-*` | This skill | Slide geometry and slide-only blocks. Not DADS, and never described as DADS. |

Everything `sld-*` paints is expressed in DADS token custom properties, so a
token update reaches the slides without editing `slide.css`.

## How the converter classifies an element

The walk is automatic; `data-pptx` only overrides it.

| The element is | Becomes |
|---|---|
| `<img>` | A picture, positioned at its measured rectangle |
| `<table>` | A native PowerPoint table — real rows, cells, fills and borders |
| `<svg>`, `<canvas>`, `<video>` | A picture, captured at 2x from the rendered element |
| A block whose subtree is only text | One text box, one paragraph per text-leaf block — including bare text sitting beside block children |
| An absolutely positioned or floated child | Its own shape at its own measured rectangle; out-of-flow boxes are never folded into a parent's paragraph flow |
| A block with a background, border or radius | A rectangle, emitted before its contents |
| Anything else | Recursed into |

### Grouping, and why a flex gap splits a box

Consecutive text blocks in normal flow become **one** text box, with margins
and padding carried over as paragraph spacing — so a `<ul>` is one editable
list, and a stack of `<p>` is one editable paragraph run.

A flex or grid container with more than one child is **not** grouped. Its
`gap` is not a margin, and PowerPoint has no way to reproduce it inside a
single text box. Each child is emitted at its own measured rectangle instead,
which is exact. This is why the layouts use flex and grid for structure and
normal flow for prose.

### `data-pptx` overrides

| Value | Effect |
|---|---|
| `raster` | Screenshot this element and place it as one picture. The escape hatch for charts, SVG diagrams, and anything too intricate to map. |
| `text` | Force one text box, even if the walk would have recursed |
| `image` / `table` / `shape` | Force that treatment |
| `notes` | Speaker notes for the slide |
| `ignore` | Drop entirely — decoration that carries no meaning |

Reach for `raster` deliberately and at the smallest scope that works. A
rasterized element cannot be edited, searched, translated or restyled in
PowerPoint, and it needs its own text alternative.

## What does not convert

- **`::before` and `::after`.** They have no DOM node and no measurable box, so
  the walk cannot see them. `slide.css` uses a real `.sld-rule` element rather
  than an `::after` rule for exactly this reason. The linter warns when a
  pseudo-element paints something.
- **CSS gradients, filters, blend modes, transforms and animation.** Put the
  result in a rasterized element if it matters.
- **Anything scrolled out of view.** A slide is `overflow: hidden`; what
  overflows is clipped in the browser and lost in the file. The linter reports
  it as an error.
- **Interactive behaviour.** Hover, focus, and JavaScript state have no meaning
  in a slide. Render the state you want to show.
- **A `transform` or `zoom` on a slide.** It scales the measured geometry but
  not the type size, which silently breaks the px-to-point mapping the whole
  pipeline rests on. The linter reports it as an error; author at 1:1 and scale
  the browser window instead.

## Working with official DADS components

Fetch the component's stylesheet, copy the markup from the official example,
and keep its classes and `data-*` attributes intact:

```html
<link rel="stylesheet" href="dads/components/table/table.css">

<div class="dads-table sld-fill-width">
  <table class="dads-table__table" data-border="hidden" data-cell-border>
    <thead><tr><th class="dads-table__col-header" scope="col">工程</th>…</tr></thead>
    <tbody><tr><td>受付・転記</td>…</tr></tbody>
  </table>
</div>
```

Components built for a page rather than a slide — navigation, drawers, modals,
form controls, anything whose point is interaction — do not belong on a slide.

Some static components are re-implemented as `sld-*` rather than used as
published, and the reason is always slide geometry rather than taste: a card
here has to be a fixed-height grid cell, a step has to sit on a shared axis, a
callout has to anchor to the foot of the body. Where a DADS component does fit
unchanged — the table, lists, dividers, the type and colour foundations — use
it. If you re-implement one, say so in the deck and keep the tokens.

## Text that must not re-wrap

The converter records how many lines the browser laid out. A text box whose
paragraphs all fit on one line is emitted with wrapping switched off, so
PowerPoint cannot break a label in two under slightly different font metrics.
A wrapping box gets a few pixels of slack on the side its text is not anchored
to, for the same reason. Neither is a substitute for having the deck's font
installed where the file is opened.

## Checklist before converting

- [ ] Every slide states one assertion in an `h1`/`h2` or `.sld-message`.
- [ ] Nothing crosses the safe area; nothing is clipped.
- [ ] Every image has `alt`; every SVG has a `<title>` or `aria-label`. A
      decorative image takes `alt=""`, which marks it decorative in the file
      rather than letting its filename be read aloud.
- [ ] Every table has `<th>` cells, so the converted table can carry a header
      row. Without it a screen reader reads a value and never names its column.
- [ ] No meaning is carried by colour or position alone.
- [ ] Decorative flourishes are real elements, not pseudo-elements.
- [ ] `data-pptx="raster"` appears only where it is genuinely needed.
- [ ] Reading order matches document order.
