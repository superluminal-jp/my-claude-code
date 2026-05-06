# Skill Routing

- Code implementation or behavior changes -> load `coder`.
- Produced artifacts (docs, decks, charts, translation, editing) -> load `editor`.
- Any ambiguity in requirements -> load `clarifier`. Triggers include:
  - Remaining text (after stripping slash commands and paths) is ≤ 32 characters.
  - Subject, object, or verb is absent or unclear, making intent ambiguous.
