# Skill Routing

Purpose: what the skill descriptions cannot tell you — how skills combine, where they stop, how to break a tie. Names, descriptions and trigger phrases are already in context; no list is kept here.

## Resolve compound work first

A request spanning two categories routes to both, in order — never collapse it to one:

- Code change **and** an update to an existing document → `coder`, then `minto-rewriter`.
- React/Tailwind work using the Digital Agency Design System → `coder`, then `digital-agency-frontend`; that skill alone for review; add `clarifier` if product or dashboard requirements stay ambiguous.
- Scrum work that also wants a finished artifact (retrospective write-up, sprint review deck) → `scrum-master`, then the document skill. The document skill alone loses the facilitation judgement.

## Boundaries

- **Document skills**: diagnosis then rewrite → reviewer first, rewriter second. An early draft with no settled conclusion → `minto-builder`, not the rewriter.
- **`scrum-master` is not general project management.** Schedules, Gantt charts, status reports, resource plans, PMBOK/PRINCE2 deliverables, budget and milestone tracking do not route here. Ask whether the request is *about* Scrum practice, not whether Scrum could be relevant to it.

## Tie-breaks

- A recognizable work category beats generic ambiguity heuristics. A concise request naming a document and asking to create it routes to `minto-builder` — that skill elicits the missing audience and purpose. Brevity alone does not override a clear artifact plus action.
- Fall back to `clarifier` only when the artifact, action, scope, or success condition is materially unclear: after stripping slash commands and paths the text is ≤32 characters with no artifact plus action, or subject, object, or verb is absent.
