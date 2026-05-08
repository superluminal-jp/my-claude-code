# Skill: ubiquitous-language

Maintain and evolve a project's Ubiquitous Language (UL) — capturing, validating, and compressing domain vocabulary across all conversations and artifact-generation phases.

## Invocation

- **Mode A** (lifecycle hook): invoked as `ubiquitous-language.collect` from any hook system
- **Mode B** (slash command): user types `/ubiquitous-language [subcommand]`
  - *(none)* — validation sweep + surface queued candidates
  - `bootstrap` — force bootstrap elicitation for a new or additional BC
  - `show [bc-name]` — display current UL table for the named BC
  - `add [term]` — interactively add a new term to a specified BC
  - `check` — run vague-term watchlist scan on the most recently generated artifact
- **Mode C** (conversational): CLAUDE.md persistent rule activates when `.specify/ubiquitous-language/` exists

---

## Pre-check

Run this section first in every invocation before determining which mode to enter.

### 1. Context-State Detection

Detect the following state variables:

| Variable | How to detect | Values |
|---|---|---|
| `ul_store_present` | Check if `.specify/ubiquitous-language/` directory exists and contains at least one `*.md` file (excluding `context-map.md` and `watchlist.md`) | `true` / `false` |
| `artifact_under_review` | Check if the current session contains an AI-generated artifact (spec, plan, tasks, etc.) that has not yet been accepted/written | `true` / `false` |
| `conversational_mode` | Check if the current invocation came from a user chat message (not a lifecycle hook or slash command) | `true` / `false` |
| `speckit_mode` | Check if the current invocation came from a speckit lifecycle hook (`before_specify`, `before_clarify`, etc.) | `true` / `false` |
| `same_turn_triggered` | Check if UL collection was already triggered in this session turn | `true` / `false` |

**Mutual exclusion**: `speckit_mode` and `conversational_mode` are mutually exclusive. If both would be true, treat as `speckit_mode`.

### 2. Mode Routing

Based on context state, route to the appropriate mode:

```
if same_turn_triggered == true:
  → EXIT (deduplication guard — do not double-process)

if ul_store_present == false:
  → BOOTSTRAP mode (FR-001)

if ul_store_present == true and (speckit_mode or slash_command):
  → COLLECT mode (scan artifact if present) + VALIDATE mode

if ul_store_present == true and conversational_mode:
  → COLLECT mode (passive monitoring only)
```

### 3. Shared In-Session Queue

Maintain a working-memory queue of candidates detected during this session. The queue is NOT persisted to disk; it lives only for the current session.

Queue entry structure:

| Field | Description |
|---|---|
| `candidate_term` | Detected candidate term |
| `source_text` | Source text excerpt (quoted) |
| `trigger_type` | `vague-term` / `new-concept` / `drift` / `missing-state` |
| `detected_at` | Lifecycle event name or conversation turn number |

Batch proposal triggers:
- A conversation turn with no new domain vocabulary detected (natural pause)
- Any speckit lifecycle event start

### 4. Error / Edge Conditions

| Condition | Behavior |
|---|---|
| UL store path not discoverable | Exit silently; note once that UL collection requires a discoverable store path (default: `.specify/ubiquitous-language/`) |
| `same_turn_triggered == true` | Exit immediately without processing |
| User defers all candidates | Queue persists; re-surface at next trigger |
| BC budget exceeded (> 30 entries) | Propose split before adding new entry; block write until resolved |
| Conflicting BC definitions detected | Present 3-option conflict resolution dialog; block silent unification |
| Vague term in final artifact with no replacement agreed | Block artifact acceptance with warning; allow override with explicit acknowledgement |
| UL entry missing 例, 反例, or 実装名 | Mark `[NEEDS DOMAIN INPUT]`; re-surface at next lifecycle event |

---

## Bootstrap Mode

**Trigger**: `ul_store_present == false`

**Goal**: Elicit an initial per-BC UL from the user via business-event-driven dialogue, producing at least one `.specify/ubiquitous-language/<bc-name>.md` file.

### Step 1 — UL Absence Confirmation (FR-001)

Confirm that `.specify/ubiquitous-language/` does not exist or is empty. Announce to the user:

> "このプロジェクトにはまだユビキタス言語ストアがありません。業務イベント起点のヒアリングを開始します。"

### Step 2 — Business-Event Elicitation Opening (FR-004)

Ask the user the opening question focused on **business events**, not roles or data:

> "このシステムで起こる重要な業務イベント（動詞+名詞の形）を 5〜10 個挙げてください。例：「注文が確定される」「請求書が発行される」「在庫が引き当てられる」"

### Step 3 — Role/Concept/State/Exception Extraction (FR-005)

For each business event provided, elicit:
1. **アクター（役割）**: 誰がこのイベントを引き起こすか？
2. **前提状態**: このイベントが発生するには何が必要か？
3. **結果状態**: このイベントの後、何が変わるか？
4. **例外ケース**: このイベントが失敗するのはどんな場合か？

### Step 4 — Developer-Derived Tagging (FR-006)

If no domain expert is present (user indicates they are the developer), mark entries with `出典: developer-derived` and proceed. Do not require external validation to create the initial UL.

### Step 5 — 7-Field Entry Creation (FR-007, FR-008)

For each term identified, create a UL entry with all 7 mandatory fields:

| Field | Requirement |
|---|---|
| 用語 | Domain language term (original language) |
| 定義 | What it means, including states and behaviors |
| 文脈（BC） | Which Bounded Context |
| 状態/ルール | State transitions in arrow notation (e.g., `確定済み→在庫引当済み`) — required for stateful terms |
| 例 | What is included (mandatory — no `[NEEDS DOMAIN INPUT]` allowed in final entry) |
| 反例 | What is excluded (mandatory — no `[NEEDS DOMAIN INPUT]` allowed in final entry) |
| 実装名 | English class/method/table/API/event/UI label name |

If 例, 反例, or 実装名 cannot be provided yet, mark with `[NEEDS DOMAIN INPUT]` and re-surface at next lifecycle event.

### Step 6 — State-Transition Capture (FR-009)

For any term that represents a stateful entity, prompt:

> "「[用語]」が取りうる状態を教えてください。通常フローと例外フローを分けて、矢印記法で記述します。例：`作成済み→確定済み→在庫引当済み`、例外：`→キャンセル済み`"

Record the result in the `状態/ルール` field using arrow notation. State transitions are one line per flow.

### Step 7 — Size Budget Check (FR-019)

After each new entry is appended, check the entry count in the target BC file. If `entry_count > 30`:

> "この BC のエントリ数が 30 を超えています。以下のいずれかを選択してください：
> 1. BC を分割する（どの用語を新 BC に移すか提案します）
> 2. 類似語を統合する（統合候補を提示します）
> 3. このまま追加する（バジェット超過を承認する）"

**Block the write** until the user selects an option.

### Step 8 — Single-Row-Entry Enforcement (FR-020)

Before appending any entry, verify the definition fits a single table row. If the user provides a multi-paragraph definition:

> "定義が複数段落になっています。UL テーブルの「定義」フィールドは 1 行に収める必要があります。以下の形式に整理してから追加してください：
> - 定義（1行）:
> - 状態/ルール（矢印記法、1行）:
> - 例:
> - 反例:"

**Block the write** until the user restructures the input.

### Step 9 — Duplicate-Term Check (FR-021)

Before appending any new entry to a BC file, scan the target file for an existing row with the same `用語` value. If a match is found:

> "「[用語]」はすでに [BC名] に登録されています。既存のエントリを更新しますか？それとも別の用語として追加しますか？"

**Block the append**; route to update flow if user confirms.

### Step 10 — Auto-populate 更新イベント (FR-027)

When creating or updating any UL entry, automatically set the `更新イベント` field to:
- The current lifecycle event name (e.g., `before_specify`) when invoked via a lifecycle hook
- `"conversational"` when invoked via Mode C
- `"manual"` when invoked via slash command

This field is set by the skill and is NOT editable directly by users.

### Step 11 — Diff-Before-Write and Confirmation (FR-018)

Before writing any UL file, display a diff of the proposed changes:

```
## 追加予定のエントリ

| 用語 | 定義 | 文脈（BC） | ... |
|------|------|-----------|...|
| [term] | [definition] | [bc] | ... |

このエントリを `.specify/ubiquitous-language/[bc-name].md` に追加してよいですか？ (yes/no)
```

**Do NOT write** until the user confirms with "yes" or equivalent. No silent writes.

---

## Collect Mode

**Trigger**: `ul_store_present == true` — passive monitoring or artifact scan

**Goal**: Detect new domain vocabulary candidates from the current conversation or artifact, queue them, and surface a batch proposal at the next natural pause without interrupting the current task.

### Step 1 — Passive Monitoring (FR-030)

While generating any response, monitor the user's messages for:
- Business events (verb + noun in past/passive form: e.g., 「注文が確定された」)
- State names (adjective + noun ending in 済み, 中, 待ち: e.g., 「承認待ち」)
- Role names (noun + 者/担当/チーム: e.g., 「請求担当者」)
- Rule conditions (〜場合、〜とき、〜なら)

Do NOT interrupt the current response to surface candidates. Queue all detections.

### Step 2 — Queue Accumulation

For each detection, add to the in-session queue:
- `candidate_term`: detected term
- `source_text`: the sentence containing the term (quoted)
- `trigger_type`: `new-concept`
- `detected_at`: current conversation turn number

### Step 3 — No-Activation Guard (FR-032)

If `.specify/ubiquitous-language/` is NOT discoverable in the current project context, do NOT activate collection. Note once and exit.

### Step 4 — Batch Proposal Trigger (FR-031)

Surface the accumulated queue as a Batch Proposal when:
- The current conversation turn contains no new domain vocabulary (natural pause), OR
- A speckit lifecycle event starts

Batch Proposal format:

```
## Ubiquitous Language — 更新候補

以下の用語を UL に追加/更新しますか？

| 操作 | 用語 | 検出元 | 提案定義 | BC |
|------|------|--------|---------|-----|
| [+] 新規 | [term] | [source] | [proposed definition] | [bc] |
| [!] 曖昧語 | [term] | [source: file line N] | → [replacement candidates] | — |
| [~] ドリフト | [term] | [source] | UL には [expected] が記録済み | [bc] |

回答例: "全て追加" / "1のみ" / "スキップ" / "1は [カスタム定義]"
```

### Step 5 — Skip/Defer Handling (FR-003)

If the user skips or defers candidates:
- Keep skipped items in the queue
- Re-surface at the next natural pause or lifecycle event
- After 3 deferrals of the same item, ask whether to permanently remove it from the queue

### Step 6 — Clarification-Trigger Pattern Detection (FR-026)

If the conversation contains clarification-question patterns (e.g., 「つまり何を指していますか？」「それはどういう意味ですか？」「〜とはどういうことですか？」), immediately propose adding or refining the relevant UL entry rather than queuing for batch proposal:

> "この質問が出た語「[term]」を UL に追加/更新しますか？今すぐ定義を整理できます。"

### Step 7 — Write Enforcement (same as Bootstrap)

Apply single-row-entry enforcement (FR-020), duplicate-term check (FR-021), auto-populate `更新イベント` (FR-027), and diff-before-write confirmation (FR-018) as defined in Bootstrap Steps 8–11.

---

## Validate Mode

**Trigger**: Active when an artifact is under review or a slash command requests validation.

**Goal**: Detect vague terms, implementation-name drift, and BC conflicts in AI-generated artifacts before they are finalized.

### A — Vague-Term Watchlist Scan (FR-010, FR-011, FR-012)

#### Default Watchlist (Japanese)

The following 10 terms are flagged when found in any artifact being generated:

`データ` / `情報` / `処理` / `管理` / `ステータス` / `フラグ` / `有効` / `完了` / `対象` / `ユーザー`

#### Project-Specific Watchlist Extension

If `.specify/ubiquitous-language/watchlist.md` exists, load it. Project-specific additions are appended to the default list. Project-specific overrides remove terms from the default list.

#### Detection and Proposal

For each watchlist term found in the artifact:
1. Quote the exact location (file, section, or line reference)
2. Check if a UL entry exists for that term's context
3. Propose UL-grounded replacement candidates

Format:

```
## 曖昧語検知

| 語 | 検出箇所 | UL 登録済み代替候補 |
|----|---------|------------------|
| ユーザー | spec.md §3 line 42 | 契約管理者 / 利用者 / 請求担当者 |
```

If the artifact is about to be finalized and the vague term has no agreed replacement, **block finalization** with:

> "「[term]」が未解決のまま残っています。置換語を選ぶか、このまま進めることを明示的に承認してください。"

### B — Drift Detection (FR-016, FR-017, FR-018)

#### Identifier Extraction

Scan the artifact for identifiers matching patterns:
- CamelCase class names (e.g., `OrderProcessor`)
- Dotted method calls (e.g., `Order.process()`)
- snake_case function names (e.g., `confirm_order`)
- API path segments (e.g., `/orders/process`)
- Event names (e.g., `OrderProcessed`)

#### Normalization

Before comparison, normalize both the artifact identifier and the UL `実装名` field:
- Lowercase all characters
- Remove separators (`_`, `-`, `.`)
- Example: `Order.confirm()` → `orderconfirm`; `order_confirm` → `orderconfirm`

If normalized forms match: **no drift** (do not flag case/separator differences).

If normalized forms do NOT match but share a common root: **semantic drift** — flag.

#### Drift Report

```
## UL ドリフト検知

| 場所 | 記述 | UL の期待値 | 推奨アクション |
|------|------|-----------|--------------|
| plan.md §3 | Order.process() | Order.confirm() | A) artifact 修正 / B) UL 更新 / C) 新語として分離 |
```

Present the 3-option resolution for each drift item:
- **A) artifact 修正**: Update the identifier in the artifact to match UL
- **B) UL 更新**: Update the UL `実装名` to match the new artifact identifier
- **C) 新語として分離**: Treat as a new distinct concept; add as a new UL entry

**No silent rewrites**: Show diff before any artifact or UL change (FR-018).

### C — BC Conflict Resolution (FR-013, FR-014, FR-015, FR-028, FR-029)

#### Multi-BC Support

Each BC has its own file at `.specify/ubiquitous-language/<bc-name>.md`. When a new term is being added, check all existing BC files for the same `用語` value.

#### Conflict Detection

If the same term exists in multiple BC files with differing definitions, flag as a conflict:

> "「[term]」は [BC-A] と [BC-B] で異なる定義が記録されています。どうしますか？"

#### 3-Option Conflict Resolution Dialog (FR-014)

1. **BC ごとに別エントリ化**: Create separate entries in each BC with distinct `実装名` values (e.g., `SalesAccount` vs. `BillingParty`)
2. **BC を統合する**: Merge the two BCs into one (user must confirm BC rename/restructure)
3. **片方を改名する**: Rename the term in one BC to eliminate the conflict

**Block silent global unification**. Do not merge BC definitions without user selection.

#### Context-Map Update (FR-015)

After conflict resolution, update `.specify/ubiquitous-language/context-map.md` with the appropriate relation type:

| Resolution chosen | Relation type |
|---|---|
| BC ごとに別エントリ化 | `same-name-different-meaning` |
| BC を統合する | `identical` |
| 片方を改名する | `synonym` (if same concept) or `same-name-different-meaning` (if different) |

#### Bilingual Entry Support (FR-028, FR-029)

- `用語` field: domain language (Japanese)
- `実装名` field: English identifier (class/method/table/API)
- Both fields are required; do not create an entry with only one language

---

## Context Compression

**Trigger**: Active at session start (if UL contains ≥ 5 terms) or when a compression command is issued.

**Goal**: Use the stabilized UL as a compression dictionary to reduce context length in multi-turn conversations.

### A — Ontology Header Generation (FR-022)

At session start or speckit lifecycle event start, if the UL store contains ≥ 5 confirmed terms, inject an Ontology Header summarizing the UL:

```
## Ubiquitous Language Reference (BC: [bc-name])

| 用語 | 1行定義 |
|------|---------|
| 確定済み注文 | 支払い承認済みで在庫引当対象の注文 |
| キャンセル可能注文 | 出荷指示前かつキャンセル期限内の注文 |
...（最大 30 エントリ / BC）
```

**Frequency-Based Depth**: High-frequency terms (appearing in ≥ 3 prior conversation turns) are included in the Ontology Header as short-form entries. Low-frequency or complex terms are expanded only on first appearance in the session.

### B — Paraphrase-to-UL-Term Substitution (FR-023)

When generating an artifact, detect paraphrases of registered UL definitions. A paraphrase is detected when a generated sentence conveys the same meaning as a UL definition but uses different wording.

For each detected paraphrase:
1. Quote the paraphrase and its UL-term equivalent
2. Show a diff proposing the substitution
3. Require explicit user confirmation before substituting

Example:

```
## 言い換え検知

「支払いが承認されて在庫を確保できる状態になった注文」
→ UL 登録済み：「確定済み注文」に置き換えますか？

Before: ...支払いが承認されて在庫を確保できる状態になった注文が...
After:  ...確定済み注文が...

承認しますか？ (yes/no)
```

### C — Linkability Guarantee (FR-024)

Every UL term that appears in an AI-generated artifact must resolve unambiguously to its BC entry. If a UL term is used in an artifact but belongs to multiple BCs (i.e., appears in the context map), add a BC qualifier:

> 「顧客（販売BC）」 / 「顧客（請求BC）」

### D — Delta Notation

When updating UL entries, present changes using Delta Notation rather than a full re-display:

```
[+] 支払い承認済み: 決済事業者から承認コードを受領した状態 (BC: 販売)
[~] 確定済み注文: 定義を「支払い承認済みで在庫引当対象の注文」に更新 (BC: 販売)
[-] 保留注文: エントリを削除（「承認待ち注文」に統合） (BC: 販売)
```

### E — State-Machine Compression

For stateful terms, use one-line arrow notation in Ontology Header entries rather than prose:

```
確定済み注文: 注文作成済み → 確定済み → 在庫引当済み → 出荷指示済み (例外: → キャンセル済み)
```

Full state details are in the UL file; the Ontology Header entry is a compressed pointer.

---

## Invariants (apply to all modes and all write operations)

1. **Diff-before-write**: Every write to a UL file must be preceded by showing the user a diff of the proposed change.
2. **Explicit confirmation**: No UL file write occurs without explicit user confirmation.
3. **No silent unification**: BC conflicts are never resolved silently; always present the 3-option dialog.
4. **Caller-agnostic**: This skill never references speckit, speckit commands, or speckit internals in its own logic. Integration with speckit is handled externally (extensions.yml hooks and CLAUDE.md routing).
5. **Single-row entries**: UL table rows must fit a single row; multi-paragraph definitions are rejected.
6. **Deduplication**: `same_turn_triggered` guard prevents double-processing in the same session turn.
7. **SC-010 timing**: Each trigger (Mode A or Mode C) must complete without delaying the user's current response by more than 5 seconds. Passive collection (queuing) adds zero latency; batch proposals are deferred to natural pauses.
