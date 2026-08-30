---
name: cloud-platform-research
description: Research current AWS, Google Cloud, or Microsoft Azure services and answer from official provider documentation through available first-party documentation tools. Use when a claim depends on a provider's current feature, API, limit, regional availability, setup, or supported behavior. Do not use for incidental provider mentions or generic engineering questions whose answer is provider-independent. Apply alongside any independently matching implementation, architecture, or document operation whenever live provider evidence is needed.
---

# Cloud Platform Research

Answer provider-specific questions from current first-party evidence, not recollection or a static capability registry.

## Establish the research contract

Identify:

- provider and service;
- exact claim or decision that needs evidence;
- region, API version, runtime, language, or date constraints that could change the answer;
- whether the user needs explanation, comparison, implementation guidance, or an exact quotation.

Ask only when a missing dimension would materially change the result. Otherwise state the narrow assumption used.

## Discover the current official capability

Use the available tool-discovery mechanism before concluding that provider documentation is unavailable. Select the provider's official source at task time:

| Subject | Preferred official capability |
|---|---|
| AWS services and regional availability | `aws-knowledge` or `aws-documentation` |
| Amazon Bedrock AgentCore | `bedrock-agentcore` |
| Strands Agents | `strands-agents` |
| Google Cloud and Google developer products | `google-developer-knowledge` |
| Microsoft Azure and Microsoft Learn | `microsoft-learn` |

Treat this table as a preference, not proof that a capability is configured, authorized, or healthy. Discover its current tools and follow any instructions returned by the server. Do not infer OAuth state or invent a tool, skill name, parameter, or response.

For AWS agent-skill questions, if the official capability exposes skill-registry search, search the `agent_skills` topic first and retrieve only an exact name returned by that search. Never guess a registry identifier.

## Research and reconcile

1. Search the narrowest official documentation source that can answer the claim.
2. Open the primary page or API reference and verify applicability, version, region, and publication freshness.
3. For consequential decisions, corroborate across the relevant product guide and API or limits reference when both exist.
4. Resolve conflicts by preferring the source closest to the product contract and the most specific/current scope. State any remaining conflict instead of silently choosing.
5. Clearly label an inference that combines multiple sources.

If official documentation tooling is unavailable, state that live provider documentation could not be reached. Use other current official provider pages if accessible; otherwise give only a clearly qualified answer from existing knowledge and identify what remains unverified.

## Answer contract

- Lead with the direct answer or recommendation.
- Cite the official page next to every claim whose current value matters.
- Separate verified provider behavior from architecture advice and local implementation choices.
- Include region, version, date, prerequisites, limits, and exceptions only when they affect the user's decision.
- Do not overquote; summarize accurately and provide a direct link.

## Completion check

- Every provider-specific material claim has current first-party support or is explicitly unverified.
- Tool availability and authorization were observed rather than assumed.
- Any cross-source inference and unresolved freshness risk is labelled.
- The answer does not broaden a provider-specific request into unrelated platform advice.
