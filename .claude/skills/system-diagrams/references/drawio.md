# draw.io views

Use draw.io when a person will move boxes by hand, restyle the diagram for
slides or print, or needs exact placement. The cost is that the source is XML,
whose diff few people can review, so keep the Markdown page (title, lead,
legend, element table) as the reviewable text and the draw.io file as the
picture.

## Files

- Source: `<view>.drawio`, saved **uncompressed**, so that the XML is
  readable and the checker can report precise problems (the checker also
  reads compressed pages).
- On the page: `<view>.drawio.svg`, an SVG export with the diagram data
  embedded. draw.io documents that PNG, SVG, and PDF exports can embed the
  diagram data so that the file opens again in the draw.io editor as the
  diagram. Embed it in the page as an image whose alt text says what the
  diagram shows (example below).
- Start from `assets/templates/view.drawio`, which passes the checker.

```text
![Deployment view: Library reservation system, production](04-deployment.drawio.svg)
```

## Conventions the checker relies on

| Cell | Rule |
|---|---|
| Title | One text cell with `id="title"` whose value is "<view type>: <scope>" |
| Legend | One container cell with `id="legend"`; the key's swatches and texts are its children (children of the legend are exempt from the text rule) |
| Element | `vertex="1"` with a value of name, `[Type: technology]`, and responsibility, separated by `<br>` (set `html=1` in the style) |
| Boundary | A container (`swimlane` or `container=1` in the style) named "<name> [Software System]" or "[Deployment Node: …]", dashed border; a system boundary follows the set's scope, every other frame is drawn only where the source states it |
| Infrastructure node | `shape=hexagon` with the `infra` colours; value "<name>", `[Infrastructure Node: technology]`, and what it does (load balancer, ingress, gateway, firewall) |
| Line | `edge="1"` with `source` and `target` set to element ids and a value saying what flows and why, plus the protocol (a protocol alone draws warning D9) |
| Group | Cells whose style starts with `group` may be empty |

Use the colours of the palette in `notation.md`: `fillColor`, `strokeColor`,
and `fontColor` take the same hex values; external systems add `dashed=1`.

## Layout

- Read left to right or top to bottom: people first, the system or its
  containers in the middle, external systems last.
- Keep the title at the top left and the legend at the bottom or right,
  outside the boundaries.
- Align to the grid and avoid crossing lines; if lines must cross, the view is
  usually two views.
- Place line labels on the line, not floating beside it.

## Shape libraries

draw.io ships a C4 shape library (enable it under the *Software* section of
the shape libraries). This skill does not use cloud vendors' official icon
sets; a diagram built from those is out of scope.

## Exporting

draw.io's documentation describes exporting from the editor (File > Export
as) and does not document a command line. The desktop app is commonly run as
`drawio -x -f svg -e -o <view>.drawio.svg <view>.drawio` (export, format,
embed the diagram, output), but these flags are not confirmed on drawio.com:
run `drawio --help` first and use what it prints. If draw.io is not installed,
say so and leave the export to the person; do not install it without their
approval.

## Sources

- Export formats and embedded diagram data: <https://www.drawio.com/docs/manual/export/export-diagram/>
- C4 shape library: <https://www.drawio.com/blog/c4-modelling>
