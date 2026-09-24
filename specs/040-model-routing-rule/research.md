# Research: Model and Effort Routing Rule

No `NEEDS CLARIFICATION` remained after the spec. Phase 0 checked how the rule layer is structured, tested, mirrored, and documented, so the plan changes every place that must change and no other.

## D1 — File name and title

**Decision**: `.claude/rules/model-routing.md`, titled "Model and Effort Routing" (the draft's title).

**Rationale**: The user named the path. Sibling titles are concern names ("Reasoning Completeness", "Requirements Certainty"); the draft's title is one too.

**Alternatives**: A verb-phrase title. Rejected: breaks the sibling naming pattern.

## D2 — Section layout

**Decision**: Purpose paragraph (the draft's opening paragraph) → `## Capability tiers` (the draft's table) → `## Escalation and hand-back` → `## Effort and delegation` → closing sufficiency test.

**Rationale**: Siblings use a purpose paragraph, `##` sections of imperative bullets, and (three of five) a closing "sufficient when" line. The draft mixes escalation and hand-back into the tier section; separating them gives each claim one home and lets the closing test enumerate them. The draft's "Prefer: decide → higher capability; …" line stays with the tiers, and its effort and delegation paragraphs go together because both are "choose deliberately" controls.

**Alternatives**: Keep the draft's exact section order. Rejected: escalation conditions would sit between tier definitions and effort, weakening the vertical logic the sibling rules follow.

## D3 — Table versus bullets for tiers

**Decision**: Keep the draft's four-row table (tier, alias, use-when).

**Rationale**: The content is a four-by-three lookup; the table is the clearest form and the only sibling-style deviation. Nothing in the structure check or documentation rules prohibits tables in rules.

**Alternatives**: Four bullets. Acceptable but hides the parallel structure the reader compares across.

## D4 — References section

**Decision**: No `## References` section unless the model aliases are verified against an official source during implementation; if verified, cite that source there.

**Rationale**: Three siblings cite primary sources, but the draft cites none, and inventing support is prohibited. The spec records the aliases as unverified. A verification task is cheap and, if it succeeds, yields a legitimate citation.

**Alternatives**: Cite from memory. Rejected: unverified support.

## D5 — Structure check change

**Decision**: In `tests/run-config-pyramid.sh`, extend RULE-01's expected list to six names (alphabetical, matching `sort`) and rename it "exactly six universal rule files"; add `RULE-11: routing owns capability tiers and effort` asserting `model-routing.md` matches `tier|capabilit|effort|モデル`. Keep existing IDs unchanged.

**Rationale**: Each existing rule has one ownership assertion (RULE-05..09). New ID RULE-11 avoids renumbering RULE-10 (legacy-file absence). RULE-02..04 already scan the whole directory, so the new file is covered without change; RULE-04's pairwise loop covers it automatically.

**Evidence**: `tests/run-config-pyramid.sh` lines 78–106.

**Alternatives**: Replace RULE-01's hard-coded list with a count. Rejected: the exact list is what catches a stray file.

## D6 — Where "five" or the rule list appears

**Decision**: Update these, and only these:

| Artifact | Location | Change |
|---|---|---|
| `tests/run-config-pyramid.sh` | RULE-01 | six-file list and name |
| `README.md` | tree, `rules/` comment ("5 independent concerns") and file list | six; add `model-routing.md` line |
| `README.md` | `.claude/rules/` paragraph enumerating the concerns | add the routing concern |
| `README.ja.md` | `.claude/rules/` paragraph enumerating the concerns | same in Japanese; its tree shows only `rules/`, so no listing change |
| `docs/claude-config-design.md` | §3.1 heading "5つのルール" and the ownership table | six; add rows for what `model-routing.md` deliberately omits |
| `docs/claude-config-design.md` | §5 body "5個のユニバーサルルール" and the layer table row "(5件)" | six |

**Rationale**: Found by grepping for the rule filenames, "five", "5つ", "5 " and "5件" across README, docs, tests, install script and CI. `docs/live-documentation-standards.md` references `thinking-lenses.md` only for a specific lens and is unaffected. `install.sh` and `tests/run-install.sh` sync the directory wholesale, so they need no change; the install test still passes because it compares directories.

**Alternatives**: None; documentation integrity requires the update.

## D7 — Japanese mirror

**Decision**: Add `.claude-ja/rules/model-routing.md` with the same section structure, English headings each followed by a Japanese gloss, Japanese body.

**Rationale**: `.claude-ja/rules/` holds a counterpart for every one of the five rules (English heading plus Japanese gloss, Japanese bullets), e.g. `# Reasoning Completeness（推論の完全性）`. Omitting one would leave the mirror incomplete and unnoticed; no test checks the mirror, so consistency depends on this plan. The spec did not mention the mirror; FR-015 was added.

**Alternatives**: Skip the mirror. Rejected: creates silent drift against the established one-to-one pattern.

## D8 — Content of "what this rule leaves elsewhere" in the design doc

**Decision**: Add one row to the §3.1 table: `model-routing.md` does not hold model IDs, prices, or context limits, or the syntax for setting a model or effort. Those belong to the harness and the vendor's model documentation, which are the sources of truth.

**Rationale**: The rule names aliases and capability classes only; concrete model versions change without changing the routing logic. Keeping them out means a model release does not make the rule stale. This states what was deliberately omitted, as §3.1 requires, and does not create a second definition.

**Alternatives**: Record no omission. Rejected: §3.1's contract is that each rule's row records what it deliberately leaves out.

## D9 — Verification of aliases

**Decision**: Add a small implementation task: check `fable`, `opus`, `sonnet`, `haiku` against the official Claude Code model configuration documentation before finishing; if any differ, stop and report rather than editing the draft's substance.

**Rationale**: SC-005 forbids substantive change to the draft, and stale aliases would make the rule misleading. The check is read-only.

**Alternatives**: Trust the draft. Acceptable but leaves the spec's only stated unverified assumption open.

**Result (2026-09-24, T004)**: Verified against <https://code.claude.com/docs/en/model-config>. `fable`, `opus`, `sonnet`, and `haiku` are all accepted aliases, and `low`/`medium`/`high`/`xhigh`/`max` are the documented effort levels. `xhigh` and `max` are supported only on some models (for example not on Opus 4.6 or Sonnet 4.6), which matches the draft's "when the selected model supports it" condition. The doc lists `high` as the harness default on most models; the rule's `medium` default is a routing policy for ordinary implementation, not a claim about the harness default. Because the aliases are confirmed by an official source, the rule carries a `## References` section citing it (T007).
