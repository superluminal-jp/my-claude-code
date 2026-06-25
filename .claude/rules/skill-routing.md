# Skill Routing

Purpose: map each request to the one skill that should load before responding. Applies on every turn, before the first answer.

**Execution pre-check** (every turn, before acting):

1. **Memory** — consult when prior preferences, decisions, or conventions may apply; write back durable learnings after significant work (`tools.md` § Memory).
2. **Parallelize** — batch independent reads, searches, and checks in one message (`tools.md` § Parallel calls).
3. **Delegate** — use subagents for broad exploration or context-heavy research; launch parallel subagents when tracks are independent (`tools.md` § Subagents).

- Code implementation or behavior changes -> load `coder`.
- Python source, tests, or packaging -> also load `python-coder`.
- TypeScript/JavaScript source, tests, or frontend/Node tooling -> also load `typescript-coder`.
- AWS CDK stacks, constructs, or `cdk.json` -> also load `aws-cdk-coder` (and `typescript-coder` or `python-coder` for the app language).
- AWS CLI commands or shell scripts against live AWS APIs -> also load `aws-cli-coder`.
- Produced artifacts (docs, translation, editing) -> load `editor`.
- Any ambiguity in requirements -> load `clarifier`. Triggers include:
  - Remaining text (after stripping slash commands and paths) is ≤ 32 characters.
  - Subject, object, or verb is absent or unclear, making intent ambiguous.
- Decision, recommendation, trade-off, or "what should I do" (options visible, path unclear) -> load `advisor`. Triggers include:
  - Compare options, pros/cons, or "which is better" (e.g. Redis vs Memcached, monolith vs microservices).
  - Architecture, tooling, or process choice without a single obvious implementation path.
  - Explicit ask for recommendation, 方針, 選定, 比較, おすすめ, メリデメ.
  - **Not** clarifier: goal and success criteria are clear enough to compare paths — use advisor. If intent/scope/acceptance is missing, use clarifier first.

## Domain knowledge memory (always-on)

`ubiquitous-language` and `domain-model` are **background memory layers**, not DDD-only tools. Load both on every turn **alongside** the primary skill (coder, editor, clarifier, advisor, etc.).

**Load when**: any task that may reveal what the system *means* — feature work, debugging, code changes, specs, architecture questions, onboarding. **Skip only** for pure meta/config edits with zero business vocabulary (formatting, hook wiring, linter config).

**Mode**:

1. **Passive Collection** — every turn, without interrupting the primary task, scan conversation *and* code touched in the session for vocabulary and structure.
2. **Surface at natural pauses** — when the candidate queue has entries AND the preceding turn added no new candidates (task boundary, confirmation point, or explicit ask). Batch-propose; never block delivery of the primary answer.
3. **Beginner framing** — propose updates as "用語・ルールの記録" / "構造の記録", not "DDD" or "ドメインモデル作成". DDD terms appear only when the user uses them or asks.

**Chain**: accepted ubiquitous-language entries auto-seed domain-model candidates in the same session.
