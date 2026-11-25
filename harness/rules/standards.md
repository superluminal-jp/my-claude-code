# Standards

Where the project is silent, the established standard for the thing being written decides, not a personal style.

- Use standards actively: follow the relevant one in everyday work without being asked, name it in the answer's Method line (`communication.md`) when it decided how the answer was reasoned or structured, and, beyond those listed here, look up the international standards, best practices, and frameworks for the subject at hand and use them the same way. This covers how an answer is thought out as well as how it is written: when the question is of a kind an established method covers, work it out with that method, and do not force one onto a question none fits.
- Use them accurately where it counts. When a design choice, a review finding, a requirement, or a disputed point rests on a standard, name it with its section, rule, or criterion number, and read the current text first when it is public. Attribute to a standard only what it says, and say so when a point comes from memory because the text could not be read.

| Writing | Standard or established practice |
|---|---|
| Python | PEP 8; PEP 257; the specification for the Python type system (PEP 484) |
| TypeScript | TSConfig `strict`; the typescript-eslint recommended rules |
| React | The Rules of React (react.dev) |
| Shell scripts | Google Shell Style Guide for Bash; POSIX for `#!/bin/sh`; ShellCheck |
| Web interfaces | WCAG 2.2 level AA; WAI-ARIA Authoring Practices; JIS X 8341-3 for Japanese public services |
| Interfaces for Japanese public services | The Digital Agency Design System (https://design.digital.go.jp/dads/) |
| HTTP APIs | OpenAPI Specification; RFC 9110 (HTTP Semantics); RFC 9457 (Problem Details) for error responses |
| The structure of an application | The Twelve-Factor App |
| Dates, times, and text encoding | ISO 8601 / RFC 3339 timestamps in UTC; UTF-8 |
| A change in behavior | Kent Beck's test-driven development (Canon TDD: a test list, one failing test at a time, make it pass, refactor), where the project has a test setup |
| Code review | Google Engineering Practices Documentation (the code review guidelines) |
| Comments and API documentation in code | PEP 257 docstrings; TSDoc; a comment gives the reason, which the code cannot show |
| Cloud architecture | The provider's Well-Architected Framework (AWS, Google Cloud, Azure), with its guidance for the workload: the AWS Serverless Applications and Generative AI lenses, Google Cloud's AI and ML perspective, Azure's AI workload guidance |
| Cloud account and resource configuration | The provider's CIS Benchmark: CIS Amazon Web Services Foundations, Google Cloud Platform Foundation, Microsoft Azure Foundations |
| Cloud identity and access | Least privilege as the provider documents it: AWS "Security best practices in IAM", Google Cloud's IAM security best practices, "Best practices for Azure RBAC" |
| Infrastructure as code | AWS CDK best practices; the Terraform Style Guide |
| Applications built on language models | OWASP Top 10 for LLM Applications; OWASP Top 10 for Agentic Applications; MITRE ATLAS for threats to AI systems; NIST AI Risk Management Framework with its Generative AI Profile (NIST AI 600-1); Japan's AI事業者ガイドライン |
| Prompts, agents, and tools | The model provider's official prompting guidance; the Model Context Protocol specification |
| Model and dataset documentation | Model Cards; Datasheets for Datasets |
| Security of any code | OWASP Top 10; OWASP ASVS for requirements; the OWASP Cheat Sheet Series for how to implement a control |
| Security of APIs and authorization | OWASP API Security Top 10; RFC 9700 (OAuth 2.0 security) |
| Dependencies and the build supply chain | SLSA; OpenSSF Scorecard; a committed lockfile; an SBOM in SPDX (ISO/IEC 5962) or CycloneDX (ECMA-424), following the format the project already uses |
| CI/CD pipelines | OWASP Top 10 CI/CD Security Risks |
| Logging and telemetry | OWASP Logging Cheat Sheet; OWASP ASVS 5.0 V16; OpenTelemetry semantic conventions |
| Threat models | STRIDE; OWASP Threat Modeling Cheat Sheet |
| Vulnerability findings and disclosure | CWE identifiers; CVSS for severity; `SECURITY.md` and `security.txt` (RFC 9116) for how to report |
| Incident response and reports | NIST SP 800-61 Rev. 3 for the response; the blameless postmortem of Google's Site Reliability Engineering book for the report |
| Defining a problem | Toyota Business Practices, "clarify the problem": current state, ideal state, and the gap; Kepner-Tregoe is / is-not; no cause or solution in the statement |
| Finding the cause of a problem | Kepner-Tregoe problem analysis: test each possible cause against the is / is-not facts |
| Weighing evidence for competing explanations | Analysis of Competing Hypotheses (Heuer): seek evidence against each, not for one |
| Comparing options and deciding | Kepner-Tregoe decision analysis: musts first, then weighted wants, then the risks of the best option |
| Confirming what was asked | A read-back: restate the request as what will be produced and have it confirmed; the Ladder of Inference to find where two readings parted |
| The structure of a document | The Minto Pyramid Principle; IMRaD for a report or analysis |
| Documents for stakeholders and decision-makers | The Minto Pyramid Principle with a situation-complication-question opening; plain language (ISO 24495-1); Amazon's PR/FAQ and narrative memo for a proposal |
| Technical writing | Google developer documentation style guide |
| Japanese prose | JTF日本語標準スタイルガイド; 「公用文作成の考え方」 for public-sector documents |
| Project documentation | Docs as Code; Diátaxis for the kind of each document; Standard Readme for a README |
| Procedures, runbooks, and SOPs | A Diátaxis how-to guide, with background and reference in their own documents; EPA QA/G-6 for an SOP's sections and document control; the Microsoft Writing Style Guide's procedures and instructions checklist; AWS Well-Architected OPS07-BP03 (runbook: a known outcome), OPS07-BP04 (playbook: an investigation), and REL08-BP01; Azure Well-Architected OE:02; IEC/IEEE 82079-1 and ISO/IEC/IEEE 26514 for instructions to users. Each step gives one action, its expected result, and how to check it; a risky step gives its stop condition and rollback; someone other than the author runs the procedure before it is relied on |
| Requirements | EARS; the key words of RFC 2119 and RFC 8174; Given-When-Then for acceptance criteria |
| Architecture documentation | arc42; the C4 model for diagrams, written as Mermaid in Markdown |
| Decision records | ADR in Michael Nygard's format, or MADR |
| Commits | Conventional Commits 1.0.0 |
| Branches and pull requests | GitHub flow: a short-lived branch, a pull request, review, then merge |
| Versions and changelogs | Semantic Versioning 2.0.0; Keep a Changelog |
| GitHub Actions and repository settings | GitHub's security hardening guidance for Actions |

## Facts no standard covers

- On macOS the interactive shell is zsh, and the system Bash (`/bin/bash`) is 3.2, so Bash 4 features (associative arrays, `mapfile`, `${var,,}`) fail in a script that it runs. The command-line tools are the BSD versions, whose options differ from GNU's.
- Temporary files go under `${TMPDIR:-/tmp}`.
- For AWS, assume the Asia Pacific (Tokyo) Region, `ap-northeast-1`, unless another is named, say so in the answer, and check availability for that Region rather than inferring it from another.
