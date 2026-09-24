# Model and Effort Routing

Use the lowest-capability model and lowest effort level that can reliably complete each independent unit of work. Route by required judgment, ambiguity, dependency breadth, and blast radius, not by task size alone.

## Capability tiers

| Tier | Alias | Use when |
|---|---|---|
| Most capable | `fable` | The task is ambiguous or high-impact: system architecture, difficult root-cause analysis, cross-cutting changes, long-horizon coordination, or final semantic judgment where mistakes have broad consequences. |
| High capability | `opus` | The task needs substantial engineering judgment: complex implementation, non-trivial debugging, refactoring, specification or plan analysis, code review, or trade-off evaluation. |
| Balanced | `sonnet` | Default for normal implementation: well-scoped features, routine bug fixes, tests, migrations, moderate refactors, and other work with a clear goal but non-trivial execution. |
| Efficient | `haiku` | The work is deterministic, local, or repetitive: repository search, Git housekeeping, formatting and lint fixes, renames, imports, comments and docstrings, documentation or changelog synchronization, and straightforward test additions. |

Prefer: decide → higher capability; implement → balanced; execute mechanically → efficient.

## Escalation and hand-back

- Escalate only when the current tier cannot determine correct behavior, encounters semantic ambiguity, requires an architectural trade-off, or fails for reasoning-related reasons.
- Do not escalate merely because work is large or repetitive; decompose or parallelize deterministic work instead.
- After a higher-capability model resolves the uncertain part, delegate bounded implementation, verification, and cleanup back to a lower tier when practical.

## Effort and delegation

- Treat model capability and reasoning effort as separate controls.
- `low` suits mechanical or obvious work; `medium` is the default for ordinary implementation; `high` suits complex reasoning or consequential review; `xhigh` and `max` are for exceptional cases where the hardest reasoning is materially useful and the selected model supports them.
- When delegating, choose both the subagent's model and effort deliberately.
- Prefer direct execution over a subagent for trivial sequential or single-file work; use subagents when work is independent, parallelizable, or benefits from isolated context.

Routing is sufficient when each unit of work has a tier and effort that follow from its judgment, ambiguity, dependency breadth, and blast radius, and every escalation names one of the conditions above.

## References

- Claude Code, "Model configuration" — the model aliases and effort levels, and which models support `xhigh` and `max`: <https://code.claude.com/docs/en/model-config>
