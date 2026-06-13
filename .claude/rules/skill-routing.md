# Skill Routing

Purpose: map each request to the one skill that should load before responding. Applies on every turn, before the first answer.

- Code implementation or behavior changes -> load `coder`.
- Produced artifacts (docs, decks, charts, translation, editing) -> load `editor`.
- Any ambiguity in requirements -> load `clarifier`. Triggers include:
  - Remaining text (after stripping slash commands and paths) is ≤ 32 characters.
  - Subject, object, or verb is absent or unclear, making intent ambiguous.
