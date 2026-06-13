# Implementation Plan: Claude Code Personal Configuration Optimization

**Branch**: `claude/speckit-claude-code-settings-lrldfc` | **Date**: 2026-06-13 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/010-claude-config-optimization/spec.md`

## Summary

Refresh the personal Claude Code configuration under `.claude/` so it (1) gives deliberate, testable guidance for Memory and Subagent usage, (2) trims standing context to the minimum a current Claude model needs while preserving every enforced behavior, (3) states the intent of each rule and skill, (4) keeps hooks lean and purposeful without weakening safety guards, (5) conforms to the repo's own Live Documentation principles, and (6) adds a lightweight internal design→plan→task discipline for non-Spec-Kit tasks. The approach is edit-in-place of Markdown/JSON/shell config, gated by a **behavior inventory** that enumerates every currently enforced behavior so trimming can be proven loss-free.

## Technical Context

**Language/Version**: Markdown (CLAUDE.md, rules, skills), JSON (`settings.json`), Bash (`.claude/hooks/*.sh`). No application runtime.

**Primary Dependencies**: Claude Code harness (settings schema `json.schemastore.org/claude-code-settings.json`); Spec Kit `0.8.14.dev0` for the `/speckit-*` workflow; lint toolchain (`jq`, `shellcheck`, `shfmt`, `yamllint`) provisioned by `session-start.sh`.

**Storage**: Plain files in the repository; no database. Standing-context size measured in lines/characters of `CLAUDE.md` plus imported rules.

**Testing**: Manual/behavioral verification against the behavior inventory and `quickstart.md`; shell hooks validated with `shellcheck`/`shfmt`; JSON validated with `jq`. No automated test framework exists for prose config.

**Target Platform**: Claude Code (CLI, web, desktop, IDE) on Linux/macOS; remote web containers gated by `CLAUDE_CODE_REMOTE=true` in `session-start.sh`.

**Project Type**: Configuration / documentation set (not a code library or service).

**Performance Goals**: Reduce standing (always-loaded) context by ≥20% (SC-002) with zero behavior loss; keep each `CLAUDE.md`-imported file ≤200 lines (SC-008).

**Constraints**: Behavior preservation outranks length reduction; safety hooks (credential/destructive/secret-scan) must remain functionally identical; English-documentation convention retained; edits stay within project-scope `.claude/` (user-scope only via `install.sh` sync path).

**Scale/Scope**: 1 root `CLAUDE.md`, 1 `.claude/CLAUDE.md`, 7 rule files, 5 owner skills (coder, editor, clarifier, domain-model, ubiquitous-language), 6 hook scripts, 1 `settings.json`. Spec Kit skills (`speckit-*`) are vendored and out of scope.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

`.specify/memory/constitution.md` is the **unratified template** (placeholder principles only). No ratified principles exist, so there are no formal gates to evaluate. The repo's de-facto governing standards used as proxy gates for this feature:

- **Minimal change** (`.claude/CLAUDE.md` Core Principles): do only what is requested. → Honored: edit-in-place, no new frameworks.
- **Live Documentation** (`.claude/rules/live-documentation.md`): proximity, no redundancy, explicit intent. → This feature's FR-010 directly enforces it on the config itself.
- **No behavior loss**: encoded as the behavior-inventory gate (FR-012).

**Result**: PASS (no ratified constitution to violate; proxy standards satisfied). No entries in Complexity Tracking.

## Project Structure

### Documentation (this feature)

```text
specs/010-claude-config-optimization/
├── plan.md              # This file
├── research.md          # Phase 0: best-practice decisions
├── data-model.md        # Phase 1: config artifact inventory + planned change per file
├── quickstart.md        # Phase 1: how to validate the optimized config
├── contracts/
│   └── behavior-inventory.md   # Enforced behaviors that MUST survive (the gate)
├── checklists/
│   └── requirements.md  # Spec quality checklist (from /speckit-specify)
└── tasks.md             # Phase 2 output (/speckit-tasks — not created here)
```

### Source Code (repository root)

The "source" being modified is the configuration tree:

```text
CLAUDE.md                       # root: imports .claude/CLAUDE.md + SPECKIT plan pointer
.claude/
├── CLAUDE.md                   # standing context: principles, response style, skill routing, MCP
├── settings.json               # model, permissions, hook wiring
├── rules/
│   ├── advisor.md              # answer-quality baseline
│   ├── clarifier.md            # clarification gate
│   ├── live-documentation.md   # doc-drift enforcement (imported → standing context)
│   ├── mcp.md                  # MCP catalog + usage rule
│   ├── permissions.md          # deny/ask/allow policy
│   ├── skill-routing.md        # routing triggers (imported → standing context)
│   └── tools.md                # tool-preference + Subagents section (target for Memory+Subagent guidance)
├── skills/
│   ├── coder/SKILL.md          # in scope: intent line + trim
│   ├── editor/SKILL.md         # in scope
│   ├── clarifier/SKILL.md      # in scope
│   ├── domain-model/SKILL.md   # in scope (322 lines — largest owner skill)
│   ├── ubiquitous-language/SKILL.md  # in scope (160 lines)
│   └── speckit-*/SKILL.md      # OUT OF SCOPE (vendored)
└── hooks/
    ├── session-start.sh        # lint toolchain bootstrap (web only)
    ├── pre-bash.sh             # destructive/network/credential command guard
    ├── pre-edit.sh             # .git/main-branch/sensitive-path guard
    ├── post-edit-format.sh     # format + lint edited files
    ├── user-prompt-submit.sh   # secret-scan submitted prompts
    └── speckit-expand-update.sh # refresh Spec Kit before /speckit-* (UserPromptExpansion)
```

**Structure Decision**: Single configuration tree edited in place. The two files imported into every session (`.claude/CLAUDE.md` via root `CLAUDE.md`, plus `skill-routing.md` and `live-documentation.md` it `@`-imports) form the **standing context** — the primary optimization target. All other rules/skills load on demand and are optimized for intent + length but weigh less on the ≥20% reduction metric.

## Complexity Tracking

> No constitution violations. Section intentionally empty.
