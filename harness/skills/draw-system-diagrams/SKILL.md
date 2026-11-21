---
name: draw-system-diagrams
description: Creates, splits, or reviews system architecture diagrams (システム構成図) as a set of views, each answering one question for one audience at one C4 level, written as Mermaid in Markdown so they are versioned with the code. Use when asked to draw, document, or review the architecture, deployment, or runtime flows of a codebase or a described system, or to untangle an overloaded diagram. Not for data charts, UI mockups, diagrams that must use a cloud vendor's official icon set, or choosing the architecture itself.
---

# Draw system diagrams

One diagram that tries to show everything shows nothing. Draw several small views, each of which answers one question for one kind of reader.

## Steps

1. **Establish the facts.** For an existing system, read them from the source: entry points, services and their manifests, infrastructure code, configuration, and CI. Mark anything inferred rather than read. For a described system, list what the person stated and what you assumed.

2. **Choose the views.** For each, write down the question it answers and who asks it. Start from the outside and add a view only when someone needs it:

   | View | Question it answers | Shows |
   |---|---|---|
   | System context (C4 level 1) | What is this system and who or what does it talk to? | The system as one box, its users, external systems |
   | Container (C4 level 2) | What are the deployable parts and how do they communicate? | Applications, data stores, queues, and the protocol on each connection |
   | Component (C4 level 3) | How is one container organized inside? | Major modules of a single container; only for the ones that need it |
   | Deployment | Where does each part run? | Environments, accounts, regions, networks, runtime services |
   | Dynamic | What happens, in order, for one scenario? | A sequence for one named use case or failure |

3. **Draw each view** in Mermaid, following `references/mermaid.md` for which diagram type to use and for syntax that renders reliably.

4. **Apply the notation rules** to every view:
   - Give it a title that states its scope and level ("Container view: order service").
   - Label every element with its name, its kind (person, web application, database, external system), and one line on what it does.
   - Label every arrow with what flows or what is asked, and the protocol where it matters ("places order - HTTPS/JSON"). Point the arrow in the direction of the call or the data, and use one meaning for arrows throughout a view.
   - Mark what is outside the system's boundary, and include a legend when shape, color, or line style carries meaning. Color is never the only carrier.
   - Keep a view to roughly fifteen elements. Beyond that, split by scenario, by subsystem, or by level.
   - Use the same name for the same thing in every view and in the code.

5. **Place the diagrams with the documentation** they explain, such as `docs/architecture/`, one view per section, with an index that lists each view and its question. Under each diagram add a short text that says what to notice; a diagram does not state its own conclusion.

6. **Check.** Confirm each view renders (Mermaid CLI, an editor preview, or the hosting site's preview; report it as not rendered when none is available). Trace every element and arrow back to the source or to a stated assumption.

## Reviewing or splitting a diagram

List the questions the diagram is trying to answer. Where there is more than one, or levels are mixed (a class beside a data center), assign each element to a view from the table and redraw. Report unlabeled arrows, elements with no stated kind, names that differ from the code, and anything that cannot be traced to the system.

## Done when

- Each view has a title, one stated question, labeled elements, and labeled arrows.
- Every element is traceable to the source or marked as an assumption.
- The views render, or the report says rendering was not checked.
