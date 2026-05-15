---
name: review
description: Review Claude Code artifacts with OpenAI Codex for code quality and security issues. Only activates when OPENAI_API_KEY is set and the codex CLI is installed.
argument-hint: "[--artifacts git-changed|user-specified|speckit-docs] [--perspectives quality,security] [<file> ...]"
user-invocable: true
disable-model-invocation: false
---

# Review: OpenAI Codex Artifact Review

Run OpenAI Codex over a selected set of artifacts and report findings for code quality and/or security. This skill is read-only — it never modifies files.

## Argument Parsing

Parse the arguments the user typed after `/review`:

**`--artifacts <mode>`** (optional)
- Allowed values: `git-changed`, `user-specified`, `speckit-docs`
- Default: `git-changed`
- Controls which files are collected for review

**`--perspectives <list>`** (optional)
- Allowed values: `quality`, `security`, or comma-separated combination `quality,security`
- Default: `quality,security`
- Controls which review lenses Codex applies

**`<file> ...`** (positional, optional)
- One or more file paths or globs
- Required when `--artifacts user-specified` is specified; ignored for other modes

If the user provides no arguments at all, use defaults: `--artifacts git-changed --perspectives quality,security`.

## Prerequisite Check

Before collecting artifacts or invoking Codex, run these two checks in order. If either fails, output the named error and stop — do not proceed.

**Check 1 — OpenAI API key**

Run in shell:
```bash
[[ -z "$OPENAI_API_KEY" ]]
```

If this returns true (the variable is unset or empty), output exactly:

```
OPENAI_API_KEY is not set. Export it with: export OPENAI_API_KEY=sk-...
```

Then halt.

**Check 2 — Codex CLI**

Run in shell:
```bash
command -v codex
```

If this returns a non-zero exit code (codex not found on PATH), output exactly:

```
`codex` is not installed. Install with: npm install -g @openai/codex
```

Then halt.

If both checks pass, proceed to Artifact Collection.

## Artifact Collection

Determine the invocation mode from `--artifacts` and build a concrete file list. All modes feed the same `codex exec` invocation downstream.

### Mode: `git-changed` (default)

Collect staged, unstaged, and untracked file paths:
```bash
{
  git diff --name-only HEAD 2>/dev/null
  git ls-files --others --exclude-standard
} | sort -u
```

If the resulting list is empty, output:
```
No reviewable artifacts found for mode git-changed.
```
Then halt. Otherwise this list is the artifact set.

### Mode: `user-specified`

Use the positional `<file>` arguments from the user's invocation as the artifact set.

If no positional arguments were provided, output:
```
No files specified. Provide file paths after --artifacts user-specified.
```
Then halt.

### Mode: `speckit-docs`

Read `.specify/feature.json` from the project root. Extract the `feature_directory` value. Enumerate all `*.md` files in that directory:
```bash
ls <feature_directory>/*.md 2>/dev/null
```

The resulting list is the artifact set. If empty, output:
```
No reviewable artifacts found for mode speckit-docs.
```
Then halt.

## Codex Invocation

Construct the review prompt based on the selected `--perspectives` and the artifact set, then invoke Codex via `codex exec`. Do NOT use the `codex review` subcommand — it ignores custom prompts and prevents per-invocation perspective control.

### Prompt construction

Build the custom instructions text. Always include the framing line. Include only the perspective sections that are selected. You may augment the perspective sections with context-specific criteria (e.g., language- or framework-specific concerns inferred from the artifact set) when it improves signal — keep additions concise and grounded in the files at hand.

```
Report findings only. Do NOT modify any files. Do NOT apply any edits. Output a structured review report.

[Include when "quality" perspective selected]
## Code Quality

For each file, evaluate:
- Correctness: logic errors, off-by-one errors, incorrect assumptions
- Naming: unclear variable/function/class names
- Readability: overly complex expressions, poor structure
- Dead code: unreachable branches, unused variables
- Error handling: unchecked returns, swallowed exceptions, missing boundary validation
- Maintainability: hard to extend or reason about

[Include when "security" perspective selected]
## Security (OWASP Top 10)

For each file, evaluate:
- Injection (SQL, command, LDAP, XPath)
- Broken authentication / session management
- Sensitive data exposure (hardcoded secrets, tokens, passwords)
- Broken access control
- Security misconfiguration
- Unsafe deserialization
- Known vulnerable component usage
- Insufficient security event logging

For each finding: file path, line number if determinable, severity (HIGH/MEDIUM/LOW), description, one-sentence fix.
If a file has no findings, note "No issues found."
```

### Shell invocation

Use `codex exec` in read-only sandbox mode for all artifact modes. Quote each file path so paths with spaces survive shell splitting:
```bash
codex exec -s read-only --ephemeral "<prompt>

Review the following files: <space-separated, shell-quoted file list>"
```

Capture stdout from this command as `CODEX_OUTPUT`.

## Output & Error Handling

### On success (Codex exits 0)

Display the review result in the conversation under this heading:

```
## Codex Review
```

Then output `CODEX_OUTPUT` verbatim below the heading.

### On Codex error (non-zero exit)

Output exactly:
```
Codex returned an error. Check that OPENAI_API_KEY is valid and that the codex CLI is up to date (npm install -g @openai/codex).
```

Do not surface raw stderr or stack traces.

## Hook Context

When this skill is invoked as an `after_implement` hook (no user arguments are passed by the hook runner), apply these defaults automatically:

- `--artifacts git-changed`
- `--perspectives quality,security`

No interactive prompting. The review result is appended to the conversation output of the implementation run.

To opt in to automatic post-implementation reviews, set `enabled: true` for the `codex-review` entry under `after_implement` in `.specify/extensions.yml`.
