# Research: Refresh Portable System Prompts

**Date**: 2026-10-05 | **Spec**: [spec.md](./spec.md)

All service facts below were read from the official pages on 2026-10-05. Pages on `help.openai.com` return HTTP 403 to plain fetchers; they were read in the in-app browser.

## R1 — ChatGPT: where instructions go and how long they may be

- **Facts** (source: [Custom Instructions FAQ](https://help.openai.com/en/articles/8096356-chatgpt-custom-instructions), "Updated: 2 months ago"; [Release notes](https://help.openai.com/en/articles/6825453-chatgpt-release-notes), "Increased custom instructions limit"):
  - Web/Desktop path: Settings → Personalization → toggle **Enable customization** → **Custom Instructions** field. Mobile: Settings → **Customize ChatGPT**.
  - Limit: Free and Go **1,500** characters; Plus, Pro, Enterprise, Business, Education **5,000**.
  - Instructions apply to all chats immediately, including existing ones; no API (use system messages instead).
- **Gap**: the official page names only the **Custom Instructions** field. The current file's "More about you" field (with Nickname/Occupation) appears only in secondary sources; **no official limit** is stated for it. The current claim "two 1,500-character fields" is therefore **unverified**, and 1,500 is a plan-dependent limit, not a universal one.
- **Decision**: Keep the two-block structure (the owner's working UI has both fields) but (a) label *Custom instructions* as the documented field, (b) label *More about you* as "present in the UI, not documented officially; 1,500 kept as the conservative budget", (c) size the main block to ≤1,500 so it pastes on every plan, and state that paid plans may use up to 5,000.
- **Alternatives**: single 5,000-char block (rejected — fails on Free/Go, which the owner may also use); drop "More about you" (rejected — loses verified-by-use context placement, but flagged as unverified).

## R2 — ChatGPT: features that change what the prompt should say

- **Memory** ([Memory in ChatGPT](https://help.openai.com/en/articles/8590148-memory-in-chatgpt), updated 16 days earlier): sources include past chats, saved memories, custom instructions, Library files, connected apps; user-controlled in Settings → Personalization → Memory; temporary chats can be unpersonalized. The current file's line "Memory off—this thread only" asserts a state the prompt cannot set → **remove**.
- **Personality** ([Customizing Your ChatGPT Personality](https://help.openai.com/en/articles/11899719-customizing-your-chatgpt-personality)): "Base style and tone" works alongside custom instructions; conflicting guidance can blunt the personality. The **Efficient** personality ("immediate direct answer first") matches the owner's conclusion-first rule → recommend in the file header; keep instructions non-conflicting.
- **Models** ([GPT-5.6 and GPT-6 Pro in ChatGPT](https://help.openai.com/en/articles/20001354-gpt-56-and-gpt-6-pro-in-chatgpt), updated 3 days earlier): current options are GPT-5.6 Luna/Sol, GPT-6 Pro; on paid plans Instant does not auto-escalate and "think harder" in a prompt does not change the Thinking level. → The prompt must **not** name models and must **not** instruct the model to self-select thinking level; the owner chooses the level in the picker. Model-routing is recorded as not ported.

## R3 — Claude.ai: where instructions go

- **Facts** ([Understanding Claude's personalization features](https://support.claude.com/en/articles/10185728-understanding-claude-s-personalization-features)): account-wide field labeled **Instructions for Claude**, opened via initials menu → Settings; **no character limit documented**; Project instructions are separate and apply only within a project; Skills customize formatting/behavior on demand.
- **Decision**: Add the missing placement header (the current file has none), state that no limit is documented, and keep the block compact anyway (target ≤ ~4,000 characters, a self-imposed budget, not a service limit).

## R4 — Claude.ai: memory, models, unified Cowork

- **Memory** ([chat search and memory](https://support.claude.com/en/articles/11817273-use-claude-s-chat-search-and-memory-to-build-on-previous-context); [release notes](https://support.claude.com/en/articles/12138966-release-notes)): on by default for Free/Pro/Max; categorized Topics editable in Settings → Memory; project-scoped memory; sensitive topics excluded unless enabled (2026-08-25); chat/Cowork memory shared (2026-08-25). Memory is **maintained by Claude**, not written by instruction. The current section "Memory (use actively) … write when they emerge" over-claims control → **rewrite** as how to treat memory (context, lower priority than explicit instructions, no duplicate facts).
- **Models/surfaces**: Fable 5.1, Opus 5.5, Sonnet 5.5 are current (release notes 2026-09); chat and Cowork unified 2026-09-16. → Do not name models; do not instruct subagent delegation or parallel tool calls (not documented for Claude.ai) → **remove** "Execution Efficiency" section.
- **Authorization**: with connectors and Cowork tasks, external effects are possible → port the authorization boundary (confirm before irreversible, external, or credential-bearing actions).

## R5 — Vendor guidance on writing instructions

Source: [Claude prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices) (covers Fable 5.1, Opus 5.5, Sonnet 5.5).

- Explain *why* behind an instruction; say what to do instead of what not to do; avoid aggressive emphasis (newer models over-trigger on "CRITICAL/MUST"); be explicit about verbosity (Opus 5 defaults to longer answers — ask for concision directly).
- **Applied**: positive phrasing, one-clause rationales, no all-caps or "never/always" stacking, explicit brevity instruction.
- OpenAI publishes no comparable page for the ChatGPT custom-instructions field in what was consulted; the same principles (clear, non-conflicting, plain) are applied and **marked as applied by analogy**, not vendor-sourced.

## R6 — Source-configuration mapping (what to convey)

| Source | ChatGPT | Claude.ai |
|---|---|---|
| Governing proposition (trustworthy outcome, evidence) | convey (accuracy, verify before claiming) | convey |
| permissions.md (authorization) | convey briefly (confirm before irreversible/external/credential actions) | convey (connectors, Cowork) |
| clarifier.md (material gaps, batch, default) | convey | convey |
| pyramid-principle.md (answer first, MECE, order) | convey | convey |
| thinking-lenses.md (dependencies, branches, bounded iteration, inference strength) | convey as one compact line | convey |
| model-routing.md | **omit** — picker is user-controlled; prompt cannot change thinking level (R2) | **omit** — no documented per-request routing |
| Skills (adr, git, speckit, apple-*, DADS, scrum, …) | omit — procedure-specific, tool-dependent | omit |
| live-documentation, hooks, repo paths | omit | omit |

Current-file content to **drop**: ChatGPT "Memory off—this thread only", "Docs/Slides/Charts" style micro-rules that duplicate nothing in `.claude/` (kept only if within budget and not contradicting); Claude.ai Execution Efficiency, Memory "write actively", FURPS+/INVEST/MoSCoW/5W2H toolkits (not in current `clarifier.md` rule; they live in a skill and add length).

## Unverified / not claimed

- Official character limit of ChatGPT "More about you" (R1).
- Whether Claude.ai exposes any parallel-tool or delegation controls to chat users.

## Pre-change observation (2026-10-05, before edits)

- `chatgpt-system-prompt.md`: blocks 1,498 and 1,499 chars; assumed "two 1,500-character fields" (PP-03 fail: unverified/plan-dependent); contained "Memory off—this thread only" (PP-03 fail); no verified-facts or not-ported sections (PP-03, PP-06 fail).
- `claude-ai-system-prompt.md`: whole file used as paste text, no placement header, no field label, sections for subagent delegation, parallel tool calls and memory writing (PP-03, PP-06 fail); no fenced block.

## Post-change observation (2026-10-05)

```
chatgpt-system-prompt.md block 0 len 1498 forbidden: []
chatgpt-system-prompt.md block 1 len 1137 forbidden: []
chatgpt-system-prompt.md fenced blocks: 2
claude-ai-system-prompt.md block 0 len 2585 forbidden: []
claude-ai-system-prompt.md fenced blocks: 1
```

- PP-01: stated lengths equal measured (generated from the measured values). PP-04/PP-07: no forbidden terms (the earlier `GPT` hit was the service name "ChatGPT", not a model name; pattern tightened to `GPT-`).
- PP-02/PP-03/PP-06: every fact in both files carries a URL read on 2026-10-05; each R6 omission appears under "Not ported".
- Link check: `check_links.py --changed` → 0 errors, 0 warnings. README files do not reference the prompt files (FR-009 n/a).
- Not verified: the "More about you" limit (flagged in the file); in-product acceptance of the pasted text (not pasted into the live apps).

## Addendum 2026-10-05 — owner evidence for ChatGPT fields

The owner's Plus-plan settings screen (Settings → Personalization) shows, under the custom-instructions box, **Nickname**, **Occupation** and **More about you**, and the owner states the Plus limit is 5,000 characters. This resolves the R1 gap about the field's existence (confirmed by the owner, still absent from official help). The per-field limit for **More about you** remains undocumented. Decision change: `chatgpt-system-prompt.md` now carries a full Custom instructions block (2,878 chars, for 5,000-limit plans) plus the 1,498-char compact block for Free/Go; **More about you** stays at 1,137 chars.

## Addendum 2026-10-05 (2) — skill methods embedded (FR-011, FR-012)

Source: `.claude/skills/{minto-pyramid,problem-definition,clarifier,coder}`. Embedded as dense model-directed notation: Minto pyramid (vertical/horizontal logic, SCQ, ordering logics, pre-send check); problem definition (BABOK v3, Ishikawa 1976, A3, Kepner-Tregoe 1981; four elements; decontamination); clarifier (drift triggers, two stages, ladder of inference, ambiguity patterns, 5W2H/SMART/INVEST/GWT/MoSCoW/FURPS+/EARS/Volere/Planguage, ISO/IEC/IEEE 29148:2018 gate, 3-round bound); coder (spec-first, TDD per Beck 2002, types, OWASP Top 10 2025, ASVS 5.0, CWE, smallest change). Sizes: ChatGPT full 4,974/5,000; ChatGPT compact 1,498/1,500; Claude.ai 6,422 (self-budget raised from ~4,000 to ~7,000; no documented limit). ChatGPT carries coder as one line (owner uses it for business writing). Limitation: the unchanged compact Free/Go block does not carry the new frameworks (size).
