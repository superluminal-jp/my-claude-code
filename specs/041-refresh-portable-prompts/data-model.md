# Data Model: Refresh Portable System Prompts

Documents, not stored data.

## Portable prompt file

| Field | Rule |
|---|---|
| Title | One H1 naming the service |
| Placement | Exact settings path and field label per [research.md](./research.md) R1/R3 |
| Verified facts | Bullet list, each with official URL and verification date (2026-10-05) |
| Paste block(s) | Fenced; each ≤ its budget; measured length stated beside the label |
| Not ported | Source behaviors omitted, one line of reason each |

## Paste block

| Attribute | ChatGPT "Custom instructions" | ChatGPT "More about you" | Claude.ai "Instructions for Claude" |
|---|---|---|---|
| Budget | ≤ 1,500 chars (Free/Go limit; paid up to 5,000) | ≤ 1,500 chars (conservative; unverified) | ≤ ~4,000 chars (self-imposed; no documented limit) |
| Content | Operating rules | Profile and deliverable preferences | Operating rules + profile |
| Measured with | Unicode code points (`python3 len()`) | same | same |

Validation: length ≤ budget; no model names; no `.claude` paths, slash commands, skill names; no framework labels required in output; no all-caps emphasis.
