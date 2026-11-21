---
name: apply-secure-logging
description: Implements, changes, or reviews application and CI logging against a bundled checklist drawn from the OWASP Logging Cheat Sheet, OWASP ASVS V16, related CWE entries, and the official logging guidance of Python, React, AWS Lambda, Google Cloud, Azure, cloud AI inference services, and GitHub Actions. Use when code or a workflow adds or changes log output, security event logging, audit trails, error handling that logs, or logging configuration (including log resources in AWS CDK, Terraform, or Bicep), or when asked whether logging follows best practice. Not for temporary debugging output that will be removed, nor for operating log infrastructure such as a SIEM or alert tuning.
---

# Apply secure logging

Logs fail in two directions: they miss the events needed to investigate an incident, or they record data that should never be stored. `references/logging-checklist.md` lists what to check for both, each item with an identifier and the source it rests on.

## Steps

1. **Set the scope.** Name the code, configuration, and workflows under review or change, the stack (language, framework, cloud, CI), and which actions the code performs that are security-relevant: authentication, authorization, input validation, session handling, privileged or high-risk actions.

2. **Read the checklist** `references/logging-checklist.md`. Group A items are verified from code. Group B items concern storage, access, retention, and monitoring; they are verified only where the repository holds the configuration (for example infrastructure code) and are otherwise reported as unverified. The `LOG-PRC` section applies only to the stacks it has a row for.

3. **Find how the project logs now:** the logger and its configuration, the output format and destination, any redaction or masking helper, and existing log tests. Search for direct output (`print`, `console.log`, `echo` of variables in workflows) that bypasses the logger.

4. **Go through every item in scope and give it a status with evidence:**

   | Status | Meaning | Evidence |
   |---|---|---|
   | Met | The code or configuration satisfies it | `path:line` |
   | Not met | It applies and is not satisfied | `path:line` of the gap, and the consequence |
   | Not applicable | The code does not perform the action | One-line reason |
   | Unverified | It cannot be decided from this repository | What would decide it |

   Check data exclusion (`LOG-DATA`) and injection (`LOG-INJ`) first, since those are where logs cause harm.

5. **When a change was asked for, make it** with the `implement-change` steps: a test that captures log output and asserts what must be present and what must be absent (a secret, an unneutralized line break), then the change. Use the project's logger and add redaction in one shared place rather than at each call site.

6. **Report** the status table, items not met ordered by risk, what was changed, and what remains unverified. Cite checklist identifiers (`LOG-DATA-1`) so findings can be traced to their source.

## Guidelines

- The checklist's sources were read on the dates it records. Before relying on a detail that decides something important, re-read the source it cites.
- Never print a real secret or personal data to demonstrate a finding; point to the line.
- A requirement from a standard the checklist does not cover (for example PCI DSS or ISO/IEC 27002) is out of its scope; say so rather than mapping it from memory.

## Done when

- Every checklist item in scope has a status and its evidence.
- No item is reported as met without a `path:line`.
- Requested changes are covered by a test that inspects log output, and the project's checks pass.
