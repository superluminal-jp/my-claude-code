# Skill: ubiquitous-language

Purpose: maintain a project's Ubiquitous Language — capture domain vocabulary from conversation, organize it in `docs/ubiquitous-language.md`, and surface cross-context conflicts in `docs/context-map.md`. Applies when the conversation introduces domain terms or business-event expressions, or when asked to build/update the glossary. Grounded in Evans' Domain-Driven Design ubiquitous-language and bounded-context concepts.

**Language**: Respond in the language of the current conversation. All examples in this file are in English; adapt to the conversation language at runtime.

## Pre-check

At every invocation:

1. Check whether `docs/ubiquitous-language.md` exists in the current project root.
   - Absent → **Bootstrap Flow**
   - Present → **Maintenance Flow**

2. Maintain an in-session candidate queue (not persisted to disk):

   | Field | Description |
   |---|---|
   | `candidate_term` | Detected term |
   | `source_text` | Source sentence (quoted) |
   | `trigger_type` | `new-concept` / `vague-term` |
   | `detected_at` | Conversation turn number |

---

## Bootstrap Flow

**Trigger**: `docs/ubiquitous-language.md` does not exist.

### Step 1 — Announce absence

Announce that no Ubiquitous Language file exists and that the elicitation session is starting. Briefly explain the purpose: a UL is a shared glossary that lets developers and domain experts use the same words with the same meanings.

### Step 2 — Business-event elicitation

Ask an opening question focused on **events**, not nouns:

> "Please list 5–10 things that actually happen in the business. Examples: 'Order confirmed', 'Invoice issued', 'Stock reserved'."

### Step 3 — Extract terms from each event

For each event provided, elicit:
1. **Actor**: Who triggers this event?
2. **Precondition**: What must be true for this event to occur?
3. **Outcome**: What changes after this event?
4. **Exception**: When does this event fail?

### Step 4 — Draft 7-field entries

For each term identified, create one table row:

| Field | Requirement |
|---|---|
| Term | Canonical domain term (in original project language) |
| Definition | What it means, including states and behaviors (single row) |
| Context | Which Bounded Context |
| States / Rules | State transitions in arrow notation (`A→B→C`); constraints |
| Examples | What is included |
| Counter-examples | What is excluded |
| Implementation name | Class / method / table / API / event / UI label name(s) |

Mark any field the user cannot yet provide as `[NEEDS DOMAIN INPUT]`. Re-surface at the next invocation.

### Step 5 — Show diff and confirm

Present the proposed contents of:
- `docs/ubiquitous-language.md` — file header, optional `## Watchlist` section, and one `## Bounded Context: <name>` section per context identified
- `docs/context-map.md` — empty table (header row only)

If `docs/` does not exist, note that it will be created.

**Do not write any file until the user confirms.**

On confirmation: create `docs/` if absent, then write both files.

---

## Maintenance Flow

**Trigger**: `docs/ubiquitous-language.md` exists.

### Step 1 — Surface queued candidates

Present all terms detected in the current session as a batch proposal:

```
## Ubiquitous Language — Update Candidates

The following terms were detected. Add or update?

| Action | Term | Source | Proposed definition | Bounded Context |
|--------|------|--------|---------------------|-----------------|
| [+] New | <term> | <source> | <proposed definition> | <context> |
| [!] Vague | <term> | <source> | → <replacement candidates> | — |

Reply: "Add all" / "1 only" / "Skip" / "1: [custom definition]"
```

If the queue is empty, skip to Step 2.

### Step 2 — Watchlist scan

Scan recent conversation for vague or overloaded terms. The default watchlist targets common placeholder words; read the `## Watchlist` section of `docs/ubiquitous-language.md` for project-specific additions and removals.

For each hit: quote the exact location and propose UL-registered replacements.

### Step 3 — Re-surface incomplete entries

Scan `docs/ubiquitous-language.md` for rows containing `[NEEDS DOMAIN INPUT]`. Present each for completion.

### Step 4 — Bounded Context conflict check

If the same term appears in multiple Bounded Context sections with differing definitions, present:

> "The term '[term]' has different definitions in [Context A] and [Context B]. How would you like to resolve this?"

Options:
1. **Separate by context** — Keep distinct entries per context with different implementation names.
2. **Rename in one context** — Rename the term in one context to eliminate the conflict.

On resolution: update `docs/context-map.md` with the appropriate relation type.

### Step 5 — Watchlist management

Offer to add or remove project-specific watchlist terms. Proposed changes are written to the `## Watchlist` section of `docs/ubiquitous-language.md`.

### Step 6 — Show cumulative diff and confirm

Present a diff of all proposed changes to `docs/ubiquitous-language.md` and `docs/context-map.md`.

**Do not write any file until the user confirms.**

---

## Passive Collection

During any conversation turn, **without interrupting the response**, monitor user messages for:

- Business event expressions (past-tense or passive verb+noun: e.g., "order confirmed", "stock reserved")
- Domain role names (noun + role suffix: e.g., "billing manager", "fulfillment team")
- State names (adjective + noun indicating a stage: e.g., "pending approval", "in transit")

Add each detection to the in-session queue with `source_text` and `trigger_type = new-concept`.

**Surface queued candidates as a batch when**:
- Queue has ≥ 1 entry, AND
- The preceding turn contained no new business-vocabulary candidates

**If `docs/ubiquitous-language.md` is absent** and vocabulary is detected: propose the Bootstrap Flow instead of silently queuing.

If no domain vocabulary is detectable in the conversation, do not activate.

---

## Invariants

1. **Diff before write**: Every write to `docs/ubiquitous-language.md` or `docs/context-map.md` is preceded by presenting the proposed diff.
2. **Explicit confirmation**: No file is written without explicit user confirmation.
3. **No silent Bounded Context unification**: Conflicts always present the split-or-rename choice; never silently merge definitions across contexts.
4. **Single-row entries**: UL table rows must fit a single row; prompt the user to restructure multi-paragraph definitions into the 7-field form.
