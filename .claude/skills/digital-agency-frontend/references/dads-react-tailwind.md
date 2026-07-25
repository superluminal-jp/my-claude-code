# DADS React/Tailwind Implementation Reference

Use this reference for every matching task. It is an operational summary, not a mirror of the official documentation. Check the linked current sources when network access is available.

## Official source record

| Source | Observed version/update | Retrieved | Scope and usage note |
|---|---|---|---|
| [Digital Agency Design System](https://design.digital.go.jp/dads/) | v2.16.0 | 2026-07-20 | Canonical foundations, components, guidance, and examples. Content reuse requires attribution; identify modified or adapted content. |
| [DADS resources](https://design.digital.go.jp/dads/resources/) | Markdown bundle dated 2026-07-15 | 2026-07-20 | Index for Figma, HTML/React examples, theme plugin, Markdown documentation, accessibility guide, and assets. |
| [Usage notices](https://design.digital.go.jp/dads/introduction/notices/) | Updated 2026-07-14 | 2026-07-20 | Documentation attribution, CC BY 4.0 Figma treatment, Material Symbols exception, and MIT code-example treatment. |
| [React examples](https://github.com/digital-go-jp/design-system-example-components-react) | Repository describes React 18, Tailwind CSS 3, and TypeScript | 2026-07-20 | Adaptable examples under the MIT License; the repository warns that React 19 can require type adjustments. |
| [Tailwind theme plugin](https://github.com/digital-go-jp/tailwind-theme-plugin) | Latest listed release v1.0.1; setup covers Tailwind CSS 3 and Tailwind CSS 4 | 2026-07-20 | Official design-token theme plugin under the MIT License. Check the current version compatibility table before use. |
| [Accessibility guidance](https://design.digital.go.jp/dads/guidance/accessibility/) | Updated guidance available on the live site | 2026-07-20 | DADS accessibility process and references to JIS, WCAG, and WAI-ARIA. |
| [Accessibility policy](https://design.digital.go.jp/dads/webaccessibility/) | Updated 2025-12-10 | 2026-07-20 | Targets JIS X 8341-3:2016 AA and adds WCAG 2.1/2.2 criteria; code-snippet Storybook pages are outside the site's conformance scope. |

### Freshness warning

The observed DADS site is v2.16.0, while the theme plugin README's displayed compatibility table ends at DADS/Figma 2.14.0. Treat this as a potential source-version drift: inspect the live plugin release and compatibility information before installation, disclose any unresolved mismatch, and do not assert v2.16.0 token parity without evidence.

## Inspect the target before choosing an example

Record:

- React and React DOM versions, rendering model, router, and server/client boundary;
- Tailwind CSS 3 or Tailwind CSS 4 configuration and existing token/theme layers;
- TypeScript settings and the component prop/ref conventions;
- package manager and lockfile;
- test runner, DOM/browser test tools, accessibility tooling, lint, format, type-check, and build commands;
- existing components that already implement the required semantics or brand rules.

The official example repository currently targets React 18 and Tailwind CSS 3 and notes React 19 compatibility adjustments. The official theme plugin documents Tailwind CSS 3 and Tailwind CSS 4 entry points. Adapt to the target versions and verify types and behavior; never downgrade the project by default.

## Select and adapt DADS patterns

1. Start from the user's task and content structure, not a desired visual component.
2. Open the current DADS foundation/component page and its accessibility subpage.
3. Prefer native elements and the smallest component composition that conveys the correct meaning and action.
4. Compare the official React example with the target project's primitives and versions.
5. Copy or translate only the necessary behavior and styles. Retain accessible names, states, focus behavior, and documented constraints.
6. Use official design tokens through the supported theme plugin when compatible; otherwise map tokens explicitly and document project-specific substitutions.
7. Add tests for product behavior and known failure modes. Do not treat a Storybook story as an integration test.

## React/Tailwind implementation rules

- Keep interaction state explicit and controlled according to project conventions. Preserve focus when content changes or overlays close.
- Render user or external text through React's normal escaping. Avoid `dangerouslySetInnerHTML`; if trusted rich content is unavoidable, use the project's reviewed sanitizer and test the boundary.
- Use semantic elements before ARIA. Do not add redundant or conflicting roles.
- Keep visible labels; do not replace them with placeholders or icon-only controls. Provide accessible names for necessary icon-only actions.
- Express state with text/icon/shape as well as Tailwind color utilities. Ensure hover styles have equivalent focus-visible styles.
- Avoid dynamic class construction that the project's Tailwind scanner cannot discover. Follow its established class composition helper and design-token conventions.
- Preserve responsive reading and focus order; CSS reordering must not create a different meaningful sequence.
- Treat loading, empty, partial, error, and stale-data states as designed states, not afterthoughts.

## Accessibility verification

Use JIS X 8341-3:2016 level AA and WCAG 2.2 level AA as the baseline.

### Structure and interaction

- Verify meaningful page title, language, heading hierarchy, landmarks, lists, tables, and form relationships.
- Verify accessible name, role, value/state, instructions, validation, and error recovery for each control.
- Complete every task with keyboard only; verify focus order, visible focus, no trap, restoration after overlays, and equivalent hover/focus disclosure.
- Verify status, loading, success, and error changes are available without unexpected focus movement.

### Perception and responsive behavior

- Verify zoom and reflow/contrast together: content must remain understandable at narrow widths and high zoom, text contrast must meet AA, and non-text UI boundaries/focus indicators must remain perceivable.
- Do not use color alone for status, selection, category, trend, validation, or required action.
- Check forced-colors/high-contrast behavior where the project supports browser testing.
- Provide text alternatives for meaningful images and hide decorative images from assistive technology.
- Respect reduced-motion preferences and avoid time limits or automatic movement unless users can control them.

### Evidence

Report:

- automated tests and their results;
- keyboard paths exercised;
- responsive/zoom and contrast checks;
- screen-reader-oriented semantics reviewed or tested;
- exceptions, affected users, and remediation owner.

Automated success is necessary where configured but not sufficient for page-level conformance.

## Attribution and license handling

- **DADS documentation/content**: Include attribution when content is reused. When it is modified or adapted, state that it was modified or created from DADS content, for example: “Based on and adapted from the Digital Agency Design System website, https://design.digital.go.jp/dads/.” Do not imply Digital Agency authorship of the derivative.
- **React examples and theme plugin**: They are published under the MIT License. Preserve license notices when the license requires them in distributed source. DADS additionally says adapted code-based UI parts need no visible source attribution, while unmodified public reuse should identify the DADS site and official GitHub source.
- **Figma data**: CC BY 4.0 applies on Figma Community, with a Material Symbols Apache License 2.0 exception. This skill does not copy Figma data; review the live terms if a future task introduces it.
- **Icons and illustrations**: They have separate usage terms. Do not copy them merely because a component example displays them.

When uncertain, link the live usage notice and describe exactly what was reused or changed.
