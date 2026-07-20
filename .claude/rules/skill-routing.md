# Skill Routing

Purpose: map each request to the one skill that should load before responding. Applies on every turn, before the first answer.

- Code implementation or behavior changes -> load `coder`.
- Document work (produce, rewrite, or diagnose a written artifact) -> load the matching document skill:
  - Diagnose or critique the structure of an existing document, outline, or slide storyline -> `minto-reviewer` (returns analysis and target requirements, not a silent rewrite).
  - Rewrite, restructure, polish, or finalize an existing draft or document -> `minto-rewriter` (returns the finished document).
  - Build a document through dialogue from a topic, notes, or incomplete material -> `minto-builder`.
  - Mixed: diagnosis then rewrite -> reviewer first, rewriter second. Early draft with no settled conclusion -> builder, not the direct rewriter.
- Any ambiguity in requirements -> load `clarifier`. Triggers include:
  - Remaining text (after stripping slash commands and paths) is ≤ 32 characters.
  - Subject, object, or verb is absent or unclear, making intent ambiguous.
