# Localization & Language Rules

Purpose: keep human-facing language and persisted-artifact language predictable, so conversations feel native while the repository stays consistent for any reader. Applies to every response and every written artifact. Composes with the `domain-model` and `ubiquitous-language` skills (which already follow conversation language) and the document skills (`minto-rewriter`, `minto-builder`, `minto-reviewer`).

## Conversation language

- **Respond in the language of the current conversation.** If the user writes in Japanese, answer in Japanese; mirror a switch when the user switches.
- Keep code identifiers, commands, file paths, and standard technical terms in their canonical form (usually English) even within a non-English reply — do not translate API names or keywords.

## Persisted artifacts

- **Code, config, commit messages, and code comments**: English (the repo convention), regardless of conversation language. This keeps history readable for all contributors.
- **User-authored docs / specs / model files**: follow the conversation language, matching the surrounding document. The `domain-model` and `ubiquitous-language` skills already do this — stay consistent with the file you are editing.
- When unsure which applies, match the language already used in the target file; do not mix languages within one artifact.

## Quality (non-English target)

- Translate for **natural, professional** target language — not literal. Preserve the author's intent and the domain's ubiquitous terms.
- On first use of a technical term, give a short plain-language gloss in the target language when it aids comprehension.
