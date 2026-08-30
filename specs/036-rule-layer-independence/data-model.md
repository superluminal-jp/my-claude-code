# Data Model: Independent Configuration Pyramid

## Entities

### ConfigurationNode

| Field | Meaning |
|---|---|
| `id` | Stable conceptual identity, not a referenced path |
| `mechanism` | `apex`, `rule`, or `skill` |
| `proposition` | One self-contained central claim |
| `scope` | What the node owns |
| `exclusions` | Adjacent concerns it does not own |
| `loading` | `always` for apex/rules; `on-demand` for skills |

**Invariant**: A node is understandable and actionable without opening another independent configuration node.

### ApexBranch

| Value | Governing question | Completion boundary |
|---|---|---|
| `definition` | Are intent, evidence, constraints, and inference sufficient to choose the right work? | A bounded, justified outcome is selectable |
| `execution` | Is the work performed within authority, risk, and quality controls? | The intended change exists without unauthorized expansion |
| `handoff` | Is the result verified, understandable, and durable? | Evidence, limitations, and synchronized contracts are delivered |

**Invariant**: Branches follow lifecycle order, do not overlap in their primary object, and cover work from request interpretation through durable delivery.

### UniversalRule

| Rule ID | Proposition | Apex branch | Excludes |
|---|---|---|---|
| `requirements-certainty` | Resolve only material gaps before committing to an outcome | `definition` | Execution permission and formal elicitation procedure |
| `reasoning-completeness` | Make dependencies, branches, iteration, and inference complete | `definition` | Reader-facing organization |
| `authorization-safety` | Act only within authorized, recoverable, least-privilege boundaries | `execution` | Ambiguity and tool-specific workflows |
| `external-expression` | Present one answer with vertically supported, horizontally coherent groups | `handoff` | Documentation source-of-truth policy |
| `documentation-integrity` | Keep durable public contracts accurate, canonical, close, and synchronized | `handoff` | General response structure and Git history policy |

### SkillPackage

| Field | Meaning |
|---|---|
| `axis` | `lifecycle-operation` or `domain-overlay` |
| `selector` | Positive request signals in standard description metadata |
| `exclusion` | Nearest non-match boundary |
| `compound_behavior` | Whether and how another independent match composes |
| `entry_point` | Self-contained `SKILL.md` |
| `owned_resources` | Optional progressive-disclosure resources inside the package |

### LifecycleOperation

| Operation | Selection principle |
|---|---|
| Requirements | Material ambiguity needs formal, testable requirements |
| Implementation | Source/configuration/observable behavior changes |
| Decision record | Significant hard-to-reverse architecture choice with a rejected alternative |
| Artifact creation | Incomplete substance requires collaborative construction |
| Artifact diagnosis | Existing material requires structural findings, not silent replacement |
| Artifact transformation | Existing substantive material requires an audience-ready final version |
| Git collaboration | Branch, commit, push, or pull-request work |
| Cloud research | Current AWS/GCP/Azure service behavior or official documentation is needed |

### DomainOverlay

| Overlay | Selection principle |
|---|---|
| Scrum | Request concerns an unmistakable Scrum event, artifact, accountability, or framework deviation |
| Digital Agency frontend | React/Tailwind work uses DADS or a Japanese public-service accessibility/design context |

## Relationships

### Allowed

- `UniversalRule --semantic_support--> ApexBranch`
- `SkillPackage --semantic_specialization--> one or more universal concerns`
- `SkillPackage --owns--> OwnedResource`
- `ConfigurationNode --cites--> ExternalPrimarySource`
- `SkillPackage --composes_at_runtime--> another independently selected SkillPackage` without naming it

### Prohibited

- `Apex --names--> Rule|Skill|Command|Registry`
- `Rule --names--> Rule|Skill|Settings|Registry|Command`
- `SkillPackage --names_or_paths--> Apex|Rule|SiblingSkillPackage`
- `OwnedResource --routes_to--> SiblingSkillPackage`
- `Rule --duplicates_ownership--> Rule`

## State Transitions

### Top-down migration

1. `legacy-apex` → `specified` → `structurally-tested-red` → `independent-green`
2. `mixed-rule-layer` → `mapped-to-final-apex` → `structurally-tested-red` → `five-universal-rules-green`
3. `centrally-routed-skills` → `classified-on-two-axes` → `structurally-tested-red` → `self-describing-green`
4. `stale-docs-tests` → `runtime-stable` → `synchronized` → `full-suite-green`

A lower transition MUST NOT enter `independent-green` before its parent level is green.

## Validation Rules

1. Every surviving rule has exactly one row in the UniversalRule table.
2. Every authored skill description contains positive selection, exclusion, and compound behavior sufficient for routing without a central table.
3. Every authored package reference resolves within the same package unless it is an external URL.
4. No independent node contains a prohibited edge, even when the edge points downward.
5. The unconditional corpus is smaller than 20,126 bytes.
6. Verbatim third-party archive paths have no diff.
