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
| Governing message | The cover's title, and the headline of the answer slide (要旨 in the paper form, 結論 in the business form) |
| Key-line point | One `point` slide each, and one branch of the answer slide's tree |
| Support that is itself a claim with its own evidence | A continuation slide (`data-continues`) after its point's slide, one per support |
| Evidence for a point | The body of that point's slide |
| Detail behind the evidence | The appendix, the footer's source line, or the speaker notes |
| What the audience needs around the tree — the introduction or the premises, the method, the discussion, the next step | Slides of their own, in the positions the deck's form sets; each is one node with its children, like any other slide |

A continuation slide is still one node with its children — the support as the
headline, its evidence in the body — so it is not a split. A slide that feels
crowded is not split into two: either its children are not one group — regroup them into at most
four — or some of them are detail, which moves down a level.

### Choose the form

Both forms build the same Minto pyramid: the governing message, the key line
and the evidence under it, the answer before its support, one node per slide,
and every headline an assertion. They differ in what the audience needs around
the tree before it can weigh the answer. Choose by the least-informed person
who must act on the deck, and declare the choice on `<body>` as `data-form`.

| | Paper form (`data-form="paper"`) | Business form (`data-form="business"`) |
|---|---|---|
| Choose it when | The audience is new to the subject, or must be able to check the evidence: 審議会資料, 調査報告, 評価報告, a deck read alone or kept as a record | The audience shares the background and must decide or act: 決裁, 経営会議, 定例報告, a deck presented in a short slot |
| Before the answer | Nothing: the summary is slide 2 | At most one introduction slide that reminds the audience of the situation, the complication and the question |
| After the answer | Premises, method, results, discussion, conclusion, each with the slides its content needs | The supporting points, then the next step; a method or discussion slide only when borrowed |
| Parts `lint` requires | `premise`, `method`, `point`, `discussion`, `closing` | `point`, `closing` |
| Shoulder and tracker | 要旨, 前提, 方法, 論点n, 考察, 結論 | 導入, 結論, 方法 if borrowed, 論点n, リスク if borrowed, 次の一手 |

When the choice is unclear, choose the paper form: an audience given premises
it already shares skims them, but one denied the premises it needs cannot
check the answer. A deck that declares no form is checked as a paper deck.

結論 names a different slide in each form: the conclusion at the end of a
paper deck (`closing`), and the answer near the start of a business deck
(`answer`). Within one deck it always means one of them.

### The paper form: the parts of a research paper, answer first

The paper form follows the order of a research paper's parts and, as a paper's
abstract does, gives the answer first: summary, premises, method, results,
discussion, conclusion. Each part has its own role (`data-layout`) and takes
the slides its content needs.

| Paper part | Role (`data-layout`) | Shoulder and tracker | Slides | What it carries | Test |
|---|---|---|---|---|---|
| Title | `title` | none | 1 | The governing message as the title | A reader who sees only this slide knows the answer |
| Summary | `answer` | 要旨 | 1, always slide 2 | The governing message, the key line drawn as a tree with one line of evidence per branch, and the ask | A reader who stops here has the answer, its reasons and what is asked of them, without having read the premises |
| Premises | `premise` | 前提 | As many as the content needs | The situation the audience already accepts, what has gone wrong, the question this raises, and the terms | Every fact on them is undisputed; every term the deck relies on is defined |
| Method | `method` | 方法 | As many as the content needs, usually 1 | The sources, the period, the procedure and the assumptions behind the evidence — or that the answer rests on reasoning alone | The audience can judge how far to trust every figure that follows |
| Results | `point` | `論点n`; `論点n-m` when continued | One per key-line point, plus one per continued support | One key-line point and its evidence | The body proves the headline without help from another slide |
| Discussion | `discussion` | 考察 | As many as the content needs, usually 1 | What the results mean, where the conclusion stops holding, and the alternative explanations not ruled out | The audience knows under what condition the answer would change |
| Conclusion | `closing` | 結論 | 1 | The decision asked for, the actions, the owners and the dates | Who does what by when, without repeating the summary |
| Appendix | `appendix` | `付録n` | Any | Detail a reader may look up | Nothing on it is needed to follow the main deck |

A part that spans several slides keeps one entry in the tracker, and each of
its slides' shoulder names the part and the slide's topic, as in
`前提：背景と問い` and `前提：用語`; a continued point keeps `論点n-m`.

**The answer comes first; its support comes in full.** The summary on slide 2
gives the audience the answer to weigh everything after it against: an
audience that learns on slide 9 what is being asked of them spent eight slides
not evaluating it. Because the answer is already given, no later part is
shortened to reach it sooner. The premises take as many slides as a newcomer
needs, and the method and the discussion each take at least one slide of their
own, not one line on another part's slide. An answer given without its premises, its
method or its limits is an assertion the audience cannot check.

### Write the summary so it stands alone

The summary comes before the premises, as a paper's abstract comes before its
introduction, so it must be read without them.

- The headline is the governing message. The tree's branches are the key-line
  points, numbered as their results slides will be, each with one line of the
  evidence that proves it.
- Write it in words a newcomer already knows. A term the premises will define
  appears in plain words or with its explanation in passing, such as
  案A（段階的オンライン化）.
- Name the question it answers in passing — in the headline or a branch —
  when the answer alone does not reveal it. The premises state the question
  in full after the summary; the audience should not meet the answer before
  it knows what the answer replies to.
- State the ask, with its deadline, at its foot.
- Show no figure the results slides do not show, and none that means
  something different there.

### Set the premises for a newcomer

The premise slides are where an audience new to the subject gets what the
answer depends on. Write them for the least-informed person who must act on
the deck.

- State only the premises the answer depends on: the situation, the change or
  problem, and the scope. Nothing on them is an argument yet.
- State the question the deck answers as soon as the problem is laid out, and
  define the terms after it, so the audience holds the question while the
  terms, the method and the results lead to its answer.
- Give them the slides they need. Each premise slide is one node with its
  children, like any other slide; a common split is one slide for the
  situation, the problem and the question, and one for the terms.
  Never fold them onto one slide to reach the answer sooner — the answer is
  already on slide 2.
- Define every term the deck uses that a newcomer would not know, in plain
  words, by what the thing is and what it does here. Use the description list,
  which is the design system's component for a term paired with its
  explanation.
- Never explain by metaphor or analogy — a comparison with something else
  carries only some of the subject's properties, and the audience infers the
  rest wrongly. Explain the thing itself: its definition, its parts, and a
  concrete instance of it. An instance of the subject is an example, not a
  comparison, and is welcome.

### State the method

The method slide tells the audience how far to trust the results before they
see them.

- Name each source of evidence, the period it covers, and how it was
  measured, counted or estimated.
- State the assumptions the figures rest on, such as a volume held level or a
  rate carried forward.
- Say which figures are measured and which are estimated.
- When the answer rests on reasoning alone, with no evidence gathered, say so
  here and name the premises the reasoning starts from. The audience must see
  it on the slide, not only in the hand-off.
- Pair each kind of figure the deck shows — 作業時間, 費用, 削減効果 — with
  where it comes from and how it was obtained in a description list, and give
  the assumptions an item of their own; use a table when several sources share
  the same columns.

### Discuss before concluding

The discussion slide comes after the results and before the conclusion, as in
a paper, so the decision is asked for with its limits in view.

- State what the results mean together, which is more than any one of them
  says.
- State where the conclusion stops holding: the condition under which the
  answer would change, and how that condition will be watched.
- State the alternative explanations the evidence does not rule out.
- Give each of the three its own block. A limit left only in the speaker
  notes is a limit the decision-maker never sees.
- Draw no conclusion the results slides do not support. A claim that needs
  evidence of its own is a result, not a discussion.

### Conclude with what follows

The conclusion is what the audience does next, not a repeat of the summary.
The summary's ask names the decision; the conclusion makes it executable: the
decision with its deadline, each action with its owner and date, and what the
decision costs or what not deciding costs.

### The business form: introduction, answer, points, next step

The business form is the order Minto gives for a presentation: a short
introduction that tells the audience what they already know, then the answer,
then the points that support it, then the next step.

| Part | Role (`data-layout`) | Shoulder and tracker | Slides | What it carries | Test |
|---|---|---|---|---|---|
| Title | `title` | none | 1 | The governing message as the title | A reader who sees only this slide knows the answer |
| Introduction | `premise` | 導入 | 0 or 1, slide 2 | The situation the audience knows, the complication that changed it, and the question it raises | Every line reminds; nothing on it is news to this audience |
| Answer | `answer` | 結論 | 1, slide 2 or 3 | The governing message, the key line drawn as a tree with one line of evidence per branch, and the ask | A reader who stops here has the answer, its reasons and what is asked of them |
| Points | `point` | `論点n`; `論点n-m` when continued | One per key-line point, plus one per continued support | One key-line point and its evidence | The body proves the headline without help from another slide |
| Next step | `closing` | 次の一手 | 1 | The decision asked for, the actions, the owners and the dates | Who does what by when |
| Appendix | `appendix` | `付録n` | Any | Background the introduction could not hold, terms, and detail a reader may look up | Nothing on it is needed to follow the main deck |

Write the introduction as a reminder, in Minto's three steps:

- **Situation**: what the audience already accepts as true, stated so that
  nobody disputes it.
- **Complication**: what changed, or went wrong, in that situation.
- **Question**: the question the complication raises, which the answer slide
  then answers.

The introduction holds one slide because it informs nobody. If the audience
needs to learn the background before it can follow the answer, it does not
share the background: put the detail in the appendix, or use the paper form.
Leave the introduction out when the audience arrives already asking the
question. A term the audience may not know is defined in passing on the slide
that uses it, or in the appendix.

### Blend the forms

The forms are two layouts of one pyramid, so a deck can take what it needs
from the other form without changing its tree.

- A business deck borrows a paper part when its audience needs it: a method
  slide (`method`, 方法) when the figures will be challenged, and a discussion
  slide (`discussion`, headed リスク) when the answer depends on a condition
  that may not hold. It may borrow both. A borrowed part sits where the paper
  form puts it — the method before the points, the discussion after them — and
  `lint` checks that order in either form.
- A borrowed risk slide may carry only where the answer stops holding and the
  explanations not ruled out: in the business form, what the results mean is
  the answer slide's job.
- A business deck borrows no premises. If its audience needs the background
  explained — more than the one introduction slide can remind them of — the
  audience does not share it, and the deck is a paper deck: change its form
  rather than stretch the introduction. `lint` reports a premise slide after
  the answer of a business deck.
- A paper deck takes nothing away: when its audience shares the background,
  its premises are short, but they stay after the summary and the method and
  the discussion keep their slides. An audience that shares every premise is
  the business form's audience.

### Slide count and place, in either form

**Slide count follows the tree.** The main deck is the cover and the parts its
form lays out, with one slide per key-line point plus one per continued
support — however many that is. Do not pad a thin argument to fill a slot, and
do not crowd two nodes onto one slide to save a page. If the deck is too long
for the occasion, cut a branch or move detail to the appendix; `lint
--max-slides N` checks a limit the occasion sets. Omit a part the form
requires only when it has nothing to say to this audience — the conclusion or
the next step when the deck asks for nothing — and say why in the hand-off,
since `lint` reports the missing part. A paper deck whose premises the audience
already shares does not drop them: it is a business deck.

Because the count is free, a reader must never lose their place. There is no
agenda slide and no section divider: the answer slide's tree is the map, every
main slide's tracker marks its part, and the shoulder text names it, in the
labels of the deck's form — `論点2` on the point's slide, `論点2-1` on its
first continuation. A slide that carries on the part of the slide before it —
a further premise, method or discussion slide, or a support of a point —
carries `data-continues`, so its tracker marks the same part.

Any paragraph on a slide opens with its claim in the first sentence; the
sentences after it support that claim.

A single key-line point means the governing message and the point say the
same thing: make the point's own supports the key line. More than five points
means the key line is at the wrong level: regroup the points under fewer,
broader ones.

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
| Tracker (`sld-tracker`) | Top right, on the shoulder text's line | The parts of the main deck after the cover, in the labels of the deck's form — 要旨, 前提, 方法, 論点1 …, 考察, 結論 in the paper form; 導入, 結論, 方法, 論点1 …, リスク, 次の一手 in the business form, 方法 and リスク only when borrowed — with this slide's part in bold, underlined in the key colour, and marked `aria-current="step"` |
| Shoulder text | Above the headline | This slide's part, in words |
| Page number | Footer, right | `n / N` in the main deck; `付録 n` in the appendix |

- The tracker's labels match the shoulder texts and the answer slide's branch
  numbers, so the audience can match the map to the slide in front of them.
- It lists the main deck only; the cover and the appendix carry none.
- The current part is never marked by colour alone.
- It takes no height from the body. If a shoulder text is long enough to
  reach it, shorten the shoulder text.
- `lint` checks every tracker against the slide's real part. Parts, not
  slides, are listed: premises over two slides are one entry, and so is a
  point continued over three.

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
independently. `assets/deck-template.html` (the paper form) implements all of
them, and `assets/deck-template-business.html` shows the business form's
introduction, answer and borrowed risk slide; copy the one that matches rather
than building layout from scratch.

| Role | Use it for | Keep to |
|---|---|---|
| `title` | The deck's cover | Governing message as the title, not the project name |
| `answer` | The answer: the summary (要旨) on slide 2 in the paper form; the answer (結論) on slide 2 or 3 in the business form | Two to four branches in `sld-tree`, plus the ask; in the paper form, readable without the premises |
| `premise` | Shared facts, terms and the question in the paper form; the one-slide introduction (導入) in the business form | Facts the audience accepts; every term defined; in the business form, nothing the audience does not already know |
| `premise`, `method` or `discussion` with `data-continues` | A further slide of the same part, such as the terms | Same tracker part as the slide before it; shoulder names the part and the slide's topic |
| `method` | How the evidence was gathered | Sources, period, procedure and assumptions; which figures are measured and which estimated |
| `point` | One key-line point and its evidence | One body pattern, or two that prove different parts of the point |
| `point` with `data-continues` | One support of the point before it, when that support is a claim with its own evidence | Same tracker part as its point; shoulder `論点n-m` |
| `discussion` | What the results mean and where they stop holding; in the business form, the borrowed risk slide (リスク) | Meaning, limits, and alternative explanations, each in its own block |
| `closing` | The conclusion (結論), or the business form's next step (次の一手): the decision, the actions, the owners, the dates | Who does what by when |
| `appendix` | Detail a reader may look up | After the conclusion; outside the tracker and the `n / N` count |

| Body pattern | Use it when | Keep to |
|---|---|---|
| List (`dads-list`) | Parallel items of the same kind | 5 items, one line each |
| Definitions (`dads-description-list`) | Terms paired with explanations | The terms the deck relies on |
| Figures (`sld-kpi`) | Two to four numbers carry the point | Value and what it measures, together |
| Comparison (`sld-card`) | Options judged on the same criteria | Same criteria, same order, both sides |
| Steps (`sld-steps`) | A sequence in time or dependency | 3–5 steps; more is a table |
| Table (`dads-table`) | Values must be looked up or compared precisely | 5 rows and 5 columns |
| Figure (`sld-figure`) | A relationship a picture shows better than prose | One figure, with a caption that states the finding |
| Caveat (`dads-notification-banner`) | A risk or condition the point depends on | One banner, close and action buttons removed; its heading states the risk in words |
| Quotation (`dads-blockquote`) | A passage the argument rests on — a policy, a statute, a minute | Verbatim, with its source; never a paraphrase inside it |

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
