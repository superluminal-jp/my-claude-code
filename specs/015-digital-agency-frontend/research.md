# Research: Digital Agency Frontend Skill

## R1: Use a shared skill, not a dedicated subagent

**Decision**: Implement one `digital-agency-frontend` skill and expose it through the existing Claude/Codex skill-discovery paths. Do not add `.claude/agents/` or `.codex/agents/` definitions.

**Rationale**: The workflow must share the main implementation context and compose with the existing `clarifier` and `coder` skills. The repository already treats `.claude/skills/` as the authored source and `.agents/skills/` as a symlinked discovery surface. A dedicated subagent would add isolated context and tool policy that the confirmed use cases do not require.

**Alternatives considered**: Claude-only subagent (rejected because it breaks cross-agent symmetry); paired Claude and Codex subagents (rejected as unnecessary scope and duplicated mechanism); skill plus wrapper agents (deferred until isolation or tool restrictions become a demonstrated need).

## R2: Bundle two concise references and no scripts or assets

**Decision**: Add `references/dads-react-tailwind.md` for general implementation and `references/dashboard-design.md` for dashboard-only decisions. Add no executable script, starter application, copied icon, template, PDF, Markdown archive, or Power BI asset.

**Rationale**: Progressive disclosure keeps dashboard content out of ordinary page work. Existing project architectures vary too much for a starter app to be safe, and the feature requires guidance rather than a deterministic file transformation. Official publications remain canonical, avoiding repository bloat and stale wholesale copies.

**Alternatives considered**: One large reference (rejected because dashboard detail would always consume context); a React starter asset (rejected because it could overwrite or distort project conventions); vendored official documentation (rejected because of drift, attribution, and maintenance cost).

## R3: Use live official sources with freshness metadata and fallback behavior

**Decision**: Every bundled reference begins with an official-source table containing URL, observed version or update date, retrieval date, scope, and licensing or attribution note. The skill checks live sources when network access is available, prefers them on conflict, and reports when live verification cannot be completed.

**Rationale**: On 2026-07-20 the DADS site reports v2.16.0, its Markdown resource is dated 2026-07-15, and the dashboard page was updated 2026-07-17. These sources change independently. A local summary without provenance would become misleading.

**Alternatives considered**: Pin permanently to current versions (rejected because the user selected current official sources); live-only behavior (rejected because temporary network failure should not erase all domain guidance); silent best-effort fallback (rejected because users need to know whether freshness was verified).

**Primary sources**:

- <https://design.digital.go.jp/dads/>
- <https://design.digital.go.jp/dads/resources/>
- <https://www.digital.go.jp/resources/dashboard-guidebook>

## R4: Preserve project versions while using official React/Tailwind sources

**Decision**: Inspect the target project's React, Tailwind CSS, TypeScript, test, lint, and build versions before selecting examples. Use the official React example repository and `@digital-go-jp/tailwind-theme-plugin` as references, but adapt them to the project and verify compatibility rather than forcing a downgrade or copying blindly.

**Rationale**: The official React examples currently describe React 18, Tailwind CSS 3, and TypeScript, while explicitly warning about possible React 19 type adjustments. The official theme plugin documents both Tailwind CSS 3 and 4 setup. Project compatibility therefore requires version-aware adaptation.

**Alternatives considered**: Require the exact example stack versions (rejected because it would cause unnecessary migrations); ignore official code examples (rejected because the user explicitly wants DADS-based development); copy entire component directories (rejected because use and accessibility depend on product context).

**Primary sources**:

- <https://github.com/digital-go-jp/design-system-example-components-react>
- <https://github.com/digital-go-jp/tailwind-theme-plugin>

## R5: Treat accessibility as a product-level release gate

**Decision**: Require semantic structure, keyboard access, visible focus, reflow, contrast, non-color cues, accessible names, status/error communication, and chart alternatives. Use JIS X 8341-3:2016 AA plus WCAG 2.2 AA as the baseline, while stating that official snippets and Storybook examples do not prove page-level conformance.

**Rationale**: DADS identifies accessibility as a first-priority quality standard and targets at least JIS AA while progressively covering WCAG 2.1/2.2 criteria. Its own accessibility policy excludes the code-snippet Storybook pages from the site's conformance scope, demonstrating why integration must be tested separately.

**Alternatives considered**: Automated checks only (rejected because keyboard flow, content meaning, and chart comprehension require manual evaluation); WCAG 2.2 only (rejected because the Japanese public-service context also requires the JIS baseline); treating official components as pre-certified (rejected by the source's stated scope).

**Primary sources**:

- <https://design.digital.go.jp/dads/guidance/accessibility/>
- <https://design.digital.go.jp/dads/webaccessibility/>

## R6: Adapt dashboard principles to web output; do not reuse Power BI artifacts

**Decision**: Apply the guidebook's requirements, prototyping, presentation-versus-exploration distinction, information hierarchy, grid, chart, color, labeling, and review principles to web dashboards. Explicitly exclude `.pbit` and Power BI theme generation.

**Rationale**: The guidebook focuses on visualization and organizes work into requirements, prototyping, and implementation. Its supplied design templates and public asset repository are Power BI artifacts, not React components. The user confirmed web-only scope.

**Alternatives considered**: Convert Power BI theme JSON to Tailwind tokens (rejected because no official equivalence or requested conversion contract exists); include Power BI deliverables (rejected by scope); use the guidebook only for color (rejected because its higher-value contribution is decision-oriented information design).

**Primary sources**:

- <https://www.digital.go.jp/resources/dashboard-guidebook>
- <https://github.com/digital-go-jp/policy-dashboard-assets>

## R7: Validate structure and repository integration deterministically

**Decision**: Create a dedicated shell contract suite that checks metadata triggers, required workflow language, source records, accessibility baselines, dashboard scope, UI metadata, symlink identity, installer registration, routing guidance, and bilingual documentation. Run the standard skill structural validator and existing sync/documentation suites after implementation.

**Rationale**: Static contracts are fast, offline, and stable. They catch the likely failure modes for a prompt-and-resource feature without depending on nondeterministic model output. Existing sync suites then prove global deployment behavior in an isolated fixture.

**Alternatives considered**: Model-only routing evaluation (rejected as the sole gate because it is nondeterministic and consumes external capacity); manual inspection only (rejected because installer and symlink drift are machine-verifiable); no dedicated test (rejected by TDD and FR-017).
