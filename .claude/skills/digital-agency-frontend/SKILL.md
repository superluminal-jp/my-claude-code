---
name: digital-agency-frontend
description: Apply the Digital Agency Design System (DADS), dashboard guidance, and public-interest accessibility as a domain overlay for React and Tailwind CSS frontend work. Use for DADS components, Japanese government or public-service interfaces, accessibility remediation, and presentation or exploration dashboards. Do not use for Power BI artifacts or projects outside React/Tailwind CSS. Apply alongside every independently matching requirements, implementation, review, or document operation; domain guidance supplements rather than replaces that operation.
---

# Digital Agency Frontend

Build source-grounded React/Tailwind interfaces that help people complete
public-service tasks or understand data. The official DADS material is an
adaptable starting point — not a drop-in component library, and not by itself
proof of accessibility.

## Scope

- Use this skill for DADS design, sourcing, dashboard, and accessibility decisions.
- Preserve the target repository's architecture and instructions. Do not introduce React or Tailwind CSS just to make this skill apply.
- Web only. `.pbit`, Power BI themes, and Power BI editing are out of scope.
- Resolve material ambiguity in users, task, use context, data, constraints, and completion criterion before implementing (step 1) rather than inventing intent.

## Bundled sources

`references/dads-docs/` is a verbatim copy of the Digital Agency's official
Markdown export of the design system site — guidance, foundations, all component
specifications, and accessibility policy. It is design guidance and contains
almost no code. Grep it rather than guessing, and never edit it.

Find the right page by Japanese name through the archive's own manifest:

```sh
DADS="${CLAUDE_SKILL_DIR}/references/dads-docs"
grep -o '\[[^]]*ボタン[^]]*\]([^)]*)' "$DADS/MANIFEST.md"    # → components/button/index.md
grep -m1 '^# ' "$DADS/index.md"                              # → current archive version
```

Each page's front matter carries a `source_url`. Open it when current detail
matters; the archive is a dated snapshot, and the live official source always wins.

## Load references progressively

| Read | When |
|---|---|
| `references/sourcing-and-licensing.md` | Choosing which source to trust, refreshing the archive, or writing attribution |
| `references/component-implementation.md` | Writing, porting, or reviewing DADS React/Tailwind code — token classes and component idioms |
| `references/accessibility-gate.md` | Before reporting any interface work complete |
| `references/dashboard-design.md` | The task creates, changes, or reviews a dashboard |
| `references/dads-docs/<path>` | The specific foundation or component being built |

Never quote a version number, token name, or package API from memory. Read it
from the archive, the installed package, or the live source.

## Workflow

### 1. Establish scope and evidence

Inspect `package.json`, lockfiles, Tailwind and TypeScript configuration,
routing, state and data access, component conventions, and the test, lint,
format, and build commands. Note whether `@digital-go-jp/*` packages are already
installed — if so, they are authoritative for tokens and component APIs.

Capture the primary users, the task or decision, use context, content or data,
constraints, and a verifiable completion criterion. For an existing interface,
inspect rendered behavior when browser or test tooling is available rather than
inferring the whole experience from source.

### 2. Verify current guidance

Prefer live official sources over the bundled archive whenever the network is
reachable, and resolve package versions at task time. Restrict research to the
Digital Agency sites and the official `digital-go-jp` organization. If live
content conflicts with the archive, follow the live source, disclose the drift,
and name the stale path. If nothing current is reachable, use the archive and
state that freshness was not verified. Details: `references/sourcing-and-licensing.md`.

### 3. Design before implementing

Map each user task to the smallest suitable foundation, content pattern, and
component set. Keep native semantics and a straightforward document structure;
add ARIA only where native HTML cannot express the behavior. Reuse the project's
existing primitives when they already meet the DADS intent, and record material
deviations with their reason. For dashboards, finish the audience, decision,
type, and information-hierarchy work in `dashboard-design.md` before choosing
charts. Use `references/dashboard-design.md` for the full decision sequence.

### 4. Implement test-first and type-safe

Write or update a failing behavior or accessibility test before implementing,
wherever the repository can automate the contract. Keep the change type-safe —
do not weaken or bypass the type checker to make code compile.

Prefer depending on the official npm packages over copying source; copy only when
the project must own and diverge from the code, and say so. Adapt what you take
to the target project's React, Tailwind, and TypeScript versions instead of
copying a directory wholesale or forcing a downgrade. Validate external data at
its boundary and render untrusted text through React's normal escaping.
Token classes and component idioms: `references/component-implementation.md`.

### 5. Apply the accessibility gate

Run `references/accessibility-gate.md` in full. Do not report completion while a known
level A or AA failure stands undisclosed.

### 6. Close out

Run the project's test, type-check, lint, format, and build commands. Update the
documentation artifact for any changed public component contract in the same
change. Report: sources checked and whether freshness was verified; DADS
adaptations and deviations; dashboard decisions where applicable; automated and
manual accessibility evidence; and unresolved risks. Apply the attribution rules
in `references/sourcing-and-licensing.md` when official content or code is reused.

## Guardrails

- Never claim an interface is a Digital Agency product or is endorsed by the Digital Agency.
- Never let color, hover, pointer precision, animation, or a chart alone carry essential meaning.
- Never invent tokens, components, chart rules, version numbers, or conformance claims. Label project-specific additions as such.
- Do not vendor the Figma data, Power BI templates, icons, or illustrations — they carry separate terms from the MIT-licensed code and the attribution-only documentation.
