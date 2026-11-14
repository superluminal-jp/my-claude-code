# my-claude-code

Reusable Claude Code **user-level** configuration that enforces the latest
official specifications and best practices from https://code.claude.com/docs/.

日本語版: [README.ja.md](README.ja.md)

Building your own config? See
[`docs/claude-config-design.md`](docs/claude-config-design.md) (Japanese) for the
test each always-on instruction has to pass, and what this repo deliberately
leaves out of it.

`install.sh` synchronizes the repository-managed parts of `harness/` to
`~/.claude/`, making its settings, rules, skills, agents, and memory available
across projects while preserving unrelated user files.

The source lives in `harness/`, not in this repository's own `.claude/`: a
sandboxed Bash command cannot write under `.claude/`, and files there would
also load a second time, as this repository's project configuration. The
redesign that produced this layout is recorded in
[`docs/harness-zero-base.md`](docs/harness-zero-base.md) (Japanese).

## What this provides

- **`harness/CLAUDE.md`** — Persistent user memory: one governing outcome and
  its three lifecycle branches (define, execute, hand off), a generic
  multi-match algorithm for applying every independently matching capability,
  a rule that scales the process to the change (a local, reversible change
  needs a failing check and a passing run; a change to an interface, a data
  flow, or several modules also needs evidence for each acceptance criterion
  and an independent review; a change to authentication, secrets, personal
  data, data migration, permissions, public exposure, or anything hard to undo
  also needs a person's approval), and a delegation policy. Under that policy,
  without waiting for the user to ask, Claude delegates to a subagent when one
  of three conditions holds: the output is long and only its result is needed,
  the pieces are independent and can run in parallel, or a reader independent
  of the author is needed. It uses the subagent type defined for that kind of
  work, which fixes the model, effort, and tools, and never lets two subagents
  write the same file; otherwise it does the work itself, because a subagent
  starts from an empty context. Decisions, design, code review, and the
  judgment that the work is complete stay on the main conversation's model.
  `harness/CLAUDE.md` names no rule, skill, server, or model — the design
  rationale is in [`docs/claude-config-design.md`](docs/claude-config-design.md)
- **`harness/settings.json`** — User-level Claude Code settings: the main
  conversation's model (`opus`) and its reasoning effort level, fixed at
  `xhigh` (the highest level the settings file accepts) by `effortLevel` and,
  for `claude-opus-5-5`, again under `modelSettings` (the reason is recorded in
  [`docs/harness-zero-base.md`](docs/harness-zero-base.md)); the credential
  deny list; the OS sandbox turned on for every Bash command with only the
  openings everyday work needs; three `SessionStart` hooks; and the two MCP
  servers it allows, with the ones it stops outright (see [Sandbox and session hooks](#sandbox-and-session-hooks)
  and [MCP Servers](#mcp-servers))
- **`harness/rules/`** — Always-on universal rules, each kept to what changes
  Claude's decisions and nothing else, and each supporting exactly one apex
  branch: requirements-certainty clarification triggers, reasoning
  completeness (four self-checks: dependencies and concurrency, conditions
  and branches, iteration, inference), authorization and safety (the enforced deny list lives in
  `settings.json`), and reader-facing structure (the Pyramid Principle
  self-check; the parts of a research paper — summary, premises, method,
  results, discussion, conclusion — in answer-first order; structure made
  visible through numbered claim headings and bold supporting claims; premises
  and plain definitions for a reader new to the subject, unless the user's own
  messages show otherwise;
  a reader who has seen none of the conversation, code, or documents, so
  every ambiguous word and pointer names what it refers to; each term in the
  form its field uses, never a coined translation; and no explanation by
  metaphor or analogy). None references
  another rule, a skill, or a config path. What each file deliberately
  omits, and where that content went, is recorded in
  [`docs/claude-config-design.md`](docs/claude-config-design.md)
- **`harness/agents/`** — Four subagent definitions, one per kind of delegated
  work. Each definition fixes the model, reasoning effort, and tools, which is
  what the delegation policy of `harness/CLAUDE.md` relies on:
  - `read-only-reviewer` (`sonnet`, `xhigh`) — the independent reviewer that
    the challenge step of `specify-requirements` and the assurance review of
    `verify-change` start. Its tools are Read, Grep, and Glob only, and it
    starts without CLAUDE.md (a CLAUDE.md in a directory whose files it reads
    still loads, as do the MCP servers' instructions). When a file it was given
    cannot be read, it answers `NOT REVIEWED: <path>: <reason>` instead of
    judging from the rest ([spec 070](specs/070-review-integrity/problem.md))
  - `check-runner` (`haiku`, `low`) — runs checks whose output is long (tests,
    builds, linters, type checkers) and reports each command, its exit code,
    and the verbatim output of every failure. Its tools are Bash, Read, Grep,
    and Glob; it starts without CLAUDE.md, changes no file, and decides
    nothing
  - `file-searcher` (`haiku`, `medium`) — a read-only search of a codebase or a
    set of documents that returns `path:line` locations with short excerpts.
    Its tools are Read, Grep, and Glob; it starts without CLAUDE.md
  - `task-worker` (`sonnet`, `xhigh`) — one self-contained task that needs
    judgment, for independent tasks that run in parallel. Its definition sets
    no tool restriction; it writes only the files its task assigns it and does
    not declare the larger work complete
- **`harness/skills/`** — On-demand playbooks loaded by relevance, 17 in all,
  self-describing so that no central router is needed. Each `SKILL.md` holds
  a `description` (when to use the skill and when not to) and, under
  `metadata`, its `kind` (`worker`, `overlay`, or `orchestrator`), its
  `permission` (`read_only`, `workspace_write`, or `external_effect`), and its
  `sandbox` declaration: `inside` (every bundled command runs in the Bash
  sandbox as it is) or `network` (some steps need the hosts the skill names).
  13 skills are `inside`; `apply-dads-frontend`, `build-dads-slides`, and
  `manage-git` are `network`. A skill is one unit — one trigger, one product,
  one completion check (`Done when`) — and meets the contract that
  `tests/assert_skill_contract.py` checks (see [Verification](#verification)).
  - Carrying a change from problem to acceptance, in the order the work goes.
    `clarify-intent` (agree on intent first: the AI states its reading in
    four parts — understanding, assumptions with confidence, what is out of
    scope, open points — for the person to reject, converges on a criterion
    rather than on cases, grounds the criterion in a named framework within
    three rounds, and records the agreement as a memo; it runs when asked or
    when drift shows itself, such as a rejected deliverable or a point
    restated twice, and writes no formal requirements),
    `define-problem` (turn a vague complaint into one verifiable problem
    statement — the gap between the current and the ideal state, with its
    significance — keeping any solution or unverified cause the person brought
    in a section of its own),
    `specify-requirements` (record an agreed problem as a problem card that
    keeps evidence, counter-evidence, hypotheses, and proposed solutions
    apart; decompose it into an AND/OR/LEAF requirements graph whose parents
    carry their own `L2` or `L3` acceptance criteria; have a read-only
    challenger (`read-only-reviewer`) object when the change is risky or the
    evidence is thin; and run a bundled standard-library checker whose gate
    answers `ready` or `blocked` before implementation starts. A requirement
    a person directed carries its `origin`, and a criterion verifiable only
    after deploy carries its `stage`; the graph is the only place for the
    acceptance criteria;
    [spec 059](specs/059-refinement-graph-checker/spec.md),
    [spec 060](specs/060-goal-refinement/spec.md)),
    `implement-change` (change code, configuration, tests, scripts, or
    interfaces test-first in the smallest coherent step: define the completion
    condition, write the specification first when observable behavior
    changes, watch a check fail for the right reason, make the smallest change
    that passes, run the repository's own checks, update the documents that
    state a changed contract, and commit, push, or open a pull request only on
    request; its guidance on specification first, type safety, and system
    boundaries such as input, errors, secrets, and logging loads only when it
    applies), and
    `verify-change` (record in a verification manifest, for every acceptance
    criterion, which check ran on which commit with what result; classify the
    change's risk; for medium and high risk have `read-only-reviewer` run an
    independent assurance review of the committed change; and run a bundled
    standard-library checker whose gate answers `pass`, `fail`, or `blocked` —
    never building a parent's pass from its children's, never counting an
    AI's claim as evidence, and stopping on unclassified risk, a missing
    approval, a high-risk change without a challenge report, a medium- or
    high-risk change without an assurance review of its commit, or a finding
    not answered. It reads JUnit XML and Jest `--json` results, decides before
    deploy with `--stage pre_deploy` when some criteria can only be verified
    after it, keeps its records in a records-only commit after the reviewed
    one, has each review round read a bundle that `review_prep.py` writes
    under `$TMPDIR` and a round after fixes read only the fix diff, prints a
    one-screen review card for the person who decides, and carries a
    preregistered pilot procedure (`references/pilot.md`, `scripts/pilot.py`)
    for deciding whether it cuts review time without losing quality;
    [spec 061](specs/061-change-assurance/spec.md),
    [spec 062](specs/062-review-card/spec.md),
    [spec 063](specs/063-pilot-metrics/spec.md),
    [spec 064](specs/064-assurance-gate-hardening/spec.md),
    [spec 068](specs/068-skill-procedure-gaps/problem.md),
    [spec 069](specs/069-assurance-review-cost/problem.md)).
    `deliver-change` is the parent skill (`kind: orchestrator`) that applies
    `define-problem`, `specify-requirements`, `implement-change`, and
    `verify-change` in that order: it goes on to implementation only when the
    requirements gate says `ready`, returns to implementation or to the
    requirements by the reason a failed or blocked gate gives, and hands the
    person the gate's decision with the review card unchanged
  - Other workers: `define-product-strategy` (vision, target users, value
    proposition, success metrics, must/should/could/won't scope, and
    constraints, framed before development begins as one strategy brief, for a
    new product or for an initiative on an existing one),
    `structure-document` (structure a document — report, proposal, design
    document, specification, README, email, slide outline, pull-request or
    issue body — as one claim tree with its answer first, checked by a bundled
    standard-library checker (`check.py`) of the text and, for a logic review,
    of a claim tree written from an existing document; a document that
    leaves the conversation is also read by a subagent that has seen none of
    the conversation ([spec 057](specs/057-context-free-reader/spec.md));
    the skill is used only for drafting, revising, or reviewing a document, while the
    always-on rule `pyramid-principle.md` covers answers),
    `sync-docs` (keep documentation consistent with code, specifications,
    decisions, and research artifacts as they change, and audit for drift:
    bundled read-only standard-library scripts inspect the project, list the
    changed artifact classes and the documents next to the changed files, and
    check links; the update goes in the same change and the report carries a
    `Documentation impact` block; `.living-documentation.json` corrects the
    scripts' classification and can declare a documentation tree of product
    and feature folders, whose READMEs `check_tree.py` requires to link parent
    to child and back; on request the skill builds that tree from per-kind
    README templates, writing only verified facts and marking the rest
    `TODO(unfilled)`),
    `manage-git` (branches, Conventional Commits, pushes, and pull requests so
    that history stays reviewable and nothing is published beyond what was
    asked; each of commit, push, and pull request needs its own request),
    `research-aws` (answer from official AWS documentation read through
    whatever first-party documentation tools the session has, not from
    recollection; every AWS-specific claim cites an official page or is marked
    unverified),
    `draw-system-diagrams` (system architecture diagrams a first-time reader,
    from a non-engineer to a specialist, can follow: a set of C4 views, each
    answering one question for one audience at one level of abstraction,
    written as Mermaid in Markdown by default, as draw.io or Structurizr DSL
    when those fit, with every element traced to a source and checked by a
    bundled standard-library checker (`check_diagrams.py`) for title, lead
    text, legend, labelled lines, the element limit per view, and an index
    that links every view; diagrams built from a cloud vendor's official icon
    set are out of scope), and
    `build-dads-slides` (16:9 slide decks delivered as one HTML file on the
    Digital Agency Design System's official HTML and CSS assets, built as a
    tree — premises, then the answer, then one slide per supporting point —
    with a tracker on every main slide showing where it sits, a
    機密性/公開範囲 classification marking at the top right of every slide,
    and checked by its own bundled linter and preview images)
  - Domain overlays, which compose with a matching worker rather than replace
    it: `apply-dads-frontend` (accessible React/Tailwind public-service
    frontends and web dashboards on DADS, from a bundled verbatim copy of the
    official documentation, with the sources checked, the deviations, and the
    accessibility evidence reported), `apply-secure-logging` (implement and
    review application and CI logging against a bundled checklist of OWASP
    Logging Cheat Sheet, ASVS V16, and CWE items and of the logging practices
    that the official documentation of each stack describes; every item gets
    one status — pass, fail, N/A, or unverified — with evidence, and an item
    about storage, transport, retention, or alerting is never passed from
    application code), and `apply-scrum-guide` (diagnose and improve Scrum
    events, artifacts, accountabilities, and deviations against the 2020 Scrum
    Guide alone; read-only, with the Guide's Japanese and US PDFs bundled;
    the skill's text is Japanese), and `manage-scrum-artifacts` (keep each
    product's Scrum artifacts as files in its repository: place the Product
    Backlog, the Definition of Done, and per-Sprint records under the product
    folder's `scrum/` from nine bundled Scrum Guide templates, add one Sprint
    folder at a time, and check the shape with a bundled read-only script
    that also warns about a Product Goal, Sprint Goal, or Definition of Done
    not yet written; it never overwrites a file and never fills in a value
    the Scrum Team decides)
  - No skill names another, except that a parent skill — one that applies
    several skills in a set order — may name, by name and never by path, the
    child skills it declares in a `## Child skills` section of its `SKILL.md`;
    a child declares no children of its own
    ([spec 058](specs/058-parent-skill-references/spec.md)). A skill may also
    name, by name, a subagent defined in `harness/agents/`: the review
    procedures of `specify-requirements` and `verify-change` start
    `read-only-reviewer` and stop when it is missing
  - The 17 skills of the earlier layout were discarded and rebuilt as 16,
    under new names; the old-to-new mapping is in
    [`docs/harness-zero-base.md`](docs/harness-zero-base.md).
    `manage-scrum-artifacts` was added after that rebuild
    ([ADR-0023](docs/adr/0023-keep-scrum-artifacts-in-the-product-repository.md)). The Apple Notes
    and Apple Reminders integrations were removed with no replacement, and the
    skill-level README files, evaluation suites, and plugin manifests that some
    earlier skills carried were not carried over. The vendored `minto-pyramid`
    plugin (replaced by `pyramid-structure`, now `structure-document`), the
    former Minto suite (`minto-builder`, `minto-reviewer`, `minto-rewriter`),
    the `adr` skill (its rules merged into `maintaining-living-documentation`,
    now `sync-docs`) and `meta-spec` (no longer needed;
    [spec 058](specs/058-parent-skill-references/spec.md)) were retired
    earlier to [`archive/`](archive/), which is not synced
  - Spec Kit's `speckit-*` skills are not vendored here — they're per-project
    artifacts generated by `specify init` under whichever agent directory
    `--integration` targets (`.claude/skills/`, `.agents/skills/`,
    `.cursor/skills/`), all gitignored (see
    [Opt-in to spec-kit](#opt-in-to-spec-kit))
- **`install.sh`** — Copies `harness/` to `~/.claude/` and installs/enables
  this repository's Claude Code plugins (see [Plugins](#plugins)). It installs
  no MCP servers — register the two allowed ones yourself (see
  [MCP Servers](#mcp-servers))
- **`team/package-safety/`** — A package-install safety bundle to hand to
  other developers: one Claude Code settings file that works as a
  repository's `.claude/settings.json` or as a managed-settings drop-in, plus
  npm, pnpm, and uv templates that keep installs to versions published at
  least 7 days ago. It is not synced by `install.sh` and does not change this
  repository's own settings; see its [README](team/package-safety/README.md)
  and [ADR-0017](docs/adr/0017-team-package-install-safety-bundle.md)
- **[`chatgpt-system-prompt.md`](chatgpt-system-prompt.md),
  [`claude-ai-system-prompt.md`](claude-ai-system-prompt.md)** — Paste-ready
  portable prompts that carry this configuration's working principles into
  the custom-instruction fields of ChatGPT and Claude.ai. The Claude.ai file
  also lists the skills under `harness/skills/` that can be uploaded to
  Claude.ai unchanged, and how to package them. They are not synced by
  `install.sh`

## Supplementary documentation

`docs/` is written for the maintainer, not for Claude. It is **not** synced to
`~/.claude/` by `install.sh`, so nothing in `harness/` links into it — the rules
and skills carry their own sources inline instead.

| Document | Covers |
|---|---|
| [`docs/claude-config-design.md`](docs/claude-config-design.md) | The test each always-on instruction must pass, what each file deliberately omits, and the reference lists the rules cite |
| [`docs/harness-zero-base.md`](docs/harness-zero-base.md) | The redesign of the harness: why the source moved to `harness/` and the 17 skills were rebuilt as 16, the old-to-new skill mapping, the sandbox contract every skill meets, and the open work |
| [`docs/mcp-servers.md`](docs/mcp-servers.md) | Why MCP servers are user-installed, what `.mcp.json` can and cannot carry, each server's vendor reference, which servers `settings.json` stops, and what to update when a server is added |
| [`docs/harness-eval.md`](docs/harness-eval.md) | The whole-harness behavior baseline: how to check the capability map and scenario suite, run the suite with `claude plugin eval` against two commits under a cost ceiling, and compare the results, and where the eval differs from a real session |
| [`docs/harness/capability-map.md`](docs/harness/capability-map.md) | Which component owns each stage of the work, which stages have no owner, which skills exclude one another, and which scenarios cover each stage (generated from `capability-map.json`) |
| [`docs/adr/`](docs/adr/) | Architecture decision records — immutable once Accepted, only superseded |

## Install as user configuration

Run the bundled installer from the cloned repo. It synchronizes the declared
managed paths from `harness/` to `~/.claude/` and installs/enables this
repository's Claude Code plugins (see [Plugins](#plugins)):

```sh
bash path/to/my-claude-code/install.sh
```

Requires the `claude` CLI and `jq`.

The installer does not register, update, or remove MCP servers, and does not
install plugins that bundle one. Register the two allowed servers yourself (see
[MCP Servers](#mcp-servers)); servers already registered at user scope, for
example by an earlier version of this installer, are left as they are, but
`settings.json` lets only the two allowed ones load.

Re-running is safe: it re-syncs managed paths and re-checks the plugins.

**Important (overwrite/replace behavior):**

- Installer-managed paths are synchronized by replacement: `rules/`,
  `skills/`, `agents/`, `commands/`, `CLAUDE.md`, and `install.sh`.
- One exception inside `skills/`: `~/.claude/skills/synced/`, where the Claude
  app syncs its own skills, is moved aside while `skills/` is replaced and put
  back unchanged. If a run stops in between, it is left in
  `~/.claude/.install-keep.*/synced`.
- `settings.json` is synchronized by **merge**, not replacement: for any key
  this repo declares (`model`, `permissions`, `hooks`, ...), the repository's
  value wins — recursing into shared objects, so e.g. `permissions.deny`
  stays enforced even if a sibling key under `permissions` is your own. A
  top-level key the repo does not declare — `env` (as written by
  `/setup-bedrock`, say), `agentPushNotifEnabled`, or anything else you or
  the CLI added — is left untouched. Under `enabledPlugins` the repo declares
  only `github@claude-plugins-official: false`; your other entries stay. An
  array the repo declares (`permissions.deny`, the `sandbox` path lists,
  `hooks.SessionStart`, `deniedMcpServers`) replaces yours rather than being
  combined with it, so put your own additions to those in project or local
  settings, which Claude Code combines with the user scope.
- Files removed from this repository are also removed from `~/.claude` under
  the replaced managed paths.
- `agents/` holds the four subagent definitions (`read-only-reviewer`,
  `check-runner`, `file-searcher`, and `task-worker`). Like the other managed
  paths it replaces `~/.claude/agents/`, so an agent file of your own there is
  removed; keep your own agents in a project's `.claude/agents/`.
- `commands/` has no source in this repository; it stays managed only to
  clean up what earlier versions installed. Every run therefore deletes
  `~/.claude/commands/`.
- Unrelated paths in `~/.claude`, including `settings.local.json`, are
  preserved. Keep personal-only files outside the managed paths above.

### Alternative: import via your own `CLAUDE.md`

If you prefer not to copy, import from any `CLAUDE.md`:

```markdown
@/absolute/path/to/my-claude-code/harness/CLAUDE.md
```

## File structure

```
my-claude-code/
├── CLAUDE.md                       # Repo purpose and how to work here (in-repo only, not synced)
├── README.md                       # This guide (README.ja.md: Japanese)
├── install.sh                      # Sync managed Claude paths from harness/ + install plugins (no MCP servers)
├── .mcp.json                       # Project-scope definitions of the two allowed MCP servers
├── .living-documentation.json      # Settings for the sync-docs scripts (excludes specs/)
├── chatgpt-system-prompt.md        # Portable prompt for ChatGPT custom instructions (not synced)
├── claude-ai-system-prompt.md      # Portable prompt for Claude.ai instructions (not synced)
├── docs/                           # Maintainer documentation: design rationale, the harness redesign, MCP background, ADRs (not synced)
├── tests/                          # Offline contract suites (run-*.sh), assert_*.py helpers + fixtures; see Verification
├── specs/                          # Spec Kit feature specifications for this repository's own changes
├── .specify/                       # Spec Kit project files, local to each checkout (gitignored; ADR-0022)
├── archive/                        # Retired skills kept for reference (not synced)
├── team/package-safety/            # Team bundle: Claude settings + npm/pnpm/uv templates (not synced; ADR-0017)
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                  # Runs the tests/run-*.sh suites it lists on every push/PR to main (required check)
│   │   └── dependabot-automerge.yml # Auto-merges patch/minor Dependabot security-fix PRs once CI is green
│   └── rulesets/main-required-checks.json # Source of truth for main's required-status-check ruleset
└── harness/                        # Source for installer-managed Claude paths (installed to ~/.claude/)
    ├── CLAUDE.md                   # Governing proposition: define → execute → hand off; rationale → docs/
    ├── settings.json               # User-level settings: deny list, sandbox, SessionStart hooks, MCP allowlist and stops
    ├── rules/                      # Always-on: loaded every session, 4 independent concerns
    │   ├── clarifier.md            # Requirements certainty: when to ask vs proceed
    │   ├── thinking-lenses.md      # Reasoning completeness: four self-checks applied every task
    │   ├── permissions.md          # Authorization and safety; enforced deny → settings.json
    │   └── pyramid-principle.md    # Reader-facing structure: pyramid, paper-part order, premises and terms
    ├── agents/                     # Subagent definitions: model, effort, and tools fixed per kind of delegated work
    │   ├── read-only-reviewer.md   # Challenger and assurance review: Read/Grep/Glob only, starts without CLAUDE.md
    │   ├── check-runner.md         # Long-output checks: reports each command, exit code, and failure verbatim
    │   ├── file-searcher.md        # Read-only search: returns path:line locations
    │   └── task-worker.md          # One self-contained task that needs judgment, run in parallel with others
    └── skills/                     # On-demand: body loaded when relevant, self-describing; 17 skills
        ├── clarify-intent/         # Shared understanding of intent (worker)
        │   ├── SKILL.md            #   playbook
        │   └── references/         #   framework inventory (named to the user) + design basis (not named)
        ├── define-problem/         # Problem = gap between current and ideal state (worker)
        │   ├── SKILL.md            #   playbook
        │   └── references/         #   framework sources
        ├── specify-requirements/   # Problem card -> requirements graph -> challenger -> ready/blocked gate (worker)
        │   ├── SKILL.md            #   playbook
        │   ├── references/         #   checker formats and rules, criteria forms, challenge procedure and prompt
        │   ├── scripts/            #   check_graph.py (read-only, standard library only)
        │   ├── examples/           #   a complete set of records whose gate is ready
        │   └── tests/              #   acceptance tests and fixtures
        ├── implement-change/       # Change workflow, test-first (worker)
        │   ├── SKILL.md            #   playbook
        │   └── references/         #   spec first, type safety, system boundaries (each loaded when it applies)
        ├── verify-change/          # Evidence per acceptance criterion -> pass/fail/blocked gate + review card (worker)
        │   ├── SKILL.md            #   playbook
        │   ├── references/         #   manifest format and rules, assurance review procedure and prompts, pilot
        │   ├── scripts/            #   assure.py (read-only, standard library only), review_prep.py (git read-only), pilot.py
        │   ├── examples/           #   a complete set of records whose gate passes
        │   └── tests/              #   acceptance tests and fixtures
        ├── deliver-change/SKILL.md # Parent skill: define-problem -> specify-requirements -> implement-change -> verify-change (orchestrator)
        ├── define-product-strategy/ # Vision/users/value-prop/metrics before development begins (worker)
        │   ├── SKILL.md            #   playbook
        │   └── references/         #   framework per section
        ├── structure-document/     # Claim tree for a document + bundled structure checker (worker)
        │   ├── SKILL.md            #   playbook
        │   ├── references/         #   templates, genres, claim-tree schema, read without context
        │   ├── scripts/            #   check.py (read-only, standard library only)
        │   └── tests/              #   unit tests
        ├── sync-docs/              # Docs kept consistent with changes (worker)
        │   ├── SKILL.md            #   playbook
        │   ├── references/         #   practices, standards and their precedence, normative basis, bibliography
        │   ├── scripts/            #   inspect_project.py, audit.py, find_related.py, check_links.py, check_tree.py (standard library only)
        │   ├── schemas/            #   config.schema.json for .living-documentation.json
        │   ├── templates/          #   ADR, architecture description, provenance, README per tree node kind, CI workflow
        │   └── tests/              #   unit tests
        ├── manage-git/SKILL.md     # Branch/commit/push/PR conventions (worker; needs the remote host)
        ├── research-aws/SKILL.md   # Current AWS doc lookup (worker)
        ├── draw-system-diagrams/   # C4 views for first-time readers in Mermaid, draw.io, or Structurizr DSL (worker)
        │   ├── SKILL.md            #   playbook
        │   ├── references/         #   view types, notation, one file per format
        │   ├── assets/templates/   #   view page, index, draw.io file, Structurizr workspace
        │   ├── examples/           #   a complete example set that passes the checker
        │   ├── scripts/            #   check_diagrams.py (read-only, standard library only)
        │   └── tests/              #   unit tests
        ├── build-dads-slides/      # DADS 16:9 HTML decks built as premise -> answer -> points (worker; needs network for assets)
        │   ├── SKILL.md            #   playbook
        │   ├── references/         #   slide design, markup contract, checks, sourcing
        │   ├── assets/             #   1280x720 layout CSS + annotated deck template
        │   └── scripts/            #   setup, official-asset fetch, in-browser checker, deck CLI
        ├── apply-dads-frontend/    # DADS React/Tailwind workflow + source-backed references (overlay; needs network for package checks)
        │   ├── SKILL.md            #   playbook
        │   └── references/         #   sourcing, component implementation, accessibility gate, dashboards, verbatim dads-docs/ archive
        ├── apply-secure-logging/   # OWASP + stack-practice logging checklist (overlay)
        │   ├── SKILL.md            #   playbook
        │   └── references/         #   source-backed checklist (ASVS V16, CWE, OWASP, official stack docs)
        ├── apply-scrum-guide/      # Scrum Guide (2020)-only diagnosis of events, artifacts, accountabilities (overlay)
        │   ├── SKILL.md            #   playbook
        │   └── references/         #   3 on-demand reference documents + the Scrum Guide PDFs
        └── manage-scrum-artifacts/ # Scrum artifacts kept as files under each product's scrum/ (worker)
            ├── SKILL.md            #   playbook
            ├── references/         #   layout conventions and check rules, event preparation
            ├── scripts/            #   scaffold.py (places new files only), check_artifacts.py (read-only)
            ├── templates/          #   9 Scrum Guide templates copied into a repository
            └── tests/              #   unit tests of the scripts and of the procedure text
                └── templates/      #   8 ready-to-use Markdown templates (artifacts + events)
```

## Verification

After changing `.mcp.json`, `install.sh`, `harness/settings.json`, or
[`harness/skills/research-aws/SKILL.md`](harness/skills/research-aws/SKILL.md):

```sh
bash tests/run-mcp-startup.sh # requires network access and a writable uv cache
bash tests/run-install.sh
bash tests/run-removed-guardrails.sh
bash tests/run-sandbox-settings.sh
```

After changing anything under `harness/skills/` or `harness/agents/`, or after
adding, removing, or renaming a skill or a subagent, or editing either README:

```sh
bash tests/run-harness-skills.sh
bash tests/run-readme-skill-index.sh
```

The first checks the skills offline and inside the Bash sandbox (no network, no
write outside the repository, temporary files only under `$TMPDIR`). It first
runs [`tests/test_skill_contract.py`](tests/test_skill_contract.py), which
shows that each rule of the contract can fail: every test builds a small valid
skill tree in a temporary directory, breaks one thing, and expects the check to
report the rule that covers it. It then runs
[`tests/assert_skill_contract.py`](tests/assert_skill_contract.py), which holds
every skill to rules C-01 to C-11 (listed in its docstring): the name matches
the directory; the `description` is one line of at most 1,024 characters and
states what the skill is not for; only the allowed frontmatter keys appear and
none switches the model; `metadata` carries a defined `kind`, `permission`, and
`sandbox`, and a skill that needs the network names its hosts; the body stays
within its size limits; a `Done when` section exists, and a `Bundled files`
section gives every bundled reference its load condition; no command breaks the
sandbox (a bare `mktemp`, a `/tmp` literal, a write outside the repository,
`osascript` or a network command in a skill that does not declare it); no skill
names another unless it is an orchestrator naming a declared child; no path
depends on the install location and none points into this repository's
`specs/` or `archive/`; package-relative links resolve; and an orchestrator
declares at least two existing children, none of them an orchestrator, while no
other kind declares any. It then runs the unit tests of the checker scripts
bundled in `specify-requirements`, `verify-change`, `draw-system-diagrams`,
`structure-document`, `sync-docs`, and `manage-scrum-artifacts`. To run one skill's unit tests alone:

```sh
python3 -B -m unittest discover -s harness/skills/sync-docs/tests -t harness/skills/sync-docs/tests -v
```

The second fails when a skill directory under `harness/skills/` or a subagent
definition under `harness/agents/` is not named in both `README.md` and
`README.ja.md`, as `` `<name>` `` or as a `<name>/` path.

After changing [`team/package-safety/`](team/package-safety/):

```sh
bash tests/run-package-safety-bundle.sh
```

It checks the bundle's files against each other without network access. How
the bundle behaves inside Claude Code is checked by hand with the procedure
in its [README](team/package-safety/README.md#check-that-it-is-in-force).

After changing [`harness/CLAUDE.md`](harness/CLAUDE.md) or
[`harness/rules/`](harness/rules/):

```sh
bash tests/run-config-pyramid.sh
```

It checks the always-loaded layers offline: the apex's three branches and its
delegation under three conditions, exactly four rule files that name no other
rule, skill, or config path and carry no reference list, the phrases each skill
description must keep so that requests route the same way, and that the apex
and the rules together stay under a size budget.

After changing [`harness/skills/specify-requirements/`](harness/skills/specify-requirements/):

```sh
bash tests/run-specify-requirements-skill.sh
bash tests/run-harness-skills.sh
```

The first runs the bundled checker's acceptance tests (Python standard library
only), checks that its example declarations pass, reads this repository's
`harness/skills/` in compatibility mode, and checks that the example problem
card, requirements graph, and challenge report pass the gate.

After changing [`harness/skills/verify-change/`](harness/skills/verify-change/):

```sh
bash tests/run-verify-change-skill.sh
bash tests/run-harness-skills.sh
```

The first runs the bundled checker's acceptance tests, checks that the example
manifest passes its own rules, that the example graph and manifest pass the
gate, and that the example review card renders; that the gate passes no
requirements graph from `specify-requirements`'s test fixtures that its checker
rejects under a rule the gate depends on
(`tests/assert_assurance_parity.py`); and carries one made-up change from
decomposition to acceptance (`tests/assert_delivery_flow.py`: a requirement a
person directed, Jest results, the decision before deploy, and both decisions
on the card) and through two assurance review rounds with `review_prep.py` in a
temporary Git repository (`tests/assert_review_prep_flow.py`). It also checks
that the `read-only-reviewer` definition allows only Read, Grep, and Glob and
that both review procedures name it (`tests/assert_reviewer_agent.py`).

After changing [`harness/skills/draw-system-diagrams/`](harness/skills/draw-system-diagrams/):

```sh
bash tests/run-draw-system-diagrams-skill.sh
bash tests/run-harness-skills.sh
```

The first runs the bundled checker's acceptance tests (Python standard library
only), checks that the bundled example set and templates pass the checker,
and checks that a page with an unlabelled line and no legend fails it.
Whether the Mermaid in a set renders is not checked; render it on GitHub or
with `mmdc`.

After changing [`harness/skills/apply-secure-logging/`](harness/skills/apply-secure-logging/):

```sh
bash tests/run-apply-secure-logging-skill.sh
bash tests/run-harness-skills.sh
```

The first checks the skill's structure and the sourcing rules of its
checklist. How the skill behaves is checked by hand with the fixture in
`tests/fixtures/secure-logging/`.

After changing [`harness/skills/apply-dads-frontend/`](harness/skills/apply-dads-frontend/):

```sh
bash tests/run-apply-dads-frontend-skill.sh
bash tests/run-harness-skills.sh
```

The first checks the skill's contract: its sourcing and licensing reference,
its component implementation, accessibility, and dashboard references, and
the bundled verbatim archive of the official documentation.

After changing [`harness/skills/build-dads-slides/`](harness/skills/build-dads-slides/):

```sh
bash tests/run-build-dads-slides-skill.sh
bash tests/run-harness-skills.sh
```

It runs the deck linter against self-contained fixtures in
`tests/fixtures/slides/`, then ends with an end-to-end section that fetches
the official DADS stylesheets and lints and previews the bundled deck
template. Both need a Python environment carrying `playwright` — point
`DECK_PYTHON` at one, or they report themselves as skipped rather than
failing — and the end-to-end section also needs network access.

After changing anything under `harness/` (the apex, a rule, a subagent, or a
skill), or the capability map or scenario suite of the whole-harness behavior
baseline:

```sh
bash tests/run-harness-eval.sh
```

It checks, without calling a model, that every rule and skill appears in
[`docs/harness/capability-map.json`](docs/harness/capability-map.json), that
every quoted phrase still exists in the file it cites, and that each stage of
the work has a scenario in
[`tests/harness-eval/scenarios.json`](tests/harness-eval/scenarios.json).
Running the scenarios themselves is a billed model call and needs a cost
ceiling (`harness_eval.py run --max-cost-usd N`); see
[`docs/harness-eval.md`](docs/harness-eval.md).

`run-removed-guardrails.sh` is a standing regression guard, not tied to any
particular change — it fails if a hooks directory (`harness/hooks/` or
`.claude/hooks/`) or `scripts/` is ever reintroduced
([ADR-0005](docs/adr/0005-remove-claude-hooks.md),
[ADR-0007](docs/adr/0007-remove-scripts.md)), and if this repository's own
`.claude/` ever holds managed configuration again (`CLAUDE.md`, `rules`,
`skills`, `agents`, `settings.json`, or `commands`: a copy there would load a
second time as project configuration). It also constrains the `permissions`
block that
[ADR-0014](docs/adr/0014-restore-credential-deny-rules.md) restored on top of
[ADR-0006](docs/adr/0006-remove-permissions-config.md): only a `deny` list is
allowed — an `allow` or `ask` tier fails — and every `deny` entry must be a
`Read` rule anchored with `~/` or `**/`, never a single leading slash, which
would resolve to a different path once `install.sh` copies the file to user
scope.

`run-sandbox-settings.sh` checks the `sandbox`, `SessionStart`, and MCP keys
of `harness/settings.json` against [spec 067](specs/067-sandbox-by-default/spec.md):
that nothing under `~/.aws` is re-opened and the GPG secrets and other
credential files stay closed, that the opened paths, sockets, hosts, and
excluded commands are exactly the reviewed ones, that only the two AWS
documentation servers are allowed and `.mcp.json` defines only those, and
that the stopped MCP servers stay stopped. It also runs each `SessionStart`
hook under `sh`, `bash`, and `zsh` with a scratch home and stub commands.
Whether Claude Code honours these keys is checked by hand in a new session
after `install.sh`.

`run-install.sh` uses an isolated home and stubbed external commands. All suites
except `run-mcp-startup.sh` are local checks; the startup suite exercises the
configured MCP server commands and therefore requires network access.

## Repository security automation

Some of the suites above also run automatically in CI
(`.github/workflows/ci.yml`) on every push and pull request to `main`; that
file is the list of which ones. The others run only when you run them. `main` is
protected by a repository ruleset
(`.github/rulesets/main-required-checks.json`) requiring that CI job (`test`)
to pass before anything merges.

On top of that, GitHub's own vulnerability detection is wired to respond, not
just alert:

- **Dependabot**: security-fix pull requests for patch/minor version bumps
  auto-merge once CI is green (`.github/workflows/dependabot-automerge.yml`).
  Major-version bumps, and anything not authored by `dependabot[bot]`, are
  never auto-merged — they wait for manual review. There is no
  `.github/dependabot.yml`: security updates work from the dependency graph
  without one, and adding an `updates:` entry would force a scheduled,
  non-security update stream this design deliberately avoids (see
  [ADR-0012](docs/adr/0012-dependabot-automerge-scope.md)).
- **CodeQL**: default setup scans this repo's Python code. Findings are
  surfaced as code-scanning alerts for manual triage — nothing is auto-fixed
  or auto-merged.
- **Secret scanning + push protection**: enabled repo-wide. New pushes
  containing a recognized secret pattern are rejected before they reach any
  branch, for the subset of secret types GitHub supports for push protection
  specifically (detection-only for the rest — see GitHub's
  [supported secret scanning patterns](https://docs.github.com/en/code-security/secret-scanning/introduction/supported-secret-scanning-patterns)
  for which is which). **Known gap**: live testing (`specs/032-github-security-automation/tasks.md`
  T013) found that AWS-shaped access-key/secret-key pairs — a type GitHub's
  own docs list as push-protection- and detection-supported — triggered
  neither on this repo across four correctly-formatted attempts. Root cause
  unconfirmed; don't treat this repo's secret scanning as a verified safety
  net for AWS-shaped credentials specifically until that's resolved.

## Sandbox and session hooks

`settings.json` turns on Claude Code's OS sandbox, which confines every Bash
command Claude runs to the files and hosts it allows (Seatbelt on macOS). The
strictness is the standard one: a command that cannot run inside may be
retried outside after the usual permission check (the auto-mode classifier,
or a prompt), and a host outside the allowlist is decided by the permission
mode. Claude's file tools, MCP servers, and hooks run outside the sandbox.
The decision is [ADR-0020](docs/adr/0020-enable-sandbox-by-default.md); the
requirements are [spec 067](specs/067-sandbox-by-default/spec.md).

The skills and tests of this repository are written to run inside it. The
skill contract (rule C-07 of `tests/assert_skill_contract.py`; see
[Verification](#verification)) rejects a bare `mktemp`, a `/tmp` literal, and a
write outside the repository, and a skill that needs the network declares its
hosts in `metadata`.

How the everyday work it was built for runs:

| Work | Where it runs | What is opened | What stays closed |
|---|---|---|---|
| Signed `git commit` (GnuPG) | Inside | Writes to `~/.gnupg`; the `S.gpg-agent` and `S.keyboxd` sockets | Reading the private keys (`private-keys-v1.d`, `secring.gpg`) and revocation certificates; writing them, the keyrings, `trustdb.gpg`, every gpg, gpgsm, and gpg-agent configuration file, and the `scd-event` script scdaemon runs |
| `aws … --profile X` | Outside, after the permission check (`excludedCommands: ["aws *"]`) | Nothing inside the sandbox | All of `~/.aws` for every sandboxed command; Claude's Read tool cannot read it either |
| Chromium, Playwright | Inside, launched with `--single-process` | Nothing extra | — |
| Installing Noto Sans from Google Fonts | Inside | Writes to `~/Library/Fonts`; `fonts.googleapis.com` and `fonts.gstatic.com` without asking | Any other host is decided by the permission mode |

Every sandboxed command is also kept from reading `~/.git-credentials`,
`~/.netrc`, `~/.config/gh/hosts.yml`, `~/.docker/config.json`, and
`~/.kube/config`, on top of the file tools' deny list. An `aws` command leaves
the sandbox only when the whole Bash call is that one command; one joined
with a pipe, `&&`, `;`, or `$(...)` stays inside and cannot read `~/.aws`.

Three `SessionStart` hooks, each a short command written into
`settings.json`, run outside the sandbox when a session starts:

- **Bedrock variables out of Bash.** When Claude Code reaches Claude through
  Amazon Bedrock (`CLAUDE_CODE_USE_BEDROCK`), Bash commands do not inherit
  `AWS_PROFILE`, `AWS_DEFAULT_PROFILE`, `AWS_REGION`, `AWS_DEFAULT_REGION`,
  `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`, or
  `AWS_BEARER_TOKEN_BEDROCK`, so an `aws` command that forgets `--profile`
  does not act as the Bedrock account.
- **gpg-agent.** When `gpgconf` and `~/.gnupg` exist, the hook starts
  gpg-agent outside the sandbox, so a signing `git commit` inside it reaches
  an agent that can read the keys and show a passphrase prompt.
- **Notes for Claude.** When the Bash tool runs zsh (`CLAUDE_CODE_SHELL`, or
  else `SHELL`), Claude is told so, with the three zsh pitfalls that broke
  its commands most often: unmatched globs, words starting with `=`, and
  unquoted variables that zsh does not split. On macOS it is told that
  Chromium needs `--single-process` inside the sandbox. When the `aws` CLI is
  installed, it is told to run `aws` as one command and to name the profile
  with `--profile`.

Risks accepted with this design, and known limits, measured on macOS with
Claude Code 2.1.319:

- While gpg-agent remembers your passphrase, any sandboxed command can sign
  data with your key through its socket; with a key that has no passphrase,
  it could also export it. Running `git commit` outside the sandbox instead
  would run the repository's git hooks outside too.
- `env` in `settings.json` reaches hooks and stdio MCP servers as well as
  Bash. A stdio MCP server that calls AWS would therefore act as the Bedrock
  account in a Bedrock session; the `deploy-on-aws` plugin, whose servers
  call AWS, is turned off, and the two allowed servers search public
  documentation. Giving Bedrock its credentials with
  `awsCredentialExport` (for example
  `aws configure export-credentials --profile <bedrock> --format process`)
  instead of `env.AWS_PROFILE` keeps the profile away from every subprocess.
- Project and local settings can loosen the sandbox this file sets; only
  managed settings can stop that.
- Chromium (and Playwright, Puppeteer) aborts at startup in the sandbox
  unless launched with `--single-process`. The slide checker of
  `build-dads-slides` adds the flag itself; anything else has to pass it.
  Through the sandbox's proxy, Chromium loaded plain HTTP but timed out on
  HTTPS.
- `mktemp` without a template ignores `$TMPDIR` on macOS and fails in the
  sandbox; scripts that call it, such as Spec Kit's `setup-plan.sh`, need to
  be retried outside.
- `/usr/bin/diff` cannot open the `/dev/fd` paths that `<(...)` creates
  inside the sandbox.
- The GnuPG openings assume `~/.gnupg`; with `GNUPGHOME` elsewhere, signing
  falls back to running outside. With keyboxd, importing public keys goes
  through the keyboxd socket and is not stopped.

## MCP Servers

Only two MCP servers may load, in any project: the two that search official
AWS documentation. `settings.json` allows them and nothing else, whoever
defines a server - you at user scope, a project's `.mcp.json`, a plugin, or
claude.ai. The reason is security: an MCP server runs outside the Bash
sandbox, several start the newest published version on every launch, and each
one adds outside text, and sometimes credentials or actions, to the same
session that can run commands.

| Allowed | Matched by | What it does |
|---|---|---|
| `aws-knowledge` | URL `https://knowledge-mcp.global.api.aws` | Searches and reads AWS documentation over HTTP, without credentials |
| `aws-documentation` | Command `uvx awslabs.aws-documentation-mcp-server@latest` | Searches and reads AWS documentation; started with `uvx`, which runs the newest version on every launch |

A remote server is matched by its URL and a local one by its exact command,
never by its name: a name is a label that anyone can choose. To use another
server you would have to change `allowedMcpServers` in `harness/settings.json`
and reinstall.

This repository still does not install MCP servers into your user
configuration. `install.sh` neither registers nor removes any, and nothing
under `harness/` assumes a particular server is present - `research-aws` uses
whatever documentation tools the session actually exposes. To register the
two at user scope (the second needs [uv](https://docs.astral.sh/uv/)):

```sh
claude mcp add -s user aws-knowledge --transport http https://knowledge-mcp.global.api.aws
claude mcp add -s user aws-documentation -- uvx awslabs.aws-documentation-mcp-server@latest
```

[`.mcp.json`](.mcp.json) defines the same two for work inside this repository.
Background - what `.mcp.json` can carry, each server's vendor reference, and
what was stopped and when - is in
[`docs/mcp-servers.md`](docs/mcp-servers.md).

A server you registered earlier and that is no longer allowed stays in your
configuration but does not load. Remove it yourself when you want it gone, for
example `claude mcp remove -s user wolfram`.

On top of the allowlist, `settings.json` denies these outright. A denial
cannot be overridden by any allowlist
([ADR-0021](docs/adr/0021-block-mcp-servers-by-settings.md)):

| Stopped | How | Why |
|---|---|---|
| The built-in Chrome integration (`claude-in-chrome`) | `deniedMcpServers` by name | A built-in server skips the allowlist. It drives your own browser, with your signed-in sessions, from the same session that reads outside text |
| GitHub's MCP server and the `github` plugin | `deniedMcpServers` by URL (`https://api.githubcopilot.com/*`); `enabledPlugins` `false` | Not used; the `gh` CLI covers the work |
| The `deploy-on-aws` and `microsoft-docs` plugins | `enabledPlugins` `false` | Their MCP servers are not on the allowlist, so the skills that depend on those servers could not do their work (see [Plugins](#plugins)) |
| `bedrock-agentcore` | `deniedMcpServers` by name and by command | Creates, changes, and deletes live AWS resources and runs code in AWS with whatever AWS credentials Claude Code holds |
| claude.ai connectors (Gmail, Google Calendar, Google Drive, Notion, Moneytree, Claude Docs, Wolfram) | `disableClaudeAiConnectors: true` | Private data and outside text in the same session as Bash is a path for prompt injection to carry data out |
| Plugins synced from claude.ai (`productivity`, `pdf-viewer`) | `syncClaudeAiPlugins: false` | Bring further SaaS MCP servers into every session |

## Plugins

`install.sh` installs three Claude Code plugins, all from Anthropic's official
`claude-plugins-official` marketplace (`anthropics/claude-plugins-official`):

| Plugin | Author | Purpose |
|---|---|---|
| `frontend-design` | Anthropic | UI/UX implementation guidance |
| `code-review` | Anthropic | Multi-agent PR review, incl. `/code-review ultra` |
| `skill-creator` | Anthropic | Scaffold, update, and evaluate skills |

It adds the marketplace if missing, then installs and enables each plugin at
user scope so it works across all your projects, not only this one.
Equivalent commands:

```sh
claude plugin marketplace add anthropics/claude-plugins-official
claude plugin install frontend-design@claude-plugins-official
claude plugin install code-review@claude-plugins-official
claude plugin install skill-creator@claude-plugins-official
```

Three plugins of the same marketplace bundle an MCP server, and
`settings.json` turns all three off. The installer never installs them, and
it does not remove an install you made yourself; a plugin that is turned off
loads none of its skills and none of its servers.

| Plugin | Author | Bundles | Why it is off |
|---|---|---|---|
| `github` | GitHub | GitHub's hosted MCP server | Not used; the `gh` CLI covers the work |
| `deploy-on-aws` | AWS | AWS architecture diagram and deploy skills, with AWS MCP servers for infrastructure code and pricing | Its servers are not on the allowlist (see [MCP Servers](#mcp-servers)), and its deploy skills depend on them |
| `microsoft-docs` | Microsoft | The Microsoft documentation MCP server, with skills that query it | Its server is not on the allowlist, and its skills do nothing without it |

To remove an install as well, run `claude plugin uninstall <name>@claude-plugins-official`.

## Overriding per project

User-level settings act as the baseline. Any project can extend or override in
its own `.claude/settings.json`:

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": ["Bash(npm run *)"],
    "deny": []
  }
}
```

Permission precedence (high → low):
managed > local (`.local.json`) > project (`settings.json`) > user (`~/.claude/settings.json`)

### Opt-in to spec-kit

Spec Kit (https://github.com/github/spec-kit) is installed and initialized
per project — nothing is vendored into this repo or `~/.claude`. Run this
sequence once per project:

```sh
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git@vX.Y.Z
specify self upgrade
specify init --here --force --integration claude
# specify init --here --force --integration cursor-agent
specify extension add git
```

- `uv tool install ... @vX.Y.Z` — pin an explicit released tag (replace
  `vX.Y.Z`) rather than tracking a branch, so the install is reproducible.
- `specify self upgrade` — updates the `specify` CLI itself to the latest
  release via its built-in updater.
- `specify init --here --force --integration <agent>` — generates
  `/speckit.*` slash commands as `speckit-*` skills under that project's own
  `.claude/skills/` (or the equivalent path for the chosen `--integration`,
  e.g. `.cursor/skills/` for `cursor-agent`)
  — a project-local artifact, gitignored regardless of which agent
  directory it lands in (see `.gitignore`). Re-run with a different
  `--integration` value to target another agent in the same project; each
  command carries its own playbook. `implement-change`'s guidance on writing
  the specification first (`references/spec-first.md`) applies regardless of
  whether spec-kit is installed.
- `specify extension add git` — installs the Git Branching Workflow
  extension (`/speckit-git.*`).

This adds 5 commands: `speckit.git.feature`, `speckit.git.validate`,
`speckit.git.remote`, `speckit.git.initialize`, and `speckit.git.commit`.

This repository follows the same rule for itself: `.specify/` is gitignored
and local to each checkout ([ADR-0022](docs/adr/0022-keep-spec-kit-project-files-local.md)).
Nothing of Spec Kit is pushed; each user runs the sequence above with the
latest release. The constitution (`.specify/memory/constitution.md`), the
hook wiring (`.specify/extensions.yml`), and the git extension's settings
are therefore each checkout's own, starting from spec-kit's defaults.

Keeping an already-adopted project's generated `speckit-*` skills current is
a manual step — run `specify init --here --force` periodically yourself. The
`specify-cli` tool itself is different: `harness/settings.json` carries a
narrow `PreToolUse` hook (docs/adr/0008) that, only before the
`speckit-specify` skill runs, checks the latest `github/spec-kit` release
tag against the `rev=` pinned in `uv`'s install receipt and reinstalls via
`uv tool install specify-cli --from git+... --force` on a mismatch — it
fails open on any network error, and no other `speckit-*` skill triggers it.
This is a deliberate, narrow exception to the broader "no `.claude/hooks/`,
no automatic enforcement" removal in docs/adr/0005 — see docs/adr/0008 for
why. Nothing in `harness/` recommends `specify init` to a project that has
not adopted Spec Kit: `implement-change` follows the Spec Kit lifecycle only
where a project already uses it.
