# Skill Routing

Purpose: map each request to the one skill that should load before responding. Applies on every turn, before the first answer.

- Resolve compound work first: a request that requires code changes and an update to an existing document routes to `coder` then `minto-rewriter`; do not collapse it to either skill alone.
- Code implementation or behavior changes -> load `coder`.
- Document work (produce, rewrite, or diagnose a written artifact) -> load the matching document skill:
  - Diagnose or critique the structure of an existing document, outline, or slide storyline -> `minto-reviewer` (returns analysis and target requirements, not a silent rewrite).
  - Rewrite, restructure, polish, or finalize an existing draft or document -> `minto-rewriter` (returns the finished document).
  - Build a document through dialogue from a topic, notes, or incomplete material -> `minto-builder`.
  - Mixed: diagnosis then rewrite -> reviewer first, rewriter second. Early draft with no settled conclusion -> builder, not the direct rewriter.
- After resolving compound work, route a recognizable single work category before applying generic ambiguity heuristics. A concise request that names a document and asks to create it routes to `minto-builder`; that skill elicits the missing audience, purpose, and content. Brevity alone does not override a clear artifact and action.
- If no specific category can be selected because the intended artifact, action, scope, or success condition is materially unclear, load `clarifier`. Signals include:
  - Remaining text (after stripping slash commands and paths) is ≤ 32 characters and does not identify a clear artifact plus action.
  - Subject, object, or verb is absent or unclear, making intent ambiguous.
