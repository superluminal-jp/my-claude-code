# Skill Routing

Purpose: map each request to the one skill that should load before responding. Applies on every turn, before the first answer.

- Resolve compound work first: a request that requires code changes and an update to an existing document routes to `coder` then `minto-rewriter`; do not collapse it to either skill alone.
- For React/Tailwind work that uses the Digital Agency Design System or dashboard guidance, load `coder` then `digital-agency-frontend` for implementation or changes; use `digital-agency-frontend` alone for review, and add `clarifier` when material product or dashboard requirements remain ambiguous.
- Code implementation or behavior changes -> load `coder`.
- Document work (produce, rewrite, or diagnose a written artifact) -> load the matching document skill:
  - Diagnose or critique the structure of an existing document, outline, or slide storyline -> `minto-reviewer` (returns analysis and target requirements, not a silent rewrite).
  - Rewrite, restructure, polish, or finalize an existing draft or document -> `minto-rewriter` (returns the finished document).
  - Build a document through dialogue from a topic, notes, or incomplete material -> `minto-builder`.
  - Mixed: diagnosis then rewrite -> reviewer first, rewriter second. Early draft with no settled conclusion -> builder, not the direct rewriter.
  - A document needs a draw.io diagram (new or edited) -> load the matching document skill (or `coder`) first, then `drawio` for the diagram-tool workflow. Same composition pattern as `digital-agency-frontend`: `drawio` never loads alone.
- Scrum and agile facilitation -> load `scrum-master`, **when Scrum or agile practice is the actual subject of the request**. Covers Scrum events (planning, daily, review, retrospective, refinement), Definition of Done, impediment removal, flow and quality metrics (velocity, burndown, cycle time, WIP), team dysfunction, and scaling frameworks (Nexus/LeSS/SAFe).
  - Route on the subject, not the vocabulary: "our stand-ups are dragging", "チームのレトロがマンネリ化している", "how do I size this sprint" all belong here even though none names the skill.
  - This entry is narrow on purpose, because it sits in the always-loaded routing list. A request does not become `scrum-master` merely because it *could* touch how a team works. A vague plea with no named artifact is still `clarifier`; a document edit is still document work; a code change is still `coder`. Ask whether the request is about Scrum practice, not whether Scrum could be relevant to it.
  - **Not** general project management. Schedules, Gantt charts, status reports, resource plans, PMBOK/PRINCE2 deliverables, and budget or milestone tracking do not route here — `scrum-master` covers Scrum and empiricism, not planning artifacts in general.
  - Compound work resolves the same way as elsewhere: a Scrum request that also asks for a finished artifact (a retrospective write-up, a sprint review deck) routes to `scrum-master` then the matching document skill — never the document skill alone, which would lose the facilitation judgement.
- After resolving compound work, route a recognizable single work category before applying generic ambiguity heuristics. A concise request that names a document and asks to create it routes to `minto-builder`; that skill elicits the missing audience, purpose, and content. Brevity alone does not override a clear artifact and action.
- If no specific category can be selected because the intended artifact, action, scope, or success condition is materially unclear, load `clarifier`. Signals include:
  - Remaining text (after stripping slash commands and paths) is ≤ 32 characters and does not identify a clear artifact plus action.
  - Subject, object, or verb is absent or unclear, making intent ambiguous.
