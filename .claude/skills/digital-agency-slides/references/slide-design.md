# Designing the deck

Load this when planning a deck's tree, choosing a layout, or setting type,
colour and density.

## The deck is a tree, not a stack of slides

A deck exists to move an audience to a decision or an understanding. Design it
top down, as one tree.

1. **Governing message.** One sentence that is the answer. Everything else
   exists to support it. If you cannot write it, the deck is not ready.
2. **Key line.** Two to four points (five at most) that together answer the
   question the governing message raises, each covering a different part of it
   and no two covering the same part.
3. **Evidence.** Under each point, the facts, figures, comparisons or steps
   that prove it.

### Write the question each slide answers

The tree holds when each node answers exactly the question its parent raises.
Write that question down before writing the slides, and keep the tree in an
HTML comment at the top of the deck so a later reader can check the chain.

```
Governing message: 案Aに着手すべきである
  → raises: なぜ案Aなのか
     Point 1 answers 遅延の原因は二重入力にある      → evidence: 3 figures, 1 flow figure
     Point 2 answers 案Aは案Bより安く早い            → evidence: the two options compared
     Point 3 answers 初年度に効果の8割が出る          → evidence: the steps and their savings
```

A point whose question nothing above it raises is orphaned: cut it, or send it
to the appendix. A question no point answers is a hole the audience will find.

### One slide is one node

A slide carries one node of the tree **and its direct children**: the
headline states the node, the body states its children. Evidence is never
given a slide of its own; it sits on the slide of the point it proves.

| Tree level | Where it goes |
|---|---|
| Governing message | The cover's title, and the answer slide's headline |
| Key-line point | One `point` slide each, and one branch of the answer slide's tree |
| Evidence for a point | The body of that point's slide |
| Detail behind the evidence | The appendix, the footer's source line, or the speaker notes |

This is what keeps the deck short. A slide that feels crowded is not split
into two: either its children are not one group — regroup them into at most
four — or some of them are detail, which moves down a level.

### The order: premises, then the answer, then the tree

| # | Role (`data-layout`) | The slide | Test |
|---|---|---|---|
| 1 | `title` | The governing message as the title | A reader who sees only this slide knows the answer |
| 2 | `premise` | What the audience must share before the answer makes sense: the situation they already accept, what has gone wrong, the terms they need, how the evidence was gathered, and the question this raises | Every fact on it is undisputed; every term the deck relies on is defined |
| 3 | `answer` | The governing message, the key line drawn as a tree, and the ask | A reader who stops here has the answer, its reasons, and what is asked of them |
| 4 … k+3 | `point` | One key-line point and its evidence | The body proves the headline without help from another slide |
| k+4 | `closing` | The decision, the actions, the owners, the dates, and where the conclusion stops holding | Who does what by when, and under what condition the answer would change |
| after | `appendix` | Detail a reader may look up | Nothing on it is needed to follow the main deck |

The answer comes by slide 3. An audience that learns on slide 9 what is being
asked of them spent eight slides not evaluating it.

**The slide budget is k + 4** for k key-line points, appendix excluded: at
most eight slides with four points, nine with five. Omit the premise slide only
when the audience already shares its facts and terms, and the closing slide
only when the deck asks for nothing. There is no agenda slide and no section
divider: the answer slide's tree is the map, and each point slide's shoulder
text (`論点2`) names its branch.

### The parts of a research paper, on slides

The deck follows the order of a research paper's parts while keeping the
answer first, and fits them into the same slide budget: the method and the
discussion each take one line on an existing slide, not a slide of their own.

| Paper part | Slide | What it carries |
|---|---|---|
| Summary | `title`, then `answer` | The governing message; the answer slide adds the key line and the ask |
| Introduction | `premise` | The background, the problem, the terms, the question |
| Method | `premise`, one line | How the evidence was gathered — sources, period, procedure — so the audience can judge how far to trust it |
| Results | `point` | One key-line point and its evidence per slide |
| Discussion | `closing`, one line | The conclusion's limits: where it stops holding, and what would change it |
| Conclusion | `closing` | The decision asked for, and who does what by when |
| Appendix | `appendix` | Detail a reader may look up |

Any paragraph on a slide opens with its claim in the first sentence; the
sentences after it support that claim.

A single key-line point is not a tree. Put its evidence directly on the answer
slide. More than five points means the key line is at the wrong level:
regroup the points under fewer, broader ones.

### Set the premises for a newcomer

The premise slide is where an audience new to the subject gets what the
answer depends on. Write it for the least-informed person who must act on the
deck.

- State only the premises the answer depends on: the situation, the change or
  problem, and the scope. Nothing on it is an argument yet.
- Define every term the deck uses that a newcomer would not know, in plain
  words, by what the thing is and what it does here. Use the description list,
  which is the design system's component for a term paired with its
  explanation.
- Never explain by metaphor or analogy — a comparison with something else
  carries only some of the subject's properties, and the audience infers the
  rest wrongly. Explain the thing itself: its definition, its parts, and a
  concrete instance of it. An instance of the subject is an example, not a
  comparison, and is welcome.
- State in one line how the evidence was gathered: its sources, the period
  it covers, and how it was measured or estimated.
- End with the question the deck answers, so the answer slide reads as its
  reply.

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

### Every headline is an assertion

The headline is the slide. A reader who skims only the headlines must get the
whole argument.

| Instead of | Write |
|---|---|
| 現状について | 処理の遅延は受付件数ではなく二重入力に起因する |
| 費用比較 | 全面刷新より段階的なオンライン化が費用対効果で優る |
| まとめ | 案Aの着手について本日ご承認いただきたい |

Write it as a complete sentence that fits on one line at the headline size. If
the slide's content does not prove the headline, one of the two is wrong.

### Every number means one thing

Before delivering, list every figure in the deck with the slide it appears on
and what it measures. A figure may recur — on the cover, on the answer slide,
on the point that proves it — but it must measure the same thing each time. A
figure that means the current cost on one slide and the saving on another is
the fastest way to lose an audience that is checking the arithmetic. Any
quantity in the governing message must be computable from a figure the deck
actually shows.

## Making the structure visible

A structure helps only an audience that can see it. Cues that show how the
material is organised — headings, an outline, a marker of the current part —
help an audience take it in (Mayer's signaling principle). A deck gives these
cues on every slide.

### Show where the slide sits

Every main slide after the cover answers "where are we?" in three ways that
agree with each other.

| Cue | Where | What it says |
|---|---|---|
| Tracker (`sld-tracker`) | Top right, on the shoulder text's line | The parts of the main deck after the cover — 前提, 結論, 論点1 … 依頼 — with this slide's part in bold, underlined in the key colour, and marked `aria-current="step"` |
| Shoulder text | Above the headline | This slide's part, in words |
| Page number | Footer, right | `n / N` in the main deck; `付録 n` in the appendix |

- The tracker's labels match the shoulder texts and the answer slide's branch
  numbers, so the audience can match the map to the slide in front of them.
- It lists the main deck only; the cover and the appendix carry none.
- The current part is never marked by colour alone.
- It takes no height from the body. If a shoulder text is long enough to
  reach it, shorten the shoulder text.
- `lint` checks every tracker against the slide's real position.

### Make the tree visible

Each level of the tree gets its own visual treatment, so the hierarchy can be
seen before a word is read.

| Tree level | Element | Visual treatment |
|---|---|---|
| The slide's node | The headline (`h2`) | 32 px bold, full width, above the body |
| Its children | Block titles (`h3`) in tiles, cards, steps or tree branches | 20 px bold; each child in its own box of equal weight, side by side or in one list, in the order the answer slide named them |
| Evidence for a child | Text inside that child's box | 18–20 px regular, inside the box it supports — never between boxes |
| What the evidence means | The takeaway band | Key-colour rule on the left, at the foot of the body |
| Detail | The footer source line, or the appendix | 14–16 px, outside the body |

- Space follows relation: elements that belong together sit closer than
  elements that do not, as the design system's spacing foundation sets out.
  Inside a box 8 px, between boxes 24 px, and more than that between the body
  and the footer.
- Numbers carry across slides: branch 2 on the answer slide is 論点2 in the
  tracker and in the shoulder text of its slide.
- One treatment means one level throughout the deck. A child's title is never
  bold on one slide and plain on another.

## The classification marking

Every slide carries a box at its top right stating how the information must
be handled, such as 「機密性2情報｜公開範囲：△△課のみ」: the classification
(機密性1情報, 機密性2情報 or 機密性3情報) and who may see it.

- **Every slide, the same marking.** The cover and the appendix included. A
  slide is printed, photographed and forwarded on its own; a page without the
  marking, or with a different one, can be handled wrongly.
- **The author decides the level, not the deck.** The levels come from the
  government's unified cybersecurity standard, but each organisation's
  security policy defines them and may prescribe its own wording. Take the
  level and the scope from the author or that policy; never guess them, and
  never copy a definition of the levels into the deck.
- **Stated in words.** The box says 機密性2情報 in text; colour never carries
  the level.
- **Outside the content.** It sits on the safe-area line above the frame, so
  it never shares space with the headline, the tracker or the body.

`lint` reports a slide without the marking, a marking that differs from the
first slide's, a level other than 1, 2 or 3, and a marking that is not at the
top right.

## Projected, distributed, or both

The delivery context is established before the deck is written because the
modes need different slides. Decide once, say which you chose, and build to it.

| Mode | The slide carries | The notes carry |
|---|---|---|
| Projected, with a presenter | The assertion and the evidence that proves it, in as few words as will do it | Everything the presenter says: reasoning, caveats, the numbers behind a figure |
| Read alone (配布資料・審議会資料) | The assertion, the evidence, and the sentence or two a reader needs to interpret the evidence with nobody there to explain it | Nothing a reader needs — notes are never rendered |
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
   presenter says), the appendix (detail a reader will look up), or the footer
   source line (provenance).

## Geometry

| | Value | Why |
|---|---|---|
| Canvas | 1280 x 720 px | 16:9; prints as one 1280 x 720 page |
| Side margin | 64 px | 5% of the width; the frame every slide sits in |
| Top / bottom margin | 80 / 80 px | Leaves the classification band and the footer band clear of the content |
| Safe area | 32 px | Projector overscan and video framing eat the outer band; the classification marking and the footer sit on its line |
| Column gap | 24 px | Wide enough that columns read as separate |

Content never crosses the safe area. The linter reports anything that does.

## The layout catalogue

A slide has a **role**, which is its place in the tree (`data-layout`), and a
**body pattern**, which is how its evidence is shown. Choose them
independently. `assets/deck-template.html` implements all of them; copy the
one that matches rather than building layout from scratch.

| Role | Use it for | Keep to |
|---|---|---|
| `title` | The deck's cover | Governing message as the title, not the project name |
| `premise` | Shared facts, terms and the question | Facts the audience accepts; every term defined |
| `answer` | The governing message and its key line | Two to four branches in `sld-tree`, plus the ask |
| `point` | One key-line point and its evidence | One body pattern, or two that prove different parts of the point |
| `closing` | The decision, the actions, the owners, the dates | Who does what by when |
| `appendix` | Detail a reader may look up | After the closing; not counted in the budget |

| Body pattern | Use it when | Keep to |
|---|---|---|
| List (`dads-list`) | Parallel items of the same kind | 5 items, one line each |
| Definitions (`dads-description-list`) | Terms paired with explanations | The terms the deck relies on |
| Figures (`sld-kpi`) | Two to four numbers carry the point | Value and what it measures, together |
| Comparison (`sld-card`) | Options judged on the same criteria | Same criteria, same order, both sides |
| Steps (`sld-steps`) | A sequence in time or dependency | 3–5 steps; more is a table |
| Table (`dads-table`) | Values must be looked up or compared precisely | 5 rows and 5 columns |
| Figure (`sld-figure`) | A relationship a picture shows better than prose | One figure, with a caption that states the finding |

## Type

Headings use the design system's heading component, which sets size, weight,
line height and the shoulder text together. Everything else uses the type
utilities the official stylesheet defines; do not invent sizes between them.

| Role | Markup | px |
|---|---|---|
| Deck title (cover, `h1`) | `dads-heading` with `data-size="45"` | 45, shoulder 22 |
| Slide headline (`h2`) | `dads-heading` with `data-size="32"` | 32, shoulder 18 |
| Block title — tree branch, card, step (`h3`) | `dads-heading` with `data-size="20"` | 20 |
| Figure value | `dads-u-dsp-48B-140` | 48 |
| Lead sentence | `dads-u-std-24N-150` | 24 |
| Body | `dads-u-std-20N-150` | 20 |
| Body in a column | `dads-u-std-18N-160` | 18 |
| Label, caption | `dads-u-dns-16N-130` / `dads-u-dns-16B-130` | 16 |
| Footer, page number | `dads-u-dns-14N-130` | 14 |

The heading size is chosen separately from the heading level: the design
system defines them independently and leaves the mapping to the style guide.
This table is that mapping for slides. The display scale is for copy that
needs visual impact; a figure value is exactly that, so it is used there and
nowhere else.

Rules the linter enforces:

- Nothing below 14 px. The foundation disallows it outright, and it is
  unreadable when projected.
- 14 px is the foundation's own exception: footers and anything genuinely
  constrained. 16 px and up is the baseline for body and UI text.
- On a slide, body copy at 18 px or larger. 16 px is legal but small at
  projection distance, so the linter warns — except on the secondary content
  the foundation's exception covers: footers, captions, shoulder text, chip
  labels, figure labels.
- Body text, lists and takeaway bands span the full width of their container,
  so their right edge lines up with the headline and the table. If a line runs
  long, shorten the sentence or split the content into columns rather than
  narrowing the text box.
- A headline that has to shrink to fit means the headline is too long.

## Colour

Use the DADS token custom properties the official stylesheet defines. Never a
raw hex value, and never a colour invented for this deck.

- `--color-key-900` is the primary action and emphasis colour; the `key` ramp
  runs 50 to 1200.
- `--color-neutral-solid-gray-900` for body text, `-700` for secondary text.
  The official heading sets its own text colour; leave it.
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
reaches 4.5:1. The linter warns on a border that misses it.

Never let colour be the only carrier of meaning. A recommended option says so
in words — a chip label reading 推奨 — not only by its tint.

**Icons are never used alone.** The icon foundation requires every icon to be
paired with a label, and the icon itself to clear 4.5:1. A label-paired icon
takes `alt=""` or `aria-hidden="true"`, so the label is announced once rather
than twice.

## Density

| Limit | Value |
|---|---|
| Ideas the reader must hold **at once** to get the point | 4. This is the binding limit: working memory holds about four chunks (Cowan, 2001), not the seven usually quoted from Miller — whose result measures recall of unrelated items and does not describe a slide the reader can look back at. It is also why a key line and a slide's children stop at four |
| Items in any one list | 5. The linter warns above this |
| List items on a slide, across every list | 10. Two groups of five compare; one list of ten does not |
| Words per item | Enough for one line at the slide's body size |
| Columns in a row | 4 |
| Table cells visible at once | About 25 |

A count is a proxy. What actually costs the reader is element interactivity —
how many items must be held simultaneously to see the relationship (Sweller).
Seven rows looked up one at a time are fine; five bullets that must be
cross-compared are not.

Blocks size to their content and stack from the top of the body; leftover
space stays empty. Three items in a row should read as three items, not as
three panels stretched to fill the slide. Use `sld-grow` only where filling the
remaining height is the point, and `sld-push` to send a closing band to the
foot of the body.

## Accessibility

The deck is a web document, so the design system's web accessibility guidance
applies to it as a whole, not only to each slide's appearance.

- **Reading order is document order.** Write the markup in the order a person
  should hear it; never reorder visually what the source orders differently.
- **One `h1`, no skipped levels.** The cover's `h1` states the deck's subject,
  as `<title>` does. Each slide's headline is an `h2`, and a block title inside
  a slide is an `h3`. A level is never skipped: screen-reader users move by
  heading level, and a gap makes them think they missed a section.
- **Every non-text element needs a text alternative**: `alt` on an image, a
  `<title>` or `aria-label` on an SVG. A decorative image takes `alt=""`; a
  decorative SVG takes `aria-hidden="true"`.
- **A list is a list, a term and its explanation are a description list.** Do
  not imitate either with headings and paragraphs.
- **Crop a figure's `viewBox` to its artwork.** Empty space inside the viewBox
  becomes empty space on the slide and strands the caption away from the thing
  it captions.
- **State the finding in the caption.** "図1：現行の申請処理の流れ" names the
  figure; "受付と審査の間で同じ内容を二度入力している" states what it shows.
  Write both.
- **Label in place, not in a legend.** Put each label on or beside the thing it
  names. A legend makes the reader hold a colour-to-meaning mapping in working
  memory while scanning the figure — the split-attention effect — and it makes
  colour the sole carrier of meaning, which the contrast rules above forbid.
- **Link text names its target.** A source cited as a link uses the design
  system's link component, and its text says what the reader will get.
