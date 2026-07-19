# Specification Quality Checklist: Codex CLI Guardrail Implementation (AGENTS.md + Native Hooks)

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-07-19
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Success criteria are technology-agnostic (no implementation details)
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
- [x] Feature meets measurable outcomes defined in Success Criteria
- [x] No implementation details leak into specification

## Notes

- This feature's subject matter is cross-agent hook and skill integration itself (Codex CLI `PreToolUse`/`PostToolUse`, `.agents/skills`; Cursor `beforeShellExecution`), so those tool/mechanism names appear as domain entities, not as an implementation choice made by this spec — consistent with the same pattern already validated in `specs/012-cross-agent-guardrail-migration/spec.md`, the decision record this feature implements.
- Revision 1: the maintainer identified, via a primary source ([learn.chatgpt.com/docs/build-skills](https://learn.chatgpt.com/docs/build-skills)), that Codex CLI natively discovers skills via `.agents/skills/`. FR-004 was revised and FR-014–FR-016, User Story 4, and SC-006 were added to supersede the original Q3 prose-transcription approach with native sync, for Codex CLI.
- Revision 2: the maintainer identified, via [learn.chatgpt.com/docs/hooks](https://learn.chatgpt.com/docs/hooks), that Codex CLI's `PreToolUse`/`PostToolUse` cover file-edit tools, not just Bash — contradicting `research.md` R4 for Codex CLI specifically. FR-002 was revised, new FRs were added, User Stories 5–6 (at the time) and SC-007–SC-009 were added.
- Revision 3: the maintainer instructed that Cursor support is explicitly out of scope for this spec. All Cursor-targeting content (the former User Story 3 Cursor destructive-command adapter, Cursor-specific FRs, the Cursor Key Entity, and Cursor mentions throughout Success Criteria and Assumptions) was removed; user stories and functional requirements were renumbered for a clean, Codex CLI-only spec (5 user stories, FR-001–FR-022, SC-001–SC-009).
- Revision 4: the maintainer supplied five further official Codex docs (customization overview, memories, agents-md, subagents, rules) for citation. Added FR-011a (AGENTS.md 32 KiB size budget) and citation-backed assumptions: AGENTS.md's discovery hierarchy (root-level file remains sufficient), Memories confirming Q13's existing treatment needs no change, and two explicitly-deferred-not-adopted design considerations (Codex's native Rules mechanism as a possible complement to the PreToolUse adapter for Q6; Codex's native Subagents mechanism as a possible future enhancement beyond Q14) — neither added to this spec's FRs/scope.
- Revision 5: the maintainer stated this spec's purpose directly — unify shareable resources so the *same* configuration applies to both Codex CLI and Claude Code — and supplied Claude Code's own official docs (features-overview, claude-directory). Confirmed Claude Code does not read `AGENTS.md` (reads `CLAUDE.md`/`.claude/rules/*.md` only) and that `.claude/skills/` and `.agents/skills/` share the identical `SKILL.md` structure. Revised FR-014 to prefer symlinks over copies for the 9 custom skills (true zero-duplication). Added User Story 6 (P2), FR-023/024, and SC-010: restructure `.claude/rules/mcp.md` (Q4, the cleanest dedup candidate) to `@path`-import `AGENTS.md` instead of duplicating it, with a documented fallback if Claude Code's `@path` import cannot target a file outside `.claude/`. Added assumptions explaining why Q1 is a deferred secondary candidate and why Q2/Q5/Q8/Q11–Q14 are not dedup candidates.
- Revision 6: the maintainer supplied MCP-specific docs (Claude Code's mcp-quickstart, Codex's customization/overview#mcp) for Q4. Confirmed Claude Code's `.mcp.json` (JSON) and Codex's `config.toml` (TOML) are incompatible connection-config formats that cannot be unified — but this doesn't affect User Story 6, since Q4's `.claude/rules/mcp.md` content is prose usage-guidance, not the connection config itself. Added a citation note; no FR/scope change.
- `/speckit-clarify` pass (2026-07-19): asked whether "align `.claude/` with official docs while unifying" extends beyond FR-023. Verified `.claude/CLAUDE.md` (87 lines, within the 200-line guideline) and all 10 `.claude/rules/*.md` files (no `paths:` frontmatter needed — content is global process guidance, not file-type-scoped) already conform; confirmed scope stays limited to FR-023. Recorded in `## Clarifications` and reflected in Assumptions (including why `.claude/agents/*.md` real subagent definitions are deliberately not added — would create a one-sided asymmetry against the already-deferred Codex TOML Subagents). All checklist items re-checked against the clarified spec and still pass.
