# Digital Agency Web Dashboard Reference

Read this reference only for dashboard creation, modification, or review. It adapts the Digital Agency guidebook's process and information-design principles to React/Tailwind web output; it does not reproduce or convert the supplied Power BI assets.

## Contents

1. Official source record
2. Define the decision and choose the dashboard type
3. Build the information hierarchy and select visual encodings
4. Apply layout, color, and accessible interaction
5. Prototype, review, and report completion evidence

## Official source record

| Source | Observed version/update | Retrieved | Scope and usage note |
|---|---|---|---|
| [Dashboard guidebook and design templates](https://www.digital.go.jp/resources/dashboard-guidebook) | Page updated 2026-07-17; guidebook updated 2026-03-31 | 2026-07-20 | Canonical guidebook, alternative text, requirements worksheet, prototype tool, checklist, and Power BI template links. The 2026-07-17 update changed palette color codes, so verify current values live. |
| [Guidebook text alternative](https://www.digital.go.jp/assets/contents/node/basic_page/field_ref_resources/1948e3cd-736a-4378-9e31-039b08d11106/e7f7ad2f/20260331_resources_dashboard-guidebook_guidebook_02.txt) | Guidebook text dated 2026-03-31 | 2026-07-20 | Searchable official alternative for the requirements, prototyping, information-expression, implementation, and accessibility chapters. |
| [Policy dashboard assets](https://github.com/digital-go-jp/policy-dashboard-assets) | Version 1.0.0 | 2026-07-20 | Power BI `.pbit`, theme JSON, and map data. Power BI artifacts are out of scope for this skill; do not copy or translate them into web tokens. |

The official asset repository applies the Public Data License 1.0 to its Power BI templates and theme JSON and separate terms to map data. This skill uses no files from that repository. If a future request introduces them, stop and review the current terms and attribution rules.

## 1. Define the decision before the display

Complete this brief before choosing charts:

- **Audience and context**: who uses it, their domain knowledge, device, display environment, frequency, and time available.
- **Decision or action**: what the audience should decide, notice, explain, prioritize, or do next.
- **Questions**: the ordered questions the view must answer; remove metrics that answer none of them.
- **Comparison**: target, threshold, prior period, peer group, baseline, or expected range needed to interpret each value.
- **Data contract**: source, definition, unit, grain, coverage, update time, freshness, quality caveat, suppression, and owner.
- **Constraints**: privacy, security, publication, performance, responsive, localization, and accessibility needs.
- **Success**: an observable comprehension or task-completion criterion, not “looks good.”

If the audience, decision/action, metric meaning, or comparison remains material and unknown, route through `clarifier` before implementation.

## 2. Choose the dashboard type

- A **presentation-oriented** dashboard helps people compare current state with a standard, notice an exception quickly, and decide whether action is required. Favor stable hierarchy, concise context, few controls, obvious thresholds, and readable default views.
- An **exploration-oriented** dashboard helps knowledgeable users find differences, filter, compare, and trace possible sources. Allow focused controls and detail-on-demand, but keep state, scope, filter effects, and reset paths explicit.

The guidebook centers on the presentation-oriented case. For exploration-oriented work, use its general requirements and visual-expression principles but do not imply that the guidebook fully specifies complex analytical interaction.

## 3. Build the information hierarchy

Order content by the audience's questions, usually:

1. Title, scope, coverage period, last updated time, and data caveat.
2. A short text summary of the current situation and required attention.
3. Primary KPI or status with its unit, comparison, target/threshold, and change context.
4. Trend or comparison views that explain the primary status.
5. Breakdowns or exceptions that identify where action is needed.
6. Definitions, sources, methodology, notes, and download or detailed table access.

One screen need not contain every layer. Progressive disclosure is appropriate when the default view still answers the primary question without hidden hover content.

## 4. Select visual encodings deliberately

Use chart selection as a question-to-encoding decision:

| Question | Prefer | Guardrail |
|---|---|---|
| Compare categories | Ordered horizontal/vertical bars or a simple table | Start from a meaningful zero where magnitude is encoded by bar length; label units and ordering. |
| Show change over time | Line or column chart | Use a consistent time axis, state missing periods, and avoid smoothing that changes meaning. |
| Compare current with target | Bar/bullet-style comparison, KPI plus explicit target, or table | Show the target and direction in text; do not communicate attainment by color alone. |
| Show distribution | Histogram, dot/box-style summary, or quantile table | Explain bins/statistics and disclose sample size or suppression. |
| Show relationship | Scatter plot with accessible explanatory summary | Do not imply causation; expose notable values in text/table. |
| Show geography | Map only when location is the actual question | Provide a ranked table alternative; avoid area/color comparisons when precise values matter. |
| Show composition | Bars or a restrained part-to-whole view | Avoid many slices and legends that require memorized color matching. |

Prefer direct labels over legends when practical. Avoid three-dimensional effects, decorative gauges, dual axes without a compelling and explained reason, truncated axes that exaggerate change, and precision unsupported by the data.

## 5. Apply a responsive layout grid

- Establish a layout grid with consistent page margins, columns, gaps, alignment, and card padding; use it to reveal hierarchy rather than pack every gap.
- Keep the primary summary and decision-critical values early in reading and DOM order.
- At narrower widths, reflow cards into the same meaningful sequence. Do not shrink charts below readable label/target sizes.
- Allow a data table to scroll within a labelled region only when simplification or reflow would destroy relationships; keep page-level horizontal scrolling out of the default experience.
- Keep filters near the scope they affect, show active filters persistently, and provide a clear reset.

## 6. Use color as a bounded encoding

- Select colors from current DADS/dashboard guidance only after checking the live 2026-07-17 palette update; do not transcribe Power BI theme JSON into Tailwind tokens.
- Reserve saturated or semantic colors for meaning and attention. Use neutral structure so every card does not compete.
- Keep one semantic mapping stable throughout the dashboard and across states.
- Do not use color as the only cue for status, category, selection, trend, threshold, or error; add text, icons/shapes, patterns, direct labels, or position.
- Verify text and non-text contrast in default, hover, focus, selected, disabled, forced-colors, and chart states.

## 7. Provide accessible equivalents and interaction

- Give every visualization a concise title that states its question, not merely its chart type.
- Provide a text summary and tabular equivalent as an alternative for every essential chart; include the values, units, comparisons, and caveats needed for the same decision.
- Keep source order meaningful and all filters, tabs, disclosures, tooltips, downloads, and drill-down paths keyboard operable with visible focus.
- Do not place essential values only in hover tooltips. Make selected points and filter results perceivable to assistive technology without announcing excessive intermediate updates.
- Use real tables for tabular data with captions and simple headers. Avoid visually simulated tables and overly complex merged headers.
- Announce asynchronous loading, errors, empty results, and completed filter changes appropriately without unexpected focus movement.
- Preserve a usable no-JavaScript or failed-chart fallback when the product's reliability requirements call for it.

## 8. Prototype and review

Before production implementation:

1. Sketch the questions and hierarchy with low-cost placeholders.
2. Review with representative stakeholders using concrete decision scenarios.
3. Test whether users can state the current status, comparison, caveat, and next action without coaching.
4. Remove unused metrics and controls; revise wording and ordering before visual polish.
5. Implement through `coder`, then verify real data extremes, missing/zero/negative values, long labels, localization, small screens, keyboard use, zoom/reflow, forced colors, and assistive-technology semantics.

## Completion evidence

Report:

- audience, decision/action, and presentation-oriented or exploration-oriented choice;
- questions and metric definitions represented;
- chart selection and rejected alternatives for non-obvious choices;
- layout/responsive behavior and active-filter behavior;
- color/non-color encoding decisions;
- text summary and tabular equivalents;
- prototype feedback, automated checks, manual accessibility checks, and unresolved data-quality or comprehension risks.
