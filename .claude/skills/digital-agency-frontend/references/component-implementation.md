# DADS component implementation (React + Tailwind)

Load this when writing, porting, or reviewing DADS component code.

The rules below are the Digital Agency's own conventions, taken from
`AGENTS.md` and `.agents/skills/component-rules/SKILL.md` in
[design-system-example-components-react](https://github.com/digital-go-jp/design-system-example-components-react).
Follow them when working inside that repo. Outside it, apply them as the default
and record any deliberate departure.

## Upstream is a package, not a snippet dump

The official React components are published to npm. Prefer depending on the
package over copying files:

| Package | Purpose |
|---|---|
| `@digital-go-jp/design-system-example-components-react` | React component implementations |
| `@digital-go-jp/tailwind-theme-plugin` | Tailwind theme (the token classes below) — <https://github.com/digital-go-jp/tailwind-theme-plugin> |
| `@digital-go-jp/design-tokens` | Raw design tokens, the source both of the above build from |

Resolve the current version at task time; never trust a version written into a
document:

```sh
npm view @digital-go-jp/design-system-example-components-react version
npm view @digital-go-jp/tailwind-theme-plugin version
npm view @digital-go-jp/design-tokens version
```

Copy a component's source only when the project must own and diverge from it.
Copying forfeits upstream fixes, so state that trade-off when choosing it.

### Plugin setup

Tailwind v3 — `tailwind.config.js`:

```js
plugins: [require('@digital-go-jp/tailwind-theme-plugin')]
```

Tailwind v4 — in the CSS entry point:

```css
@import 'tailwindcss';
@import '@digital-go-jp/tailwind-theme-plugin/v4';
```

The plugin declares `tailwindcss` as a peer dependency accepting v3 and v4, so
it does not by itself force a Tailwind major version on the project.

## Token vocabulary

Snapshot of the classes the theme plugin adds. It is a convenience index, not the
authority — when the plugin is installed, `node_modules/@digital-go-jp/tailwind-theme-plugin`
wins. Regenerate this section from source with:

```sh
curl -fsSL --proto '=https' https://raw.githubusercontent.com/digital-go-jp/tailwind-theme-plugin/develop/scripts/generate-theme.ts
```

The plugin extends only these theme keys: `colors`, `fontSize`, `fontFamily`,
`fontWeight`, `lineHeight`, `borderRadius`, `screens`, `listStyleType`,
`aspectRatio`, `boxShadow`. Everything else — notably **spacing** — stays on
Tailwind's stock scale, so `px-4` / `gap-2` / `min-h-12` remain correct.

### Colors

- Brand ramp: `key-{50,100,…,1200}` in 100 steps. This is the primary action color; `bg-key-900` is the standard filled-button background.
- Primitive ramps, same 50–1200 steps: `blue`, `light-blue`, `cyan`, `green`, `lime`, `yellow`, `orange`, `red`, `magenta`, `purple`.
- Neutrals: `solid-gray-{50,100,200,300,400,420,500,536,600,700,800,900}` and `opacity-gray-` with the same steps. The off-scale `420` and `536` values are deliberate contrast-critical stops — do not round them to 400/500.
- Semantic: `success-1`, `success-2`, `error-1`, `error-2`, `warning-yellow-1`, `warning-yellow-2`, `warning-orange-1`, `warning-orange-2`.
- Focus: `focus-yellow`, `focus-blue`.
- `white` and `black` are the only stock Tailwind colors permitted. Never `text-blue-500` in the stock sense — `blue-500` here is the DADS ramp, not Tailwind's.

### Text styles

One token sets font-size, weight, line-height, and letter-spacing together, so it
usually replaces several classes. Naming is `{family}-{size}{weight}-{lineHeight}`,
where weight `N` = 400 and `B` = 700.

| Prefix | Use |
|---|---|
| `text-dsp-*` | Display: `dsp-{64,57,48}{B,N}-140` |
| `text-std-*` | Standard body and headings: `std-{45,36}{B,N}-140`, `std-{32,28,26,24,22}{B,N}-150`, `std-20{B,N}-{150,160}`, `std-18{B,N}-160`, `std-17{B,N}-170`, `std-16{B,N}-{170,175}` |
| `text-dns-*` | Dense: `dns-{17,16,14}{B,N}-{120,130}` |
| `text-oln-*` | One-line, for controls: `oln-{17,16,14}{B,N}-100` |
| `text-mono-*` | Monospace: `mono-{17,16,14}{B,N}-150` |

Body text is 16 CSS px or larger; 14 px is reserved for space-constrained
secondary content and anything under 14 px is disallowed by the foundation.

Related: `font-sans` / `font-mono`, `font-400` / `font-700`, and
`leading-{100,120,130,140,150,160,170,175}`. The older `leading-1-0` … `leading-1-75`
aliases still resolve but are marked for removal upstream — use the numeric form.

### Shape, elevation, layout

- `rounded-4`, `rounded-6`, `rounded-8`, `rounded-12`, `rounded-16`, `rounded-24`, `rounded-32`, `rounded-full`. Stock `rounded-md` / `rounded-lg` are not DADS values.
- `shadow-{1..8}` map to the elevation tokens.
- Breakpoints are **`desktop`** (48em) and **`desktop-admin`** (62em) — there is no `sm:` / `md:` / `lg:` in this theme.
- `list-lower-latin`, `list-circle`, `list-square`; `aspect-1/1`, `aspect-3/2`, `aspect-16/9`.

## Component conventions

### Structure

- Compose with `children`; do not lock structure into props (`<Dialog body={…}>` is wrong).
- Base props on native element props: `type Props = ComponentProps<'button'> & { … }`.
- No cross-component imports (a `Slot` primitive is the exception) and no shared `BaseButton` / `CommonProps` abstractions — UI requirements diverge per project and shared bases become liabilities.
- Keep component bodies logic-free: no `useState`, `useRef`, or `useEffect` in the body, which preserves React Server Component compatibility. Push state into a Story, a separate hook file, or a util.
- Components must be self-contained: no per-component `tailwind.config.js` entries, no additions to global CSS. Component-specific `@keyframes` go in a `.css` file inside the component folder. A consumer should be able to copy the folder and have it work.
- Start with everything in `Foo.tsx`; propose a split only past roughly 300 lines.

### Styling

- Tokens only. No stock Tailwind colors, font sizes, or radii.
- Prefer shorthand over arbitrary values where one exists: `ml-[calc(…)]` not `[margin-left:calc(…)]`.
- Do not re-implement Preflight. The HTML reference ships without a CSS reset and normalizes `<button>`, `<ul>`, `<a>` explicitly; Tailwind's Preflight already does this. Drop `m-0`/`p-0` on lists, `border-0`/`bg-transparent` on buttons, `list-none`, `no-underline`, `box-sizing` when porting.
- Express state with `data-*` on the root and let children react via `group-data-[…]/name` or `has-[…]`, rather than branching `className` in JS.

### The four idioms that are easy to get wrong

**1. `aria-disabled`, not `disabled`.** Disabled controls stay focusable and
discoverable; the handler suppresses the action instead:

```tsx
const handleDisabled = (e: React.MouseEvent<HTMLButtonElement>) => e.preventDefault();

<button onClick={props['aria-disabled'] ? handleDisabled : props.onClick} {...rest} />
```

Style the state through `aria-disabled:` variants. Components that also accept a
native `disabled` carry both variant sets.

**2. The focus indicator is a fixed recipe** — a black outline plus a yellow ring,
not a single ring:

```
focus-visible:outline focus-visible:outline-4 focus-visible:outline-black
focus-visible:outline-offset-[calc(2/16*1rem)]
focus-visible:ring-[calc(2/16*1rem)] focus-visible:ring-yellow-300
```

Form controls that must show the indicator on programmatic focus use `focus:`
rather than `focus-visible:`. Do not substitute `[box-shadow:…]`.

**3. Small controls still need a 44 px target.** When the visual box is under
44 px (`sm`, `xs`), the target is extended with a pseudo-element rather than by
growing the control:

```
relative after:absolute after:inset-x-0 after:-inset-y-full after:m-auto after:h-[44px]
```

**4. Forced-colors mode is handled explicitly**, using system color keywords —
`forced-colors:!border-[ButtonText]`, `forced-colors:checked:!bg-[Highlight]`,
`aria-disabled:forced-colors:text-[GrayText]`. Mirror the HTML reference's
`forced-colors` and `prefers-reduced-motion: reduce` handling when porting.

### Reference implementation

`Button.tsx` shows the whole set together: exported `buttonBaseStyle` /
`buttonVariantStyle` / `buttonSizeStyle` string maps, variants
`solid-fill | outline | text`, sizes `lg | md | sm | xs`, an `asChild` escape
hatch via `Slot`, `forwardRef`, and the `aria-disabled` handler.

```sh
curl -fsSL --proto '=https' https://raw.githubusercontent.com/digital-go-jp/design-system-example-components-react/main/src/components/Button/Button.tsx
```

## Toolchain

The upstream repo pins React 18, Tailwind 3, Storybook 10, TypeScript, Biome,
Markuplint, and Vitest in browser mode via Playwright — there is no jsdom
environment, and tests reuse Stories through `composeStories` +
`vitest-browser-react`. Several components build on `react-aria-components`,
so a port inherits that dependency unless the behavior is reimplemented.

Match the **target** project's versions instead of importing upstream's. Verify
current dependencies before relying on any of this:

```sh
curl -fsSL --proto '=https' https://raw.githubusercontent.com/digital-go-jp/design-system-example-components-react/main/package.json
```

Upstream's own completion gate is `npm run lint`, `npm run lint:markup`,
`npm run build`, `npm test`. Use the target project's equivalents.
