---
name: Permission Rules
description: Permission and access control best practices for Claude Code
type: rules
---

# Permission Rules

## Destructive Operations

Always confirm before executing:
- `rm -rf` or equivalent recursive deletion
- `git reset --hard` (discards uncommitted work)
- `git push --force` or `git push -f` (overwrites remote history)
- `git clean -f` (deletes untracked files)
- Dropping database tables or collections
- Overwriting files with uncommitted changes

## Credential Safety

Never read, display, log, or commit:
- `.env` and `.env.*` files
- Files in `secrets/`, `credentials/`, `.aws/`, `.ssh/` directories
- Any file whose name contains `secret`, `credential`, `token`, or `key`
- Private keys (`.pem`, `.p12`, `.pfx`)

## Network Access

Default deny for:
- `curl | bash` patterns
- Downloading and executing scripts from external URLs
- Requests to non-HTTPS endpoints unless localhost

## Permission Evaluation Order

deny → ask → allow (first matching rule wins; deny always takes precedence)
