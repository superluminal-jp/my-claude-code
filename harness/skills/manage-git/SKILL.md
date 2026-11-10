---
name: manage-git
description: Create branches, commits, pushes, and pull requests so that history stays reviewable and nothing is published beyond what was asked. Use when the person explicitly asks for one of those operations, or when a requested implementation needs its feature branch created before the first edit. Do not use for read-only repository inspection, and do not take a request to implement as authorization to commit, push, or open a pull request.
metadata:
  kind: worker
  permission: external_effect
  sandbox: network
  network-hosts: the repository's remote host, for push and pull-request operations only
  produces: the requested Git operation, with its identifier and what was not done
---

# Manage Git state

Keep repository history reviewable without extending the person's authorization from implementation into publication.

## Steps

1. **Inspect before changing.** Read the current branch, the status, the remotes, and the project's conventions.
2. **Treat uncommitted changes as the person's** unless their origin is known. Preserve unrelated files; never discard or rewrite them to simplify the task.
3. **Do only the operation that was asked for.** Committing, pushing, merging, and opening a pull request each need their own request; authorization for one does not cover another. Create or switch branches only when the requested workflow needs it, and never write directly to a protected trunk branch.
4. **Show the exact target before a consequential write,** and prefer non-interactive commands.
5. **Report** the resulting commit or pull-request identifier, the verification evidence, and anything not performed.

## Branches

- Follow the repository's branch grammar when it has one. Otherwise use `<type>/<short-kebab-summary>` with a conventional change type and a specific outcome.
- Keep a numbered feature branch that a structured feature workflow already created; do not rename or duplicate it.
- Keep a branch to one coherent outcome. Remove it after integration only when removal is authorized.

## Commits

- Use Conventional Commits: `<type>(<scope>)?: <imperative subject>`. Follow the repository's types when it defines them; otherwise use the smallest fitting one of `feat`, `fix`, `docs`, `refactor`, `test`, `perf`, `build`, `ci`, `style`, `chore`, `revert`.
- Aim for a subject of 50 characters or fewer and never exceed 72. No trailing period.
- Keep one logical change, with its tests and synchronized documentation, in one commit. Do not mix cleanup into it.
- Inspect the staged diff before committing.

## Pull requests and remote operations

- Use the same subject grammar for the title. In the body put the conclusion first, then what changed, why, how it was verified, and any known limitation; link stable requirements or issues when there are any.
- Push only the designated branch, and set its upstream explicitly on the first push.
- Retry only a failure that is plausibly transient, with bounded backoff. Authentication, authorization, rejected-history, policy, and validation failures are not network noise.
- Inside the Bash sandbox, a push or a pull-request command needs the remote host. When the sandbox blocks it, report the host and stop; do not work around the sandbox.

## Safety boundaries

- Ask for explicit authorization immediately before a destructive or hard-to-recover operation: a hard reset, a forced push, cleaning untracked files, rewriting history, deleting a branch, overwriting uncommitted work.
- Never bypass hooks, required checks, review policy, or branch protection unless the person explicitly authorizes a documented exception and the environment permits it.

## Done when

- The requested operation, and only that operation, happened on the intended repository, branch, and remote.
- The diff or commit holds one coherent change with its tests and documentation.
- The verification results, the remote state changes, and anything not performed are reported.

## Sources

- Conventional Commits 1.0.0: <https://www.conventionalcommits.org/en/v1.0.0/>
- Git documentation: <https://git-scm.com/docs>
