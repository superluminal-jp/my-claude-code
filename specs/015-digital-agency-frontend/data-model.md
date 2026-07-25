# Data Model: Digital Agency Frontend Skill

## SkillPackage

| Field | Type | Rules |
|---|---|---|
| `name` | kebab-case identifier | Exactly `digital-agency-frontend`; matches directory and frontmatter |
| `description` | routing text | Names what the skill does and concrete trigger contexts |
| `workflow` | ordered instructions | Covers discovery, source check, design, implementation, verification, and close-out |
| `references` | list of `BundledReference` | Exactly the required DADS and dashboard references for v1 |
| `interface_metadata` | UI metadata | Display name, 25–64 character description, and prompt explicitly naming `$digital-agency-frontend` |

## BundledReference

| Field | Type | Rules |
|---|---|---|
| `path` | relative path | One level below `SKILL.md` under `references/` |
| `topic` | enum | `dads-react-tailwind` or `dashboard-design` |
| `load_condition` | text | DADS reference loads for all matching work; dashboard reference loads only for dashboard work |
| `source_records` | list of `SourceRecord` | At least one official source; no third-party authority substitutes |
| `guidance` | concise operational rules | Summarizes decisions without wholesale-copying source content |

## SourceRecord

| Field | Type | Rules |
|---|---|---|
| `title` | text | Human-readable official source title |
| `url` | HTTPS URL | Digital Agency or official `digital-go-jp` repository |
| `observed_version` | text or date | Version when exposed; otherwise official update date |
| `retrieved` | date | `2026-07-20` for initial implementation |
| `scope` | text | What decisions the source supports |
| `usage_note` | text | Attribution, modification, or license guidance where relevant |

## CrossAgentEntry

| Field | Type | Rules |
|---|---|---|
| `repo_link` | symlink | `.agents/skills/digital-agency-frontend` resolves to the authored Claude skill |
| `installer_name` | token | Included exactly once in `CUSTOM_SKILLS` |
| `global_link` | symlink | Installer creates `~/.agents/skills/digital-agency-frontend` to installed `~/.claude/skills/digital-agency-frontend` |

## Invariants

1. There is one authored `SKILL.md`; cross-agent entries never copy it.
2. `SKILL.md` references every bundled reference directly; references do not form deeper chains.
3. Live official information overrides a bundled summary, and the mismatch is disclosed.
4. General frontend work does not require loading dashboard-only detail.
5. Power BI artifact generation remains outside the skill contract.
6. Official examples are adapted and product-tested; they are not treated as proof of conformance.
7. Repository routing, installer, deployment map, and bilingual documentation describe the same skill name and scope.
