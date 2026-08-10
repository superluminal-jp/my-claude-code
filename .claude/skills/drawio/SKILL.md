---
name: drawio
description: Apply this repo's draw.io (.drawio) diagram policy — file placement, uncompressed saving, and Live Documentation compliance — whenever a document needs an architecture, flow, sequence, or network diagram. Composes with jgraph's official `drawio` Claude Code plugin (or the project's own `drawio` MCP entry in `.mcp.json`) for the actual MCP tool surface; this skill does not hand-document tool names, since that list has drifted before.
when_to_use: create a draw.io diagram, drawio diagram, architecture diagram, .drawio file, edit an existing diagram, add AWS/GCP/Azure icons to a diagram
---

# Skill: drawio

Purpose: apply this repo's diagram *policy* — where files go, how they're saved, how they stay in sync with the code they depict — whenever a draw.io diagram is involved. This skill governs policy only, not the MCP tool surface, and composes with the document skill or `coder` already in play for the surrounding work.

## Composition: this skill + the tool surface

Do not treat this file as documentation of the `drawio` MCP server's tools — a prior version hard-coded "exactly two tools: `create_diagram`, `search_shapes`", which drifted: the currently connected `@drawio/mcp@1.5.0` server actually exposes `get_page`, `list_pages`, `open_drawio_csv`, `open_drawio_mermaid`, `open_drawio_xml`, `search_shapes`, `set_page`. Hand-listing tool names here goes stale every time the upstream package changes.

Instead, get the current tool surface from whichever source is live in the session:

- **Preferred**: jgraph's official Claude Code plugin (`/plugin marketplace add jgraph/drawio-mcp`, then `/plugin install drawio@drawio`) — maintained alongside the `@drawio/mcp` releases, so its bundled skill and tool descriptions can't drift the way a hand-copied list does. Once installed, remove the project's own `drawio` entry from `.mcp.json` to avoid registering the same MCP server twice.
- **Fallback**: this project's own `.mcp.json` `drawio` entry (`npx @drawio/mcp@<version>`), for sessions where the plugin isn't installed. Read the connected server's live tool list (or `search_shapes` for shape-specific style strings) rather than assuming names from this doc.

The policy below applies no matter which of the two is providing the tools.

## Cloud provider icons (AWS / GCP / Azure)

No additional setup is required. AWS, Azure, and GCP stencil libraries ship bundled with draw.io itself (desktop, web, and viewer) — a shape-search tool already indexes them, and any XML referencing their `mxgraph.aws4.*` / `mxgraph.azure.*` / `mxgraph.gcp2.*` style strings renders correctly in any standard draw.io app without enabling "More Shapes" or installing an icon pack. That toggle only affects the sidebar's manual drag-and-drop panel, not rendering of already-placed shapes.

## Creating or editing a diagram

1. Search for any specialized shapes (cloud icons, UML, network) to get correct style strings — do not hand-guess `mxgraph.*` style strings.
2. Compose or modify the diagram as draw.io XML, rendering it to verify before saving. Prefer a targeted edit of the relevant `<mxCell>` (or group of cells) over full regeneration when changing an existing diagram — regenerating from scratch discards manual layout/style adjustments made in the draw.io editor. `mxCell` ids and `source`/`target` edge references must stay internally consistent, so don't renumber existing cells casually.
3. Save the XML as a `.drawio` file **uncompressed** (draw.io can compress `mxGraphModel` content by default — turn this off, e.g. via `File > Properties` or the corresponding export option) so the file stays readable in a diff. Compressed diagrams make every edit an opaque blob in git history.
4. Place the file next to what it documents (Proximity Enforcement, `rules/live-documentation.md` §4) — e.g. alongside the ADR, README, or arc42 doc that references it, not in a centralized top-level `diagrams/` folder.
5. A human who wants free-form edits (repositioning, restyling by eye) should open the file directly in the draw.io editor — that remains the right tool for interactive edits; this skill's XML-editing path is for programmatic/reviewable changes.

## Live Documentation compliance

A diagram that depicts current code or architecture is a Documentation Artifact per `rules/live-documentation.md`:

- **Drift**: if a diagram depicts a contract that changes in the same commit, update the `.drawio` (and any exported PNG/SVG) in that same change, or flag the drift explicitly.
- **Proximity**: co-locate the `.drawio` with the document/spec/ADR it illustrates, not in a remote or centralized location.
- **No Redundancy**: before creating a new diagram, check whether an existing `.drawio` already covers the same structure — extend it rather than duplicating.

## References

- draw.io MCP server — <https://github.com/jgraph/drawio-mcp>
- draw.io MCP server manual — <https://www.drawio.com/docs/manual/generate/drawio-mcp-server/>
- Official Claude Code plugin: `/plugin marketplace add jgraph/drawio-mcp`, then `/plugin install drawio@drawio`
