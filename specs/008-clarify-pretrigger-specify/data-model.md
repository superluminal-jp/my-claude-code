# Data Model: Clarify Skill Pre-Trigger on Speckit Specify

**Feature**: 008-clarify-pretrigger-specify  
**Date**: 2026-05-26

## Entities

### HookEntry (extensions.yml before_specify item)

A single entry in the `hooks.before_specify` list of `.specify/extensions.yml`.

| Field       | Type    | Required | Description |
|-------------|---------|----------|-------------|
| `extension` | string  | yes      | Human-readable identifier for the extension (e.g., `clarifier`) |
| `command`   | string  | yes      | Slash-command name; dots replaced with hyphens at invocation time |
| `enabled`   | boolean | yes      | `false` disables the hook without removing it from config |
| `optional`  | boolean | yes      | `true` → user-prompted (may skip); `false` → automatically executed |
| `prompt`    | string  | yes      | Text presented to the user when `optional: true` |
| `description` | string | yes    | One-line description shown in hook output headers |
| `condition` | string? | no       | If non-null, hook execution is deferred to HookExecutor |

**Constraint**: `command` must resolve to a registered Claude Code skill or slash command.  
**Constraint**: List order determines execution sequence. clarifier must precede ubiquitous-language and speckit.git.feature.

---

### ClarifierHookEntry (concrete instance)

The specific HookEntry added by this feature.

| Field       | Value |
|-------------|-------|
| `extension` | `clarifier` |
| `command`   | `clarifier` |
| `enabled`   | `true` |
| `optional`  | `true` |
| `prompt`    | `Run clarifier before specifying to sharpen requirements?` |
| `description` | `Elicit intent, scope, constraints, and acceptance criteria before generating the spec` |
| `condition` | `null` |

---

### ConversationContext (implicit passthrough)

Not a persisted entity — represents the mechanism by which clarifier output reaches speckit-specify.

| Attribute        | Description |
|------------------|-------------|
| `origin`         | User's original feature description (`$ARGUMENTS`) |
| `clarified_answers` | Q&A turns produced by the clarifier skill |
| `synthesis_point` | speckit-specify Outline step, where Claude reads both origin + answers |

**Constraint**: This entity exists only while Claude Code processes the conversation. It is not serialised to disk.

---

## State Transitions

```
/speckit-specify <description>
  └─► Pre-Execution Checks: process before_specify hooks in order
        │
        ├─► ClarifierHookEntry (optional: true)
        │     ├─ user skips   → ConversationContext.clarified_answers = empty
        │     └─ user answers → ConversationContext.clarified_answers = Q&A pairs
        │
        ├─► ubiquitous-language hook (optional: true)
        │
        └─► speckit.git.feature hook (optional: false → auto-execute)
              └─► Outline: spec.md generated using
                    ConversationContext.origin + ConversationContext.clarified_answers
```
