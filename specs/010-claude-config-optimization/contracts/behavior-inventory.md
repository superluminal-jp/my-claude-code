# Contract: Enforced Behavior Inventory

This is the **gate** for the optimization. Every behavior listed MUST still be present and firing after the config is trimmed (FR-012, SC-002, SC-004). Verify each item post-edit; any missing item fails the change.

## A. Permissions (`.claude/settings.json`)

**deny (Read):** `.env`, `.env.*`, `**/secrets/**`, `**/credentials/**`, `**/.aws/**`, `**/.ssh/**`, `**/*.pem`, `**/*.p12`, `**/*.pfx`
**ask (Bash):** `git add *`, `git commit *`, `git checkout *`, `git branch *`, `git stash *`, `git pull *`
**allow:** `git status`, `git diff *`, `git log *`, `git fetch *`; MCP servers `aws-knowledge`, `aws-documentation`, `bedrock-agentcore`, `strands-agents`, `google-developer-knowledge`, `microsoft-learn`
**flags:** `defaultMode=acceptEdits`, `model=claude-opus-4-8`, fallback chain, `effortLevel=high`, `alwaysThinkingEnabled=true`, `autoMemoryEnabled=true`, `enableAllProjectMcpServers=true`

## B. Hook guards (must still block/gate identically)

**pre-bash.sh (Bash):**
1. `git push -f/--force` → block (exit 2)
2. `git reset --hard` → block
3. `git clean -f` → block
4. `rm -rf` targeting `/`, `~`, `.`, `/*`, `$HOME` → permanent block
5. other `rm -rf` → ask (JSON permissionDecision)
6. `>/dev/sd*`, `mkfs`, `dd if=/dev/zero`, fork bomb → block
7. `curl|wget | bash/sh/zsh` → block
8. non-HTTPS `http://` except localhost/127.0.0.1 → block
9. credential-path reads (`cat/less/more/head/tail/od/hexdump` of `.ssh/.aws/.env/secrets/credentials/.pem/.p12/.pfx` or file arg matching `secret|credential|token|key`), heredoc excluded → block
10. credential-path writes (redirection/`tee`) → block
11. `sudo` → ask (JSON)

**pre-edit.sh (Edit|Write|Delete):**
12. edit of `.git/` → block
13. edit on `main`/`master` branch → block
14. warnings (non-blocking) for CI/CD, `.claude/settings*.json`, prod config

**user-prompt-submit.sh (UserPromptSubmit):**
15. AWS key `AKIA|ASIA…` → block
16. GitHub tokens `gh[porus]_…`, `github_pat_…` → block
17. Slack `xox[abpors]-…` → block
18. private key header → block
19. Google API key `AIza…` → block

**post-edit-format.sh (Edit|Write):** JSON validity check; `*.sh` → `shfmt -i 2` + `shellcheck`; `*.yml/yaml` → `yamllint` (non-fatal)

**session-start.sh (SessionStart, web only):** provision `jq`, `shellcheck`, `shfmt`, `yamllint`; never fatal

**speckit-expand-update.sh (UserPromptExpansion, `speckit.*`):** upgrade Spec Kit before `/speckit-*`

## C. Skill-routing triggers (`.claude/CLAUDE.md` + `skill-routing.md`)

- `coder` — code implementation/modification/refactor/test/debug
- `editor` — documents/slides/charts/translation/editing
- `clarifier` — any ambiguity (intent/scope/acceptance/constraint gaps; ≤32 chars residual; missing subject/object/verb)
- `ubiquitous-language` — business-event expressions / domain vocab candidates (passive queue)
- `domain-model` — DDD structural patterns / model create-update (passive queue)
- mixed code+doc → `coder` then `editor`; `/speckit-*` excluded
- preflight: clarification gate → minimum relevant skill → advisor baseline

## D. Skill obligations (must survive trimming)

- **coder**: TDD red→green→refactor (no impl without failing test); SDD spec = source of truth; docs-sync in same change; OWASP/boundary validation; no drive-by refactors
- **editor**: pyramid/MECE/SCQA/BLUF; action titles; Cleveland–McGill chart choice; Tufte data-ink; frameworks implicit in shipped copy
- **clarifier**: batch blocking gaps; defaults+alternatives; convert to Given/When/Then or SC-###; confidence-tag assumptions
- **advisor**: BLUF; facts vs inference; 2–4 options; one recommendation; risks+mitigations; next steps
- **live-documentation**: drift detection, separate-doc-PR detection, auto-gen recommendation, proximity, no-redundancy, override handling (reason required)
- **MCP usage rule**: AWS→aws-knowledge/aws-documentation, GCP→google-developer-knowledge, Azure→microsoft-learn before answering cloud questions

## E. CLAUDE.md core directives

- Priorities: Accuracy > Defensible practice > Human-centered
- Minimal change; verify before reporting; edit over create
- Response style: short; `file_path:line_number`; no trailing summaries; no emojis; name frameworks in reasoning only

## Verification method

Post-edit, for each item: confirm the rule/guard/trigger still exists (grep the artifact) and, for hooks, optionally exercise a representative input. Record pass/fail in `quickstart.md`. Zero failures required to satisfy SC-002 and SC-004.
