# Phase 0 Research: Cross-Agent Guardrail & Rule Migration Decision Record

**Status**: No `NEEDS CLARIFICATION` markers remain in `spec.md` — all 14 items were resolved during `/speckit-clarify` before this plan was generated. This document does not resolve new unknowns; it consolidates the technical findings from this session's prior investigation that the 14 recorded verdicts rely on, so a future implementation phase knows what is load-bearing and what should be re-verified before acting on it.

## R1 — Codex CLI hook coverage is Bash-only

- **Decision** (as used by Q6, Q7): Assume Codex CLI's `PreToolUse`/`PostToolUse` hooks intercept Bash tool calls only; file-edit tools (`apply_patch`, Edit/Write/Read) and MCP calls are not covered.
- **Rationale**: Multiple independent secondary sources (community docs, blog write-ups) converged on this claim; one primary-source fact was confirmed directly from `github.com/openai/codex`'s `docs/config.md` — hooks are real and layered (user/project/session, plus an admin-only `allow_managed_hooks_only` override in `requirements.toml`) — but the exact event list and its Bash-only scope were **not** independently verified against `developers.openai.com/codex/hooks` (blocked by 403 from this session on every fetch strategy tried).
- **Alternatives considered**: Treating Codex's hook coverage as equivalent to Claude Code's (rejected — no primary-source confirmation, would overstate Q7's Cursor/Codex parity) and re-attempting primary-source verification before finalizing the spec (rejected — out of scope for this feature; the spec's Assumptions accept prior-session research as given).
- **Confidence**: Medium (one layer confirmed primary-source; event-level detail unconfirmed).

## R2 — Cursor's 6 lifecycle hooks and their scope

- **Decision** (as used by Q5, Q6, Q7): Assume Cursor supports `beforeSubmitPrompt`, `beforeShellExecution`, `beforeMCPExecution`, `beforeReadFile`, `afterFileEdit`, and `stop`, each returning `{permission: allow|deny|ask, user_message, agent_message}`, with `beforeShellExecution` supporting `failClosed: true`.
- **Rationale**: Two independent `WebSearch` queries converged on the same 6 hook names and JSON shape. Direct primary-source fetches (`cursor.com/docs/hooks`, `.md` variant, Jina Reader proxy) all returned 403 in this session.
- **Alternatives considered**: None — this is the best available evidence short of primary-source access.
- **Confidence**: Medium (consistent secondary-source convergence, no primary-source confirmation).

## R3 — Cursor's `permissions.json` allowlist is explicitly not a security guarantee

- **Decision** (as used by Q6, indirectly Q5/Q7): Do not rely on Cursor's `permissions.json` allow/denylist as the enforcement mechanism for any unified guardrail; use the `beforeShellExecution` hook (with `failClosed: true`) instead.
- **Rationale**: Cursor deprecated its denylist in v1.3 after documented bypasses (Base64 encoding, shell-script wrapping, write-then-execute); Cursor's own documentation states allowlists/auto-run instructions are "best-effort convenience," not a security guarantee.
- **Alternatives considered**: Using `permissions.json` for a lighter-weight implementation (rejected — would silently reproduce a known-bypassable control for the one item, Q6, that this feature treats as the highest-priority real-enforcement candidate).
- **Confidence**: Medium-high (direct quoted claims from secondary sources, consistent across sources).

## R4 — No tool has a pre-edit (before-the-fact) file-write block

- **Decision** (as used by Q9, Q10): Both Codex CLI and Cursor lack a hook that fires *before* a file edit completes (Codex's file-edit tools aren't covered by `PreToolUse` per R1; Cursor's `afterFileEdit` fires only after the edit, and `beforeReadFile` covers reads, not writes).
- **Rationale**: Same secondary-source basis as R1/R2. This is why Q9 (main/master block) and Q10 (`.git/` block) could not receive a "reimplement natively" verdict — the maintainer chose prose-only warnings for both instead.
- **Alternatives considered**: GitHub Branch Protection as a non-agent-level replacement for Q9 was presented as the recommended option but declined by the maintainer in favor of a weaker prose note.
- **Confidence**: Medium (consistent with R1/R2's confidence level).

## R5 — `AGENTS.md` is read natively by Codex CLI and Cursor

- **Decision** (as used by all "共通化"/"弱い共通化" verdicts): Assume both target tools read a root-level `AGENTS.md` without additional configuration.
- **Rationale**: Convergent WebSearch results (industry-standard adoption claims, OpenAI's own Codex documentation excerpts surfaced via search) plus Cursor's own documented behavior (nested `AGENTS.md` support with path precedence). This is the highest-confidence finding of the whole investigation — unlike R1–R4, it was corroborated by direct quotes attributed to both vendors' own docs sites, not just third-party blogs.
- **Alternatives considered**: Per-tool instruction files (`CLAUDE.md`, a hypothetical `CODEX.md`, `.cursor/rules`) instead of one shared file (rejected for this feature — the whole premise of "共通化" is a single shared `AGENTS.md`; per-tool files remain available for tool-specific extensions but are out of scope here).
- **Confidence**: High.

## Summary

No further research is required before Phase 1. Every recorded verdict in `spec.md`'s Clarifications section traces to one of R1–R5 above (or, for the "何もしない" and "対象外" cases, to no external tool capability at all — those verdicts stand on the *absence* of a relevant hook, not a positive claim). Where a verdict's confidence is only Medium (R1–R4), the corresponding entry in `data-model.md` and the final decision record flag it as **unconfirmed against primary sources**, per FR-009.
