---
name: research-aws
description: Answer a question about a current AWS service from official AWS documentation, read through whatever first-party documentation tools the session has, instead of from recollection. Use when a claim depends on an AWS service's current feature, API, quota, regional availability, pricing, setup, IAM or service-specific behavior, or SDK, CLI, CloudFormation, or CDK syntax. Do not use for an incidental mention of AWS, for another cloud provider, or for a general engineering question whose answer does not depend on the provider.
metadata:
  kind: worker
  permission: read_only
  sandbox: inside
  produces: an answer in which every AWS-specific claim cites an official page or is marked unverified
---

# Research AWS

Answer AWS-specific questions from current first-party evidence. Service names, APIs, quotas, and regional availability change, so memory and a static list of capabilities are not evidence.

## Steps

1. **Fix what is being asked.** Identify the service and feature by the exact AWS name, the claim or decision that needs evidence, and whether the person wants an explanation, a comparison, implementation guidance, or an exact quotation.
   - Region and partition: unless the person names another, assume the Asia Pacific (Tokyo) Region, `ap-northeast-1`, in the commercial partition, and state that assumption in the answer.
   - Note any API version, SDK or CLI version, runtime, language, or date that could change the answer.
   - Ask only when a missing dimension would change the result; otherwise state the assumption used.
2. **Find the official capability the session actually has.** Use the available tool-discovery mechanism before concluding that AWS documentation is unreachable. Nothing here assumes that a particular tool is installed, authorized, or healthy; follow the instructions a discovered tool returns, and never invent a tool, a parameter, or a response. Match the claim to the capability that holds its authoritative value:

   | Claim | Prefer a tool that can |
   |---|---|
   | Behavior, concepts, setup | search and read AWS documentation pages |
   | Quotas, supported models or instance types, other large tables | query table rows rather than read a truncated page |
   | Regional availability of a service, feature, API, or CloudFormation resource | query availability for the target region directly |
   | Pricing | query the AWS price list rather than quote a documentation page |
   | CloudFormation, CDK, or other infrastructure-as-code syntax | search the documentation specific to it |
   | Recent launches or changes | read the service's "what's new" or related-content listing |

   If the capability offers a search over a registry of agent skills, search it first and retrieve only an exact name that the search returned.
3. **Research and reconcile.**
   - Search the narrowest official source that can answer the claim, then open the primary page or API reference and check applicability, version, region, and freshness.
   - For a consequential decision, corroborate across the user guide and the API reference, quotas, or availability data.
   - Resolve a conflict by preferring the source closest to the product contract and the most specific and current scope, such as a quota table over a prose summary. State a conflict that remains.
   - Label an inference that combines several sources.
4. **Answer.** Lead with the direct answer or recommendation. Cite the official page next to every claim whose current value matters. Keep verified AWS behavior apart from architecture advice and local implementation choices. Name the region the answer applies to. Include version, date, prerequisites, quotas and whether they are adjustable, IAM permissions, and exceptions only when they affect the decision. Summarize and link rather than quote at length.

If the official documentation tooling cannot be reached, say so. Use other current official AWS pages (docs.aws.amazon.com, aws.amazon.com) if they can be read. Otherwise give a clearly qualified answer from existing knowledge and say what remains unverified.

## Done when

- Every material AWS-specific claim has current first-party support or is marked unverified.
- Applicability to the target region was checked directly, not inferred from another region, and anything unavailable there is flagged.
- Tool availability and authorization were observed, not assumed.
- Every inference across sources and every remaining freshness risk is labelled.
- The answer stays within the AWS-specific question that was asked.
