# Planning the view set

A view set is chosen from the readers and their questions, not from the
diagram types a tool offers. This file gives the C4 model's view types with
the reader each is for, when to draw it, what belongs in it and what does
not, and where it goes in an arc42 document.

## Terms

- **Stakeholder, concern, view, viewpoint** (ISO/IEC/IEEE 42010:2022,
  *Software, systems and enterprise — Architecture description*): a
  stakeholder is a person or group with an interest in the system; a concern
  is a matter of interest to them (cost, who it talks to, where it runs); a
  view expresses the architecture from the perspective of those concerns; a
  viewpoint is the convention used to build such a view. This skill turns
  them into practice by having the index list, for every view, its reader
  (stakeholder) and its question (concern).
- **Software system**: the highest level of abstraction; something that
  delivers value to its users, human or not.
- **Container**: a separately running or separately deployed unit inside a
  software system that executes code or stores data: a web application, a
  mobile app, a service, a database, a file store, a queue. Not a Docker
  container specifically.
- **Component**: a grouping of related functionality behind an interface
  inside one container.
- **Boundary**: a dashed frame that groups elements belonging to the same
  system, container, organisation, or deployment node.

## View types

The C4 model has a core set of four static structure diagrams (system
context, container, component, code) and three supporting diagrams (system
landscape, dynamic, deployment), and says to use only the levels that add
value.

| View | Question it answers | Reader (C4 model) | Draw when | Contains | Leaves out | arc42 section |
|---|---|---|---|---|---|---|
| System context | Who uses the system, and which other systems does it depend on? | Everybody, technical and non-technical | Always | The one system as a box; people; external systems; labelled relationships | Technology choices, containers, protocols beyond the essentials | 3 Context and Scope |
| Container | What is the system made of, and how do the parts talk? | Technical people: architects, developers, operations | The system has more than one deployable unit or data store | Containers inside the system boundary with technology; the people and external systems they touch; protocols on every line | Components, classes, servers, replicas | 5 Building Block View (level 1) |
| Component | What is inside this one container? | Architects and developers | Someone asked how a specific container is organised | Components of one container with technology; the containers and systems they call | Other containers' insides, code-level detail | 5 Building Block View (level 2) |
| Code | How is this component implemented? | Architects and developers | Do not hand-draw; the C4 FAQ recommends not creating it or generating it on demand with tooling | — | — | — |
| Dynamic | What happens, step by step, in this one use case? | Technical and non-technical | A flow that readers ask about: a purchase, a sign-in, a nightly batch | Numbered interactions between the elements of one level, in order | Branches that belong to another flow; elements not taking part | 6 Runtime View |
| Deployment | What runs where, in this one environment? | Technical people, including infrastructure and operations | Environments, network zones, scaling, or hosting matter to the reader | Deployment nodes (environment, region, cluster, server, managed service) as nested boundaries; container instances inside them; infrastructure nodes (load balancer, ingress, gateway, firewall); the lines between them | Other environments (draw one view per environment) | 7 Deployment View |
| System landscape | Which systems exist in this organisation, and how do they relate? | Technical and non-technical | The scope is several systems rather than one | Software systems and people, without the inside of any one system | Containers | 3 Context and Scope (enterprise scope) |

## Units and splitting

- One view per page, one page per question. If two questions come up for the
  same diagram ("who uses it" and "how is it hosted"), they are two views.
- One level per view. A database inside the system context view, or a server
  inside the container view, is a level leaking; move it to the level where
  it belongs and link the pages.
- Split a view that grows past the element limit (the checker's default is
  20; this number is a starting point, not a standard — the C4 model gives
  none). Split a container view by subsystem boundary, a component view by
  container, and a dynamic view by use case.
- Draw a deployment view per environment that a reader needs (production
  first); do not overlay environments.
- The system boundary in a container or component view is the scope chosen
  for the set; mark it as an assumption when the source does not state it.
  Draw any other frame (network zone, deployment node, grouping) only where
  the source states it. An element whose placement is unknown stays outside
  those frames and appears in the open questions; a frame labelled
  "unconfirmed" reads as a claim.
- Write a view for one kind of reader. A view for non-engineers (usually the
  system context view, or a flow between people and systems) uses their
  words for types and lines and shows no technology; the index points each
  reader only to the views written for them.
- Keep ids and names identical across views, so that "API" in the container
  view is visibly the same thing as "API" in the deployment view.

## Notations outside the default

Use these only when the user or their organisation asks for them; their
symbols must be learned before the diagram can be read.

| Notation | Use for |
|---|---|
| UML 2.5.1 (Object Management Group) sequence, deployment, or component diagrams | A team that already reads UML and needs its precise semantics |
| ArchiMate 3.2 (The Open Group) | Enterprise architecture across business, application, and technology layers |
| BPMN 2.0 (ISO/IEC 19510) | Business processes rather than system structure — out of this skill's scope |

## Sources

- C4 model, diagrams and their audiences: <https://c4model.com/diagrams>,
  <https://c4model.com/diagrams/system-context>,
  <https://c4model.com/diagrams/container>,
  <https://c4model.com/diagrams/component>,
  <https://c4model.com/diagrams/code>,
  <https://c4model.com/diagrams/dynamic>,
  <https://c4model.com/diagrams/deployment>,
  <https://c4model.com/diagrams/system-landscape>,
  <https://c4model.com/diagrams/faq>
- arc42 sections 3, 5, 6, 7: <https://docs.arc42.org/section-3/>,
  <https://docs.arc42.org/section-5/>, <https://docs.arc42.org/section-6/>,
  <https://docs.arc42.org/section-7/>
- ISO/IEC/IEEE 42010:2022: <https://www.iso.org/standard/74393.html>. The
  standard is paywalled; the terms above are paraphrased, not quoted.
- C4 abstractions (software system, container, component), paraphrased:
  <https://c4model.com/abstractions>
- UML 2.5.1: <https://www.omg.org/spec/UML/2.5.1>; ArchiMate 3.2:
  <https://pubs.opengroup.org/architecture/archimate32-doc/>; BPMN 2.0.2:
  <https://www.omg.org/spec/BPMN/2.0.2>. Named for orientation only.
