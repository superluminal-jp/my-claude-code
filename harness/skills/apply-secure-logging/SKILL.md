---
name: apply-secure-logging
description: Implement, change, or review application and CI logging against a bundled checklist of security requirements (OWASP Logging Cheat Sheet, OWASP ASVS V16, related CWE entries) and of the logging practices in the official documentation of Python, React, AWS Lambda, Google Cloud including Cloud Run functions, Azure including Azure Functions, cloud AI inference services, and GitHub Actions. Use when code or a workflow adds or modifies log output, security event logging, audit trails, error handling that logs, or logging configuration, including logging resources in infrastructure code (AWS CDK, Terraform, Bicep), and when asked whether logging follows best practice. Do not use for operating log infrastructure such as a SIEM or alert tuning, for observability that records no log or trace content, or for a change that touches no logging behavior.
metadata:
  kind: overlay
  permission: workspace_write
  sandbox: inside
  produces: a status with evidence for every checklist item, and the logging change when one was asked for
---

# Apply secure logging

Make application logging record the events an investigation needs, with the attributes it needs, without leaking data or opening an injection path, in the way the official guidance of its stack expects, and show each claim with evidence from the code. This skill adds its criteria to whatever implementation or review is under way; it does not replace that work. The sources and every item are in `references/logging-checklist.md`.

## Scope

- **Judged from the repository (group A):** which events are logged, their attributes, excluded data, injection defenses, failure handling, log levels, and tests.
- **Not judged from application code (group B):** storage permissions, transport and retention, host time sync, tamper detection, alerting, network separation. Never mark these passed from application code. Report them as unverified with the evidence the person must supply, unless the repository holds the configuration, in which case inspect and cite it.
- **Stack practice (LOG-PRC):** practice from the official documentation of the stacks the checklist covers. Each item applies only when the code in scope uses its stack. Never apply a practice the checklist does not list, whether from memory or borrowed from another stack.
- Keep the project's existing logger, format, and conventions. Add a dependency or a new format only when no existing mechanism can satisfy an item.
- Use only the sources the checklist names. Read a requirement ID, version, or CWE name from the checklist, never from memory.

## Steps

1. **Establish scope and mode.** Identify the target (a diff, files, or the whole repository), the language and framework, the logging library and handler in use, where log output goes, the platform the code runs on, any AI inference service it calls, the infrastructure code that deploys it, and the CI workflows that build it. The stacks found decide which LOG-PRC items apply. When the request names no target, use the working-tree diff if there is one, otherwise the whole repository, and say so.
   - Review: run steps 2 and 5 only, and change nothing.
   - Implement or fix: run steps 2 to 6. Fixing a finding is implementation.
   - Ask only when a missing fact would change the result, such as whether the system handles payment or personal data.
2. **Inventory what exists.** Locate the shared logging entry point, every direct print or ad hoc logging call, the events already logged, redaction or masking helpers, and the logging tests. The inventory is the baseline for review and for implementation.
3. **Decide what to log.** Map each security-relevant action of the code in scope to the events in checklist section LOG-EVT. Log what the code can see; do not invent events for actions it never performs. Keep severity proportional to risk. Never log a value the checklist's exclusion list forbids, even to make an event more informative.
4. **Implement** through the shared entry point, not scattered calls.
   - First write a failing test that captures log output and asserts the event, its required attributes, the redaction of a secret sentinel, and the neutralization of an input containing CR, LF, and delimiter characters. Where the contract cannot be automated, record the current behavior and how the change will be checked.
   - Make the smallest change that passes: event calls at the decision points, attributes from the checklist, redaction before the call reaches the output, encoding for the output format, UTC timestamps, and a logging failure path that cannot crash the request or leak data.
   - Keep error responses to the caller generic and put the detail in the log.
   - Run the project's tests, linters, and type checks.
5. **Check every checklist item for the scope.** Each item gets exactly one status:

   | Status | Meaning |
   |---|---|
   | Pass | Satisfied; cite `file:line` or the test that shows it |
   | Fail | Violated or missing for code in scope; cite the location and the item ID |
   | N/A | The condition does not occur in scope; say why |
   | Unverified | Group B, or group A with no available evidence; say what evidence would settle it |

   - Never turn Unverified into Pass by inference.
   - Prefer a mechanical check the project already has: its linters and tests, or the infrastructure checks the checklist's evidence section names. Do not add a tool to get one.
   - In implement mode, a Fail in code the change adds or modifies blocks the report: fix it and run this step again. Stop after two rounds that leave the same Fail, and report it as remaining with what blocked the fix. A Fail in untouched code is reported as pre-existing.
   - In implement mode this is a self-check by the agent that made the change. When the scope also handles authentication, payment, or personal data, have a subagent with a fresh context evaluate the group A items against the diff, and report any item whose status differs. With no subagent available, say that the result is a self-check only.
6. **Report.** Lead with the verdict: the counts of Fail and Unverified and the most serious failures, with security failures ranked before stack-practice ones. Then the item table in checklist order, the changes made with the checks run and their results, the group B evidence the person must supply, and what was not checked.

## Edge cases

- No logging mechanism exists: a review reports the missing events as Fail; an implementation uses the language's standard logging facility rather than adding a dependency.
- No log call in scope: every item that depends on one is N/A.
- A standard outside the checklist is requested (for example ISO/IEC 27002, PCI DSS, or NIST SP 800-53): say that the checklist excludes it because no primary text was read, and do not map to it.
- A source's version differs from the checklist's: read the source again and report the difference.
- The stack has no LOG-PRC items: report the practice group as N/A for that reason and apply the security items only.

## Done when

- Every checklist item has a status with evidence or a stated reason.
- For an implementation, LOG-DATA-1, LOG-DATA-2, LOG-INJ-1, and LOG-INJ-4, and every LOG-PRC item whose security impact names one of them, are Pass or N/A for what the change adds or modifies. If one is still Fail after the stop condition of step 5, the work is reported as incomplete.
- For an implementation, the test written first now passes and the project's existing checks still pass; a check that could not run is named with the reason.

## Bundled files

| File | Read when |
|---|---|
| `references/logging-checklist.md` | Every run: the items, their sources, and the evidence each accepts |
