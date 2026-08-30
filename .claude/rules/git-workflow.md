# Git Workflow Rules

Purpose: repository-specific git conventions. What the model and harness already do — Conventional Commits grammar, imperative mood, trailer placement, committing only when asked — is not restated here.

## Commits

- **Conventional Commits 1.0.0**: `<type>(<scope>)?: <subject>`, imperative, ≤50 chars (hard cap 72), no trailing period. Types beyond `feat`/`fix` follow the Angular set.
- **One logical change per commit.** Code plus its doc or test is *one* logical change and belongs in one commit (Live Documentation).

## Branches

- `<type>/<short-kebab-summary>` — e.g. `feat/order-confirmation`, `fix/null-cart`.
- **Spec Kit features are exempt**: they follow `/speckit-git-feature` numbering. Do not hand-name those.
- Keep branches short-lived: branch off the trunk, integrate back within roughly a day, delete after merge.

## Pull requests

- **Title**: same grammar as a commit subject.
- **Body**: *What / Why / How verified* — link the spec or issue, state how the change was tested. Scannable: BLUF, lists.

## Mechanics

- `git push -u origin <branch>`; on network failure retry up to 4× with exponential backoff (2s/4s/8s/16s).
- Never push to a branch other than the designated one without explicit permission.
- Destructive git operations require confirmation — see `permissions.md`.
