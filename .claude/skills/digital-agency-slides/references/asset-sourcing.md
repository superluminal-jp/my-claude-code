# Sourcing official DADS assets, and attribution

Load this when fetching or refreshing the Digital Agency's assets, or when
writing the source notice for a published deck.

## Nothing official is vendored here

This skill ships no Digital Agency code. `scripts/fetch-dads-assets.sh`
resolves it when a deck is built, so a deck is always built against the current
upstream reference implementation and an update is a re-run rather than a
patch. The script records the resolved commit in the deck's `dads/SOURCE.md`.

Do not write a DADS version number or a retrieval date into this skill's
documents. Read the version from the assets or the live site at the time it
matters.

## Which source wins

In descending order of authority:

1. **The live official site and repositories.** Always authoritative.
2. **The assets fetched into the deck** (`dads/`), for what this deck actually
   renders against, and the packages installed in the surrounding project for
   what it builds against.
3. Anything else, including this document, which is operational guidance rather
   than a copy of the design system.

If a fetched asset and the live site disagree, follow the live source, re-fetch,
and say what changed.

## Where each thing comes from

| Asset | Source | Form |
|---|---|---|
| Design tokens and the `dads-u-*` type utilities | `digital-go-jp/design-system-example-components-html`, `src/global.css` | Plain CSS, no build step — what the fetch script takes |
| Component CSS and reference markup | the same repository, `src/components/<name>/` | Plain HTML and CSS per component |
| Raw design tokens | `@digital-go-jp/design-tokens` on npm | CSS custom properties and a JS module |
| Tailwind theme | `@digital-go-jp/tailwind-theme-plugin` on npm | A Tailwind plugin, for projects on Tailwind |
| React components | `digital-go-jp/design-system-example-components` | React source in the repository |

Resolve what is actually available and at what version at task time rather than
trusting this table's shape:

```sh
npm view @digital-go-jp/design-tokens version
npm view @digital-go-jp/tailwind-theme-plugin version
```

The HTML reference is the right substrate for a deck: it needs no build step,
the browser can load it directly, and its `dads-*` classes are stable selectors
for the converter. Use the React or Tailwind route only inside a project that
already builds with them, render the deck to static HTML, and point the
converter at that.

## Restrict research to the official sources

The Digital Agency design system site and the `digital-go-jp` GitHub
organization. If nothing current is reachable, use what is already fetched and
state that freshness was not verified.

## Licensing

The Digital Agency splits the design system into parts with different terms.
The full notice is at <https://design.digital.go.jp/dads/introduction/notices/>;
read it rather than relying on this summary when the answer matters.

### Code — the repositories and npm packages

MIT licensed, and written to be adapted. A deck built by adapting them needs no
visible source notice. Publishing them unmodified does:

> 出典：デジタル庁デザインシステムウェブサイト https://design.digital.go.jp/dads/ およびデジタル庁GitHub https://github.com/digital-go-jp

A deck that links `global.css` and component stylesheets as fetched is using
them unmodified. `scripts/fetch-dads-assets.sh` writes this notice into the
deck's `dads/SOURCE.md` so it travels with the files.

### Documentation and specifications — the design system site

Reuse requires attribution:

> 出典：デジタル庁デザインシステムウェブサイト https://design.digital.go.jp/dads/

If the content is edited or adapted, say so separately and in addition:

> デジタル庁デザインシステムウェブサイト https://design.digital.go.jp/dads/ のコンテンツを加工して作成

### Illustrations, icons and Figma data

Governed by their own terms, not by the above. Do not copy them into a deck
merely because a component example displays one. The bundled fonts, polyfills
and search libraries the site redistributes likewise carry their own licences.

## Standing limits

- Never present a deck as a Digital Agency product or as endorsed by the
  Digital Agency, however closely it follows the design system.
- State plainly what was reused and what was changed.
- When uncertain about terms, link the live usage notice rather than
  paraphrasing it.
