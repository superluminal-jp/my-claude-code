---
name: research-aws
description: Answers a question about an AWS service from current official AWS documentation instead of from recollection, citing the page behind each claim. Use when an answer depends on an AWS service's current features, API, quotas, regional availability, pricing, IAM behavior, or SDK, CLI, CloudFormation, or CDK syntax. Not for an incidental mention of AWS, another cloud provider, or a general engineering question whose answer does not depend on the provider.
---

# Research AWS

AWS service names, APIs, quotas, and regional availability change often, so recollection is not evidence for them. Read the current official source and cite it.

## Steps

1. **Fix the question.** Name the service and feature by their exact AWS names and the claim that needs evidence. Unless the person names another Region, assume Asia Pacific (Tokyo), `ap-northeast-1`, in the commercial partition, and say so in the answer. Note any SDK, CLI, runtime, or API version that could change the answer.

2. **Use the official sources the session has.** Check which AWS documentation tools are available (search for them among the session's tools before concluding there are none) and pick by the kind of claim:

   | Claim | Source to prefer |
   |---|---|
   | Behavior, concepts, setup | Search, then read the user-guide or API-reference page |
   | Quotas, supported models or instance types | A table query, since long tables are cut off when a page is read whole |
   | Availability of a service, feature, or resource type in a Region | A regional-availability query for that Region |
   | CloudFormation or CDK syntax | The resource or construct reference page |
   | Recent launches | The service's "What's New" or related-content listing |

   Without such tools, read `docs.aws.amazon.com` and `aws.amazon.com` pages directly. If nothing official can be reached, say so and give a clearly marked answer from memory.

3. **Check that the page applies:** the right service and feature, the Region, the version, and the page's date. For a consequential decision, confirm across two official sources, such as the user guide and the API reference. When sources disagree, prefer the one closest to the product contract (API reference, quota table) and report the disagreement.

4. **Answer.** Lead with the direct answer. Put the page URL next to each claim whose current value matters. Keep what AWS documents apart from your own architecture advice, and mark any conclusion drawn by combining pages as an inference. Include quotas, IAM permissions, prerequisites, and exceptions only where they affect the decision.

## Done when

- Every AWS-specific claim that matters cites an official page or is marked unverified.
- Applicability to the target Region was checked for that Region, not inferred from another.
- The answer names the Region and any version it assumes.
