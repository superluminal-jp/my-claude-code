# Git Workflow Rules

Purpose: make every commit, branch, and PR follow one observable, reviewable standard, so history reads as intent. Applies whenever Claude commits, branches, or opens a PR (including this session's own git operations). Grounded in Conventional Commits 1.0.0, the Tim Pope / Pro Git commit-message conventions (the 50/72 rule and imperative mood), and trunk-based development (see [References](#references)). Composes with `permissions.md` (git writes stay on `ask`) and `live-documentation.md` (docs move with code).

## Commit messages — Conventional Commits

Format: `<type>(<scope>)?: <subject>` (Conventional Commits 1.0.0).

- **Types**: only `feat` and `fix` are mandated by the spec; `docs`, `refactor`, `test`, `chore`, `perf`, `build`, `ci`, `style`, `revert` follow the Angular / `@commitlint/config-conventional` set.
- **Subject**: imperative mood ("add", not "added"/"adds"); aim for ≤50 characters (hard cap 72); no trailing period. The length and mood come from Tim Pope / Pro Git — the Conventional Commits spec itself sets no length limit.
- **Body** (optional): separate from the subject with one blank line; wrap at 72 columns; explain *why*, not *what* (the diff shows what).
- **Footers**: follow the git trailer convention — `Token: value` (e.g. `Co-Authored-By: …`, `Refs: #123`).
- **Breaking change**: indicate with `!` before the colon (`feat!:`) **or** a `BREAKING CHANGE:` footer — either alone satisfies the spec; add the footer when the migration impact needs describing (`BREAKING-CHANGE:` is a synonymous token).
- **One logical change per commit** — do not bundle unrelated edits. If a change spans code + its doc/test, that is one logical change and belongs in one commit (Live Documentation).

## Branch naming

`<type>/<short-kebab-summary>` (e.g. `feat/order-confirmation`, `fix/null-cart`). Spec Kit features follow the `/speckit-git-feature` numbering; do not hand-name those.

Keep branches **short-lived** (trunk-based development): branch off the trunk (default branch), integrate back frequently — within roughly a day — and delete the branch after merge; avoid long-lived divergent branches.

## Pull requests

- **Title**: same Conventional Commits grammar as a commit subject.
- **Body**: *What / Why / How verified* — link the spec or issue; state how the change was tested. Keep it scannable (BLUF, lists).
- Do **not** open a PR unless the user explicitly asks (see harness rules).

## Safety and mechanics

- `git push -u origin <branch>`; on network failure retry up to 4× with exponential backoff (2s/4s/8s/16s).
- Commit or push **only when asked**; never push to a branch other than the designated one without explicit permission.
- Destructive git operations (`reset --hard`, `push --force`, `clean -f`) require confirmation — see `permissions.md`.
- Never commit secrets or files matching the credential-safety list in `permissions.md`.

## References

- Conventional Commits 1.0.0 — <https://www.conventionalcommits.org/en/v1.0.0/>
- Tim Pope, "A Note About Git Commit Messages," 2008 (origin of the 50/72 rule and imperative mood) — <https://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html>
- Pro Git (Chacon & Straub), 2nd ed., "Distributed Git — Commit Guidelines" — <https://git-scm.com/book/en/v2/Distributed-Git-Contributing-to-a-Project>
- Trunk-Based Development — <https://trunkbaseddevelopment.com/>
