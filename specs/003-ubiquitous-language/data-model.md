# Data Model: Ubiquitous Language Skill Simplification

**Feature**: 003-ubiquitous-language
**Date**: 2026-05-09

## Overview

This feature is implemented as a Claude Code skill (Markdown playbook). "Data model" here refers to file schemas and state transitions, not database schemas.

---

## 1. `docs/ubiquitous-language.md`

Single file containing all UL data for the project.

### File Structure

```markdown
# Ubiquitous Language

**Project**: <project-name>
**Last Updated**: YYYY-MM-DD
**Total Entries**: N

## Watchlist

<!-- Project-specific additions to the default vague-term watchlist -->
**Add**: <term1>, <term2>
**Remove**: <term3>

## Bounded Context: <name>

| 用語 | 定義 | 文脈 | 状態/ルール | 例 | 反例 | 実装名 |
|------|------|------|-----------|-----|------|--------|
| ...  | ...  | ...  | ...       | ... | ...  | ...    |
```

### UL Table Schema

| Field | Required | Description |
|---|---|---|
| 用語 | yes | Canonical domain term (original language) |
| 定義 | yes | What it means, including states and behaviors (single row) |
| 文脈 | yes | Which Bounded Context |
| 状態/ルール | stateful terms: yes | State transitions in arrow notation (`A→B→C`); constraints |
| 例 | yes | What is included |
| 反例 | yes | What is excluded |
| 実装名 | yes | Class/method/table/API/event/UI label name(s) |

**Incomplete entries**: any missing required field → marked `[NEEDS DOMAIN INPUT]`; re-surfaced on next `/ubiquitous-language` invocation.

### Watchlist Section

- Default watchlist (built into skill): `データ, 情報, 処理, 管理, ステータス, フラグ, 有効, 完了, 対象, ユーザー`
- **Add**: terms appended to default list for this project
- **Remove**: terms removed from default list for this project
- Section is optional; if absent, default watchlist applies

### Bounded Context Sections

- Heading format: `## Bounded Context: <name>` (not abbreviated "BC")
- One section per Bounded Context
- Entry count budget per section: ≤ 30 (configurable)
- When budget exceeded: skill proposes consolidation or Bounded Context split before adding new entry

---

## 2. `docs/context-map.md`

Records cross-Bounded-Context term relationships.

### File Structure

```markdown
# Context Map

**Project**: <project-name>
**Last Updated**: YYYY-MM-DD

| 用語 | Context A | Context B | 関係種別 | 備考 |
|------|-----------|-----------|---------|------|
```

Created at bootstrap alongside `docs/ubiquitous-language.md` with empty table (header row only). Entries added when a Bounded Context conflict is resolved.

### Relationship Types

| 種別 | 意味 |
|------|------|
| `same-name-different-meaning` | Same term, different meanings per context |
| `synonym` | Different terms, same concept |
| `identical` | Same term, same meaning across contexts |
| `refines` | One context's definition is a specialization of the other |

---

## 3. Candidate Queue (in-session memory only)

Not persisted to disk. Held in working memory for the session duration.

| Field | Description |
|---|---|
| `candidate_term` | Detected candidate term |
| `source_text` | Source sentence (quoted) |
| `trigger_type` | `new-concept` / `vague-term` / `drift` |
| `detected_at` | Conversation turn number |

Cleared when session ends or when all candidates are accepted/rejected by user.

---

## 4. Entry Lifecycle

```
[Draft / NEEDS DOMAIN INPUT]
  ↓ user provides missing fields
[Complete Entry]
  ↓ implementation name diverges in AI-generated artifact
[Drift Warning] → user resolves → [Complete Entry]
```

---

## 5. File Lifecycle

```
[Absent]
  ↓ /ubiquitous-language triggered + business vocab detected
[Bootstrap: docs/ created, ubiquitous-language.md + context-map.md created]
  ↓ ongoing /ubiquitous-language invocations
[Growing UL]
  ↓ entry count > 30 in a section
[Split Proposal] → user approves → [New Bounded Context section added]
  ↓ project matures
[Stable UL]
```
