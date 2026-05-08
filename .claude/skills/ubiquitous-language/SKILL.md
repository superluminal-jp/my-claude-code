# Skill: ubiquitous-language

Maintain a project's Ubiquitous Language — capture domain vocabulary from conversation, organize it in `docs/ubiquitous-language.md`, and surface cross-context conflicts in `docs/context-map.md`.

## Pre-check

At every invocation, first:

1. Check whether `docs/ubiquitous-language.md` exists in the current project root.
   - Absent → **Bootstrap flow**
   - Present → **Maintenance flow**

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

> 「このプロジェクトにはまだユビキタス言語ファイルがありません。業務イベント起点のヒアリングを開始します。  
> （ユビキタス言語とは「このチームでは『注文』とは〇〇のことを指す」と決めた共通の言葉の辞書です。開発者と業務担当者が同じ言葉で話せるようにするために作ります。）」

### Step 2 — Business-event elicitation

Ask the opening question focused on **events**, not nouns:

> 「業務で実際に起きる出来事を 5〜10 個挙げてください。例：「注文が確定される」「請求書が発行される」「在庫が引き当てられる」」

### Step 3 — Extract terms from each event

For each event provided, elicit:
1. **アクター**: 誰がこのイベントを引き起こすか？
2. **前提状態**: このイベントが発生するには何が必要か？
3. **結果状態**: このイベントの後、何が変わるか？
4. **例外ケース**: このイベントが失敗するのはどんな場合か？

### Step 4 — Draft 7-field entries

For each term identified, create one table row:

| Field | Requirement |
|---|---|
| 用語 | Canonical domain term (original language) |
| 定義 | What it means, including states and behaviors (single row) |
| 文脈 | Which Bounded Context |
| 状態・ルール | State transitions in arrow notation (`A→B→C`); constraints |
| 例 | What is included |
| 反例 | What is excluded |
| 実装名 | Class/method/table/API/event/UI label name(s) |

Mark any field the user cannot provide yet as `[NEEDS DOMAIN INPUT]`. Re-surface at next invocation.

### Step 5 — Show diff and confirm

Show the proposed contents of:
- `docs/ubiquitous-language.md` — using the structure from the template: file header, optional `## Watchlist` section, and one `## Bounded Context: <name>` section per context identified
- `docs/context-map.md` — empty table (header row only)

If `docs/` directory does not exist, note that it will be created.

**Do NOT write any file until the user confirms.**

On confirmation: create `docs/` if absent, then write both files.

---

## Maintenance Flow

**Trigger**: `docs/ubiquitous-language.md` exists.

### Step 1 — Surface queued candidates

Display all terms detected in the current session as a batch proposal:

```
## Ubiquitous Language — 更新候補

以下の用語を追加/更新しますか？

| 操作 | 用語 | 検出元 | 提案定義 | Bounded Context |
|------|------|--------|---------|-----------------|
| [+] 新規 | <term> | <source> | <proposed definition> | <context> |
| [!] 曖昧語 | <term> | <source> | → <replacement candidates> | — |

回答例: "全て追加" / "1のみ" / "スキップ" / "1は [カスタム定義]"
```

If queue is empty, skip to Step 2.

### Step 2 — Watchlist scan

Scan recent conversation for **default watchlist terms**: `データ` / `情報` / `処理` / `管理` / `ステータス` / `フラグ` / `有効` / `完了` / `対象` / `ユーザー`

Read the `## Watchlist` section of `docs/ubiquitous-language.md` for project-specific additions and removals; apply them to the effective watchlist.

For each hit: quote the exact location and propose UL-registered replacements.

### Step 3 — Re-surface incomplete entries

Scan `docs/ubiquitous-language.md` for rows containing `[NEEDS DOMAIN INPUT]`. Present each for completion.

### Step 4 — Bounded Context conflict check

If the same term appears in multiple Bounded Context sections with differing definitions, present:

> 「「[用語]」は [Context A] と [Context B] で異なる定義が記録されています。どうしますか？」

Options:
1. **コンテキスト別エントリ化** — Keep separate entries per context with distinct 実装名
2. **片方を改名** — Rename the term in one context to eliminate the conflict

On resolution: update `docs/context-map.md` with the appropriate relation type.

### Step 5 — Watchlist management

Offer to add or remove project-specific watchlist terms. Proposed changes are added to the `## Watchlist` section of `docs/ubiquitous-language.md`.

### Step 6 — Show cumulative diff and confirm

Show a diff of all proposed changes to `docs/ubiquitous-language.md` and `docs/context-map.md`.

**Do NOT write any file until the user confirms.**

---

## Passive Collection

During any conversation turn, **without interrupting the current response**, monitor user messages for:

- Business event expressions (動詞+名詞の過去形/受動形: e.g., 「注文が確定された」「在庫が引き当てられた」)
- Domain role names (noun + 者/担当/チーム: e.g., 「請求担当者」)
- State names (adjective + noun ending in 済み/中/待ち: e.g., 「承認待ち」)

Add each detection to the in-session queue with `source_text` and `trigger_type = new-concept`.

**Surface queued candidates as a batch proposal when**:
- Queue has ≥ 1 entry, AND
- The preceding conversation turn contained zero new business-vocabulary candidates

**If `docs/ubiquitous-language.md` is absent** and vocabulary is detected: propose Bootstrap flow instead of silently queuing.

If no domain vocabulary is detectable in the conversation, do not activate.

---

## Invariants

1. **Diff before write**: Every write to `docs/ubiquitous-language.md` or `docs/context-map.md` is preceded by showing the user a diff of the proposed changes.
2. **Explicit confirmation**: No file is written without explicit user confirmation.
3. **No silent Bounded Context unification**: Conflicts always present the split-or-rename choice; never silently merge definitions across contexts.
4. **Single-row entries**: UL table rows must fit a single row. Multi-paragraph definitions are not accepted; prompt the user to restructure into the 7-field form.
