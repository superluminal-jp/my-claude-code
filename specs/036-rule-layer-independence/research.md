# Research: Independent Configuration Pyramid

## Sources consulted

- Claude Code, [How Claude remembers your project](https://code.claude.com/docs/en/memory): always-loaded instructions should be concise, specific, well-structured, and non-conflicting; rules should be modular and each file should cover one topic; task-specific instructions belong in skills.
- Claude Code, [Extend Claude with skills](https://code.claude.com/docs/en/slash-commands): a skill's description tells Claude when to load it, while the full body and supporting files load on demand.
- Claude Code, [Extend Claude Code](https://code.claude.com/docs/en/features-overview): project memory, rules, skills, MCP tools, and subagents solve different extension problems and have different context-loading costs.
- Claude Code, [Connect Claude Code to tools via MCP](https://code.claude.com/docs/en/mcp): MCP Tool Search discovers tool descriptions dynamically, so a static always-loaded server capability registry duplicates changing environment state.
- GitHub Spec Kit, [README](https://github.com/github/spec-kit): the core delivery order is specify → plan → tasks → implement; checklist tests requirement quality and analyze checks cross-artifact consistency before implementation.
- Barbara Minto, *The Minto Pyramid Principle* (1987): a parent summarizes/supports its children; sibling groups use one logical relationship and are collectively exhaustive within their defined question.

## Decision 1: Use a semantic hierarchy, not a citation hierarchy

**Decision**: The apex, rules, and skills relate by aligned meaning and abstraction. Independent configuration nodes do not name one another.

**Rationale**: A parent that delegates its meaning to named children is not independently interpretable. It also breaks when a child is renamed, split, or removed. Semantic support preserves a pyramid without runtime coupling.

**Alternatives rejected**:

- Permit parent-to-child references: keeps centralized routing but contradicts the user's explicit independence requirement and creates downward coupling.
- Ban only sibling references: removes lateral cycles but leaves parent and child unable to move independently.
- Ban every link: would also prohibit external evidence and a skill's encapsulated resources, causing duplication and context bloat.

## Decision 2: Partition the apex by lifecycle stage

**Decision**: The apex's first-level support is definition → execution → handoff.

**Rationale**: The current headings mix values, timing, mechanisms, and registries. Lifecycle stage is one ordering principle and covers the complete path from intent to delivered result. Each branch can be stated as a necessary condition for the apex outcome.

**Alternatives rejected**:

- Keep five values as siblings: accuracy, grounding, verifiability, and traceability overlap and do not cover authorization or process sequencing cleanly.
- Partition by file mechanism: “rules/skills/MCP” describes implementation containers, not what makes the outcome trustworthy.
- Partition by current rule filenames: entrenches accidental structure and cannot explain why registries are peers of safety constraints.

## Decision 3: Keep five unconditional quality concerns

**Decision**: Retain requirements certainty, internal reasoning, authorization and safety, external expression, and documentation integrity as independent one-topic rules.

**Rationale**: These apply to every relevant session regardless of task-specific tool or artifact. Their ownership boundaries are distinguishable by object: unsettled work definition; agent reasoning; authorized action; reader-facing response; durable contract documentation.

**Alternatives rejected**:

- One large rule: reduces filenames but increases conflicts and prevents focused maintenance.
- Eight current rules: mixes universal constraints with Git workflow, a dynamic tool registry, and named skill routing.

## Decision 4: Move Git and cloud guidance to on-demand skills

**Decision**: Replace the unconditional Git and MCP rules with `git-workflow` and `cloud-platform-research` skills.

**Rationale**: Git collaboration and provider documentation research are conditional workflows. Skills provide metadata-driven discovery and progressive disclosure while retaining repository-specific behavior. The cloud skill may name external providers and server/tool identifiers because they are capabilities it operates, not independent configuration files.

**Alternatives rejected**:

- Delete the content: loses branch/commit/PR and provider-research obligations.
- Keep it in the apex: makes the apex environment-specific and violates the chosen lifecycle abstraction.
- Move it only to explanatory docs: documentation is not an executable on-demand procedure.

## Decision 5: Replace the central router with self-describing multi-match

**Decision**: Delete the named routing table. Put one generic multi-match invariant in the apex and encode triggers, exclusions, and compound applicability in every relevant skill's standard description metadata.

**Rationale**: Claude loads skill descriptions for selection and full skill bodies only when invoked. A second routing table is duplicate state, raises unconditional context cost, and drifts when skill boundaries change.

**Tie-breaking**:

1. Match every available capability description, not only the first plausible one.
2. A specific requested operation, artifact, or domain outranks generic ambiguity handling.
3. Apply prerequisites and requirements work before execution; apply validation, transformation, and decision recording at their actual dependency point.
4. A domain overlay supplements rather than replaces a lifecycle operation.

## Decision 6: Classify skills on two axes

**Decision**: Lifecycle operations and domain overlays are separate groups.

**Lifecycle operations**:

- requirements formalization;
- code/configuration/observable-behavior implementation;
- architecture decision recording;
- communication artifact creation, diagnosis, or final transformation;
- Git collaboration;
- cloud-platform documentation research.

**Domain overlays**:

- Scrum accountability and empiricism;
- Digital Agency React/Tailwind accessibility and design-system constraints.

**Rationale**: A DADS implementation is both implementation and a domain-specific frontend task. A Scrum review deck is both a Scrum-domain task and an artifact task. The intersection is intentional and cannot be made mutually exclusive without discarding necessary guidance.

## Decision 7: Preserve owned resources as encapsulation

**Decision**: A skill may reference paths within its own package and external primary sources. Hard-coded repository installation paths and references to sibling packages are prohibited.

**Rationale**: Progressive disclosure is the documented skill mechanism. Package-owned resources reduce entry-point context and remain independent when resolved relative to the skill directory.

**Portable path rule**: authored instructions use relative package links for model-readable files and `${CLAUDE_SKILL_DIR}` when a shell command needs an absolute package root.

## Decision 8: Use both automated and semantic verification

**Decision**: Add one offline structural suite and maintain a relation table/checklist for semantic MECE.

**Rationale**: Pattern scans reliably catch named dependencies, deleted-path regressions, unresolved links, and byte budgets. They cannot prove that concepts overlap or collectively support the apex. Human review supplies that judgment with explicit questions and traceability.

## Baseline findings

- Unconditional corpus before the top-down rewrite: 20,126 bytes (`CLAUDE.md` plus eight rule files).
- Apex: mixes five values, temporal workflow, close-out, skill routing, and MCP registry pointers.
- Rule layer: three conditional/non-universal files and five universal concerns with several overlapping ownership claims.
- Skill layer: rule dependencies in three entry points, hard-coded package location in the DADS skill, named routing inside DADS resources and Scrum output guidance, and inconsistent reliance on nonstandard duplicate trigger metadata.
