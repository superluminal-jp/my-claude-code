# Skill: ubiquitous-language

Purpose: maintain a project's shared business vocabulary as durable, version-controlled memory — capture terms, events, roles, states, and rules from everyday work (conversation and code), organize them in `docs/ubiquitous-language.md`, and surface cross-context conflicts in `docs/context-map.md`. Runs **always-on** alongside other skills (like agent Memory), not only during explicit DDD work. Grounded in Evans' Ubiquitous Language and Bounded Context concepts, but surfaced to users as "用語・ルールの記録" unless they use DDD vocabulary themselves.

**Language**: Respond in the language of the current conversation. All examples in this file are in English; adapt to the conversation language at runtime.

## Always-on Memory Layer

This skill loads on **every turn** with the primary skill. It does not replace Claude Memory (`autoMemoryEnabled`); it persists **project domain meaning** in repo docs.

| Layer | Persists | Audience |
|---|---|---|
| Claude Memory | harness preferences, conventions, locations | agent across sessions |
| `docs/ubiquitous-language.md` | business terms, rules, events | team + agent |
| `docs/models/` | structure (via `domain-model`) | team + agent |

**Operating mode during active work**:

1. Run Passive Collection silently — never delay or block the primary answer.
2. Queue candidates in-session; dedupe by canonical term.
3. Surface a batch proposal only at a **natural pause** (see Passive Collection).
4. Prefer **incremental** updates (1–3 terms) over a full bootstrap session unless the user asks for a full glossary.

**Beginner UX**: Do not lead with "DDD" or "Ubiquitous Language". Say e.g. 「作業中に出てきた用語を記録しておきませんか？」 and show a short table. Full 7-field rows can be filled over multiple sessions; mark unknown fields `[NEEDS DOMAIN INPUT]`.

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

**Incremental default**: If Passive Collection already has candidates, skip the long elicitation and propose writing those 1–3 terms first. Offer full business-event elicitation only when the user wants a comprehensive glossary.

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

During **every** conversation turn, **without interrupting the response**, monitor all inputs for domain signals:

### Conversation signals

- Business event expressions (past-tense or passive verb+noun: e.g., "order confirmed", "stock reserved")
- Domain role names (noun + role suffix: e.g., "billing manager", "fulfillment team")
- State names (adjective + noun indicating a stage: e.g., "pending approval", "in transit")
- Requirements language ("must", "cannot", "only when", "after X", user-story verbs)
- Repeated nouns used as product concepts (same term ≥2 times in session)

### Code signals (files read or edited this session)

- Type/class/enum/interface names and docstrings
- API routes, event names, queue/topic names, DB table/column names
- Validation messages and business-rule comments
- Status literals and state-machine transitions

Add each detection to the in-session queue with `source_text` and `trigger_type` (`new-concept` or `vague-term`).

**Surface queued candidates as a batch when**:

- Queue has ≥ 1 entry, AND
- The preceding turn contained no new business-vocabulary candidates, AND
- The primary task is not mid-blocking clarification

**If `docs/ubiquitous-language.md` is absent** and vocabulary is detected: propose an **incremental** start (add detected terms now; offer full bootstrap later) instead of silently queuing or forcing a long elicitation session.

**On user acceptance**: notify `domain-model` by enqueueing structural inference for each new term (same session; no extra user prompt).

If no domain vocabulary is detectable in the turn, still run Pre-check but do not surface an empty proposal.

---

## Invariants

1. **Diff before write**: Every write to `docs/ubiquitous-language.md` or `docs/context-map.md` is preceded by presenting the proposed diff.
2. **Explicit confirmation**: No file is written without explicit user confirmation.
3. **No silent Bounded Context unification**: Conflicts always present the split-or-rename choice; never silently merge definitions across contexts.
4. **Single-row entries**: UL table rows must fit a single row; prompt the user to restructure multi-paragraph definitions into the 7-field form.
