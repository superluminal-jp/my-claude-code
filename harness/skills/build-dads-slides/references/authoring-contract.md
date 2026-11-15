# The deck markup contract

Load this when writing or editing slide HTML. The deck is a web document as
well as a set of slides, so this contract covers both what makes a slide lay
out correctly and what makes the document accessible.

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

Deliver the whole folder: `deck.html` loads `slide.css` and `dads/` by
relative path.

## The document

```html
<html lang="ja">
<head>
  <title>…the governing message…｜…organisation…</title>
  …dads/global.css, the component stylesheets, slide.css…
</head>
<body class="sld-deck" data-form="paper">
<main>
  <section class="sld-slide" data-layout="title" aria-labelledby="s1-title">
    <p class="sld-marking dads-u-dns-16N-130" data-level="2"><span class="sld-marking__level">機密性2情報</span><span class="sld-marking__scope">公開範囲：△△課のみ</span></p>
    <div class="sld-slide__frame">
      <hgroup class="dads-heading" data-size="45" data-rule="8">
        <p class="dads-heading__shoulder">…organisation…</p>
        <h1 class="dads-heading__heading" id="s1-title">…the governing message…</h1>
      </hgroup>
    </div>
    <footer class="sld-slide__footer dads-u-dns-14N-130">…</footer>
  </section>

  <section class="sld-slide" data-layout="point" aria-labelledby="s6-title">
    <p class="sld-marking dads-u-dns-16N-130" data-level="2">…the same marking…</p>
    <div class="sld-slide__frame">
      <hgroup class="dads-heading" data-size="32">
        <p class="dads-heading__shoulder">論点1</p>
        <h2 class="dads-heading__heading" id="s6-title">…one assertion…</h2>
      </hgroup>
      <ol class="sld-tracker dads-u-dns-16N-130" aria-label="資料の構成">
        <li>要旨</li><li>前提</li><li>方法</li><li aria-current="step">論点1</li>…<li>考察</li><li>結論</li>
      </ol>
      <div class="sld-slide__body">…the evidence…</div>
    </div>
    <footer class="sld-slide__footer dads-u-dns-14N-130">…source…<span>6 / 11</span></footer>
    <div class="sld-notes">…speaker notes…</div>
  </section>
</main>
</body>
</html>
```

- One `.sld-slide` per slide, in presentation order, inside one `<main>`.
  `aria-labelledby` on each section names it by its headline, so the slides
  are listed as regions in a screen reader's landmark list. Override the
  selector with `--selector` if a project uses different markup.
- `data-form` on `<body>` declares the deck's form: `paper` or `business`.
  The linter checks the deck against that form; a deck without it is checked
  as a paper deck, and any other value is reported as `form-unknown` and
  checked as a paper deck too.
- `data-layout` names the slide's part of the deck: `title` (the cover),
  `answer`, `premise`, `method`, `point`, `discussion`, `closing`, `appendix`.
  The same roles serve both forms under their own labels:

  | Role | Paper form | Business form |
  |---|---|---|
  | `answer` | Summary (要旨), slide 2 | Answer (結論), slide 2, or slide 3 after the introduction |
  | `premise` | Premises (前提), one or more slides after the summary | Introduction (導入), at most one slide, before the answer |
  | `method` | Method (方法), required | Method (方法), when borrowed |
  | `point` | Results (論点n), required | Points (論点n), required |
  | `discussion` | Discussion (考察), required | Risks (リスク), when borrowed |
  | `closing` | Conclusion (結論), required | Next step (次の一手), required |

  The linter reads the roles to check where the answer is for the deck's
  form, that `premise`, `method`, `point`, `discussion` and `closing` come in
  that order, that no part the form requires is missing, that the appendix
  comes last, and to group the main deck into the tracker's parts. A slide
  without `data-layout` counts as a main slide with the role `custom`, which
  the order checks pass over.
- `.sld-slide__frame` is the safe content area; `.sld-slide__footer` is
  positioned separately so it sits on the safe-area line at the foot of the
  slide, with the page number as `n / N` in the main deck and `付録 n` in the
  appendix.
- Every slide opens with the same `p.sld-marking`: `data-level` is the
  機密性 level (1, 2 or 3), `.sld-marking__level` states it as 機密性1情報,
  機密性2情報 or 機密性3情報, and
  `.sld-marking__scope` states the 公開範囲. It is the section's first child,
  so it is read first, and it is positioned at the top right of the slide,
  outside the frame. The linter checks that every slide carries it, that all
  of them are identical, and where it sits.
- `data-continues` makes a slide carry on the part of the slide before it, so
  it takes the same tracker part. On a `premise`, `method` or `discussion`
  slide it marks a further slide of that part, such as the terms. When a part
  spans several slides, each of their shoulder texts names the part and the
  slide's topic, as in `前提：背景と問い` and `前提：用語`. On a `point` slide it marks one support of
  that point, given its own slide because it is a claim with its own
  evidence; its shoulder text is `論点n-m`. The business form's introduction
  is one slide and never carries it: an introduction that needs a second
  slide belongs in a paper deck.
- Every main slide after the cover carries an `ol.sld-tracker` after its
  heading: one item per part of the main deck after the cover, in order, with
  `aria-current="step"` on this slide's item and no other. The cover and the
  appendix carry none. The linter checks the item count and the marked item
  against the slide's position.
- Speaker notes live in `.sld-notes`, next to the slide they belong to. They
  are never rendered — not on screen, not in print — so nothing a reader needs
  goes there.

### Headings

The design system's heading guidance decides the outline, and the linter
enforces it.

- **Exactly one `h1`**, on the cover. It states the deck's subject, which is
  the governing message, and `<title>` states the same subject followed by the
  organisation.
- **One `h2` per slide**: the slide's headline, in the heading component with
  its shoulder text. The shoulder names the slide's place in the deck, in the labels
  of its form (`要旨`, `前提`, `方法`, `論点2`, `考察`, `結論` in the paper form;
  `導入`, `結論`, `方法`, `論点2`, `リスク`, `次の一手` in the business form; `付録1` in
  either). It is a `<p>` inside the `<hgroup>`, never a
  heading itself.
- **An `h3` for a block title** inside a slide — a tree branch, a card, a step.
- **Never skip a level.** An `h4` straight after an `h2` is an error.

### Two class families, one namespace each

| Prefix | Owner | Rule |
|---|---|---|
| `dads-*` | Digital Agency | Use as published, with the published markup and `data-*` attributes. Never redefine one; never invent one. |
| `sld-*` | This skill | Slide geometry, and the slide blocks DADS does not publish. Not DADS, and never described as DADS. |

Everything `sld-*` paints is expressed in DADS token custom properties, so a
token update reaches the slides without editing `slide.css`.

## Official components used as published

Fetch the component's stylesheet and copy the markup from its official
example. `scripts/fetch-dads-assets.sh` without arguments fetches the set the
template uses.

| Need | Component | Markup |
|---|---|---|
| Any heading | Heading | `hgroup.dads-heading[data-size]` with `p.dads-heading__shoulder` and `h1`–`h3.dads-heading__heading`; a `div.dads-heading` when there is no shoulder. `data-rule` adds the key-colour rule: `8` on the cover, `4` on the answer slide, whose rule the tree hangs from |
| Parallel items | List | `ul.dads-list` (or `ol`) with `data-spacing` |
| A term and its explanation | Description list | `dl.dads-description-list` > `div.dads-description-list__item` > `dt` + `dd` |
| Values to compare or look up | Table | `div.dads-table` > `table.dads-table__table`, with `<th scope>` cells |
| A status stated in words | Chip label | `span.dads-chip-label[data-style][data-color]` |
| A cited source | Link | `a.dads-link` whose text names the target |

```html
<dl class="dads-description-list dads-u-std-18N-160">
  <div class="dads-description-list__item">
    <dt>転記</dt>
    <dd>紙の申請書に書かれた内容を、職員が基幹システムに手で入力し直すこと</dd>
  </div>
</dl>
```

Components built for a page rather than a slide — navigation, drawers, modals,
form controls, anything whose point is interaction — do not belong on a slide.

## This skill's slide blocks

The design system publishes no static, non-interactive panel for a slide: its
cards are linked examples, and its step navigation is a navigation control. So
these blocks are this skill's own, built on the tokens.

| Class | What it is |
|---|---|
| `sld-marking`, `sld-marking__level`, `sld-marking__scope` | The classification marking: 機密性 and 公開範囲 in a two-part box at the top right of every slide |
| `sld-tracker` | Where the slide sits in the deck. The design system's step navigation also marks a current step, but at about 90 px tall it does not fit on every slide; the tracker follows its `aria-current` convention in one line |
| `sld-tree`, `sld-tree__node` | The answer slide's key line: an `<ol>` whose items hang from the headline's rule |
| `sld-index` | A position number, as text inside the heading it numbers |
| `sld-card`, `sld-card__head` | A static panel; `data-tone="accent"` or `"sub"` |
| `sld-kpi`, `sld-kpi__value`, `sld-kpi__label` | One figure and what it measures |
| `sld-steps-axis`, `sld-steps`, `sld-steps__track`, `sld-steps__index` | A sequence on one shared axis |
| `sld-takeaway` | The band that states what the evidence means |
| `sld-figure`, `sld-figure__caption` | A figure and the caption that states its finding |
| `sld-cols[data-cols]`, `sld-stack`, `sld-grow`, `sld-push` | Layout within the body |
| `sld-num`, `sld-total`, `sld-fill-width` | Numeric columns, a total row, a full-width table |

The outer margin of every element on a slide is zeroed, components included:
on a slide the spacing between blocks is the layout's gap. A component's inner
spacing is left as published.

## What the linter cannot see

- **Anything scrolled out of view.** A slide is `overflow: hidden`; what
  overflows is clipped. The linter reports text clipped by its own box and
  content that crosses the slide's edge, but not a block that slides under the
  footer — look at the preview.
- **Interactive state.** Hover and focus have no meaning on a projected slide.
  Render the state you want to show. A link keeps the design system's focus
  style, because a reader of the HTML can still tab to it.

## Checklist before delivering

- [ ] Every slide carries the same classification marking, with the level and
      the 公開範囲 the author or the organisation's policy set.
- [ ] `<html lang>` and `<title>` are set; the `<title>` subject matches the `h1`.
- [ ] One `h1`, one `h2` per slide, no skipped level.
- [ ] `<body>` declares the form chosen for the audience, `paper` or
      `business`.
- [ ] The answer (`data-layout="answer"`) is slide 2 — or, in the business
      form, slide 3 after a one-slide introduction — and the parts run
      premise, method, point, discussion, closing; every continuation carries
      `data-continues` and follows the slide whose part it carries on.
- [ ] Every main slide after the cover has a tracker marking its own part, and
      a page number `n / N`.
- [ ] Every slide states one assertion in its `h2`.
- [ ] Nothing crosses the safe area; nothing is clipped.
- [ ] Every image has `alt`; every SVG has a `<title>`, `aria-label`, or
      `aria-hidden="true"`.
- [ ] Every table has `<th>` cells with `scope`.
- [ ] Every term a newcomer would not know is defined, without metaphor — on
      a premise slide in the paper form; in passing or in the appendix in the
      business form.
- [ ] In the paper form, the method slide states how the evidence was
      gathered and the discussion slide states where the conclusion stops
      holding; in the business form, a borrowed method or risk slide does.
- [ ] No meaning is carried by colour or position alone.
- [ ] Reading order matches document order.
