# Tasks: CLAUDE.md Configuration Improvements

**Input**: Design documents from `specs/006-claude-md-mcp-effort-tui/`
**Prerequisites**: plan.md, spec.md, research.md

**Organization**: Three user stories mapped to three targeted file edits. No setup or foundational phase required — this is a pure configuration change with no project initialization.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to

---

## Phase 3: User Story 1 — MCP Enforcement for AWS/GCP (Priority: P1) 🎯 MVP

**Goal**: Strengthen the MCP usage rule so Claude must invoke the appropriate MCP server when a question directly concerns AWS, GCP, or Azure services.

**Independent Test**: Start a new session; ask "What Lambda runtimes does AWS support?" — confirm an `mcp__aws-*` tool call appears before the answer. Then ask "I'm on AWS but how do I write a Python list comprehension?" — confirm no MCP call is made.

- [x] T001 [P] [US1] Replace the "Usage rule" section in `.claude/rules/mcp.md` with a MUST rule: invoke the matching MCP server when a question directly concerns AWS/GCP/Azure; warn + fall back to training knowledge when MCP is unreachable; skip MCP for incidental mentions

**Checkpoint**: MCP rule now says MUST, includes trigger condition, fallback, and incidental-mention exception.

---

## Phase 4: User Story 2 — Default Effort Set to High (Priority: P2)

**Goal**: Raise the default effort level from `medium` to `high` in the project settings file so all sessions start with maximum reasoning depth.

**Independent Test**: Run `grep effortLevel .claude/settings.json` — confirm value is `"high"`. Open a new Claude Code session without flags; confirm effective effort is high.

- [x] T002 [P] [US2] Change `"effortLevel": "medium"` to `"effortLevel": "high"` in `.claude/settings.json`

**Checkpoint**: `effortLevel` is `"high"` in `.claude/settings.json`.

---

## Phase 5: User Story 3 — Default TUI Set to Fullscreen (Priority: P3)

**Goal**: Add `"tui": "fullscreen"` to `.claude/settings.json` so interactive sessions render in fullscreen mode by default.

**Independent Test**: Run `grep '"tui"' .claude/settings.json` — confirm value is `"fullscreen"`. Launch Claude Code interactively; confirm TUI is fullscreen.

- [x] T003 [US3] Add `"tui": "fullscreen"` after the `"effortLevel"` line in `.claude/settings.json` (depends on T002 — same file)

**Checkpoint**: `"tui": "fullscreen"` is present in `.claude/settings.json`.

---

## Phase N: Polish & Verification

**Purpose**: Distribute settings and verify no regressions.

- [x] T004 Run `~/.claude/install.sh` and confirm `~/.claude/settings.json` contains both `"effortLevel": "high"` and `"tui": "fullscreen"`
- [x] T005 Verify regression: ask a generic non-AWS/GCP question and confirm no MCP call is triggered
- [x] T006 [P] Verify override: confirm that explicitly passing `--effort medium` at CLI takes precedence over the `high` default

---

## Dependencies & Execution Order

### Phase Dependencies

- **US1 (Phase 3)**: No dependencies — can start immediately, independent file
- **US2 (Phase 4)**: No dependencies — can start immediately, independent of US1
- **US3 (Phase 5)**: Depends on US2 completion (same file — `.claude/settings.json`)
- **Polish (Phase N)**: Depends on US1, US2, US3 all complete

### User Story Dependencies

- **US1**: Independent — edits `.claude/rules/mcp.md` only
- **US2**: Independent — edits `.claude/settings.json`
- **US3**: Depends on US2 (same file, must not create a merge conflict)

### Parallel Opportunities

- T001 (US1) and T002 (US2) can run in parallel — different files
- T003 must follow T002 — same file

---

## Parallel Example: US1 + US2

```bash
# These two tasks can run simultaneously:
Task T001: Edit .claude/rules/mcp.md (US1)
Task T002: Edit .claude/settings.json effortLevel (US2)

# Then sequentially:
Task T003: Edit .claude/settings.json tui (US3, depends on T002)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete T001 — update `mcp.md`
2. Validate: ask AWS question in new session, confirm MCP call

### Incremental Delivery

1. T001 → validate MCP enforcement
2. T002 → validate effort default
3. T003 → validate TUI default
4. T004–T006 → run install.sh, check regressions

---

## Notes

- No source code changes — all tasks are text edits to config/rules files
- T001 and T002 are marked [P] because they touch different files
- T003 is NOT marked [P] because it edits the same file as T002
- After T004 (install.sh), `~/.claude/settings.json` becomes the active config
