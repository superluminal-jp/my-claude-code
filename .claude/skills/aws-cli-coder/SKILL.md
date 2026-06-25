---
name: aws-cli-coder
description: Run and script AWS operations with AWS CLI v2 using explicit profiles/regions, JMESPath queries, pagination, dry-run safety, and least-privilege patterns. Use when invoking aws commands, writing shell scripts against AWS APIs, debugging live resources, or performing one-off ops — EC2, S3, IAM, Lambda, CloudFormation, STS, logs. Composes with the coder skill for scripting discipline and security boundaries.
when_to_use: aws cli, aws s3, aws ec2, aws lambda, aws iam, aws cloudformation, aws sts, aws logs, JMESPath, --profile, --region, AWS CLI, boto3 companion scripts, shell AWS
---

Purpose: AWS CLI v2 operational discipline. Applies when interacting with AWS via the CLI or thin shell wrappers — not when defining infrastructure in CDK (use `aws-cdk-coder`). Composes with `coder` for scripting, validation, and security.

# Command hygiene

- **AWS CLI v2** syntax. Always set **`--region`** and **`--profile`** explicitly (or confirm `AWS_REGION` / `AWS_PROFILE` env) — never assume the default account.
- **`--output json`** (or `table` for human inspection) for scripting; parse with **`jq`**, not fragile `grep`/`awk` on tables.
- **`--query`** with JMESPath to fetch only needed fields — reduces noise and accidental data exposure in logs.
- **`--no-cli-pager`** (or `export AWS_PAGER=""`) in non-interactive automation so commands do not block.
- Prefer **`aws <service> help`** and **`aws <service> <op> help`** over guessing flag names.

# Safety

- **`--dry-run`** when the service supports it (EC2, IAM policy simulation, etc.) before mutating calls.
- **Destructive operations** (`delete`, `terminate`, `remove`, `purge`, `empty`) require explicit user confirmation — state resource IDs and account/region in the prompt.
- **No secrets on the command line** — use env vars, `aws secretsmanager get-secret-value`, or files with restrictive permissions. Warn if the user pastes keys into chat.
- **Idempotency**: check existence (`describe`, `head-object`, `get-function`) before create; use conditional flags where available.
- **Least privilege**: suggest minimal IAM actions; do not recommend `AdministratorAccess` for routine tasks.

# Pagination and limits

- Use **`--page-size`** and **`--max-items`** / **`--starting-token`** (or `aws <svc> paginate` where available) — never assume a single page returns all results.
- For high-volume reads, filter at the API with `--query` rather than downloading everything locally.

# Common patterns

```bash
# Who am I — run before destructive work in an unfamiliar shell
aws sts get-caller-identity --profile "$PROFILE" --region "$REGION"

# S3 copy with encryption (match bucket policy)
aws s3 cp src s3://bucket/key --sse AES256 --profile "$PROFILE" --region "$REGION"

# Tail Lambda logs (replace group name)
aws logs tail "/aws/lambda/FnName" --follow --profile "$PROFILE" --region "$REGION"
```

- **CloudFormation**: prefer `describe-stacks`, `describe-stack-events` for triage; use `delete-stack` only with confirmation.
- **S3**: `s3api` for precise control; `s3 sync` with `--delete` only when the user explicitly wants mirror-delete behavior.
- **IAM**: `simulate-principal-policy` to validate permissions before blaming "access denied".

# Scripting

- **`set -euo pipefail`** in bash scripts; quote variables; pass ARNs/IDs as arguments, not interpolated unchecked strings.
- Capture **`$?`** and stderr on failure; print actionable errors (service, operation, error code).
- Use **`aws configure list`** / **`sts get-caller-identity`** at script start when the target account must be verified.

# When to use CDK instead

If the operation will be repeated, shared across environments, or reviewed as infrastructure — **propose `aws-cdk-coder`** rather than growing a permanent shell script. CLI is for inspect, debug, bootstrap, and one-off migrations.

# Before reporting done

- [ ] Caller identity and region confirmed for mutating commands
- [ ] Output verified (not just exit code 0)
- [ ] No credentials echoed in terminal output or logs
- [ ] Scripts documented with required profile, region, and prerequisites

# Related skills

- **Always** → `coder` when writing or changing scripts
- **Infrastructure as code** → `aws-cdk-coder`
- **Python automation** → `python-coder` for boto3-heavy tooling
