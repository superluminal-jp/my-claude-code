---
name: secure-logging
description: Implement, change, or review application and CI logging as a domain overlay, against security requirements (OWASP Logging Cheat Sheet, OWASP ASVS 5.0.0 V16, related CWE entries) and the logging practices in the official documentation of Python, React, AWS Lambda, Google Cloud including Cloud Run functions, Azure including Azure Functions, cloud AI inference services, and GitHub Actions. Use when code or a workflow adds or modifies log output, security event logging, audit trails, error handling that logs, or logging configuration, including logging resources in infrastructure code (AWS CDK, Terraform, Bicep), and when asked whether logging follows best practice. Do not use for operating log infrastructure (SIEM, alert tuning), observability that records no log or trace content (metrics design), or changes that touch no logging behavior. Apply alongside every independently matching requirements, implementation, review, or document operation; this guidance supplements rather than replaces that operation.
---

# Secure Logging

Make application logging record the events an investigation needs, with the
attributes it needs, without leaking data or opening an injection path, in the
way the official guidance of its stack expects, and prove each claim with
evidence from the code. Sources and the checklist are in
`references/logging-checklist.md`.

## Scope

- **Code-verifiable (group A):** which events are logged, their attributes,
  excluded data, injection defenses, failure handling, log levels, and tests.
  Judge these from the repository.
- **Not code-verifiable (group B):** storage permissions, transport and
  retention, host time sync, tamper detection, alerting, network separation.
  Never mark these passed from application code. Report them as unverified with
  the evidence the user must supply, unless the repository holds the
  configuration (infrastructure code, logger config), in which case inspect it
  and cite it.
- **Stack practice (LOG-PRC, judged from code like group A):** logging practice
  from the official documentation of Python, React, AWS Lambda and CDK, Google
  Cloud (Cloud Run and Cloud Run functions), Azure (including Azure Functions),
  the AI inference services Amazon Bedrock, Vertex AI, and Azure AI Foundry,
  and GitHub Actions workflows. Most are not security requirements; an item
  whose *Security impact* names a security item counts and ranks with it. Each
  applies
  only when the code in scope uses its stack, and TypeScript follows the items
  of its runtime. Never apply a practice the checklist does not list, whether
  from memory or borrowed from another stack.
- Preserve the project's existing logger, format, and conventions. Add a
  dependency or a new format only when no existing mechanism can satisfy an item.
- Use only the sources named in the checklist. Do not quote a requirement ID,
  version, or CWE name from memory; read it from the checklist.

## Workflow

### 1. Establish scope and mode

Identify the target (diff, files, or whole repository), language, framework,
the logging library and handler already in use, where log output goes, and the
platform the code runs on (for example AWS Lambda, Cloud Run, Cloud Run
functions, or Azure Functions), any AI inference service it calls, and the
infrastructure code that deploys it (AWS CDK, Terraform, or Bicep), and the
CI workflows that build and deploy it (GitHub Actions). The stacks found decide
which LOG-PRC items apply.
When the request names no target, use the working-tree diff if there is one,
otherwise the whole repository, and say so in the report. Choose the mode from
the request:

- **Review:** run steps 2 and 5 only; change nothing.
- **Implement or fix:** run steps 2 to 6. Fixing a finding is implementation.

Ask only when a missing fact would change the result, such as whether the
system handles payment or personal data, or a compliance regime the user wants
mapped. Otherwise state the assumption.

### 2. Inventory what exists

Locate the shared logging entry point, every direct print or ad hoc logging
call, the events already logged, redaction or masking helpers, and the logging
tests. Record them: the inventory is the baseline for both review and
implementation (ASVS 16.1.1).

### 3. Decide what to log

For the code in scope, map each security-relevant action to the events in
checklist section LOG-EVT. Log what the code can see; do not invent events for
actions it never performs. Keep severity proportional to risk so alerts stay
meaningful. Do not log a value the checklist's exclusion list forbids, even to
make an event more informative. Write each log call and its configuration the
way the applicable LOG-PRC items require.

### 4. Implement

Work through the shared entry point, not scattered calls.

1. Where the contract is automatable, first write a failing test that captures
   log output and asserts the event, its required attributes, the redaction of
   a secret sentinel, and neutralization of an input containing CR, LF, and
   delimiter characters. Run it and observe the failure. Otherwise record the
   current behavior and how the change will be checked.
2. Implement the smallest change that makes it pass: event calls at the
   decision points, attributes from the checklist, redaction before the log
   call reaches the output, encoding for the output format, UTC timestamps,
   and a logging failure path that cannot crash the request or leak data.
3. Keep error responses to the caller generic; put the detail in the log.
4. Run the project's tests, linters, and type checks, then return to step 5 and
   check the result against the whole checklist before reporting.

### 5. Check

Evaluate every checklist item for the scope. Each item gets exactly one
status:

| Status | Meaning |
|---|---|
| Pass | Satisfied; cite `file:line` or the test that shows it |
| Fail | Violated or missing for code in scope; cite the location and the item ID |
| N/A | The condition does not occur in scope; say why |
| Unverified | Group B, or group A with no available evidence; say what evidence would settle it |

Never convert Unverified into Pass by inference. Observed behavior, sourced
requirement, and your inference stay distinguishable in the wording.

Prefer a mechanical check where the project already has one: its linters and
tests for LOG-PRC items, and for infrastructure code the checks the
checklist's evidence section names (an AWS CDK template assertion, or
`terraform test` in plan mode). A CI workflow that runs a check counts; cite
it. Do not add a tool to get one; say which items rest on reading the code
instead.

In implement mode, a Fail in code the change adds or modifies blocks the
report: fix it and run this step again. Stop after two rounds that leave the
same Fail, and report it as remaining with what blocked the fix. Report a Fail
in code the change leaves untouched as pre-existing, and fix it only when the
request covers it or the user asks.

In implement mode, this step is a self-check by the agent that made the
change. When the scope also handles authentication, payment, or personal data,
a subagent should evaluate the group A items against the diff in a fresh
context; report any item whose status differs. If no subagent is available, say the result is a
self-check only.

### 6. Report

Lead with the verdict: counts of Fail and Unverified, and the most serious
failures; in implement mode, separate remaining Fail from pre-existing Fail.
Count LOG-PRC Fail apart from security Fail, and rank security failures first;
a LOG-PRC item whose Security impact names a security item counts with it.
Then give the item table in checklist order; N/A items may share one row per
checklist section that lists their IDs and the common reason. Then give the
changes made (if any) with the checks run and their results, and the group B
evidence the user must supply. State what was not checked.

## Edge cases

- **No logging mechanism exists:** a review reports the missing events as Fail.
  An implementation picks the language's standard logging facility rather than
  adding a dependency.
- **No log call in scope:** report every item that depends on one as N/A.
- **A standard outside the checklist is requested** (for example ISO/IEC 27002,
  PCI DSS, or NIST SP 800-53): say the checklist excludes it because no primary
  text was read, and do not map to it.
- **A source's version differs from the checklist's:** re-read the source and
  report the difference instead of silently using either.
- **The stack has no LOG-PRC items** (for example Java or Go): report the
  practice group as N/A for that reason and apply the security items only.

## Completion check

- Every checklist item has a status with evidence or a stated reason.
- For implementation, LOG-DATA-1, LOG-DATA-2, LOG-INJ-1, and LOG-INJ-4, and
  every LOG-PRC item whose Security impact names one of them, are Pass or N/A
  for the code and workflows the change adds or modifies, shown by a test or by
  reading the call. If one is still Fail after the stop condition in step 5,
  report the work as incomplete.
- For implementation, the test written first now passes and the project's
  existing checks still pass; if a check could not run, say which and why.
