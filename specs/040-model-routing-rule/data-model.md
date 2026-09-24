# Data Model: Model and Effort Routing Rule

The feature stores no data. These are the concepts the rule defines and the mapping from the source draft that the rule must preserve (SC-005).

## Capability tier

| Attribute | Rule |
|---|---|
| Name | most capable · high capability · balanced · efficient |
| Alias | `fable` · `opus` · `sonnet` · `haiku` (one-to-one, ordered high to low) |
| Suits | judgment-driven work, from ambiguous/high-impact (most capable) down to deterministic/local/repetitive (efficient) |

Ordering: most capable > high capability > balanced > efficient. Balanced is the default for normal implementation.

## Effort level

| Level | Suits |
|---|---|
| `low` | mechanical or obvious work |
| `medium` | ordinary implementation (default) |
| `high` | complex reasoning or consequential review |
| `xhigh` / `max` | exceptional cases where the hardest reasoning is materially useful and the selected model supports it |

Independent of tier: any tier may pair with any supported effort.

## Routing decision

| Field | Meaning |
|---|---|
| Unit of work | independent, completable, checkable piece |
| Tier | chosen from the four |
| Effort | chosen from the five |
| Basis | required judgment, ambiguity, dependency breadth, blast radius (never size alone) |

### Transitions

- **Escalate** (tier up) only when the current tier cannot determine correct behavior, meets semantic ambiguity, needs an architectural trade-off, or fails for reasoning-related reasons. Large or repetitive work is decomposed or parallelized instead.
- **Hand back** (tier down) once a higher tier has resolved the uncertain part, for bounded implementation, verification, and cleanup, where practical.

## Delegation

A subagent is spawned only for independent, parallelizable, or context-isolated work; trivial sequential or single-file work is done directly. When spawned, both model and effort are chosen on purpose.

## Draft-to-rule preservation map

| Draft element | Rule section |
|---|---|
| Opening principle (lowest capability, lowest effort, route by judgment, ambiguity, dependency breadth, blast radius) | Purpose paragraph |
| Tier table and "decide / implement / execute mechanically" line | Capability tiers |
| Escalate-only conditions; do not escalate for size or repetition; hand back after resolution | Escalation and hand-back |
| Capability and effort as separate controls; five effort levels; subagent model and effort chosen deliberately; direct execution preferred for trivial work | Effort and delegation |
