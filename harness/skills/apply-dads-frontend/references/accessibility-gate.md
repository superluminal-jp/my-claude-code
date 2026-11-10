# Accessibility release gate

Load this before reporting any DADS interface work complete.

Baseline: **JIS X 8341-3:2016 level AA**, plus WCAG 2.1 and 2.2 level A/AA
criteria. WCAG 2.0 is the version compatible with JIS X 8341-3:2016; DADS tracks
2.2 as current.

## Two facts that decide how this gate is applied

**Using DADS does not make a page conformant.** The Digital Agency states that
the design system eases conformance for the areas it controls — color contrast,
font size, keyboard operation and focus indicators, target size, interaction
feedback, motion, and layouts that survive resizing — but that the accessibility
of a site's own content remains the implementer's responsibility. Test the
integrated page, not the component in isolation.

**The official Storybook examples are outside the conformance scope.** The DADS
accessibility policy excludes the code-snippet sites (`/dads/html/`, `/dads/react/`)
because Storybook itself has known level-A failures — missing `h1` per story,
control tables using `td` where `th` belongs, unlabelled control fields, ambiguous
"Show code"/"Copy" buttons. Never cite a Storybook page as evidence of
conformance, and expect to fix these classes of issue when porting from one.

## The gate

The Digital Agency's own rule is that content passes a JIS-based test before
release and is not published while it fails AA. Apply the same rule: do not
report work complete while a known level A or AA failure stands undisclosed.

Run the project's automated checks where configured, then the manual checks —
automation is necessary but never sufficient for page-level conformance.

### Structure and semantics

- Meaningful page title, correct `lang`, no skipped heading levels, landmarks present and non-duplicated.
- Lists, tables, and form relationships marked up as such — `th` for header cells, labels programmatically associated.
- Native element first; ARIA only where native HTML cannot express the behavior, and never contradicting the element's own semantics.

### Interaction

- Every task completable by keyboard alone: focus order matches reading order, focus is visible, no traps, focus restored after overlays close.
- Anything revealed on hover is equally reachable on focus.
- Accessible name, role, and state correct for each control — including the DADS `aria-disabled` pattern, where the control stays focusable.
- Status, loading, success, and error changes are announced without stealing focus unexpectedly.
- Target size at least 44 CSS px, including the pseudo-element extension used by small controls.

### Perception

- Text contrast meets AA; non-text UI boundaries and focus indicators stay perceivable. Verify contrast, zoom, and reflow together — content must hold at narrow widths and high zoom.
- Color is never the sole carrier of status, selection, category, trend, validation, or required action. Pair it with text, icon, or shape.
- Meaningful images have text alternatives; decorative images are hidden from assistive technology.
- Forced-colors / high-contrast mode behaves correctly where browser testing is available.
- `prefers-reduced-motion: reduce` respected; no uncontrollable movement or time limits.

## Evidence to report

State each of these, or say explicitly that it was not checked:

- automated tests run and their results;
- keyboard paths actually exercised;
- zoom, reflow, and contrast checks;
- semantics reviewed or screen-reader tested;
- any exception, who it affects, the remediation owner, and the follow-up.

"Not verified" is an acceptable report. Silence is not.

## Why the bar is set here

Japan's revised 障害者差別解消法 (in force 2024-04-01) makes environmental
improvement — web accessibility included — an obligation to strive for, ahead of
the duty to provide reasonable accommodation. Public-sector and public-interest
sites are the intended audience of this standard.

Current source: <https://design.digital.go.jp/dads/webaccessibility/> and
<https://design.digital.go.jp/dads/guidance/accessibility/>; archived copies at
`dads-docs/webaccessibility/index.md` and `dads-docs/guidance/accessibility/index.md`.
