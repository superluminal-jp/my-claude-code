# System boundaries: errors, logging, and security

Read when the change touches input from outside, output to users, files, network, databases, external APIs, secrets, error handling, or logging. Where the project's own security documents are stricter than a shortcut, follow them. When a requirement is unclear, such as a data classification or a choice of cryptography, ask before implementing.

## Error handling

- At a system boundary, validate clearly, use typed or narrow error paths, and give the user a message that is safe to show. Fail fast on programmer mistakes where the language does so idiomatically.
- Do not add catch-all handling for internal states that cannot occur; trust the framework.
- Do not hide a failure without a documented reason.
- Do not leak stack traces or internal detail to end users.

## Logging

- Follow the project's logger, levels, and format. Log what an operator needs to debug and audit.
- Never log secrets, tokens, or unredacted personal data.
- At input, output, and request boundaries, include a correlation identifier when the codebase already uses one.
- Avoid log noise in hot paths unless diagnosing a problem.

## Security in the code

- Never introduce command injection, cross-site scripting, SQL injection, or another flaw of the classes the OWASP Top 10 lists. Validate and encode at the boundary.
- Apply least privilege to secrets and capabilities. Use vetted cryptography and keep dependencies current when touching those layers.
- Prefer current recommendations over deprecated patterns, and handle the common weakness classes that CWE catalogues.
- Insecure or misleading behavior found in code the change adds or modifies is fixed before the change is reported as done.

## Security in the development environment

- Do not expose credentials. Keep secrets in the stores the project designates.
- Do not execute unreviewed remote content. Use official sources over HTTPS.
- Obtain explicit authorization before an effect that is destructive, machine-wide, credential-bearing, or visible outside the workspace, when that authority is not already clear.
- When suggesting a command or an integration, default to the safer option and name the material risk.

## Out of scope but worth saying

When a practice would clearly help but lies outside the task, such as a missing timeout on a new client or missing structured logs for a new integration, state the gap, why it matters, and a minimal follow-up. Do not implement it without the person's agreement.

## Sources

- OWASP Top 10 (2025): <https://owasp.org/www-project-top-ten/>
- OWASP Application Security Verification Standard (ASVS), version 5.0 (2025): <https://owasp.org/www-project-application-security-verification-standard/>
- CWE, Common Weakness Enumeration (MITRE): <https://cwe.mitre.org/>
