# Logging checklist and sources

Every source below was read from its primary publication on 2026-10-17 unless
marked otherwise. Re-read the source before relying on a detail that matters.

## Sources

| Short name | Source | Note |
|---|---|---|
| CS | [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html) | Primary basis; cited by section name |
| ASVS | [OWASP ASVS 5.0.0, V16 Security Logging and Error Handling](https://raw.githubusercontent.com/OWASP/ASVS/master/5.0/en/0x25-V16-Security-Logging-and-Error-Handling.md) | Requirement text; the ASVS site shows 5.0.0 as both "stable" and "bleeding edge", so cite the version explicitly |
| Top10 | [OWASP Top 10:2025 A09 Security Logging & Alerting Failures](https://top10.owasp.org/2025/A09_2025-Security_Logging_and_Alerting_Failures) | Maps CWE-117, 221, 223, 532, 778. CWE-221 and CWE-223 were not read in full, so no item uses them as a basis |
| CWE-117 | [Improper Output Neutralization for Logs](https://cwe.mitre.org/data/definitions/117.html) | |
| CWE-532 | [Insertion of Sensitive Information into Log File](https://cwe.mitre.org/data/definitions/532.html) | |
| CWE-778 | [Insufficient Logging](https://cwe.mitre.org/data/definitions/778.html) | |
| CWE-779 | [Logging of Excessive Data](https://cwe.mitre.org/data/definitions/779.html) | Not in the A09:2025 mapping |
| Vocab | [OWASP Logging Vocabulary Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Vocabulary_Cheat_Sheet.html) | Event names start with a category prefix such as `authn`, `authz`, `session`, `sys`, `malicious` |
| OTel | [OpenTelemetry Logs Data Model](https://opentelemetry.io/docs/specs/otel/logs/data-model/) | Stable. Optional format reference: Timestamp, TraceId, SpanId, SeverityText/Number, Body, Resource, Attributes, EventName |
| NIST | [NIST SP 800-92 Rev. 1 initial public draft, Cybersecurity Log Management Planning Guide](https://csrc.nist.gov/pubs/sp/800/92/r1/ipd) | Background only; a draft (2023-10-11), never cited as a requirement |
| PyLog | [Python `logging` module reference](https://docs.python.org/3/library/logging.html) | Read 2026-10-24; basis for LOG-PRC only |
| PyHowto | [Python Logging HOWTO](https://docs.python.org/3/howto/logging.html) | Read 2026-10-24; basis for LOG-PRC only |
| React | [React `Component` reference](https://react.dev/reference/react/Component) | Read 2026-10-24; basis for LOG-PRC only |
| LambdaLog | [AWS Lambda, Configuring advanced logging controls](https://docs.aws.amazon.com/lambda/latest/dg/monitoring-logs.html) | Read 2026-10-24; basis for LOG-PRC only |
| PT-Py | [Powertools for AWS Lambda (Python), Logger](https://docs.aws.amazon.com/powertools/python/latest/core/logger/) | Read 2026-10-24; basis for LOG-PRC only |
| PT-TS | [Powertools for AWS Lambda (TypeScript), Logger](https://docs.aws.amazon.com/powertools/typescript/latest/features/logger/) | Read 2026-10-24; basis for LOG-PRC only |
| CDK-Lambda | [AWS CDK v2 `aws_lambda.Function`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_lambda.Function.html) | Read 2026-10-24; basis for LOG-PRC only |
| CDK-Assert | [AWS CDK v2 `assertions.Template`](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.assertions.Template.html) | Read 2026-10-24; a verification method, never a requirement |
| GC-Run | [Cloud Run, Logging and viewing logs](https://docs.cloud.google.com/run/docs/logging) | Read 2026-10-24; basis for LOG-PRC only |
| GC-Node | [Cloud Logging, Setting up Cloud Logging for Node.js](https://docs.cloud.google.com/logging/docs/setup/nodejs) | Read 2026-10-24; basis for LOG-PRC only |
| Az-OTel | [Azure Monitor, Enable OpenTelemetry for .NET, Node.js, Python, and Java applications](https://learn.microsoft.com/azure/azure-monitor/app/opentelemetry-enable) | Read 2026-10-24; basis for LOG-PRC only. Microsoft recommends its Microsoft OpenTelemetry Distro for new apps; existing Azure Monitor Distro users need no change |
| CFN-Logs | [AWS CloudFormation `AWS::Logs::LogGroup`](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-resource-logs-loggroup.html) | Read 2026-10-24; infrastructure-code evidence for group B |
| TF-GLog | [Terraform Google provider `google_logging_project_bucket_config`](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/logging_project_bucket_config) | Read 2026-10-24 from the page's source in `hashicorp/terraform-provider-google`; infrastructure-code evidence for group B |
| Az-Workspace | [Azure Bicep `Microsoft.OperationalInsights/workspaces`](https://learn.microsoft.com/azure/templates/microsoft.operationalinsights/workspaces) | Read 2026-10-24; infrastructure-code evidence for group B |
| TF-Test | [Terraform tests](https://developer.hashicorp.com/terraform/language/tests) | Read 2026-10-24; a verification method, never a requirement |
| Bicep-Lint | [Bicep linter](https://learn.microsoft.com/azure/azure-resource-manager/bicep/linter) | Read 2026-10-24; a verification method, never a requirement |
| Bicep-Config | [Configure your Bicep environment](https://learn.microsoft.com/azure/azure-resource-manager/bicep/bicep-config) | Read 2026-10-24; states that the Bicep test framework is an experimental feature |
| GC-Fn | [Cloud Run functions, Monitoring and logging](https://docs.cloud.google.com/functions/docs/monitoring/logging) | Read 2026-10-24; basis for LOG-PRC only. Points Cloud Run functions to the Cloud Run logging guide |
| AzFn | [Configure monitoring for Azure Functions](https://learn.microsoft.com/azure/azure-functions/configure-monitoring) | Read 2026-10-24; basis for LOG-PRC only |
| Bedrock | [Amazon Bedrock, Monitor model invocation using CloudWatch Logs and Amazon S3](https://docs.aws.amazon.com/bedrock/latest/userguide/model-invocation-logging.html) | Read 2026-10-24; basis for LOG-PRC only |
| GC-RRLog | [Gemini Enterprise Agent Platform (formerly Vertex AI), Log and share requests and responses](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/request-response-logging) | Read 2026-10-24; basis for LOG-PRC only. The page does not state the default state of logging |
| Az-Trace | [Microsoft Foundry, Add client-side tracing to Foundry agents (preview)](https://learn.microsoft.com/azure/foundry/observability/how-to/trace-agent-client-side) | Read 2026-10-24; basis for LOG-PRC only. A preview feature |
| GH-Commands | [GitHub Actions, Workflow commands](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-commands) | Read 2026-10-24; basis for LOG-PRC only |
| GH-Secure | [GitHub Actions, Secure use reference](https://docs.github.com/en/actions/reference/security/secure-use) | Read 2026-10-24; basis for LOG-PRC only |
| GH-Logs | [GitHub Actions, Using workflow run logs](https://docs.github.com/en/actions/how-tos/monitor-workflows/use-workflow-run-logs) | Read 2026-10-24; basis for LOG-PRC only |
| GH-Repo | [GitHub, About repositories](https://docs.github.com/en/repositories/creating-and-managing-repositories/about-repositories) | Read 2026-10-24; basis for LOG-PRC only |
| GH-Settings | [GitHub, Managing GitHub Actions settings for a repository](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository) | Read 2026-10-24; evidence for group B |

Deliberately excluded because no primary text was read: ISO/IEC 27002,
PCI DSS, NIST SP 800-53 AU. Map to them only after reading the standard.
Stacks without a row in LOG-PRC (for example Java or Go) have no practice
items; only the security items apply to them.

## Group A: verify from code

### LOG-INV Inventory and collection

| ID | Requirement | Basis |
|---|---|---|
| LOG-INV-1 | A documented or discoverable inventory of what is logged, in which format, and where it goes exists, and logs are sent only to those destinations | ASVS 16.1.1, 16.2.3; CS Event collection |
| LOG-INV-2 | Events pass through the framework logger or one application-wide handler, not scattered ad hoc output | CS Event collection |
| LOG-INV-3 | The format is common and machine-parseable so a log processor can read and correlate it | ASVS 16.2.4; CS Event collection; OTel optional |

### LOG-EVT Events to log

An event is required only where the code in scope performs the action.

| ID | Event | Basis |
|---|---|---|
| LOG-EVT-1 | Every authentication attempt, success and failure, with authentication type and factor metadata | ASVS 16.3.1; CS Which events to log |
| LOG-EVT-2 | Failed authorization attempts; for the highest assurance level, all authorization decisions and sensitive data access, without the data itself | ASVS 16.3.2; CS |
| LOG-EVT-3 | Input and output validation failures and attempts to bypass validation, business logic, or anti-automation controls | ASVS 16.3.3; CS |
| LOG-EVT-4 | Session management failures such as tampered session identifiers or invalid tokens | CS Which events to log |
| LOG-EVT-5 | Unexpected errors and security control failures, such as backend TLS or certificate validation failures | ASVS 16.3.4; CS |
| LOG-EVT-6 | Higher-risk actions: user and privilege changes, administrative and break-glass actions, sensitive data access, cryptographic key use and rotation, creation or deletion of system objects, data import or export, file uploads, deserialization failures | CS Which events to log |
| LOG-EVT-7 | Application startup, shutdown, and logging initialization, pause, or stop | CS Which events to log |
| LOG-EVT-8 | Missing or omitted security-relevant events and missing key details are findings in themselves | CWE-778; Top10 |
| LOG-EVT-9 | Event names follow one stable vocabulary, optionally the category-prefix scheme | Vocab (category-prefix event names) |

### LOG-ATT Event attributes

| ID | Requirement | Basis |
|---|---|---|
| LOG-ATT-1 | Each entry carries when, where, who, and what: timestamp, application or service, endpoint or code location, source address or actor identity when known, event type, severity, description | ASVS 16.2.1; CS Event attributes |
| LOG-ATT-2 | Related events can be linked by an interaction or correlation identifier | CS Event attributes; OTel TraceId/SpanId optional |
| LOG-ATT-3 | Timestamps use UTC or an explicit offset | ASVS 16.2.2 |

### LOG-DATA Data exclusion

| ID | Requirement | Basis |
|---|---|---|
| LOG-DATA-1 | Passwords, secrets, connection strings, keys, access tokens, and session identifiers are never written in clear text; hash a session identifier if tracking is needed | CS Data to exclude; CWE-532 |
| LOG-DATA-2 | Sensitive personal data, payment cardholder data, and data above the log system's classification are removed, masked, hashed, or encrypted | ASVS 16.2.5; CS; CWE-532 |
| LOG-DATA-3 | Rules by sensitivity are enforced in code, not left to each call site | ASVS 16.2.5 |
| LOG-DATA-4 | Only data needed for the event's purpose is logged; verbose payloads, stack traces, and bodies are kept out of the main stream | CS; CWE-779 |
| LOG-DATA-5 | Events from known or trusted users are flagged, never suppressed | CS Data to exclude |

### LOG-INJ Injection and robustness

| ID | Requirement | Basis |
|---|---|---|
| LOG-INJ-1 | Untrusted data is encoded or neutralized for the output format, including CR, LF, and delimiter characters | ASVS 16.4.1; CS Event collection; CWE-117 |
| LOG-INJ-2 | A malformed untrusted field is omitted or replaced with a bounded validation-failure note, not allowed to drop or corrupt the whole event | CS Event collection |
| LOG-INJ-3 | Database log writes use parameterized queries | CS Event collection |
| LOG-INJ-4 | A logging failure does not crash the application, change the request outcome, or leak information | CS Event collection |
| LOG-INJ-5 | Log volume cannot be driven by one input to exhaust resources | CS Verification; CWE-779 |

### LOG-ERR Error handling

| ID | Requirement | Basis |
|---|---|---|
| LOG-ERR-1 | Callers receive generic error messages without stack traces, queries, keys, or tokens; detail goes to the log | ASVS 16.5.1 |
| LOG-ERR-2 | The application keeps operating securely and fails closed, not open, when an external resource or an exception occurs | ASVS 16.5.2, 16.5.3 |
| LOG-ERR-3 | A last-resort handler catches unhandled exceptions, preserves the error log, and keeps the process available | ASVS 16.5.4 (highest assurance level) |

### LOG-CFG Levels and configuration

| ID | Requirement | Basis |
|---|---|---|
| LOG-CFG-1 | The default level meets the business and security need | CS Customizable logging |
| LOG-CFG-2 | Logging, and events a requirement mandates, cannot be fully disabled by configuration | CS Customizable logging |
| LOG-CFG-3 | Level changes follow approved logic or change management | CS Customizable logging |

### LOG-TST Verification

| ID | Requirement | Basis |
|---|---|---|
| LOG-TST-1 | Tests assert that required events are emitted with their attributes | CS Verification |
| LOG-TST-2 | Tests assert that a secret sentinel does not appear in output | CS Verification; CWE-532 |
| LOG-TST-3 | Tests assert that CR, LF, and delimiter input is neutralized | CS Verification; CWE-117 |
| LOG-TST-4 | Tests cover logger failure, such as an unwritable destination, without changing the request outcome | CS Verification |
| LOG-TST-5 | Log-driven actions such as lockouts cannot be abused to deny service to other users | CS Verification |

### LOG-PRC Logging practice of the stack

These items make logs follow the official guidance of the language,
framework, or platform in use, rather than the security standards above. Most
are not security requirements. The *Security impact* column names the
security items that a Fail would also violate, for items that prevent the
exposure of secrets or personal data or log injection; a Fail of such an item
counts and ranks as a security failure. An item
applies only where the code in scope uses the stack named in its *Applies to*
column; otherwise it is N/A. TypeScript publishes no logging guidance of its
own, so TypeScript code follows the items for its runtime and for React.
Prompts and model responses can carry personal data and secrets; in the
application's own logs they fall under LOG-DATA-1, LOG-DATA-2, and LOG-DATA-4,
and the items below cover what the inference platforms record.

| ID | Requirement | Applies to | Security impact | Basis |
|---|---|---|---|---|
| LOG-PRC-1 | Each module logs through a logger named for it (`logging.getLogger(__name__)`), never through the root logger | Python | none | PyHowto Advanced Logging Tutorial; Configuring Logging for a Library |
| LOG-PRC-2 | Library code adds no handler other than `NullHandler`; the application decides where output goes | Python libraries | none | PyHowto Configuring Logging for a Library |
| LOG-PRC-3 | Variable data is passed as logger arguments instead of being formatted into the message first, and arguments that are costly to compute are guarded by `isEnabledFor` | Python | none | PyHowto Logging variable data; Optimization |
| LOG-PRC-4 | `exception()` is called only from an exception handler, and the deprecated `warn` is not used | Python | none | PyLog Logger Objects |
| LOG-PRC-5 | Azure Monitor export is configured for the application's named logger, so the SDK's own messages are not collected | Python on Azure | none | Az-OTel Enable OpenTelemetry with Application Insights |
| LOG-PRC-6 | Each Lambda function emits JSON, through Lambda's JSON log format or a JSON logger | AWS Lambda | none | LambdaLog Configuring advanced logging controls for Lambda Event Functions |
| LOG-PRC-7 | The logger's configured level and Lambda's application log level agree; Lambda's level takes precedence and discards events below it | AWS Lambda | none | PT-Py Advanced Logging Controls; PT-TS log levels and `AWS_LAMBDA_LOG_LEVEL` |
| LOG-PRC-8 | Each Lambda function writes to a log group the CDK app declares and configures (the `logGroup` property), not to the auto-created default group whose settings the app cannot change, and the legacy `logRetention` property is not used | AWS CDK | none | CDK-Lambda `logGroup`; `logRetention` |
| LOG-PRC-9 | Structured entries are single lines of serialized JSON on stdout or stderr, with `severity` and `message` so Cloud Logging maps them to the entry's severity and display text | Google Cloud Run services and Cloud Run functions | none | GC-Run Write container logs; Special JSON fields in messages; GC-Fn Writing and viewing logs |
| LOG-PRC-10 | A Node.js logger's levels map onto Cloud Logging severities: the Winston and Bunyan integrations do this, and another logger such as Pino needs an explicit mapping | Node.js on Google Cloud | none | GC-Node Configure logging |
| LOG-PRC-11 | The OpenTelemetry distro is initialized at the application entry point, before the libraries it instruments are loaded | Python and Node.js on Azure | none | Az-OTel Enable OpenTelemetry with Application Insights |
| LOG-PRC-12 | The Application Insights connection string comes from the environment in production; code sets it only for local development and test | Azure | none | Az-OTel Paste the connection string in your environment |
| LOG-PRC-13 | Rendering errors are caught by an error boundary, a class component because function components cannot be one, that reports them from `componentDidCatch` | React | none | React Catching rendering errors with an Error Boundary; componentDidCatch |
| LOG-PRC-14 | Errors that error boundaries do not catch (event handlers, asynchronous code, server rendering, the boundary itself) are reported where they are handled | React | none | React Catching rendering errors with an Error Boundary, for the limits; reporting them elsewhere is this checklist's design decision |
| LOG-PRC-15 | `host.json` sets `logging.logLevel` per category, and keeps `Host.Results` and `Host.Aggregator` at `Information` or lower, because a higher level stops request and metric telemetry | Azure Functions | none | AzFn Configure log levels |
| LOG-PRC-16 | The `Trace` level is not enabled in production, because its messages might contain sensitive application data | Azure Functions | LOG-DATA-2 | AzFn Configure log levels |
| LOG-PRC-17 | When sampling is enabled, `samplingSettings.excludedTypes` keeps the telemetry that must not be dropped, such as `Request` and `Exception` | Azure Functions | none | AzFn Configure sampling |
| LOG-PRC-18 | The app connects with `APPLICATIONINSIGHTS_CONNECTION_STRING`, not the deprecated `APPINSIGHTS_INSTRUMENTATIONKEY` | Azure Functions | none | AzFn Enable Application Insights integration |
| LOG-PRC-19 | Model invocation logging, disabled by default, records full request and response bodies once enabled; it is enabled only deliberately, and its CloudWatch Logs or S3 destination is treated as a log store under LOG-DATA and group B | Amazon Bedrock | LOG-DATA-2 | Bedrock Monitor model invocation using CloudWatch Logs and Amazon S3; Log entry format; treating the destination as a log store is this checklist's design decision |
| LOG-PRC-20 | Request-response logging records full requests and responses to BigQuery for the sampled fraction; its sampling rate is set deliberately, and the BigQuery table is treated as a log store under LOG-DATA and group B | Vertex AI (Gemini Enterprise Agent Platform) | LOG-DATA-2 | GC-RRLog Logging table schema; Enable request-response logging; treating the table as a log store is this checklist's design decision |
| LOG-PRC-21 | Content recording (`OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT`, false by default) stays off in production unless privacy requirements allow it; prompts, tool arguments, and span attributes carry no secrets; and Python functions under `@trace_function` are reviewed, because all their parameters and return values are traced regardless of that setting | Azure AI Foundry | LOG-DATA-1, LOG-DATA-2 | Az-Trace Enable content recording; Control tracing behavior with environment variables; Security and privacy |
| LOG-PRC-22 | A sensitive value that is not a GitHub secret, such as a token obtained during the run, is registered with `::add-mask::` before it is printed or used in another workflow command | GitHub Actions | LOG-DATA-1 | GH-Commands Masking a value in a log |
| LOG-PRC-23 | Each sensitive value is its own secret, never part of structured data (JSON, XML, YAML) that redaction can fail to match, and a value derived from a secret (a signed token, a Base64 or URL encoding) is registered as a secret too | GitHub Actions | LOG-DATA-1 | GH-Secure Use secrets for sensitive information |
| LOG-PRC-24 | Output that may contain workflow-command syntax, such as untrusted input or generated scripts, is printed between `::stop-commands::` and the matching resume token, which is generated randomly for each run | GitHub Actions | LOG-INJ-1 | GH-Commands Stopping and starting workflow commands; applying it to untrusted input is this checklist's design decision |
| LOG-PRC-25 | A workflow in a public repository prints nothing that only collaborators may see, because a public repository is accessible to everyone and reading its logs needs only read access and a GitHub login | GitHub Actions in public repositories | LOG-DATA-1, LOG-DATA-2 | GH-Logs Viewing logs to diagnose failures; GH-Repo About repository visibility |
| LOG-PRC-26 | Errors, warnings, and notices meant for reviewers are emitted with `::error`, `::warning`, or `::notice` so they become annotations, and long output is folded between `::group::` and `::endgroup::` | GitHub Actions | none | GH-Commands Setting an error message; Grouping log lines |

## Group B: report as Unverified unless the repository holds the configuration

| ID | Requirement | Basis |
|---|---|---|
| LOG-OPS-1 | Logs are protected from unauthorized access and modification; read access is restricted and reviewed | ASVS 16.4.2; CS Protection |
| LOG-OPS-2 | Logs are sent securely to a logically separate system for analysis, detection, alerting, and escalation | ASVS 16.4.3; CS Protection |
| LOG-OPS-3 | Server and device clocks are synchronized | ASVS 16.2.2; CS Event collection |
| LOG-OPS-4 | Tampering, deletion, unauthorized access, and a stopped logger are detected | CS Operation, Protection |
| LOG-OPS-5 | Serious events alert the responsible team immediately and feed incident response | CS Monitoring of events; Top10 |
| LOG-OPS-6 | Retention follows legal, regulatory, and contractual duration, neither shorter nor longer | CS Disposal |
| LOG-OPS-7 | Disk and quota limits prevent log exhaustion; collection, storage, and viewing are separated on the network | CS Network architecture, Attacks on logs |

When infrastructure code or logger configuration in the repository settles one
of these, evaluate it as group A evidence and cite the file. Infrastructure
code shows the declared configuration, not the deployed state: say so, because
a deployment pipeline such as GitHub Actions may not be the only path that
changes the cloud. A declared retention settles LOG-OPS-6 only against the
duration the user says the law or a contract requires; without that duration,
cite the value and report the item as Unverified.

GitHub Actions workflow logs are kept for 90 days by default, adjustable to 1
to 90 days in a public repository and 1 to 400 days in a private one, in the
repository's Actions settings (GH-Settings Configuring the retention period
for checks, workflow runs, commit statuses, artifacts, and logs in your
repository). That setting is not in the code, so report LOG-OPS-6 for
workflow logs as Unverified, naming the setting the user must confirm.

### Evidence in infrastructure code

Where each cloud's infrastructure code settles a group B item. An attribute
that is absent is evidence too; the basis says what its absence means.

| Item | AWS CDK (synthesized CloudFormation) | Google Cloud (Terraform) | Azure (Bicep) | Basis |
|---|---|---|---|---|
| `LOG-OPS-1` | `AWS::Logs::LogGroup` `KmsKeyId` (absent: not AWS KMS) and `DeletionProtectionEnabled` | `google_logging_project_bucket_config` `cmek_settings.kms_key_name`, and `locked` (a locked bucket's retention cannot change, and it can be deleted only when empty) | `Microsoft.OperationalInsights/workspaces` `properties.features.disableLocalAuth` | CFN-Logs Properties; TF-GLog Argument Reference; Az-Workspace WorkspaceFeatures |
| `LOG-OPS-6` | `RetentionInDays` (absent: events never expire) | `retention_days` | `properties.retentionInDays` | CFN-Logs Properties; TF-GLog Argument Reference; Az-Workspace WorkspaceProperties |
| `LOG-OPS-7` | none in the sources read | none in the sources read | `properties.publicNetworkAccessForIngestion`, `properties.publicNetworkAccessForQuery`, and `properties.workspaceCapping.dailyQuotaGb` | Az-Workspace WorkspaceProperties; WorkspaceCapping |

Check this evidence mechanically where the project already can; a CI workflow
that runs the check counts, and is cited:

- AWS CDK: an assertion over the synthesized template (CDK-Assert
  `allResourcesProperties`).
- Terraform: `terraform test` with `command = plan`, which creates no
  infrastructure (TF-Test Run blocks); mocked providers need Terraform 1.7.0
  or later.
- Bicep: the linter in `bicep build` or `bicep lint` (Bicep-Lint) checks best
  practices, not these values, and the Bicep test framework is experimental
  (Bicep-Config), so read the values from the file.
