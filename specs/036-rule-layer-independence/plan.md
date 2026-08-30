# Implementation Plan: Independent Configuration Pyramid

**Branch**: `036-rule-layer-independence` | **Date**: 2026-08-30 | **Spec**: [spec.md](./spec.md)

## Summary

Rebuild the authored Claude Code configuration from the top downward. First replace the apex's mixed value/routing/registry outline with one outcome and three lifecycle conditions. Then reduce the unconditional rule layer to five independent universal concerns. Move conditional Git and cloud-documentation guidance into self-describing skills and remove the central routing rule. Finally, make authored skills expose their own operation/domain boundary, remove upward and sibling dependencies, preserve package-owned resources, and synchronize tests and durable documentation.

The hierarchy is semantic: children support a parent's proposition without the parent naming them. Horizontal MECE is evaluated within one classification principle at a time. The apex uses lifecycle stage; universal rules use quality concern; skills use two independent axes, lifecycle operation and domain overlay.

## Technical Context

**Language/Version**: Markdown, YAML front matter, POSIX-compatible shell tests  
**Primary Dependencies**: Claude Code project memory/rules/skills loading behavior; existing repository shell test harness  
**Storage**: Repository files only  
**Testing**: New `tests/run-config-pyramid.sh`; existing `tests/run-*.sh`; `git diff --check`; frontmatter and relative-link checks  
**Target Platform**: Claude Code configuration installed by `install.sh`  
**Project Type**: Configuration, skills, documentation, and regression tests  
**Performance Goal**: Reduce unconditional bytes below the captured 20,126-byte baseline  
**Constraints**: Top-down red→green; no modification of vendored DADS archive; no loss of Git, provider-research, safety, documentation, or routing behavior; no commit/push  
**Scale/Scope**: 1 apex, 8 existing rules normalized to 5, 8 existing authored skills revised, 2 on-demand skills added, supporting authored resources, 1 structural suite, synchronized README/design/ADR/test docs

## Constitution Check

The Spec Kit constitution remains an unfilled template, so repository governance is evaluated directly:

- **Accuracy and grounding**: Architecture choices are tied to current official Claude Code documentation and the cited primary structural source; inference is labelled in `research.md`.
- **Verifiability**: Every structural claim has an offline check or an explicit human relation-table review.
- **Traceability**: The revised spec, research decisions, data model, checklist, tasks, and Proposed ADR retain alternatives and consequences.
- **Human control**: No commit, remote publication, destructive operation, or ADR acceptance is included.
- **Live documentation**: Runtime configuration, installer-facing README content, design guide, ADR, and tests change together.

**Gate result**: PASS. The prior design failed the current request because it permitted downward citations and treated two heterogeneous skill axes as one sibling set; those constraints are explicitly superseded.

## Architecture

### Semantic hierarchy

```text
Trusted outcome under user control
├── Define the right work
├── Execute it safely and proportionately
└── Hand off a verified, understandable, durable result
```

The five universal rules support exactly one branch:

| Rule concern | Apex branch | Excludes |
|---|---|---|
| Requirements certainty | Define | Permission decisions and formal implementation procedure |
| Internal reasoning | Define | Reader-facing organization |
| Authorization and safety | Execute | Ambiguity elicitation and tool-specific workflow |
| External expression | Hand off | Documentation source-of-truth policy |
| Documentation integrity | Hand off | General answer structure and Git history policy |

### Conditional skills

Skill selection uses two independent axes:

1. **Lifecycle operation**: formalize requirements; implement/configure; record an architectural decision; create, diagnose, or transform a communication artifact; perform Git collaboration; research cloud-platform documentation.
2. **Domain overlay**: apply Scrum accountability; apply Digital Agency React/Tailwind constraints.

Multiple matches are expected across axes. Within the document-operation group, source maturity and requested outcome make creation, diagnosis, and transformation mutually exclusive for a single phase; a request for diagnosis followed by transformation legitimately selects two sequential phases.

## Project Structure

```text
.claude/
├── CLAUDE.md
├── rules/
│   ├── clarifier.md
│   ├── thinking-lenses.md
│   ├── permissions.md
│   ├── pyramid-principle.md
│   └── live-documentation.md
└── skills/
    ├── {clarifier,coder,adr}/SKILL.md
    ├── {minto-builder,minto-reviewer,minto-rewriter}/SKILL.md
    ├── {scrum-master,digital-agency-frontend}/...
    ├── git-workflow/SKILL.md
    └── cloud-platform-research/SKILL.md

tests/run-config-pyramid.sh
docs/claude-config-design.md
docs/mcp-servers.md
docs/adr/0015-rule-layer-independence.md
README.md
README.ja.md
```

The removed `git-workflow.md`, `mcp.md`, and `skill-routing.md` rule paths are intentionally absent.

## Implementation Sequence

1. Add a failing structural contract and record the 20,126-byte unconditional baseline.
2. Rewrite and validate the apex alone.
3. Compare all rule nodes to the finalized apex and each other; rewrite five concerns, then remove three heterogeneous rules.
4. Compare skill descriptions to the finalized apex/rules and to same-axis siblings; revise existing packages and add two replacements.
5. Update repository documentation, ADR, and legacy tests after runtime structure is stable.
6. Run Spec Kit analysis, the structural suite, every repository suite, link/frontmatter/archive checks, and whitespace validation.

## Complexity Tracking

| Choice | Why needed | Simpler alternative rejected |
|---|---|---|
| Two skill-selection axes | Operation and domain intentionally compose; forcing one sibling list creates false overlap | One flat MECE list cannot classify DADS implementation or Scrum artifacts without duplication |
| Two new conditional skills | Preserves useful Git and provider guidance while removing it from unconditional context | Deletion would violate behavior preservation; keeping rules would violate one-topic universal rule design |
| Structural test plus relation table | Syntax scans cannot prove semantic MECE, while manual review alone regresses silently | Either mechanism by itself leaves a known verification gap |

## Post-design Constitution Check

**PASS**. The design reduces unconditional context, preserves conditional behavior, keeps owned resources encapsulated, adds durable regression evidence, and introduces no remote or irreversible action. ADR-0015 remains Proposed.
