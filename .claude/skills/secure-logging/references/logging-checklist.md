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

Deliberately excluded because no primary text was read: ISO/IEC 27002,
PCI DSS, NIST SP 800-53 AU. Map to them only after reading the standard.

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
of these, evaluate it as group A evidence and cite the file.
