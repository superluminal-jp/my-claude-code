---
paths:
  - ".github/workflows/*.{yml,yaml}"
  - "**/action.{yml,yaml}"
---

# GitHub Actions

- Declare `permissions` explicitly, starting from `contents: read` and adding a scope only to the job that needs it; the default token is broader than most jobs need.
- Pass untrusted values (issue and pull-request titles and bodies, branch names, commit messages, anything under `github.event`) to a script through `env:` and read them as quoted shell variables. Interpolating `${{ }}` directly into `run:` lets that text execute as shell.
- Pin a third-party action to a full commit SHA with the version in a comment; a tag can be moved to different code. Follow the repository's existing convention for first-party `actions/*`.
- Keep secrets out of logs and out of `pull_request_target` or `workflow_run` jobs that check out or run code from a fork.
- Authenticate to a cloud provider with OpenID Connect and a short-lived role rather than a stored long-lived key when the provider supports it.
- Set `timeout-minutes` on each job and a `concurrency` group on workflows where a newer run makes an older one pointless.
- Check the change with `actionlint` when it is installed. A local check does not reproduce GitHub's runners, permissions, or secrets, so say in the report that the workflow is unverified until it has run on GitHub.
