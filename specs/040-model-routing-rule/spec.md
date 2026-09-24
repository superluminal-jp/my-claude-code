# Feature Specification: Model and Effort Routing Rule

**Feature Branch**: `040-model-routing-rule`

**Created**: 2026-09-24

**Status**: Implemented

**Input**: User description: "Add a new rule file `.claude/rules/model-routing.md` (source draft: `/Users/taikiogihara/Downloads/model-routing.md`) that tells the agent to use the lowest-capability model and lowest effort that reliably completes each independent unit of work: capability tiers (fable/opus/sonnet/haiku), escalation criteria, delegation back to lower tiers, and separate effort levels (low/medium/high/xhigh/max) when choosing subagent model and effort. Follow the conventions of existing rules and keep repository documentation synchronized."

## Clarifications

### Session 2026-09-24

- Q: Should adding a sixth always-on rule be recorded as a new Architecture Decision Record? → A: No ADR; record the rule's ownership in the configuration design document only.

## Scope and Definitions

The feature adds one always-loaded rule that governs **how the agent chooses a model and a reasoning effort** for each independent unit of work, including work it delegates to a subagent. It does not change how work is decomposed, what is verified, or who is authorized to act.

- **Unit of work**: a task, or a part of a task, that can be completed and checked independently of its siblings.
- **Capability tier**: one of four ordered model classes — most capable, high capability, balanced, efficient — each identified by the model alias the harness accepts (`fable`, `opus`, `sonnet`, `haiku`).
- **Effort level**: the reasoning depth setting, chosen independently of the tier — `low`, `medium`, `high`, `xhigh`, `max`.
- **Escalation**: moving a unit of work to a higher tier than the one first chosen.

The source draft's substance is the authority for tier membership, escalation conditions, and effort semantics. This feature changes its form to match the existing rule layer, not its meaning.

The rule layer's existing contract applies to the new file: it must stay independently usable, so it names no configuration path, no authored skill, no slash command, and no sibling rule file, and it does not restate what another rule already owns.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The agent picks the cheapest sufficient model and effort (Priority: P1)

As the repository owner, I want every session to start with a rule that ties model and effort to the judgment a unit of work actually needs, so routine work does not consume the most capable model and consequential work is not under-resourced.

**Why this priority**: This is the whole behavioral change. Without the rule loaded in every session, none of the routing guidance reaches the agent.

**Independent Test**: Read `.claude/rules/model-routing.md` alone and, for each of four sample units of work (a repository-wide text search, a well-scoped bug fix, a non-trivial refactor, a cross-cutting architecture decision), derive a tier and effort level using only that file. The four results must be `haiku`/low, `sonnet`/medium, `opus`/high, and `fable`/high-or-above respectively.

**Acceptance Scenarios**:

1. **Given** a session in which the rule is loaded, **When** the agent faces a deterministic, local, or repetitive unit of work, **Then** the rule directs it to the efficient tier at low effort.
2. **Given** a well-scoped feature or routine fix with a clear goal, **When** the agent chooses a tier, **Then** the rule directs it to the balanced tier at medium effort as the default.
3. **Given** a unit of work that needs substantial engineering judgment, **When** the agent chooses, **Then** the rule directs it to the high-capability tier, and to the most capable tier only when the work is ambiguous or its mistakes have broad consequences.
4. **Given** a rule statement of the routing basis, **When** the agent applies it, **Then** it routes by required judgment, ambiguity, dependency breadth, and blast radius — and a large or repetitive task alone does not raise the tier.

---

### User Story 2 - Escalation and hand-back are bounded (Priority: P1)

As the repository owner, I want the rule to say when moving up a tier is justified and when to move back down, so the agent neither stays on a weak tier past its competence nor stays on an expensive one after the hard part is settled.

**Why this priority**: Routing without escalation and hand-back criteria produces either wasted capability or unreliable results; the criteria are what make "lowest that reliably completes" checkable.

**Independent Test**: Give a reviewer the rule and three scenarios — a mechanical rename that is large, a task where the current tier cannot decide correct behavior, and an architectural decision already resolved with implementation remaining. The reviewer must correctly answer: do not escalate; escalate; delegate the remaining work back to a lower tier.

**Acceptance Scenarios**:

1. **Given** a unit of work that is large or repetitive but deterministic, **When** the agent considers escalating, **Then** the rule directs it to decompose or parallelize instead.
2. **Given** the current tier cannot determine correct behavior, meets semantic ambiguity, needs an architectural trade-off, or fails for reasoning-related reasons, **When** the agent decides, **Then** the rule permits escalation and names those conditions as the only triggers.
3. **Given** a higher-capability model has resolved the uncertain part, **When** bounded implementation, verification, or cleanup remains, **Then** the rule directs delegation back to a lower tier where practical.

---

### User Story 3 - Delegation sets model and effort deliberately (Priority: P2)

As the repository owner, I want the rule to treat model capability and reasoning effort as separate controls and to say when spawning a subagent is worth it, so delegated work is neither over-provisioned nor wasteful of context and coordination.

**Why this priority**: It extends the routing decision to subagents, which matter only after the tier and effort model of User Story 1 exists.

**Independent Test**: Read the rule alone and state, for a trivial single-file edit and for three independent parallel searches, whether to delegate, and if so which `model` and `effort` to pass. The edit is done directly; the searches are delegated with an efficient-tier model at low effort.

**Acceptance Scenarios**:

1. **Given** a subagent is about to be spawned, **When** the agent configures it, **Then** the rule requires choosing both the model and the effort on purpose, not inheriting either by default.
2. **Given** trivial, sequential, or single-file work, **When** the agent considers a subagent, **Then** the rule prefers direct execution.
3. **Given** independent, parallelizable work or work that benefits from isolated context, **When** the agent considers a subagent, **Then** the rule permits delegation.
4. **Given** the effort scale `low`, `medium`, `high`, `xhigh`, `max`, **When** the agent chooses an effort, **Then** `xhigh` and `max` are reserved for exceptional cases where the selected model supports them and the hardest reasoning is materially useful.

---

### User Story 4 - The new rule fits the rule layer and the docs stay true (Priority: P2)

As a maintainer, I want the new file to meet the rule layer's independence contract and every place that describes the rule set to be updated together, so the repository's own checks and documentation do not contradict its contents.

**Why this priority**: The rule set is currently described and mechanically checked as exactly five files. Adding a sixth without updating those artifacts makes the repository fail its own verification and mislead readers.

**Independent Test**: Run the repository's configuration structure check and the full test suite; both pass with six rules. Search the README, the Japanese README, and the configuration design document for the previous rule count; no stale count remains.

**Acceptance Scenarios**:

1. **Given** the new file, **When** the rule-independence scans run, **Then** they find no configuration path, skill name, slash command, or sibling-rule filename in it.
2. **Given** the structure check currently asserts an exact list of five rule files, **When** the sixth is added, **Then** the check asserts the six-file set and adds an ownership assertion for the new rule, the same way each existing rule has one.
3. **Given** documents state that the rule layer has five rules, **When** the change lands, **Then** each such statement, and the file tree listings in the READMEs, reflect six rules and describe the new one at the same level of detail as its siblings.
4. **Given** the rule layer is defined as independent concerns each supporting one apex branch, **When** a reader asks what the new rule owns, **Then** the design documentation states its concern and what it deliberately leaves to other places.

---

### Edge Cases

- A unit of work spans tiers (for example, a design decision followed by mechanical edits): the rule must route the parts separately, not the whole at the highest tier.
- The selected model does not support `xhigh` or `max`: the rule must limit those levels to models that support them and leave a supported level as the fallback.
- A tier alias is renamed or retired by the harness: the rule should identify tiers by capability first and alias second, so the routing logic survives an alias change.
- The apparent need to escalate is only size or repetition: the rule must send it to decomposition or parallelization, not escalation.
- The `model-routing.md` name is later referenced by another rule: the independence contract forbids it; this is a violation, not a supported extension.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The repository MUST contain a rule file for model and effort routing in the rule layer's directory, loaded unconditionally like its siblings.
- **FR-002**: The rule MUST state the governing principle: use the lowest-capability model and lowest effort level that can reliably complete each independent unit of work.
- **FR-003**: The rule MUST state that routing depends on required judgment, ambiguity, dependency breadth, and blast radius, and not on task size alone.
- **FR-004**: The rule MUST define four ordered capability tiers — most capable, high capability, balanced, efficient — each with the model alias `fable`, `opus`, `sonnet`, `haiku` respectively and the class of work it suits.
- **FR-005**: The rule MUST state the heuristic *decide → higher capability; implement → balanced; execute mechanically → efficient*.
- **FR-006**: The rule MUST limit escalation to these conditions: the current tier cannot determine correct behavior, encounters semantic ambiguity, requires an architectural trade-off, or fails for reasoning-related reasons.
- **FR-007**: The rule MUST state that size or repetition alone is not a reason to escalate and direct such work to decomposition or parallelization.
- **FR-008**: The rule MUST direct bounded implementation, verification, and cleanup back to a lower tier once a higher-capability model has resolved the uncertain part, where practical.
- **FR-009**: The rule MUST treat model capability and reasoning effort as separate controls and define the five effort levels `low`, `medium`, `high`, `xhigh`, `max` with the situation each suits and `medium` as the ordinary default.
- **FR-010**: The rule MUST require that delegation choose the subagent's model and effort deliberately, prefer direct execution for trivial sequential or single-file work, and allow subagents for independent, parallelizable, or context-isolated work.
- **FR-011**: The rule MUST NOT contain a configuration path, an authored skill name, a slash command, or another rule's filename, and MUST NOT restate authorization, verification, or requirements-certainty content that another rule owns.
- **FR-012**: The rule MUST follow the layout conventions of its sibling rules: a title stating the concern, a one-paragraph statement of purpose, titled sections of imperative bullets, and a closing sufficiency test where siblings have one.
- **FR-013**: The configuration structure check MUST assert the six-file rule set, and MUST include an ownership assertion for the new rule equivalent to those of the existing rules.
- **FR-014**: Every artifact that states the number of always-on rules or lists the rule files MUST be updated to six rules and to include the new one, and the configuration design document MUST record what the new rule owns and what it does not.
- **FR-015**: The Japanese mirror of the rule layer MUST gain a counterpart for the new rule, following the existing one-to-one pattern in which every English rule has a Japanese counterpart with the same section structure.
- **FR-016**: The change MUST NOT alter the content of the existing rules, the apex instruction, or any skill.

### Key Entities

- **Capability tier**: an ordered class of model — most capable, high capability, balanced, efficient — with its alias and the work profile it suits.
- **Effort level**: a reasoning-depth setting with a defined suitable situation, independent of the tier.
- **Routing decision**: the pairing of a unit of work with a tier and effort level, plus the reason (judgment, ambiguity, dependency breadth, blast radius) that justifies it.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reader using only the new rule reaches the expected tier and effort for 4 of 4 sample units of work in User Story 1 and 3 of 3 escalation/hand-back scenarios in User Story 2, with no need to consult another file.
- **SC-002**: The rule-independence scans report zero configuration-path, skill-name, slash-command, and sibling-filename violations for the new file.
- **SC-003**: The configuration structure check and the full repository test suite pass with six rule files, with zero failing checks.
- **SC-004**: A search of the README, the Japanese README, and the configuration design document finds zero remaining statements that the rule layer has five rules.
- **SC-005**: Every one of the source draft's tiers, escalation conditions, delegation preferences, and effort levels is present in the rule, with no additional tier, escalation condition, or effort level beyond the draft's; only framing text (purpose paragraph, headings, closing sufficiency test) may be added.

## Assumptions

- **Placement is settled**: the user chose the always-on rule layer explicitly. This spec does not revisit whether a skill or a setting would be a better home, and accepts the rule layer's per-session context cost for a short file.
- **Apex mapping**: the concern is *execute under control*, since it chooses resources proportional to complexity and impact; the apex text is unchanged. No ADR is written for the sixth rule (confirmed in Clarifications); if the concern is later judged to need its own apex branch, that is a separate decision.
- **Form, not substance, is adapted**: the draft's table and bullets are kept where they match sibling style; the heading, the purpose paragraph, the sectioning, and a closing sufficiency test are adapted to the sibling layout. Wording is tightened only where needed to meet FR-011.
- **Aliases are current**: `fable`, `opus`, `sonnet`, `haiku` are the model aliases the harness accepts today, as stated in the draft; they are not re-verified against a live model list in this spec.
- **Effort support varies**: not every model supports every effort level, as the draft states for `xhigh` and `max`; the rule defers to the harness for which combinations are valid.
- **Language**: the rule is written in English like its siblings, and gets a Japanese counterpart in the Japanese mirror (FR-015); the Japanese documentation is updated in the Japanese README and the Japanese design document only where they state the rule count or list the rules.
- **Existing checks remain valid**: the structure check's other assertions (apex, skills, document contracts) are unaffected by adding a rule.
