# Claude Code Configuration

This directory contains modular configuration for Claude Code following best practices.

## Structure

```
.claude/
├── CLAUDE.md         # Project constitution (<5KB, core principles)
├── settings.json     # Hook configuration
├── rules/            # Standards (always applied)
│   ├── output-standards.md
│   ├── file-editing.md
│   ├── model-selection.md
│   └── documentation.md
├── skills/           # Auto-invoked capabilities
│   ├── file-editing-strategy/
│   └── documentation-management/
├── agents/           # Specialized subagents
│   └── doc-updater.md
└── commands/         # User-initiated shortcuts
    ├── update-readme.md
    └── update-changelog.md
```

## How It Works

### CLAUDE.md (Constitution)
- Loaded at every session start
- Keep under 5KB
- Core principles and pointers
- Quick reference only

### Rules (Always Applied)
- Standards enforced on all outputs
- Professional writing guidelines
- File editing strategy
- Model selection guidance

### Skills (Auto-Invoked)
- Activate based on task context
- YAML frontmatter for metadata
- Provide specialized guidance
- Load automatically when relevant

### Subagents (Specialized)
- Isolated context windows
- Specific tool permissions
- Delegate heavy/parallel work
- Return summaries to main agent

### Commands (User-Initiated)
- Explicit shortcuts (`/command`)
- Manual workflow triggers
- Project-specific automations

### Hooks (Lifecycle Events)
- Pre/Post tool use validation
- Automated quality checks
- Branch protection
- Next-step guidance
- Agent teams: TeammateIdle & TaskCompleted hooks; see CLAUDE.md § Agent Teams

## Usage

### For Developers

```bash
# Use commands
/update-readme
/update-changelog

# Let skills activate automatically
# (editing large files → file-editing-strategy activates)

# Delegate to subagents
# "Update all documentation" → doc-updater subagent runs
```

### For Claude Code

1. Loads CLAUDE.md at startup
2. Applies rules to all work
3. Activates skills when relevant
4. Delegates to subagents for specialized work
5. Runs hooks at lifecycle events

## Best Practices

**CLAUDE.md**:
- Keep minimal (<5KB)
- Link to detailed content
- Update quarterly

**Rules**:
- Always-applicable standards
- No task-specific content
- Reference materials

**Skills**:
- Task-triggered guidance
- Clear activation criteria
- Link to rules for details

**Subagents**:
- Isolated heavy work
- Specific tool access
- Clear responsibilities

**Commands**:
- Repeatable workflows
- Explicit user control
- Single-purpose actions

## Customization

Edit files to match your project:

1. **CLAUDE.md** - Add project-specific principles
2. **Rules** - Adjust standards for your domain
3. **Skills** - Add project patterns
4. **Subagents** - Create specialized agents
5. **Commands** - Add workflow shortcuts

---

**For comprehensive guidance**, see individual files and https://code.claude.com/docs
