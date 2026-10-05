---
name: aws-research
description: Research current AWS services and answer from official AWS documentation through available first-party documentation tools. Use when a claim depends on an AWS service's current feature, API, quota, regional availability, pricing, setup, IAM or service-specific behavior, or SDK/CLI/CloudFormation/CDK syntax. Do not use for incidental AWS mentions, other cloud providers, or generic engineering questions whose answer is provider-independent. Apply alongside any independently matching implementation, architecture, or document operation whenever live AWS evidence is needed.
---

# AWS Research

Answer AWS-specific questions from current first-party evidence, not recollection or a static capability registry.

## Establish the research contract

Identify:

- service and feature (use the exact AWS service name; names and APIs change);
- exact claim or decision that needs evidence;
- region and partition: unless the user names another, assume the Asia Pacific (Tokyo) Region, `ap-northeast-1`, in the commercial partition, and state that assumption in the answer; API version, SDK or CLI version, runtime, language, or date constraints that could change the answer;
- whether the user needs explanation, comparison, implementation guidance, or an exact quotation.

Ask only when a missing dimension would materially change the result. Otherwise state the narrow assumption used.

## Discover the current official capability

Use the available tool-discovery mechanism before concluding that AWS documentation is unavailable. Select official AWS sources at task time from whatever documentation tools the current session actually exposes. Nothing here assumes a particular tool is installed, configured, authorized, or healthy. Follow any instructions a discovered tool returns. Do not infer OAuth state or invent a tool, skill name, parameter, or response.

Match the claim to the capability that holds its authoritative value:

| Claim type | Prefer a tool that can |
|---|---|
| Behavior, concepts, setup | search and read AWS documentation pages |
| Service quotas, supported models or instance types, other large tables | query table rows rather than read a truncated page |
| Regional availability of a service, feature, API, or CloudFormation resource | query availability for the target region directly rather than infer it from prose |
| Pricing | query the AWS price list rather than quote a documentation page |
| CloudFormation, CDK, or IaC syntax | search the IaC-specific documentation |
| Recent launches or changes | check the service's "what's new" or related-content listing |

If the official capability exposes skill-registry search, search the `agent_skills` topic first and retrieve only an exact name returned by that search. Never guess a registry identifier.

## Research and reconcile

1. Search the narrowest official AWS source that can answer the claim.
2. Open the primary page or API reference and verify applicability, version, region, and publication freshness.
3. For consequential decisions, corroborate across the relevant user guide and API reference, quotas, or availability data when they exist.
4. Resolve conflicts by preferring the source closest to the product contract and the most specific/current scope (for example, a service quota table over a prose summary). State any remaining conflict instead of silently choosing.
5. Clearly label an inference that combines multiple sources.

If official AWS documentation tooling is unavailable, state that live AWS documentation could not be reached. Use other current official AWS pages (docs.aws.amazon.com, aws.amazon.com) if accessible; otherwise give only a clearly qualified answer from existing knowledge and identify what remains unverified.

## Answer contract

- Lead with the direct answer or recommendation.
- Cite the official page next to every claim whose current value matters.
- Separate verified AWS behavior from architecture advice and local implementation choices.
- Name the region the answer applies to. Include version, date, prerequisites, quotas (and whether they are adjustable), IAM permissions, and exceptions only when they affect the user's decision.
- Do not overquote; summarize accurately and provide a direct link.

## Completion check

- Every AWS-specific material claim has current first-party support or is explicitly unverified.
- Applicability to the target region (default `ap-northeast-1`) was checked directly, not inferred from another region such as `us-east-1`, and any feature unavailable there is flagged.
- Tool availability and authorization were observed rather than assumed.
- Any cross-source inference and unresolved freshness risk is labelled.
- The answer does not broaden an AWS-specific request into unrelated platform advice.
