# Quickstart: Clarify Skill Pre-Trigger on Speckit Specify

## What this does

When you run `/speckit-specify <description>`, the clarifier skill fires first and asks targeted questions to sharpen intent, scope, and acceptance criteria. The clarified answers are incorporated into the generated spec automatically via conversation context.

## Enabling the hook

Add the following entry as the **first** item under `before_specify` in `.specify/extensions.yml`:

```yaml
hooks:
  before_specify:
    - extension: clarifier
      command: clarifier
      enabled: true
      optional: true
      prompt: Run clarifier before specifying to sharpen requirements?
      description: Elicit intent, scope, constraints, and acceptance criteria before generating the spec
      condition: null
    # ... existing hooks below (ubiquitous-language, speckit.git.feature, etc.)
```

## Usage

```
/speckit-specify <feature description>
```

The playbook will display:

```
## Extension Hooks

**Optional Pre-Hook**: clarifier
Command: `/clarifier`
Description: Elicit intent, scope, constraints, and acceptance criteria before generating the spec

Prompt: Run clarifier before specifying to sharpen requirements?
To execute: `/clarifier`
```

Run `/clarifier` to start the clarification session, answer the questions, then continue with the specify workflow.

## Skipping clarification

To skip for a single invocation: do not invoke `/clarifier` when prompted and proceed.

To disable project-wide: set `enabled: false` in the hook entry.

## Order matters

The clarifier hook must appear **before** `ubiquitous-language` and `speckit.git.feature` in the list so requirements are clarified before UL validation and branch creation run.
