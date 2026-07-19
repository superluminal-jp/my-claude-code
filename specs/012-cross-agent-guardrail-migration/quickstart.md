# Quickstart: Validating the Decision Record

This feature has no code to run. "Validation" means checking the produced `decision-record.md` against `spec.md`'s Success Criteria and Functional Requirements.

## Prerequisites

- `spec.md`'s `## Clarifications` section complete (14/14 Q&A recorded) — done as of `/speckit-clarify`.
- `data-model.md` available as the structural reference for what the record must contain.

## Validation checklist

Run through this after `decision-record.md` is authored (in `/speckit-implement` or a direct authoring pass):

1. **SC-001 — exactly 14 verdicts**:
   ```bash
   grep -c '^### Q[0-9]' specs/012-cross-agent-guardrail-migration/decision-record.md
   ```
   Expect `14`.

2. **SC-002 — independently readable items**: pick any single item at random and confirm it states, without scrolling elsewhere: (a) the current Claude Code behavior, (b) the options that were considered, (c) the chosen verdict, (d) the rationale.

3. **SC-003 — per-tool verdicts are labeled where the underlying research showed asymmetric support**: confirm Q5 and Q7 explicitly state that Cursor had a viable native hook (`beforeSubmitPrompt`, `afterFileEdit`) that was deliberately not implemented, rather than presenting a single undifferentiated "no" for both tools.

4. **SC-004 — zero implementation artifacts**:
   ```bash
   git status --porcelain -- .claude/ AGENTS.md
   ```
   Expect no output — this feature must not touch the live `.claude/` configuration or create `AGENTS.md` itself; only `specs/012-cross-agent-guardrail-migration/` and the two `docs/adr` / `install.sh` changes from the unrelated prior work in this branch should show history.

5. **FR-009 — unconfirmed dependencies flagged**: confirm every item whose verdict traces to a Medium-confidence research finding (R1–R4 in `research.md` — Q5, Q6, Q7, Q9, Q10) carries a visible note that the underlying tool-capability claim was not verified against primary sources in this session.

6. **Cross-check against `data-model.md`**: the record's verdict-class distribution (6 `unify_full`, 8 `unify_weak`, 0 dropped) should match the table in `data-model.md`.

## Out of scope for this quickstart

- No `AGENTS.md` is written by this feature (per FR-008) — a future implementation feature would consume `decision-record.md` as its input.
- No hook scripts (Codex `PreToolUse`, Cursor `beforeShellExecution`) are written here either, even for Q6 which recommends building one — this feature's deliverable stops at the decision.
