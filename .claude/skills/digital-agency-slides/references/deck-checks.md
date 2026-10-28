# Checking and previewing a deck

Load this when running `lint` or `preview`, reading a finding, or deciding
what to do about one.

## How it works

1. Chromium loads the deck and lays it out. Nothing is inferred from the CSS —
   every position, size, colour and font is a measured value.
2. `check_slides.js` runs in the page and reads the laid-out document: the
   document as a whole, each slide's content, and the order of the slides'
   roles.
3. `deck.py` prints the findings, or writes one PNG per slide.

## Commands

```sh
deck.py lint    deck.html                    # findings; non-zero exit on errors
deck.py lint    deck.html --json             # slides and findings as JSON on stdout
deck.py preview deck.html -o preview         # one PNG per slide, plus the findings
```

| Option | Default | Use |
|---|---|---|
| `--selector` | `.sld-slide` | A project whose slides use different markup |
| `--max-slides` | 9 | Slides in the main deck, appendix excluded: k + 4 with k = 5 key-line points |
| `--safe-area` | 32 px | Tighter or looser edge band |
| `--min-font` / `--body-font` | 14 / 18 px | The legibility floor and the body-copy warning |
| `--secondary-selector` | footers, captions, shoulders, trackers, markings, chip and figure labels | What is exempt from the body-copy warning |
| `--max-list-items` | 5 | Items in any one list |
| `--max-slide-items` | 10 | List items on a slide, pooled |
| `--text-contrast` | 4.5 | Minimum ratio for text, at every size |
| `--nontext-contrast` | 3 | Minimum ratio for a border or rule |
| `--chromium PATH` | Playwright's own | A preinstalled browser (also `DECK_CHROMIUM`) |

## Findings

A finding on slide 0 is about the whole document.

### Structure — is the tree in order?

| Code | Level | Means |
|---|---|---|
| `deck-long` | warn | The main deck is longer than `--max-slides`. Put evidence on its point's slide and detail in the appendix |
| `late-answer` | warn | No slide has `data-layout="answer"`, or it comes after slide 3 |
| `appendix-order` | warn | A main slide follows an appendix slide |
| `tracker` | error | A tracker lists a different number of parts than the main deck has after the cover, or marks a part other than this slide's — it tells the audience they are somewhere they are not |
| `tracker-missing` | warn | Other main slides carry a tracker and this one does not. A deck with no trackers at all is not reported |

### Document — can assistive technology navigate it?

| Code | Level | Means |
|---|---|---|
| `no-lang` | error | `<html>` declares no `lang`, so a screen reader cannot choose a voice |
| `no-title` | error | `<title>` is empty |
| `h1-count` | error | The document has no `h1`, or more than one |
| `heading-skip` | error | A heading level is skipped, such as an `h4` after an `h2` |
| `no-heading` | error | A slide has no `h1` or `h2`, so it states no assertion |
| `no-alt` | error | An image with no `alt`, or an SVG with no accessible name that is not `aria-hidden` |
| `table-no-header` | error | A table with no `<th>`, so no cell is announced with its column or row |

### Classification — can every page be handled correctly?

| Code | Level | Means |
|---|---|---|
| `marking-missing` | error | A slide carries no classification marking; on slide 0, no slide in the deck does |
| `marking` | error | The marking differs from the first slide's, its `data-level` is not 1, 2 or 3, its text does not state that level, it has no 公開範囲, or it is not at the top right |

The checker checks the marking's form and consistency, not whether the level
is right for the content: that is the author's call under their
organisation's policy.

### Slide — does it fit and can it be read?

| Code | Level | Means |
|---|---|---|
| `off-slide` | error | Content extends past the slide edge and is cut off |
| `clipped` | error | Text does not fit its box and is clipped |
| `contrast` | error | Text below 4.5:1 against its composited background, at any size |
| `font-too-small` | error | Text below the 14 px floor, including text inside a figure |
| `size-mismatch` | error | A slide is not the same size as slide 1 |
| `no-slides` | error | The selector matched nothing |
| `safe-area` | warn | Content inside the edge band |
| `font-small` | warn | Body copy below the comfortable projected size |
| `nontext-contrast` | warn | A border or rule below 3:1 against its background |
| `contrast-unknown` | warn | Text on a gradient or image, or in a colour that did not resolve: contrast has no single answer |
| `dense` | warn | More list items than the per-list or per-slide threshold. The tracker is not counted: it states position, not content |

Errors make `lint` exit non-zero. Warnings do not, but each one should be a
decision: fix it, or say in the hand-off why it stays.

## What the checks do not cover

- **Whether the tree is sound.** The linter sees roles and counts, not
  meaning. It cannot tell that a point fails to support the governing message,
  that siblings overlap, or that a term went undefined. Check those against
  `references/slide-design.md`.
- **Whether a slide reads well.** Look at every preview image.
- **Content that slides under the footer.** A body that runs past the frame
  but not past the slide edge is neither clipped nor off the slide. The
  preview shows it.
- **Text in a pseudo-element.** Anything drawn by `::before` or `::after`
  has no element to measure. Keep text in the document; use pseudo-elements
  only for decoration.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Lines wrap differently on another machine | The viewer's browser lacks Noto Sans JP and used a fallback | Make the font reachable: online from Google Fonts as the template links it, or installed locally |
| Unstyled slides in the preview | `dads/` was not fetched, or the paths in `deck.html` do not match | Run `fetch-dads-assets.sh` in the deck folder |
| `heading-skip` on a card title | A block title was written as `h4` under the slide's `h2` | Make it an `h3` |
| `deck-long` on a deck with few points | Evidence was given slides of its own | Move it onto its point's slide, or to the appendix |
| Chromium will not launch | Playwright's browser build does not match | `--chromium PATH`, or re-run `scripts/setup.sh` |

## Dependencies

`scripts/setup.sh` installs Playwright into a project-local virtual
environment, and Chromium unless `PLAYWRIGHT_BROWSERS_PATH` already points at a
browser set. The version resolves at install time; pin it in the consuming
project's lockfile if it needs reproducible builds.
