---
name: manage-git
description: Creates branches, commits, pushes, and pull requests so that history stays reviewable and nothing is published beyond what was asked. Use when the person asks for one of those operations, or when requested work needs a feature branch before the first edit. Not for read-only inspection of a repository.
---

# Manage Git

Each of committing, pushing, merging, and opening a pull request needs its own request. A request to implement something covers none of them.

## Steps

1. **Inspect.** Read the current branch, `git status`, the remotes, and the project's conventions (contribution guide, recent `git log`, pull-request template).
2. **Protect existing work.** Uncommitted changes you did not make are the person's. Leave them out of the commit and do not discard, stash, or overwrite them without asking.
3. **Do the operation that was asked for,** and only that one.
4. **Report** the resulting commit hash or pull-request URL, and anything asked for that was not done.

## Branches

- Work on a branch, not on the default branch. Follow the project's naming; otherwise `<type>/<short-kebab-summary>`, such as `fix/login-timeout`.
- Keep a branch that a project workflow already created (for example a numbered feature branch); do not rename or duplicate it.
- If another session may be using this checkout, use a separate worktree rather than switching its branch.

## Commits

- Look at the staged diff before committing, and stage files by name so that nothing unrelated or secret goes in.
- One logical change per commit, with its tests and documentation.
- Follow the project's message style. Otherwise use Conventional Commits: `<type>(<scope>): <imperative subject>` with a type such as `feat`, `fix`, `docs`, `refactor`, `test`, `build`, `ci`, `chore`. Keep the subject under 72 characters with no trailing period, and write it in the language the project's history uses.
- Use the body for why the change was made when the diff does not show it.

## Pull requests and remotes

- Push only the branch being worked on, setting its upstream on the first push.
- Title in the same style as a commit subject. Body: what the change does and why first, then how it was verified, then known limits. Link the issue or specification when there is one.
- When the sandbox blocks a push or a pull-request command the person asked for, rerun that one command through the permission prompt and say what was blocked. If that is refused, give the person the exact command. Do not reach the remote through another credential or tool.
- Retry only a failure that looks like a network fault. An authentication, permission, rejected-push, or policy failure is an answer; report it.

## Ask first

Ask immediately before any of these, naming the exact target: a hard reset, a force push, a rebase or amend of commits already pushed, `git clean`, deleting a branch, discarding uncommitted changes, and skipping hooks or required checks (`--no-verify`).

## Done when

- The requested operation, and only it, happened on the intended repository, branch, and remote.
- The commit or pull request holds one coherent change.
- The identifier and anything not done are reported.
