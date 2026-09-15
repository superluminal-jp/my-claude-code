# Designing the deck

Load this when planning a deck's argument, choosing a layout, or setting type,
colour and density.

## The deck is an argument, not a container

A deck exists to move an audience to a decision. Design it top down.

1. **Governing message.** One sentence that is the answer. Everything else
   exists to support it. If you cannot write it, the deck is not ready.
2. **Sections.** Three to five groups that together support the governing
   message, each covering a different part of it and no two covering the same
   part.
3. **Slides.** One assertion per slide, supporting its section's claim.

A common and reliable arc for a decision deck: the situation the audience
already accepts, the complication that makes it a problem, the question that
raises, and the answer — then the evidence, the plan, and the ask.

### Every headline is an assertion

The headline is the slide. A reader who skims only the headlines must get the
whole argument.

| Instead of | Write |
|---|---|
| 現状について | 処理の遅延は受付件数ではなく二重入力に起因する |
| 費用比較 | 全面刷新より段階的なオンライン化が費用対効果で優る |
| まとめ | 案Aの着手について本日ご承認いただきたい |

Write it as a complete sentence. If the slide's content does not prove the
headline, one of the two is wrong.

### One slide, one job

If a slide needs two headlines, it is two slides. If it needs none, cut it.
Section dividers are the exception: one per top-level group, never more.

## Geometry

| | Value | Why |
|---|---|---|
| Canvas | 1280 x 720 px | Exactly 13.333 x 7.5 in — PowerPoint's 16:9 slide |
| Side margin | 64 px | 5% of the width; the frame every non-cover layout sits in |
| Top / bottom margin | 48 / 40 px | Leaves the footer band clear of the content |
| Safe area | 32 px minimum | Projector overscan, video framing and PowerPoint themes eat the outer band |
| Column gap | 24 px | Wide enough that columns read as separate |

Content never crosses the safe area. The linter reports anything that does.

## The layout catalogue

`assets/deck-template.html` implements all of these. Copy the one that matches
the slide's job rather than building layout from scratch.

| Layout | Use it when | Keep to |
|---|---|---|
| `title` | The deck's cover | Governing message as the title, not the project name |
| `section` | Opening a top-level group | One per group |
| `bullets` | Listing parallel items of the same kind | 5 items, one line each |
| `kpi` | Two to four numbers carry the point | Value and what it measures, together |
| `compare` | Two options judged on the same criteria | Same criteria, same order, both sides |
| `steps` | A sequence in time or dependency | 3–5 steps; more is a table |
| `table` | Values must be looked up or compared precisely | 5 rows and 5 columns |
| `figure` | A relationship a picture shows better than prose | One figure, with a caption that states the finding |
| `closing` | The decision, the actions, the owners, the dates | Who does what by when |

Anything that does not fit is usually two slides.

## Type

Slide type comes from the DADS type scale. These are the classes the official
stylesheet defines; do not invent sizes between them.

| Role | Class | px | pt in PowerPoint |
|---|---|---|---|
| Deck title | `dads-u-dsp-48B-140` | 48 | 36 |
| Section divider | `dads-u-dsp-48B-140` | 48 | 36 |
| Slide message | `dads-u-std-32B-150` | 32 | 24 |
| Sub-head, card title | `dads-u-std-22B-150` / `dads-u-std-24B-150` | 22 / 24 | 16.5 / 18 |
| Body | `dads-u-std-20N-150` | 20 | 15 |
| Dense body in a column | `dads-u-std-18N-160` | 18 | 13.5 |
| Label, caption, eyebrow | `dads-u-dns-16N-130` | 16 | 12 |
| Footer, page number | `dads-u-dns-14N-130` | 14 | 10.5 |

Rules the linter enforces:

- Nothing below 14 px. The DADS foundation disallows it, and it is unreadable
  when projected.
- Body copy at 18 px or larger. The 14–16 px dense scale is for secondary
  content only — footers, captions, eyebrows, tile labels — and the linter
  exempts exactly those.
- A headline that has to shrink to fit means the headline is too long.

## Colour

Use the DADS token custom properties the official stylesheet defines. Never a
raw hex value, and never a colour invented for this deck.

- `--color-key-900` is the primary action and emphasis colour; the `key` ramp
  runs 50 to 1200.
- `--color-neutral-solid-gray-900` for body text, `-700` for secondary text.
- Semantic colours — `--color-semantic-success-*`, `-error-*`, `-warning-*` —
  mean what they say. Do not use them decoratively.
- The off-scale greys `420` and `536` exist because they are the contrast
  thresholds. Do not round them to 400 or 500.

Text must clear 4.5:1 against its background, or 3:1 at 24 px and above (or
18.66 px bold). The linter computes this against the effective background and
fails the deck below the threshold.

Never let colour be the only carrier of meaning. A red tile and a green tile
must also say which is which.

## Density

| Limit | Value |
|---|---|
| List items on one slide | 7, and fewer is better |
| Words per bullet | Enough for one line at the slide's body size |
| Columns in a row | 4 |
| Table cells visible at once | About 25 |

Blocks size to their content and stack from the top of the body; leftover space
stays empty. Three items in a row should read as three items, not as three
panels stretched to fill the slide. Use `sld-grow` only where filling the
remaining height is the point, and `sld-push` to send a closing band to the
foot of the body.

## Accessibility

A deck that will be distributed is a document, not just a projection.

- **Reading order is DOM order.** The converter emits shapes in document order,
  and PowerPoint reads them in that order. Write the markup in the order a
  person should hear it.
- **Every non-text element needs a text alternative**: `alt` on an image, a
  `<title>` or `aria-label` on an SVG. The converter copies it into the
  PowerPoint shape description; the linter fails an image without one.
- **Headings are headings.** Use `h1`/`h2` for the governing message so the
  structure survives into the outline and into assistive technology.
- **State the finding in the caption.** "図1：現行の申請処理フロー" names the
  figure; "受付と審査の間で同じ内容を二度入力している" states what it shows.
  Write both.
- Speaker notes carry what you would say, not a second copy of the slide.
