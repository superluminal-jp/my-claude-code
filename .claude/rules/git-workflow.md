# Git Workflow Rules

Purpose: make every commit, branch, and PR follow one observable, reviewable standard, so history reads as intent. Applies whenever Claude commits, branches, or opens a PR (including this session's own git operations). Grounded in Conventional Commits 1.0.0 and trunk-based development. Composes with `permissions.md` (git writes stay on `ask`) and `live-documentation.md` (docs move with code).

## Commit messages — Conventional Commits

Format: `<type>(<scope>)?: <subject>` — imperative mood, ≤72-char subject, no trailing period.

- **Types**: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `perf`, `build`, `ci`.
- **Body** (optional): wrap at 72 cols; explain *why*, not *what* (the diff shows what).
- **Breaking change**: append `!` after type/scope (`feat!:`) and add a `BREAKING CHANGE:` footer.
- **One logical change per commit** — do not bundle unrelated edits. If a change spans code + its doc/test, that is one logical change and belongs in one commit (Live Documentation).

## Branch naming

`<type>/<short-kebab-summary>` (e.g. `feat/order-confirmation`, `fix/null-cart`). Spec Kit features follow the `/speckit-git-feature` numbering; do not hand-name those.

## Pull requests

- **Title**: same Conventional Commits grammar as a commit subject.
- **Body**: *What / Why / How verified* — link the spec or issue; state how the change was tested. Keep it scannable (BLUF, lists).
- Do **not** open a PR unless the user explicitly asks (see harness rules).

## Safety and mechanics

- `git push -u origin <branch>`; on network failure retry up to 4× with exponential backoff (2s/4s/8s/16s).
- Commit or push **only when asked**; never push to a branch other than the designated one without explicit permission.
- Destructive git operations (`reset --hard`, `push --force`, `clean -f`) require confirmation — see `permissions.md`.
- Never commit secrets or files matching the credential-safety list in `permissions.md`.
