---
name: aws-cdk-coder
description: Design and implement AWS infrastructure with AWS CDK (TypeScript/Python) following construct patterns, least-privilege IAM, stack boundaries, and safe deploy workflows. Use when creating or changing CDK apps, stacks, constructs, cdk.json, or IaC that synthesizes to CloudFormation — including Lambda, API Gateway, DynamoDB, S3, VPC, and event-driven architectures. Composes with the coder skill for TDD/SDD and with typescript-coder or python-coder for the implementation language.
when_to_use: AWS CDK, cdk synth, cdk deploy, cdk diff, CloudFormation, construct, Stack, App, cdk.json, aws-cdk-lib, @aws-cdk, IaC, infrastructure as code, CDK Nag, aspect
---

Purpose: AWS CDK-specific implementation discipline. Applies when infrastructure is defined as CDK code. Composes with `coder` plus `typescript-coder` or `python-coder` for the app language.

# Design principles

- **L2 constructs** over L1 unless L2 lacks a required knob — then compose L1 inside a custom construct, not scattered in stacks.
- **One concern per stack** — separate stateful (data) from stateless (compute/API) when blast radius or lifecycle differs. Use **stack references** or **SSM parameters** for cross-stack values, not hard-coded ARNs.
- **Constructs encapsulate** defaults: tagging, logging, encryption, removal policy. Stacks wire constructs; avoid 200-line stack bodies.
- **Environment context** via `cdk.Environment` (account/region) — no account IDs or regions hard-coded except in documented bootstrap/config. Use **CDK context** or env vars for per-stage settings (`dev`, `staging`, `prod`).

# IAM and security

- **Least privilege** — grant actions on specific resources (`grantRead`, `grantWrite`, scoped policies). No `*` actions on `*` resources unless a documented platform requirement.
- **Encryption at rest** by default (S3, DynamoDB, RDS, SQS). **TLS** for data in transit.
- **No secrets in source** — use Secrets Manager, SSM SecureString, or CDK `SecretValue`. Never commit `.env` with credentials.
- Run **cdk-nag** or project compliance aspects when available; fix or suppress with documented reasons.

# Resource patterns

| Service | Defaults |
|---|---|
| Lambda | Explicit timeout, memory, env; dead-letter queue for async; log retention set |
| API Gateway | Throttling, auth (Cognito/IAM/Lambda authorizer) at the edge |
| DynamoDB | On-demand or auto-scaling per spec; PITR when data is durable |
| S3 | Block public access; encryption; lifecycle rules for logs/backups |
| SQS/SNS | DLQ on queues; KMS when compliance requires |

- **RemovalPolicy**: `RETAIN` for production data stores unless the spec says ephemeral. `DESTROY` only for dev/sandbox with explicit approval.
- **Tagging**: apply `Environment`, `Project`, `Owner` (or repo standard) via `Tags.of(scope)`.

# Workflow

1. **Read existing app entry** (`bin/`, `lib/`, `stacks/`) — match naming, stage pattern, and construct library.
2. **Implement** in constructs first; wire in stacks.
3. **`cdk synth`** — inspect generated template for unexpected resources or overly broad IAM.
4. **`cdk diff`** before deploy — summarize material changes to the user (IAM, deletion, replacement).
5. **Deploy** only with explicit user confirmation for shared or production accounts.

Use **AWS IaC MCP** (`search_cdk_documentation`, `validate_cloudformation_template`) when API details or template validation are needed.

# Testing

- **assertions** (`Template.fromStack`) for unit tests — snapshot only when the team already snapshots; prefer explicit `hasResourceProperties` / `hasResource` checks.
- Test **construct defaults** (encryption, IAM scoping) in the construct's test file.
- Integration tests against real AWS only when the project has a harness — otherwise synth-level tests suffice.

# Anti-patterns

- Monolithic single stack for unrelated services
- `env` omitted on `Stack` (environment-agnostic lookups hiding wrong-account deploys)
- Inline policies copied across stacks instead of shared constructs or managed policies
- `cdk deploy --all` without reviewing diff in shared accounts
- Hard-coded VPC IDs, subnet IDs, or ARNs from a developer's account

# Before reporting done

- [ ] `cdk synth` succeeds; no unexpected IAM `*` expansions
- [ ] Construct/stack tests pass
- [ ] README or `docs/` updated for new stacks, context keys, or deploy steps
- [ ] User informed of `cdk diff` highlights if deploy is in scope

# Related skills

- **Always** → `coder`
- **CDK app language** → `typescript-coder` or `python-coder`
- **Ad-hoc AWS operations** (no CDK change) → `aws-cli-coder`
- **Significant irreversible architecture choice** → `adr` skill
