---
name: drawio
description: Create and edit draw.io (.drawio) diagrams as part of documentation, using the drawio MCP server. Use when a document needs an architecture, flow, sequence, or network diagram and draw.io is the target format. Covers the two available tools (create_diagram, search_shapes — no edit/get tool exists), the edit workflow for a previously created diagram, cloud-provider icon usage (AWS/GCP/Azure ship built into draw.io, no extra setup), and Live Documentation compliance for diagrams that depict code or architecture.
when_to_use: create a draw.io diagram, drawio diagram, architecture diagram, .drawio file, edit an existing diagram, add AWS/GCP/Azure icons to a diagram, search_shapes, create_diagram
---

# Skill: drawio

Purpose: use the `drawio` MCP server correctly when a document needs a draw.io diagram. Composes with the document skill or `coder` already in play for the surrounding work — this skill governs the diagram tooling only, not the document's structure or prose.

## Available tools

The `drawio` MCP server (`@drawio/mcp`) exposes exactly two tools:

- **`create_diagram`** — renders draw.io XML as an interactive diagram inline in chat.
- **`search_shapes`** — searches 10,000+ shapes across draw.io's libraries (AWS, Azure, GCP, Cisco, Kubernetes, UML, BPMN, P&ID, electrical, etc.) by keyword and returns style strings for use in XML.

There is **no `edit_diagram`, `update_diagram`, or `get_diagram` tool** — the server does not track diagram state between calls. Every `create_diagram` call is a fresh render of the XML you pass it.

## Cloud provider icons (AWS / GCP / Azure)

No additional setup is required. AWS, Azure, and GCP stencil libraries ship bundled with draw.io itself (desktop, web, and viewer) — `search_shapes` already indexes them, and any XML referencing their `mxgraph.aws4.*` / `mxgraph.azure.*` / `mxgraph.gcp2.*` style strings renders correctly in any standard draw.io app without enabling "More Shapes" or installing an icon pack. That toggle only affects the sidebar's manual drag-and-drop panel, not rendering of already-placed shapes.

## Creating a new diagram

1. `search_shapes` for any specialized shapes (cloud icons, UML, network) to get correct style strings — do not hand-guess `mxgraph.*` style strings.
2. Compose the diagram as draw.io XML and call `create_diagram` to render and verify it inline before saving.
3. Save the XML as a `.drawio` file **uncompressed** (draw.io can compress `mxGraphModel` content by default — turn this off, e.g. via `File > Properties` or the corresponding export option) so the file stays readable in a diff. Compressed diagrams make every edit an opaque blob in git history.
4. Place the file next to what it documents (Proximity Enforcement, `rules/live-documentation.md` §4) — e.g. alongside the ADR, README, or arc42 doc that references it, not in a centralized top-level `diagrams/` folder.

## Editing an existing diagram

Since there is no stateful edit tool, treat the `.drawio` file as the source of truth and edit it as XML, the same as any other text file:

1. **Read** the existing `.drawio` file.
2. **Prefer a targeted edit** over full regeneration: locate the relevant `<mxCell>` (or group of cells) and change just that XML with `Edit`. Regenerating the whole diagram from scratch discards any manual layout/style adjustments made in the draw.io editor.
3. If adding a new shape, use `search_shapes` first for its style string, then insert the new `<mxCell>` referencing an unused `id` — `mxCell` ids and `source`/`target` edge references must stay internally consistent, so don't renumber existing cells casually.
4. Optionally re-render with `create_diagram` on the updated XML to visually confirm the edit before saving.
5. A human who wants free-form edits (repositioning, restyling by eye) should open the file directly in the draw.io editor — that remains the right tool for interactive edits; this skill's XML-editing path is for programmatic/reviewable changes.

## Live Documentation compliance

A diagram that depicts current code or architecture is a Documentation Artifact per `rules/live-documentation.md`:

- **Drift**: if a diagram depicts a contract that changes in the same commit, update the `.drawio` (and any exported PNG/SVG) in that same change, or flag the drift explicitly.
- **Proximity**: co-locate the `.drawio` with the document/spec/ADR it illustrates, not in a remote or centralized location.
- **No Redundancy**: before creating a new diagram, check whether an existing `.drawio` already covers the same structure — extend it rather than duplicating.

## References

- draw.io MCP server — <https://github.com/jgraph/drawio-mcp>
- draw.io MCP server manual — <https://www.drawio.com/docs/manual/generate/drawio-mcp-server/>
