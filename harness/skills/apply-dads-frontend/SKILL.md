---
name: apply-dads-frontend
description: Applies the Digital Agency Design System (DADS, デジタル庁デザインシステム), its dashboard guidance, and public-sector accessibility requirements to React and Tailwind CSS frontend work, from a bundled copy of the official documentation. Use for DADS components and tokens, Japanese government or public-service interfaces, accessibility remediation of such interfaces, and dashboards built on DADS. Not for Power BI artifacts, projects that use neither React nor Tailwind CSS, or slide decks.
---

# Apply DADS to a frontend

The official DADS material is a starting point to adapt: it is not a drop-in component library, and using it does not by itself make an interface accessible. This skill adds DADS and accessibility criteria to the implementation work; the project's own architecture and conventions stay as they are.

## Bundled sources

`references/dads-docs/` is an unmodified copy of the Digital Agency's official Markdown export of the design system site: guidance, foundations, component specifications, and accessibility policy. Search it instead of recalling, and leave it unedited.

```sh
DADS="${CLAUDE_SKILL_DIR}/references/dads-docs"
grep -o '\[[^]]*ボタン[^]]*\]([^)]*)' "$DADS/MANIFEST.md"    # find a page by its Japanese name
grep -m1 '^# ' "$DADS/index.md"                              # the snapshot's version
```

Each page's front matter has a `source_url`. The copy is a dated snapshot; where the live site differs, the live site is right.

| File | Read when |
|---|---|
| `references/sourcing-and-licensing.md` | Deciding which source to trust, checking package versions, or writing attribution |
| `references/component-implementation.md` | Writing, porting, or reviewing DADS React and Tailwind code |
| `references/dashboard-design.md` | The task creates, changes, or reviews a dashboard |
| `references/accessibility-gate.md` | Before reporting any interface work as complete |
| `references/dads-docs/` | Looking up the specific foundation or component; find its page through `MANIFEST.md` |

## Steps

1. **Read the project.** Check the package manifest and lockfile, the Tailwind and TypeScript configuration, the component conventions, and the test, lint, and build commands. Note whether `@digital-go-jp/*` packages are installed; when they are, they are the authority for token names and component APIs. Establish who uses the interface, the task they are completing, and what will show the work is done.

2. **Check current guidance.** Read version numbers, token names, and package APIs from the bundled copy, the installed package, or the live source, since they change between releases. When the network is reachable, prefer the live official sources (the Digital Agency sites and the `digital-go-jp` GitHub organization). When it is not, use the bundled copy and report that freshness was not verified.

3. **Design before coding.** Map each user task to the smallest suitable set of foundations and components. Use native HTML semantics and a plain document structure, adding ARIA only where native HTML cannot express the behavior. Reuse the project's existing primitives where they meet the DADS intent, and note each deliberate deviation with its reason. For a dashboard, settle the audience, the decision it supports, and the information hierarchy in `references/dashboard-design.md` before choosing charts.

4. **Implement test-first.** Write a failing behavior or accessibility test where the project can automate it. Take each official piece the way it is distributed: design tokens and the Tailwind theme as npm dependencies, React components from their repository. A copied component is owned by the project and receives no upstream fixes, so copy only what is used and say that it was copied.

5. **Run the accessibility gate** in `references/accessibility-gate.md` in full.

6. **Close out.** Run the project's checks. Report the sources consulted and whether freshness was verified, the DADS adaptations and deviations, the automated and manual accessibility evidence, and open risks. Follow the attribution rules in `references/sourcing-and-licensing.md` when official content or code is reused.

## Limits

- An interface built with DADS is not a Digital Agency product; do not present it as one or as endorsed by the agency.
- Essential meaning needs a carrier besides color, hover, animation, or a chart alone, because some users cannot perceive each of those.
- The Figma data, Power BI templates, icons, and illustrations carry terms different from the MIT-licensed code and the documentation, so they stay out of the project unless the person has reviewed those terms.
- A token, component, or conformance claim that cannot be found in a source is labeled as the project's own addition.

## Done when

- Every token, component, and version used was read from a source, and the report says which.
- The accessibility gate was run in full, and every known level A or AA failure is fixed or disclosed.
- The project's checks pass, or each failure is reported.
