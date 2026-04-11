# Model Selection

**Purpose**: Choose appropriate AI model based on task complexity.

---

## Default Configuration: Advisor Pattern

**Executor**: Claude Sonnet 4.6 (`sonnet` alias) — handles all generation  
**Advisor**: Claude Opus 4.6 (`opus` alias) — provides strategic guidance server-side via the built-in advisor tool

Configured in `settings.json`: `"model": "sonnet"` and `"advisorModel": "opus"`.

When Claude needs stronger judgment — a complex decision, an ambiguous failure, a problem it is circling without progress — it escalates to the advisor model for guidance, then resumes. The advisor runs server-side and uses additional tokens. For most workloads this gives near-Opus quality at near-Sonnet cost.

### Claude Code advisor tool

Claude Code has a built-in server-side advisor tool (Anthropic `advisor_20260301` API). It is activated automatically when `advisorModel` is set and a supported executor model is running.

**Supported combinations** (v2.1.101+):
- Executor `sonnet-4-6` + Advisor `opus-4-6` ← this project's default
- Executor `opus-4-6` + Advisor `opus-4-6`

**Session management** — use the `/advisor` built-in slash command:
```
/advisor opus     # set advisor to Opus (saves to user settings)
/advisor off      # disable advisor for this session
```
The `advisorModel` key in `settings.json` persists the setting across sessions for this project.

### When to call the advisor tool

Call `advisor()` **before** substantive work — not after orientation reads, but before writing, committing to an interpretation, or building on an assumption.

Also call advisor:
- When the task is believed complete (before declaring done — make the deliverable durable first)
- When stuck: errors recurring, approach not converging, results that don't fit
- When considering a change of approach
- On tasks longer than a few steps: at least once before committing to an approach, and once before declaring done

Do **not** call advisor on short reactive tasks where the next action is dictated by the tool output just read — it adds most value before the approach crystallizes.

### Advisor guidance weight

Give advice serious weight. If a step fails empirically, or primary-source evidence contradicts a specific claim (the file says X, the paper states Y), adapt. A passing self-test is not evidence the advice is wrong — it is evidence the test does not check what the advice is checking.

If retrieved data points one way and the advisor points another, surface the conflict in one more advisor call — "I found X, you suggest Y, which constraint breaks the tie?" — rather than silently switching.

---

## Decision Tree

```
Is task well-defined and simple?
├─ YES → Haiku (file ops, validation, formatting, conversion)
└─ NO
   ├─ Requires deep reasoning? → Opus (architecture, security, trade-offs)
   │                              or: use Sonnet + advisor=Opus pattern
   └─ Standard work? → Sonnet (implementation, debugging, testing, docs)
```

## Quick Reference

| Model | Use For | Examples |
|-------|---------|---------|
| **Haiku** | Simple, well-defined tasks | File I/O, format conversion, validation, search, formatting |
| **Sonnet** | Standard development (executor) | Feature implementation, debugging, tests, docs, code review |
| **Opus** | Deep reasoning or advisor role | Architecture design, security analysis, complex algorithms, critical decisions |

## Constraints

- **Default**: Sonnet as executor + Opus as advisor (via advisor tool)
- **Never** use Opus for simple file operations or formatting
- **Never** use Haiku for architecture decisions or security analysis
- **Decompose** complex work: Opus advises → Sonnet implements → Haiku validates
- **Parallelize** independent tasks across models when possible

## Cost

Relative: Haiku 1x, Sonnet 3x, Opus 15x.  
Advisor pattern cost: Sonnet bulk generation + Opus sub-inference per advisor call (typically 1,400–1,800 tokens per call). Enables near-Opus quality at near-Sonnet cost for long-horizon tasks.

---

**For detailed task decomposition examples**: Use `model-selector` agent.

**Last Updated**: 2026-04-11
