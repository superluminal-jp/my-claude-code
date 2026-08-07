---
status: Proposed
date: 2026-08-07
deciders: repository maintainer
---

# 0004. Adopt AWS's official deploy-on-aws plugin

## Context and problem statement

This repository needs AWS architecture diagrams that are validated against
official AWS4 icon conventions and, ideally, generated from the actual
CDK/CloudFormation/Terraform in a codebase rather than hand-drawn. AWS
publishes exactly this capability as the `aws-architecture-diagram` skill —
but only bundled inside its `deploy-on-aws` Claude Code plugin
(`awslabs/agent-plugins`, marketplace name `agent-plugins-for-aws`), alongside
a second skill, `deploy`, that analyzes a codebase, recommends AWS services,
estimates cost, generates IaC, and — given AWS CLI credentials — can deploy it.
Claude Code plugins install as one unit; there is no way to take
`aws-architecture-diagram` without also taking `deploy`. Adopting the plugin
therefore means granting this repository's Claude Code sessions a live-AWS-
deployment capability it does not have today, as the price of the diagram
capability it does want.

## Decision drivers

- Diagram correctness for AWS-specific architecture (icon set, legends, dark
  mode) is better sourced from AWS itself than reimplemented by hand.
- Codebase-driven diagram generation (reading actual CDK/CloudFormation/
  Terraform) is a capability this repository's own `drawio` skill does not
  have and cannot easily replicate.
- Granting deployment capability is a blast-radius change (`rules/
  permissions.md`) that must be a deliberate, recorded decision, not a side
  effect of wanting a diagram tool.

## Considered options

- Adopt `deploy-on-aws` in full (diagram skill + deploy skill together).
- Hand-port only the diagramming *ideas* (AWS4 icon validation, legends, dark
  mode) into this repository's own `.claude/skills/drawio/SKILL.md`, without
  installing the plugin or gaining any deployment capability.
- Do nothing; keep generating AWS diagrams through the generic `drawio` skill
  and its bundled AWS4 shape search only.

## Decision outcome

We will adopt `deploy-on-aws` in full via `install.sh` (`claude plugin
marketplace add awslabs/agent-plugins`, then `claude plugin install
deploy-on-aws@agent-plugins-for-aws`), accepting the `deploy` skill's
capability as the cost of the AWS-vendored `aws-architecture-diagram` skill,
because codebase-driven, AWS-validated diagrams were judged to outweigh
hand-porting a subset of the same behavior and maintaining it independently
of AWS's own upstream.

### Consequences

- Positive: architecture diagrams for AWS workloads can be generated directly
  from the actual IaC in a project, with AWS-maintained AWS4 icon validation,
  instead of hand-assembled `drawio` XML.
- Positive: cost estimation and CDK/CloudFormation generation become available
  as a byproduct, without separate integration work.
- Negative: this repository's Claude Code sessions gain the ability to
  generate and, given AWS CLI credentials, actually deploy infrastructure to
  AWS — a materially larger blast radius than any capability this repository
  granted before. No credentials are provisioned by this change itself, but
  the capability is now present whenever they are.
- Negative: three additional MCP servers enter the toolset (`awsiac`,
  `awsknowledge`, `awspricing`). `awsknowledge` points at the same endpoint
  (`https://knowledge-mcp.global.api.aws`) as this repository's own
  `aws-knowledge` server under a different name — redundant registration, not
  a conflict, left as-is because the two entries are consumed under different
  names by different tooling.
- Negative: the `aws-architecture-diagram` skill's validation step requires
  Python `defusedxml>=0.7.1`, a system dependency `install.sh` does not
  install or check for.
- Negative: `aws-architecture-diagram` does not use `@drawio/mcp` — AWS
  diagrams and non-AWS diagrams in this repository are now produced by two
  independent code paths with different validation and export mechanics.

## Confirmation

Re-running `install.sh` is idempotent for this step (`claude plugin
marketplace list` / `claude plugin list` checks before adding or installing).
There is no automated fitness function for the deployment blast radius; the
control is this ADR plus `rules/permissions.md`'s existing requirement that
destructive or blast-radius actions be confirmed before execution.

## More information

- [`awslabs/agent-plugins`](https://github.com/awslabs/agent-plugins) —
  plugin source, `deploy-on-aws` plugin manifest and `.mcp.json`.
- [`docs/adr/0001-remove-vendored-speckit-skills.md`](0001-remove-vendored-speckit-skills.md) —
  establishes this repository's operative distinction: depend on an upstream
  when it has a real generator/release process (Spec Kit's `specify init`
  there; AWS's own maintained plugin repo here), vendor a local copy only
  when no such upstream exists (the opposite call in
  [ADR 0003](0003-vendor-scrum-master-skill.md), where the source skill had
  neither).
- [`.claude/skills/drawio/SKILL.md`](../../.claude/skills/drawio/SKILL.md) —
  the non-AWS diagram path this decision leaves unchanged.
