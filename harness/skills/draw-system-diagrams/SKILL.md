---
name: draw-system-diagrams
description: Create, split, or review system architecture diagrams (システム構成図) that a first-time reader, from a non-engineer to a specialist, can follow - a set of views, each answering one question for one audience at one C4 level, written as Mermaid in Markdown by default, draw.io when a person will hand-edit the layout, or Structurizr DSL when many views share one model, and checked by a bundled checker. Use when asked to draw, document, or review the architecture, configuration, deployment, or runtime flows of a codebase or a described system, or to split an overloaded diagram. Do not use for diagrams built from a cloud vendor's official icon set, data charts or dashboards, UI mockups, BPMN process models, schema or class diagrams generated from code, or choosing the architecture itself.
metadata:
  kind: worker
  permission: workspace_write
  sandbox: inside
  produces: a set of diagram pages with an index, which passes the checker
---

# Draw system diagrams

Produce a diagram set that someone who has never seen the system, the code, or this conversation can read. Three rules cut the work:

- **One view, one question, one reader, one level.** A diagram that mixes a user's journey with database tables answers neither question.
- **The page carries what the conversation knew.** Every page says what the diagram shows, explains its notation in a legend, and lists its elements in plain words.
- **Nothing is drawn without a source.** Every element and line comes from a file, a document, or a statement by the person. Anything else is marked as an assumption on the page.

## Steps

1. **Fix the scope and the readers.** Name the system the set is about (what is inside its boundary and what is external), the readers, and the questions they bring. Ask only when the boundary itself is unclear; otherwise state the assumption.
2. **Inventory the facts.** List people, software systems, containers (units that run or store data separately), and the relationships between them, each with its source: `path:line`, a document, or "user". In a codebase read the README, compose files, Kubernetes manifests, infrastructure code, package manifests, configuration files, API clients, connection strings, and queue or topic names. Record what you could not determine as an open question.
3. **Plan the view set.** Read `references/views.md`. Choose views in this reading order, drawing each only when its condition holds:
   1. System context (always).
   2. Container (when the system has more than one deployable unit or data store).
   3. Dynamic (one per key flow the readers care about, usually one to three).
   4. Deployment (when where it runs matters).
   5. Component (only for a container whose inside someone asked about).
   6. System landscape (when the scope is several systems).

   Never hand-draw the code level. Put one view on one page. Split a view that exceeds the element limit (checker default 20) or mixes levels: by boundary or by flow.
4. **Choose the format per view,** and read only the reference for it.

   | Use | When | Reference |
   |---|---|---|
   | Mermaid `flowchart` in Markdown (default) | Pages live in a Git repository or a Markdown renderer | `references/mermaid.md` |
   | Mermaid `sequenceDiagram` | Dynamic views | `references/mermaid.md` |
   | draw.io | A person will rearrange the layout by hand, or the diagram goes into slides or print | `references/drawio.md` |
   | Structurizr DSL | The repository already keeps a workspace, or the person asks for a model that generates the views | `references/structurizr.md` |

   Do not use Mermaid `architecture-beta`: its lines cannot carry labels.
5. **Draw each view to the notation** in `references/notation.md`.
   - Title: "<view type>: <scope>".
   - Every element: its name, its type and technology in brackets, and one line on what it is responsible for.
   - Every line: one direction, labelled with what flows and why. Add the protocol from the container level down, after the words, never instead of them.
   - Draw the system boundary fixed in step 1. Draw any other frame (a network zone, a deployment node) only where the source states it; otherwise write the question under the open questions.
   - The same element keeps the same id and name in every view.
   - Colour is never the only signal: shape, the type text, and a dashed border for external systems carry the same meaning.
   - For non-engineers, use the words of the business, write the type in their language with the C4 term in the legend, and show no technology or protocol.
6. **Write the pages** from `assets/templates/view-page.md` and the index from `assets/templates/index.md`, in the person's language, where the repository keeps its documentation or where the person says. A page has a title, a lead of one to three sentences that answers the view's question, the diagram, a legend, an element table, assumptions and open questions, and links to the views one level up and down. The index lists every view in reading order with its reader and question, and the views deliberately not drawn with the reason.
7. **Check.** Run the checker on the set and on any `.drawio` or `.dsl` source:

   ```sh
   python3 -B "${CLAUDE_SKILL_DIR}/scripts/check_diagrams.py" <output directory>
   ```

   - Fix every `E`. Fix every `W`, or say on the page why it stays. Exit status 1 means an error remains.
   - The checker checks form, not truth. Read every view again against the inventory: each element and line traced, nothing from one level leaking into another.
   - The checker does not parse Mermaid syntax. If a renderer is already installed, render each block. Do not install one without the person's approval, because it downloads code and a browser; report the syntax as not rendered instead.
8. **Report** where the set is, which views it has and why, which were left out and why, the assumptions and open questions, the checker result, and what was not verified.

## Reviewing or redoing existing diagrams

- Review: run the checker first, then judge what it cannot - one question and one reader per view, mixed levels, names agreeing across views, meaningful labels, and support for every element. Report findings in order of how much they mislead a newcomer, each with its fix. Change the diagrams only when asked.
- Redo: build the new set as above, then make the file the person named the entry point, so that every link to it still leads somewhere useful. Keep the original as `<name>.original.md` next to it, unless Git already holds it unchanged. Mark every label or meaning inferred because the original lacked it as an assumption.

## Done when

- The checker reports no `E` on the set, and every remaining `W` is explained on its page.
- Every element and line in every view has a source in the inventory or is marked as an assumption.
- The report names what was not verified, such as rendering.

## Bundled files

| File | Read or run when |
|---|---|
| `references/views.md` | Planning the view set (step 3) |
| `references/notation.md` | Drawing any view (step 5); it also lists the checker's codes |
| `references/mermaid.md` | The view is Mermaid |
| `references/drawio.md` | The view is draw.io |
| `references/structurizr.md` | The set is generated from Structurizr DSL |
| `assets/templates/` | Writing pages, the index, a draw.io file, or a workspace |
| `examples/library-reservation/` | A complete set that passes the checker, to imitate |
| `scripts/check_diagrams.py` | Step 7. Standard library only; reads files and writes nothing |
