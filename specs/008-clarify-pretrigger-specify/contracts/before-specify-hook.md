# Contract: before_specify Hook Entry (extensions.yml)

**Feature**: 008-clarify-pretrigger-specify  
**Date**: 2026-05-26

## Overview

This contract defines the YAML structure for a `before_specify` hook entry in `.specify/extensions.yml`. Any hook registered here is processed by the speckit-specify playbook before spec generation begins.

## Schema

```yaml
hooks:
  before_specify:
    - extension: <string>       # Identifier (no spaces; used in hook output headers)
      command: <string>         # Slash command base name; dots → hyphens at runtime
      enabled: <boolean>        # false suppresses the hook without removing it
      optional: <boolean>       # true = user-prompted; false = auto-execute
      prompt: <string>          # Shown to user when optional: true
      description: <string>     # One-line summary shown in hook output
      condition: <string|null>  # null = always run; non-null = HookExecutor evaluates
```

## Behaviour Contract

### optional: true (user-prompted hook)

Output emitted by speckit-specify playbook:

```
## Extension Hooks

**Optional Pre-Hook**: {extension}
Command: `/{command}`
Description: {description}

Prompt: {prompt}
To execute: `/{command}`
```

The user decides whether to invoke the hook. If skipped, the playbook continues to the next hook.

### optional: false (mandatory hook)

Output emitted by speckit-specify playbook:

```
## Extension Hooks

**Automatic Pre-Hook**: {extension}
Executing: `/{command}`
EXECUTE_COMMAND: {command}

Wait for the result of the hook command before proceeding to the Outline.
```

The playbook executes the hook immediately and waits for completion before proceeding.

## ClarifierHookEntry (this feature)

```yaml
- extension: clarifier
  command: clarifier
  enabled: true
  optional: true
  prompt: Run clarifier before specifying to sharpen requirements?
  description: Elicit intent, scope, constraints, and acceptance criteria before generating the spec
  condition: null
```

**Invariants**:
- Must appear as the **first** entry in `before_specify` (before ubiquitous-language and speckit.git.feature).
- `command: clarifier` resolves to `/clarifier` at runtime (no dot substitution needed).
- Setting `enabled: false` disables the hook for the project without affecting other hooks.
