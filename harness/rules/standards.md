# Standards

The project's own configuration, conventions, and documented choices come first. Where the project is silent, follow the established standard for the thing being written rather than a personal style, and name the standard when a decision rests on it.

| Writing | Standard to follow |
|---|---|
| Python | PEP 8, PEP 257, PEP 484 |
| TypeScript | TSConfig `strict`; the typescript-eslint recommended rules |
| React | The Rules of React (react.dev) |
| Web interfaces | WCAG 2.2 level AA; WAI-ARIA Authoring Practices |
| Interfaces for Japanese public services | The Digital Agency Design System (https://design.digital.go.jp/dads/) |
| Shell scripts | Google Shell Style Guide; ShellCheck; POSIX for `#!/bin/sh` |
| The structure of a document | The Minto Pyramid Principle; IMRaD for a report or analysis |
| Project documentation | Docs as Code; Diátaxis for the kind of each document |
| Architecture diagrams | The C4 model, written as Mermaid in Markdown |
| Decision records | ADR in Michael Nygard's format, or MADR |
| A change in behavior | Test-driven development: red, green, refactor |
| Commits | Conventional Commits 1.0.0 |
| Branches and pull requests | GitHub flow: a short-lived branch, a pull request, review, then merge |
| Versions and changelogs | Semantic Versioning 2.0.0; Keep a Changelog |
| GitHub Actions and repository settings | GitHub's security hardening guidance: least-privilege `permissions`, actions pinned to a commit SHA, untrusted input kept out of `run:`, OpenID Connect over stored keys |
| Security of any code | OWASP Top 10; OWASP ASVS for requirements |
| Logging | OWASP Logging Cheat Sheet; OWASP ASVS V16 |

For something not listed, use the standard its practitioners treat as authoritative and say which one. A standard changes over time, so check the current text before relying on a detail.

Facts no standard covers:

- On macOS the interactive shell is zsh, and the system Bash (`/bin/bash`) is 3.2, so Bash 4 features (associative arrays, `mapfile`, `${var,,}`) fail in a script that it runs. The command-line tools are the BSD versions, whose options differ from GNU's.
- Temporary files go under `$TMPDIR`.
- For AWS, assume the Asia Pacific (Tokyo) Region, `ap-northeast-1`, unless another is named, say so in the answer, and check availability for that Region rather than inferring it from another.
