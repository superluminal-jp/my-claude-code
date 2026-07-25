---
name: digital-agency-frontend
description: Build, modify, or review React and Tailwind CSS web frontends using the Digital Agency Design System (DADS) and dashboard guidebook. Use for DADS component implementation, Japanese government or public-service interfaces, public-interest accessibility remediation, and presentation or exploration dashboard design; covers requirements, design, implementation, testing, JIS/WCAG verification, and source attribution. Do not use for Power BI artifacts or projects outside React/Tailwind CSS.
---

# Digital Agency Frontend

Create source-grounded React/Tailwind interfaces that help people complete public-service tasks or understand data. Treat official examples as adaptable starting points, not a component package or proof of accessibility.

## Compose the workflow

1. Load `coder` before changing code; keep TDD, type safety, security, and documentation sync there.
2. Use this skill for DADS-specific design, source, dashboard, and accessibility decisions.
3. Load `clarifier` when the users, task, decision, data meaning, constraints, or success criteria are materially ambiguous.
4. Preserve the target repository's architecture and instructions. Do not introduce React or Tailwind CSS solely to make this skill applicable.

## Load references progressively

- Read [references/dads-react-tailwind.md](references/dads-react-tailwind.md) for every matching task.
- Read [references/dashboard-design.md](references/dashboard-design.md) only when the task creates, changes, or reviews a dashboard.
- Do not follow a deeper reference chain. Open the official URLs named by the relevant reference when current detail affects the work.

## Execute the workflow

### 1. Establish scope and evidence

- Inspect `package.json`, lockfiles, React/Tailwind configuration, routing, state and data access, component conventions, tests, lint, formatting, and build commands.
- Confirm a web-only React/Tailwind deliverable. Treat `.pbit`, Power BI themes, and Power BI editing as out of scope.
- Capture the primary users, task or decision, use context, content/data, constraints, and a verifiable completion criterion.
- For an existing interface, inspect the rendered behavior when a local browser/testing capability is available; do not infer the whole experience from source alone.

### 2. Verify current official guidance

- Prefer live official Digital Agency sources over the dated bundled summary whenever network access is available.
- Restrict source research to the Digital Agency sites and official `digital-go-jp` repositories listed in the references.
- If live official content conflicts with a bundled reference, follow the current source, disclose the drift, and identify the local reference that needs an update.
- If current sources cannot be reached, use the bundled reference as a dated fallback and state that freshness was not verified.

### 3. Design before implementation

- Map each user task to the smallest suitable DADS foundation, content pattern, and component set.
- Keep native semantics and straightforward document structure. Add ARIA only when native HTML cannot express the required behavior.
- Reuse the project's existing primitives when they already meet the DADS intent; record material visual or behavioral deviations and their reason.
- For dashboards, complete the audience/decision/type/information hierarchy work in the dashboard reference before selecting charts.

### 4. Implement through `coder`

- Write or update a failing behavior or accessibility test before implementation where the repository can automate the contract.
- Adapt only the needed official React example. Reconcile its React, Tailwind, and TypeScript assumptions with the active project instead of copying a directory wholesale or forcing a downgrade.
- Use the official theme plugin only after checking current compatibility and installation guidance. Do not replace an established project token system without approval.
- Validate external data at its boundary and render untrusted text through React's normal escaping; do not add unsafe HTML injection.

### 5. Apply the accessibility release gate

- Verify semantics, headings, landmarks, labels, names/roles/values, keyboard operation, focus order and visibility, status/error communication, zoom and reflow, text/non-text contrast, non-color cues, target size, motion, and text alternatives.
- Apply JIS X 8341-3:2016 level AA and WCAG 2.2 level AA. Test the integrated page; an official component or Storybook example alone does not establish conformance.
- Run the project's automated accessibility checks when configured, then perform the applicable manual keyboard, screen-reader-oriented, responsive, forced-colors, and content-comprehension checks.
- Do not report completion while a known level A or AA failure remains undisclosed. State any exception, user impact, owner, and follow-up.

### 6. Close out with traceability

- Run the project test, type-check, lint, format, and build commands required by `coder` and the repository.
- Report the official sources checked and whether live freshness was verified.
- Report DADS adaptations or deviations, dashboard decisions when applicable, automated and manual accessibility evidence, and unresolved risks.
- Apply the attribution or license guidance in the DADS reference when official content or code is reused.

## Guardrails

- Do not claim that an interface is a Digital Agency product or endorsed by the Digital Agency.
- Do not use color, hover, pointer precision, animation, or a visual chart as the sole carrier of essential meaning.
- Do not invent official tokens, components, chart rules, or conformance claims. Label project-specific additions as such.
- Do not vendor the DADS documentation archive, dashboard publication, Power BI templates, icons, or illustrations without a separately confirmed need and license review.
