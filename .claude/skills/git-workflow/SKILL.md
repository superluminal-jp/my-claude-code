---
name: git-workflow
description: Manage Git collaboration state for branches, commits, pushes, and pull requests. Use when the user explicitly asks for one of those write operations or when a requested implementation requires creating its feature branch before edits. Do not use for read-only repository inspection or infer authorization to commit, push, or open a pull request. Apply alongside every independently matching work procedure, creating a required branch first and performing commit or publication only after the logical change and its verification are complete.
---

# Git Workflow

Keep repository history reviewable without extending the user's authorization from implementation into publication.

## Establish authority and state

1. Inspect the current branch, status, remotes, and relevant project conventions before changing Git state.
2. Treat uncommitted changes as user-owned unless their origin is known. Preserve unrelated files and never discard or rewrite them to simplify the task.
3. Create or switch branches only when required by the requested workflow. Do not write directly to a protected trunk branch.
4. Commit, push, merge, or open a pull request only when the user requested that operation. Authorization for one does not imply authorization for the others.

## Branches

- Follow a repository-defined branch grammar when present. Otherwise use `<type>/<short-kebab-summary>` with a conventional change type and a specific outcome.
- Preserve a numbered feature branch already established by a structured feature workflow; do not hand-rename or duplicate it.
- Keep a branch focused on one coherent outcome and remove it after integration only when removal is authorized.

## Commits

- Use Conventional Commits: `<type>(<scope>)?: <imperative subject>`.
- Follow repository-defined types when present. Otherwise use the smallest fitting type from `feat`, `fix`, `docs`, `refactor`, `test`, `perf`, `build`, `ci`, `style`, `chore`, or `revert`.
- Aim for a subject of 50 characters or fewer and never exceed 72 characters. Do not add a trailing period.
- Keep one logical change—including its tests and synchronized documentation—in one commit. Do not mix drive-by cleanup into it.
- Inspect the staged diff before committing and report the resulting commit identifier and verification evidence.

## Pull requests and remote operations

- Use the same subject grammar for a pull-request title.
- Put the conclusion first in the body, then explain what changed, why, how it was verified, and any known limitation; link stable requirements or issues when available.
- Push only the designated branch and set upstream explicitly on its first push.
- Retry only failures that are plausibly transient, with bounded exponential backoff. Do not retry authentication, authorization, rejected-history, policy, or validation failures as though they were network noise.

## Safety boundaries

- Require explicit authorization immediately before destructive or hard-to-recover operations, including hard reset, forced push, cleaning untracked files, history rewriting, branch deletion, and overwriting uncommitted work.
- Never bypass hooks, required checks, review policy, or branch protection unless the user explicitly authorizes a documented exception and the environment permits it.
- Prefer non-interactive commands and show the exact target before any consequential write.

## Completion check

- The requested Git operation—and only that operation—occurred on the intended repository, branch, and remote.
- The diff or commit contains one coherent change with its tests and documentation.
- Verification results, remote state changes, and anything not performed are reported explicitly.

## References

- [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)
- [Git documentation](https://git-scm.com/docs)
