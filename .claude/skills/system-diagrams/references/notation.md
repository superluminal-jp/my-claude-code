# Notation every view follows

These rules make a diagram readable without its author. The first group comes
from the C4 model's notation guidance and review checklist; the second makes
the page work for readers who are not engineers; the third makes it work for
readers who use a screen reader or do not distinguish colours. The last
section lists what the bundled checker enforces.

## 1. C4 notation (applies to every format)

| Rule | How to meet it |
|---|---|
| A title naming the view type and its scope | Page H1 and diagram title: "Container view: Library reservation system" |
| A key or legend explaining the notation | A section whose heading contains 凡例, Legend, or Key, listing every shape, colour, border, and line style used |
| The type of every element stated | `[Person]`, `[Software System]`, `[Software System: external]`, `[Container: PostgreSQL]`, `[Component: Spring Bean]`, `[Deployment Node: Kubernetes]`, `[Infrastructure Node: NGINX Ingress]`; in a view written for non-engineers, the same types in their words (`[人]`, `[このシステム]`, `[外部のシステム]`) with the C4 term in the legend |
| A short description of every element | One line in the label on what it is responsible for, and the same in the element table |
| The technology of every container and component | Inside the brackets after the type |
| Every line labelled, consistent with its direction | The label reads from the tail to the head: "reads and writes reservations" from the API to the database. A protocol or port alone ("SQL", "HTTP/JSON", "port 3000") is not a label |
| The technology or protocol of lines between containers | `[JSON/HTTPS]`, `[SQL/TLS]`, `[SMTP]` after the label |
| One arrowhead per line | Show the direction of the request or the data that matters to the reader; for a two-way exchange, label the initiating direction |
| Acronyms explained | In the element table, or avoided |

## 2. Writing for readers who are not engineers

- Lead each page with the answer to the view's question in one to three
  sentences, in words the reader already uses. Example: "The reservation
  system takes reservations from library members, checks the existing
  library catalogue for availability, and has the mail service tell members
  when their book is ready."
- Name people by their role in the business ("library member", "librarian"),
  not by system role ("client").
- Label lines with what the person or system wants ("reserve a book",
  "ask whether the book is on the shelf"), not with endpoints or method names.
  Engineers get the protocol in brackets after the words.
- Keep technical terms in the type brackets and the element table, where each
  is defined once in plain words.
- In the system context view, show no technology at all unless the reader
  needs it.

## 3. Accessibility

| Requirement | Source | How |
|---|---|---|
| Text alternative for the diagram | WCAG 2.2 SC 1.1.1 Non-text Content | Mermaid `accTitle:` and `accDescr:` (or `accDescr { ... }` for several lines); for images, alt text that says what the diagram shows; the lead and the element table repeat the content in text |
| Colour is not the only way meaning is conveyed | WCAG 2.2 SC 1.4.1 Use of Color | External systems are grey and have a dashed border and the word "external" in their type; data stores are cylinders; people are rounded |
| Graphical objects contrast with their surroundings | WCAG 2.2 SC 1.4.11 Non-text Contrast (3:1) | Use the palette below |

### Palette

Light fills with dark text and dark borders, so the boxes stand out on both a
light page (the border carries the contrast) and a dark page (the fill
carries it). Ratios were computed with the WCAG relative-luminance formula;
the dark background is GitHub's dark theme `#0d1117`.

| Class | Fill | Border | Text | Text on fill | Border on white | Fill on `#0d1117` |
|---|---|---|---|---|---|---|
| `person` | `#CFE0F3` | `#1F4E79` | `#0B1F33` | 12.4:1 | 8.7:1 | 14.1:1 |
| `system` | `#DCE9F7` | `#1F4E79`, 2px | `#0B1F33` | 13.5:1 | 8.7:1 | 15.4:1 |
| `container` | `#E8F1FB` | `#1F4E79` | `#0B1F33` | 14.6:1 | 8.7:1 | 16.6:1 |
| `component` | `#F3F8FD` | `#1F4E79` | `#0B1F33` | 15.6:1 | 8.7:1 | 17.7:1 |
| `external` | `#EDEDED` | `#4D4D4D`, dashed | `#0B1F33` | 14.3:1 | 8.5:1 | 16.2:1 |
| `infra` (hexagon) | `#FFFFFF` | `#1F4E79` | `#0B1F33` | 16.7:1 | 8.7:1 | 18.9:1 |
| boundary | none | `#808080`, dashed | theme default | — | 3.9:1 | 4.8:1 |

Do not set line colours; leave them to the renderer's theme so they follow
light and dark mode.

## 4. What the checker enforces

`scripts/check_diagrams.py` prints one line per finding: severity (`E` error,
`W` warning), code, location, and what to do. It checks form, not truth.

| Code | Severity | Finding |
|---|---|---|
| P1 | E | View page has no H1 title before its diagram |
| P2 | E | No lead text between the title and the diagram |
| P3 | E | No legend section (heading containing 凡例, Legend, or Key) |
| P4 | E | Image without alt text |
| P5 | W | More than one diagram on a page |
| M1 | E | Mermaid block without `accTitle` |
| M2 | E | Mermaid block without `accDescr` |
| M3 | E | Line, relationship, or message without a label |
| M4 | E | Element or participant without a `[Type]` in its label |
| M5 | E | Element drawn by id only, never given a label |
| M6 | W | More elements than `--max-elements` (default 20) |
| M7 | W | Line without an arrowhead |
| M8 | E | Mermaid `architecture-beta` (its lines cannot carry labels) |
| M9 | W | Mermaid diagram type the checker does not inspect |
| M10 | W | Line, relationship, or message whose label names only a protocol, format, or port |
| D1 | E | draw.io file cannot be read (XML, compression, or missing embedded data) |
| D2 | E | Duplicate cell id |
| D3 | E | Line whose source or target is missing |
| D4 | E | Line without a label (neither its value nor a label child) |
| D5 | E | No cell with id `title` holding the view's title |
| D6 | E | No cell with id `legend` holding the key |
| D7 | E | Shape without text |
| D8 | W | More elements than `--max-elements` on one page |
| D9 | W | Line whose label names only a protocol, format, or port |
| S1 | E | Structurizr workspace without `workspace`, `model`, or `views` |
| S2 | E | Relationship without a description |
| S3 | W | Element without a description |
| S4 | W | Container or component without a technology |
| S5 | W | View without a description or title |
| S6 | W | Relationship whose description names only a protocol |
| I1 | E | Directory with view pages but no single index: `README.md`, `index.md`, the one top-level page without a diagram that links to the views, or the file given with `--index` |
| I2 | E | View page not linked from the index |
| X1 | W | One id with different names across views |

## Sources

- C4 model notation: <https://c4model.com/diagrams/notation>; review
  checklist: <https://c4model.com/diagrams/checklist>
- Mermaid accessibility options: <https://mermaid.js.org/config/accessibility.html>
- WCAG 2.2: <https://www.w3.org/TR/WCAG22/> (SC 1.1.1, 1.4.1, 1.4.11)
