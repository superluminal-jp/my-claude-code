# MCP servers

Purpose: know which MCP server answers which cloud question, and when calling one is mandatory. Server definitions live in `.mcp.json`; each server's own tool descriptions are already in context.

## Routing — mandatory

When a question directly concerns a provider's services, features, or documentation, invoke the matching server **before** answering:

- **AWS** → `aws-knowledge` or `aws-documentation`
- **GCP** → `google-developer-knowledge`
- **Azure** → `microsoft-learn`

If the server is unreachable, warn that live documentation is unavailable, then answer from training knowledge.

Incidental mentions do not require a call ("I'm deployed on AWS but my question is about Python loops").

## Official provider skill registries

Prefer a provider's own guided skill over ad-hoc guidance where one exists.

- **AWS**: `aws-knowledge` exposes AWS's official skill registry. Call `aws___search_documentation` with `topics: ["agent_skills"]` to find a match, then `aws___retrieve_skill` with the **exact** `skill_name` returned — never invent or guess one — to fetch its `SKILL.md` (and any referenced file via the `file` param). Use this in place of freehand advice for workflows it covers.
- **GCP**: no equivalent. `google-developer-knowledge` exposes docs search and answer tools only; no skill-retrieval tool exists in its schema.
- **Azure**: unverified. `microsoft-learn` requires OAuth authorization; until authorized, its tool set cannot be checked. Re-check once authorized rather than assuming either way.
