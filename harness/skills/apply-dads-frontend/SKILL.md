---
name: apply-dads-frontend
description: Apply the Digital Agency Design System (DADS), its dashboard guidance, and public-interest accessibility to React and Tailwind CSS frontend work, from a bundled copy of the official documentation. Use for DADS components, Japanese government or public-service interfaces, accessibility remediation, and presentation or exploration dashboards. Do not use for Power BI artifacts, for projects outside React and Tailwind CSS, or for slide decks.
metadata:
  kind: overlay
  permission: workspace_write
  sandbox: network
  network-hosts: registry.npmjs.org, raw.githubusercontent.com, github.com, design.digital.go.jp, www.digital.go.jp
  produces: interface code with the sources checked, the deviations, and the accessibility evidence reported
---

# Apply the Digital Agency Design System to a frontend

Build React and Tailwind interfaces, grounded in the official sources, that help people complete public-service tasks or understand data. The official material is an adaptable starting point: not a drop-in component library, and not by itself proof of accessibility. This skill adds its criteria to whatever implementation or review is under way; it does not replace that work.

## Scope

- DADS design, sourcing, dashboard, and accessibility decisions for the web. Power BI files and themes are out of scope.
- Keep the target repository's architecture and instructions. Do not introduce React or Tailwind CSS only to make this skill apply.
- Never quote a version number, token name, or package API from memory. Read it from the bundled archive, the installed package, or the live source.

## Bundled sources

`references/dads-docs/` is a verbatim copy of the Digital Agency's official Markdown export of the design system site: guidance, foundations, component specifications, and accessibility policy. It contains almost no code. Search it rather than guessing, and never edit it.

```sh
DADS="${CLAUDE_SKILL_DIR}/references/dads-docs"
grep -o '\[[^]]*ボタン[^]]*\]([^)]*)' "$DADS/MANIFEST.md"    # a page by its Japanese name
grep -m1 '^# ' "$DADS/index.md"                              # the archive's version
```

Each page's front matter carries a `source_url`. The archive is a dated snapshot, and the live official source wins.

## Steps

1. **Establish scope and evidence.** Inspect the package manifest and lockfiles, the Tailwind and TypeScript configuration, routing, state and data access, component conventions, and the test, lint, format, and build commands. Note whether `@digital-go-jp/*` packages are installed; if so, they are authoritative for tokens and component APIs. Capture the primary users, the task or decision, the context of use, the content or data, the constraints, and a verifiable completion criterion.
2. **Verify current guidance.** Prefer the live official sources when the network is reachable, and resolve package versions at task time. Keep research to the Digital Agency sites and the official `digital-go-jp` organization. If live content conflicts with the archive, follow the live source, say so, and name the stale path. If nothing current is reachable, use the archive and state that freshness was not verified. Details: `references/sourcing-and-licensing.md`.
3. **Design before implementing.** Map each user task to the smallest suitable foundation, content pattern, and component set. Keep native semantics and a plain document structure; add ARIA only where native HTML cannot express the behavior. Reuse the project's existing primitives when they meet the DADS intent, and record material deviations with their reason. For a dashboard, finish the audience, decision, type, and information hierarchy in `references/dashboard-design.md` before choosing charts.
4. **Implement test-first and type-safe.** Write or update a failing behavior or accessibility test first, wherever the repository can automate the contract. Take each official piece the way it is distributed: the design tokens and the Tailwind theme as npm dependencies, the React components from their repository. Where a component has to be copied, the project owns that copy and gets no upstream fixes: say so, copy only what it uses, and adapt it to the project's React, Tailwind, and TypeScript versions. Validate external data at its boundary. Token classes and component idioms: `references/component-implementation.md`.
5. **Apply the accessibility gate.** Run `references/accessibility-gate.md` in full. Do not report completion while a known level A or AA failure stands undisclosed.
6. **Close out.** Run the project's test, type-check, lint, format, and build commands. Report the sources checked and whether freshness was verified, the DADS adaptations and deviations, the dashboard decisions where they apply, the automated and manual accessibility evidence, and the unresolved risks. Apply the attribution rules of `references/sourcing-and-licensing.md` when official content or code is reused.

## Inside the Bash sandbox

Reading the bundled archive and running the project's local checks need no network. Checking a package version, installing a package, and fetching a component from its repository do: they reach the hosts this skill declares. When the sandbox blocks a host, report the host, continue from the archive, and state that freshness was not verified. Do not work around the sandbox.

## Guardrails

- Never claim that an interface is a Digital Agency product or is endorsed by the Digital Agency.
- Never let color, hover, pointer precision, animation, or a chart alone carry essential meaning.
- Never invent tokens, components, chart rules, version numbers, or conformance claims. Label project-specific additions as such.
- Do not copy the Figma data, Power BI templates, icons, or illustrations into a project. They carry separate terms from the MIT-licensed code and the attribution-only documentation.

## Done when

- Every token, component, and version used was read from the archive, the installed package, or the live source, and the report says which.
- The accessibility gate was run in full, and no known level A or AA failure is undisclosed.
- The project's own checks pass, or each failure is reported.
- Freshness is reported as verified or not verified.

## Bundled files

| File | Read when |
|---|---|
| `references/sourcing-and-licensing.md` | Choosing which source to trust, refreshing the archive, or writing attribution |
| `references/component-implementation.md` | Writing, porting, or reviewing DADS React and Tailwind code |
| `references/accessibility-gate.md` | Before reporting any interface work complete (step 5) |
| `references/dashboard-design.md` | The task creates, changes, or reviews a dashboard |
| `references/dads-docs/` | The specific foundation or component being built; find the page through `MANIFEST.md` |
