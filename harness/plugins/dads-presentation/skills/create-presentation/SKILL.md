---
name: create-presentation
description: Write explanatory material as HTML built on the components of the Digital Agency Design System (DADS, デジタル庁デザインシステム), as slides (fixed 16:9, one per screen and per PDF page) or as a page that scrolls, and check the result in a browser. Use when asked for slides, a deck, a presentation, or an explanatory page in the DADS style, or to add to or fix material made this way. Do not use for PowerPoint or Keynote files, or for a web application's own interface.
---

# Create a presentation with the DADS components

The material is plain HTML that opens from the file system: no server and no build. The DADS components are cloned beside it and are never edited; this skill adds only what DADS does not provide.

## Before starting

Settle these with the person, in one message, when the request does not say:

- **Format**: slides, a page, or both. Slides suit a talk; a page suits material read alone.
- **Content**: the source to explain, the reader, and the one thing the reader should keep.
- **Language** of the material. Set `lang` on `<html>` to match.

Cloning DADS contacts github.com, and the templates load Noto Sans JP from Google Fonts as the DADS samples do. Say so before the first run in a project; to stay offline, remove the three font lines from `<head>`.

## Steps

1. **Place the base.** In the project root, create `presentation/` and copy into it `${CLAUDE_SKILL_DIR}/assets/base/` (as `presentation/base/`) and `${CLAUDE_SKILL_DIR}/assets/setup.sh`. If `presentation/base/` already exists, keep it unless the person asks for the newer base.
2. **Fetch DADS.** Run `bash presentation/setup.sh`. It clones the components at a pinned tag into `design-system-example-components-html/` in the project root. Add that directory to `.gitignore` if the project uses Git.
3. **Start from a template.** Copy `${CLAUDE_SKILL_DIR}/assets/templates/slides.html` or `page.html` to `presentation/<name>.html`. Each pattern in it is marked with a `<!-- Pattern: ... -->` comment. Keep the patterns the content needs and delete the rest.
4. **Write the content.** One claim per slide, stated in the slide's heading; the body supports it. Choose components with `references/components.md`.
5. **Check in a browser.** Run `node ${CLAUDE_SKILL_DIR}/scripts/check.cjs --screenshots <dir> presentation/<name>.html`, with `<dir>` outside the project. Fix every `FAIL`, then look at the screenshots: the check finds content that is cut off, not content that is ugly.
6. **Report** the files written, the result of the check, and what was not checked.

## Rules that keep the material working

- **Never edit a file under `design-system-example-components-html/`.** Add what is missing to `presentation/base/deck.css`, with DADS colour tokens (the custom properties in `global.css`).
- **Write every size in `rem`.** `slide.css` sets the root font size to the window width / 1280 x 24px, so a component appears at 1.5 times its web size and scales with the window. A size in `px` does not scale.
- **Link each DADS stylesheet the page uses**, after `global.css` and before `base/`. A component without its stylesheet is unstyled. The file is `src/components/<name>/<name>.css`.
- **On slides, use `data-size="28"` for headings, `data-size="dense"` for tables, and `data-size="small"` for step navigation.** At 1.5 times, the default sizes do not fit one slide.
- **Put nothing on a slide that needs a click to read.** Accordions and tabs lose their content in print; use them in the page format only.
- **Content past the edge of a slide is not shown** (`overflow: hidden`). When a slide is full, split it; do not shrink the text.
- **Take the markup of a DADS component from its sample**, `src/components/<name>/*.html` in the clone, not from memory. `component-manifest.json` lists every component with its files.

## Slide layouts

`<section class="slide">` is one slide. `data-layout` selects the kind.

| `data-layout` | Use |
|---|---|
| `cover` | The first slide: title and one line under it |
| `section` | Opens a chapter |
| `statement` | One sentence the audience should keep |
| (none) | A heading and a body in `<div class="slide__body">` |

The cover is white with the key colour as an accent only. Do not fill a slide with the key colour: it is tiring to look at on a screen.

## What `deck.css` adds

| Class | Use |
|---|---|
| `deck-columns` | Equal columns; `data-cols="3"` for three |
| `deck-panel` | A bordered box for one of several parallel items |
| `deck-code` | A code block, on `<pre>` |
| `deck-tree` | A tree diagram from a nested list; `data-orientation="vertical"` (root at the top) or `"horizontal"` (root at the left) |
| `deck-stack` | Vertical space between the children of a container |

Choose the horizontal tree when the leaves are many: a vertical tree uses its width up first.

## When the check cannot run

`check.cjs` needs Node.js and Playwright with a Chromium browser. Exit status 2 means it did not run. Do not install anything to make it run without asking; report that the material was not checked in a browser, and what the person can open to check it.
