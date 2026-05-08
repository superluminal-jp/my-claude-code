# Quickstart: Ubiquitous Language Skill

**Feature**: 003-ubiquitous-language
**Date**: 2026-05-09

## What this skill does

Single slash command `/ubiquitous-language` that:
- Creates `docs/ubiquitous-language.md` and `docs/context-map.md` on first run
- Surfaces queued domain vocabulary candidates for review on subsequent runs
- Passively collects business event expressions from conversation without interrupting

---

## Implementation Checklist

### Step 1: Rewrite SKILL.md

Overwrite `.claude/skills/ubiquitous-language/SKILL.md` with the simplified playbook:
- Pre-check: detect `docs/ubiquitous-language.md` presence
- Bootstrap flow (file absent)
- Maintenance flow (file present)
- Passive collection rules
- Invariants section (diff-before-write, no silent writes, no speckit references)

Reference: `contracts/skill-interface.md` for exact flow and output formats.

### Step 2: Update UL template

Update `.claude/skills/ubiquitous-language/ubiquitous-language-template.md` to:
- Use `docs/ubiquitous-language.md` as the target path (not `.specify/ubiquitous-language/`)
- Use `## Bounded Context: <name>` heading format (not abbreviated "BC")
- Include `## Watchlist` section

### Step 3: Update context-map template

Update `.claude/skills/ubiquitous-language/context-map-template.md` to:
- Use `docs/context-map.md` as the target path
- Remove any `.specify/` references

### Step 4: Update CLAUDE.md routing rule

In `.claude/CLAUDE.md` under `## Skills (mandatory routing)`, replace the `ubiquitous-language` line per `contracts/extensions-yml-additions.md`.

---

## Validation Steps

### Test 1: Bootstrap (User Story 1)

In a project without `docs/ubiquitous-language.md`:
1. Type `/ubiquitous-language`
2. Expected: skill announces file absence, asks for business events
3. Provide 3–5 events; expected: skill drafts UL entries, shows diff, creates files on confirmation
4. Verify `docs/ubiquitous-language.md` and `docs/context-map.md` created

### Test 2: Maintenance (User Story 2)

With `docs/ubiquitous-language.md` present:
1. Have a conversation that mentions domain terms
2. Type `/ubiquitous-language`
3. Expected: batch proposal of detected candidates
4. Accept some, skip others; verify file updated after confirmation

### Test 3: Passive collection + natural pause (User Story 3)

1. Send a message: 「注文が確定されると在庫引当が走ります」
2. Send a follow-up with no business vocabulary: 「ありがとうございます」
3. Expected: after the second message, batch proposal surfaces the queued candidates

### Test 4: No speckit references (SC-003)

Read `.claude/skills/ubiquitous-language/SKILL.md` and `.claude/CLAUDE.md`:
- Confirm no occurrence of "speckit", "spec-kit", or speckit command names

### Test 5: Watchlist management (FR-012)

1. Type `/ubiquitous-language`
2. When prompted, add a custom vague term (e.g., 「エンティティ」)
3. Confirm; verify `## Watchlist` section in `docs/ubiquitous-language.md` updated
