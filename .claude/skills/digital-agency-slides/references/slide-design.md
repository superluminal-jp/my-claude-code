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

### Write the question each slide answers

The pyramid holds when each slide answers exactly the question its parent
raises. Write that question down before writing the slide, and keep it in the
slide's HTML comment so a later reader can check the chain.

```
Governing message: 案Aに着手すべきである
  → raises: なぜ今なのか / 他の案ではだめなのか / いくらかかるのか
     Section 1 answers なぜ今なのか
       → raises: 遅延の原因は何か
          Slide 4 answers 遅延は二重入力に起因する
```

A slide whose question nothing above it raises is orphaned: cut it, or send it
to an appendix. A question no slide answers is a hole the audience will find.

### One grouping basis per group

| Basis | Use for | Order |
|---|---|---|
| Time | A process, a plan, a history | Earliest first |
| Structure | Parts of a whole — organisations, systems, budgets | However the whole is normally divided |
| Degree | Reasons, risks, options | Most decision-relevant first |

Mixing bases inside one group is why a deck reads as a list of topics rather
than an argument. Within a group, siblings are either like-kind evidence for a
generalisation (inductive) or premises leading to a conclusion (deductive) —
not both.

### SCQA, as slides

| Part | The slide | Test |
|---|---|---|
| Situation | A fact the audience already accepts | If they could dispute it, it is not the situation |
| Complication | What changed, or what is now wrong | This is the slide that earns their attention |
| Question | Usually not a slide — what the complication forces | Write it down anyway; it decides every later slide |
| Answer | The governing message, on the cover and again at the close | An action or a judgement, never a topic |

For a decision deck, state the answer **and the ask** by the second slide. An
audience that learns on slide 9 what is being asked of them spent eight slides
not evaluating it.

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

### Every number appears once, meaning one thing

Before converting, list every figure in the deck with the slide it appears on
and what it measures. A figure that means the current cost on one slide and the
saving on another is the fastest way to lose an audience that is checking the
arithmetic. Any quantity in the governing message must be computable from a
figure the deck actually shows.

### One slide, one job

If a slide needs two headlines, it is two slides. If it needs none, cut it.
Section dividers are the exception: one per top-level group, never more.

## Projected, distributed, or both

The delivery context is established before the deck is written because the three
modes need different slides. Decide once, say which you chose, and build to it.

| Mode | The slide carries | The notes carry |
|---|---|---|
| Projected, with a presenter | The assertion and the evidence that proves it, in as few words as will do it | Everything the presenter says: reasoning, caveats, the numbers behind a figure |
| Read alone (配布資料・審議会資料) | The assertion, the evidence, and the sentence or two a reader needs to interpret the evidence with nobody there to explain it | Nothing a reader needs — notes are a separate print and are often not circulated at all |
| Both | Build it for reading alone, and rely on the presenter not to read the slide aloud | The presenter's own additions only |

Whatever the decision-maker must act on — the ask, the deadline, the owner, the
cost, the consequence of not deciding — belongs on a slide, never only in the
notes.

For a projected deck, do not write on-slide prose that repeats what the
presenter will say: spoken narration plus duplicate on-screen text teaches less
than narration with the evidence alone (Mayer's redundancy principle). The
effect has limits worth knowing — it does not apply when there is no narration,
which is exactly the read-alone case, and it weakens for an audience reading in
a second language or meeting unfamiliar terms.

## What the slide leaves out

Every element competes for the same working memory, and material that does not
prove the headline measurably lowers what an audience takes away (Mayer's
coherence principle). Cutting is design work, not tidying. On each slide:

1. Cover the headline. Can you still tell what the slide claims? If not, the
   body is doing the headline's job.
2. Delete each block in turn. If the headline is still proven without it, it
   does not belong on the slide.
3. Send what you removed somewhere, never nowhere: the speaker notes (what the
   presenter says), an `appendix` slide after the closing (detail a reader will
   look up), or the footer source line (provenance).

If nothing can be deleted and the slide is still crowded, it is making two
claims. Split it.

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
| Deck title, section divider | `dads-u-dsp-48B-140` | 48 | 36 |
| KPI value | `dads-u-dsp-48B-140` | 48 | 36 |
| Slide message | `dads-u-std-32B-150` | 32 | 24 |
| Figure headline in a card | `dads-u-std-28B-150` | 28 | 21 |
| Card title, sub-head | `dads-u-std-24B-150` / `dads-u-std-22B-150` | 24 / 22 | 18 / 16.5 |
| Lead sentence, agenda item | `dads-u-std-24N-150` / `dads-u-std-22N-150` | 24 / 22 | 18 / 16.5 |
| Body | `dads-u-std-20N-150` | 20 | 15 |
| Body in a column | `dads-u-std-18N-160` | 18 | 13.5 |
| Tile label, eyebrow, caption | `dads-u-dns-16N-130` / `dads-u-dns-16B-130` | 16 | 12 |
| Footer, page number | `dads-u-dns-14N-130` | 14 | 10.5 |

The display scale is documented for headline copy that needs visual impact. A
KPI value is exactly that, so it is used there and nowhere else — not for a
sub-head that merely wants to be large.

The pt column holds because one CSS px is 1/96 in at a 16 px root font size,
which is what the official stylesheet's `calc(N / 16 * 1rem)` sizes assume. The
converter measures the laid-out result rather than trusting the arithmetic, so a
project that changes the root size stays correct — but its slides stop matching
this table.

Rules the linter enforces:

- Nothing below 14 px. The foundation disallows it outright, and it is
  unreadable when projected.
- 14 px is the foundation's own exception: footers and anything genuinely
  constrained. 16 px and up is the baseline for body and UI text.
- On a slide, body copy at 18 px or larger. 16 px is legal but small at
  projection distance, so the linter warns — except on the secondary content
  the foundation's exception covers: footers, captions, eyebrows, tile labels.
- Cap the measure at about 42 zenkaku. `slide.css` does this with
  `max-width: 42em`, which holds at any size because 1em is one zenkaku.
- A headline that has to shrink to fit means the headline is too long.

## Colour

Use the DADS token custom properties the official stylesheet defines. Never a
raw hex value, and never a colour invented for this deck.

- `--color-key-900` is the primary action and emphasis colour; the `key` ramp
  runs 50 to 1200.
- `--color-neutral-solid-gray-900` for body text, `-700` for secondary text.
- Semantic colours are `--color-semantic-success-1|2`, `-error-1|2`,
  `-warning-yellow-1|2` and `-warning-orange-1|2`. They are pairs, not a 50–1200
  ramp, and they mean what they say — do not use them decoratively.
- The off-scale greys `420` and `536` exist because they are the contrast
  thresholds. Do not round them to 400 or 500.

**All text clears 4.5:1 against its background, whatever its size.** WCAG
relaxes this to 3:1 for large text; the Digital Agency's colour foundation
explicitly removes that relaxation and holds every size to 4.5:1. The linter
implements the design system's rule, not the looser one, and computes it
against the composited background.

Borders, rules and anything else that separates content need **3:1** (WCAG
1.4.11). This is why the greys stop where they do: `solid-gray-420` is the
lightest grey that reaches 3:1 on white, and `solid-gray-536` the lightest that
reaches 4.5:1. Anything lighter is below a threshold the system chose
deliberately. The linter warns on a border that misses it.

Never let colour be the only carrier of meaning. A red tile and a green tile
must also say which is which.

**Icons are never used alone.** The icon foundation requires every icon to be
paired with a label, and the icon itself to clear 4.5:1. A label-paired icon
takes `alt=""` and no `aria-label`, so the label is announced once rather than
twice.

## Density

| Limit | Value |
|---|---|
| Ideas the reader must hold **at once** to get the point | 4. This is the binding limit: working memory holds about four chunks (Cowan, 2001), not the seven usually quoted from Miller — whose result measures recall of unrelated items and does not describe a slide the reader can look back at |
| Items in any one list | 5. The linter warns above this |
| List items on a slide, across every list | 10. Two groups of five compare; one list of ten does not |
| Words per item | Enough for one line at the slide's body size |
| Columns in a row | 4 |
| Table cells visible at once | About 25 |

A count is a proxy. What actually costs the reader is element interactivity —
how many items must be held simultaneously to see the relationship (Sweller).
Seven rows looked up one at a time are fine; five bullets that must be
cross-compared are not.

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
- **Headings are headings.** The governing message in an `h1`/`h2` (or
  `.sld-message`) becomes the converted slide's title placeholder, which is what
  puts it in PowerPoint's outline, in the reading-order pane and in front of a
  screen reader. A slide without one converts untitled, so the linter treats it
  as an error.
- **Crop a figure's `viewBox` to its artwork.** Empty space inside the viewBox
  becomes empty space on the slide and strands the caption away from the thing
  it captions.
- **State the finding in the caption.** "図1：現行の申請処理フロー" names the
  figure; "受付と審査の間で同じ内容を二度入力している" states what it shows.
  Write both.
- **Label in place, not in a legend.** Put each label on or beside the thing it
  names. A legend makes the reader hold a colour-to-meaning mapping in working
  memory while scanning the figure — the split-attention effect — and it makes
  colour the sole carrier of meaning, which the contrast rules above forbid.
