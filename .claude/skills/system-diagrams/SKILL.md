---
name: system-diagrams
description: Create, split, or review system architecture diagrams (システム構成図) that a first-time reader, from a non-engineer to a specialist, can follow - a set of views, each answering one question for one audience at one C4 level (context, container, component, deployment, dynamic), written as Mermaid in Markdown by default, draw.io when a person will hand-edit or present the layout, or Structurizr DSL when many views share one model, and checked by a bundled checker for title, legend, element types, labelled lines, and accessible text. Use when asked to draw, document, or review the architecture, configuration, deployment, or runtime flows of a codebase or a described system, or to split an overloaded diagram. Do not use for diagrams built from a cloud vendor's official icon set (AWS, Azure, Google Cloud), data charts or dashboards, UI mockups, BPMN process models, schema or class diagrams generated from code, or choosing the architecture itself. Apply alongside any other matching operation.
---

# System diagrams

Produce a diagram set that someone who has never seen the system, the code,
or this conversation can read: each view answers one question for one kind
of reader at one level of abstraction, sits on its own page with the words
that page needs, and is traced to evidence rather than invented.

## Why the work is cut this way

- **One view, one question, one reader, one level.** ISO/IEC/IEEE 42010
  defines a view as addressing the concerns of particular stakeholders, and
  the C4 model gives each level its own audience (a system context diagram
  is for everybody; a container diagram is for technical people). A diagram
  that mixes the user's journey with database tables answers neither
  question, so a newcomer cannot tell what to look at.
- **The page carries what the conversation knew.** A first-time reader has
  no one to ask, so every page states what the diagram shows, explains its
  notation in a legend, and lists its elements in plain words.
- **Nothing drawn without a source.** An invented box is worse than a missing
  one, because readers trust diagrams. Every element and line comes from a
  file, a document, or a statement by the user; anything else is marked as an
  assumption on the page.

## Workflow

1. **Fix the scope and the readers.** Name the system the set is about (what
   is inside its boundary and what is external), the readers (for example
   managers, new developers, operators), and the questions they bring. Ask
   only when the boundary itself is unclear, because it changes every view;
   otherwise state the assumption and continue.
2. **Inventory the facts.** List people, software systems, containers (units
   that run or store data separately: an app, a service, a database, a
   queue), and the relationships between them, each with its source
   (`path:line`, a document, or "user"). In a codebase look at the README,
   compose files, Kubernetes manifests, infrastructure-as-code, package
   manifests, configuration and environment files, API clients, connection
   strings, and queue or topic names. Record what you could not determine as
   an open question rather than guessing.
3. **Plan the view set.** Read `references/views.md`. Choose views in this
   reading order, drawing each only when its condition holds:
   1. System context (always): who uses the system and what it depends on.
   2. Container (when the system has more than one deployable unit or data
      store): what it is made of and how the parts talk.
   3. Dynamic (one per key flow the readers care about, usually one to
      three): what happens, step by step, in one use case.
   4. Deployment (when where it runs matters: environments, network
      zones, scaling): what runs where.
   5. Component (only for a container whose inside someone asked about).
   6. System landscape (when the scope is several systems, not one).
   Never hand-draw the code level; the C4 model recommends not creating it or
   generating it with tools. Put one view on one page. Split a view that
   exceeds the element limit (checker default 20, a starting point rather
   than a standard) or mixes levels: by boundary (one component view per
   container) or by flow (one dynamic view per use case).
4. **Choose the format per view.**

   | Use | When |
   |---|---|
   | Mermaid `flowchart` in Markdown (default) | The pages live in a Git repository or any Markdown renderer; context, container, component, and deployment views |
   | Mermaid `sequenceDiagram` | Dynamic views |
   | draw.io (`.drawio` source, `.drawio.svg` on the page) | A person will rearrange or restyle the layout by hand, the diagram goes into slides or print, or exact placement matters |
   | Structurizr DSL (`workspace.dsl`) | The repository already keeps a Structurizr workspace, or the user asks for a model from which the views are generated |

   The number of views is not by itself a reason to leave Mermaid: keep names
   identical across Mermaid views by reusing each element's id and name (the
   checker warns when they drift). Do not use Mermaid `architecture-beta`: its lines cannot carry labels. Use
   Mermaid's `C4Context` family only when the reader expects that look; it
   has no automatic layout and no legend. Read only the reference for the
   chosen format: `references/mermaid.md`, `references/drawio.md`, or
   `references/structurizr.md`.
5. **Draw each view to the notation** in `references/notation.md`:
   - Title "<view type>: <scope>", for example "Container view: Library
     reservation system".
   - Every element: its name, its type and technology in brackets
     (`[Container: Python / FastAPI]`), and one line on what it is
     responsible for.
   - Every line: one direction, labelled with what flows and why; add the
     protocol from the container level down, after the words, never instead
     of them ("Reads and writes orders [SQL]", not "SQL").
   - The system boundary of a container or component view is the scope fixed
     in step 1; draw it, and mark it as an assumption when the source does not
     state the scope. Draw every other frame (network zone, deployment node,
     grouping) only where the source states it. When the source does not say
     where something sits, write that under the open questions instead of
     inventing a frame such as "outside the VPC (unconfirmed)".
   - In a deployment view, draw load balancers, ingresses, gateways, and
     firewalls as `[Infrastructure Node: technology]` with the `infra` class,
     not as containers or components.
   - The same element keeps the same id and the same name in every view.
   - Colour is never the only signal: shape, the `[Type]` text, and a dashed
     border for external systems carry the same meaning.
   - For non-engineers, describe responsibilities and lines in the words of
     the business ("reserve a book"), not of the code ("POST /reservations").
     In a view written for them (usually the system context view), write the
     type in their language too (`[人]`, `[このシステム]`, `[外部のシステム]`
     for Japanese readers; `[Person]`, `[Our system]`, `[External system]` in
     English) and give the C4 term in the legend; show no technology or
     protocol. If they need a flow, draw it at the level of people and
     systems, not containers. Point them in the index only to views written
     for them.
6. **Write the pages** from `assets/templates/view-page.md`: title, a lead of
   one to three sentences that answers the view's question, the diagram, a
   legend section whose heading contains 凡例, Legend, or Key, an element
   table (name, type, responsibility, technology, source), assumptions and
   open questions, and links to the views one level up and down. Write the
   index from `assets/templates/index.md`: every view in reading order with
   its reader and question, and the views deliberately not drawn with the
   reason. Write the pages in the user's language. Put the set where the
   repository keeps its documentation (for example `docs/architecture/`),
   or where the user says.
7. **Check.** Run the checker on the set and on any `.drawio` or `.dsl`
   source:

   ```sh
   python3 -B <this skill's base directory>/scripts/check_diagrams.py <output directory>
   ```

   Fix every `E`; fix every `W` or say on the page why it stays. Exit status
   1 means an error remains. The index is found as `README.md`, `index.md`,
   or the one top-level page without a diagram that links to the views; name
   it with `--index <file>` when that is ambiguous. Backups named
   `*.original.md` are skipped when a directory is checked. The checker checks form, not truth, so then
   re-read every view against the inventory: each element and line traced,
   nothing from one level leaking into another. Mermaid syntax is not parsed
   by the checker; if a renderer such as `mmdc` is already installed, render
   each block to catch syntax errors. Do not install one without the user's
   approval, because it downloads code and a headless browser; report the
   syntax as unrendered instead.
8. **Report** where the set is, which views it has and why, which views were
   left out and why, the assumptions and open questions, the checker result,
   and what was not verified (for example rendering).

## Reviewing existing diagrams

Run the checker first, then judge what it cannot: does each view answer one
question for one reader, are levels mixed, do names agree across views, are
labels meaningful (not "uses" or "calls"), and is every element supported by
the system's own evidence. Report findings in order of how much they mislead
a newcomer, each with its fix. Change the diagrams only when asked.

When asked to redo or rework an existing diagram file, build the new set as in
the workflow, then make the file the user named the entry point: replace its
content with the index of the new set (or with the single view, if one is
enough), so that every link to it still leads somewhere useful. Keep the
original first: as `<name>.original.md` next to it, unless the file is tracked
by Git and unchanged since its last commit, in which case Git already keeps
it; say which in the report. Mark every label or meaning inferred because the
original lacked it as an assumption on the page.

## Bundled files

| File | Read when |
|---|---|
| `references/views.md` | Planning the view set (step 3) |
| `references/notation.md` | Drawing any view (step 5); also lists the checker's codes |
| `references/mermaid.md` | The view is Mermaid |
| `references/drawio.md` | The view is draw.io |
| `references/structurizr.md` | The set is generated from Structurizr DSL |
| `assets/templates/` | Writing pages, the index, a draw.io file, or a workspace |
| `examples/library-reservation/` | A complete set that passes the checker, to imitate |
| `scripts/check_diagrams.py` | Step 7; standard library only, reads files and writes nothing |
