# Data Model: Remove .claude/hooks/ Entirely

No runtime data entities — this feature deletes files and rewrites documentation. The entities below are the artifacts affected and their dependency relationships.

## Entities

### `.claude/hooks/` (7 files)
- **Relationship**: Each file is wired from `.claude/settings.json`'s `hooks`/`statusLine` keys (the wiring must be removed no later than the files, to avoid `settings.json` pointing at nothing) and synced by `install.sh`'s `sync_path "hooks"` call (which handles an absent source gracefully — no ordering constraint there).

### `.claude/settings.json` `hooks` / `statusLine` keys
- **Relationship**: Depends on the 7 files existing to make sense; removed in the same change as them.

### `install.sh` hook-sync steps
- **Relationship**: `sync_path "hooks"` (kept, becomes the uninstall path per R1) and `chmod +x .../hooks/*.sh` (removed, would error on empty glob).

### `scripts/guardrails/` (4 files) — explicitly NOT an entity being removed
- **Relationship**: Was called exclusively by 4 of the 7 deleted wrapper files. After this change, has no automatic caller but remains directly invokable (tests, manual runs, `settings.json`'s unrelated `permissions.allow` entries for `Bash(scripts/guardrails/*.sh)`).

### README.md / README.ja.md "What Codex enforces" comparison table
- **Relationship**: Describes the 7 deleted files' effects relative to Codex's independent guardrails. Content inverts (see research.md R2) once the files are gone — this is a content dependency, not a structural one.

### AGENTS.md "unaffected" claim (line 90) and its section framing
- **Relationship**: Directly asserts `.claude/hooks/pre-edit.sh` still runs. Becomes false the moment that file is deleted.

### Four guardrail test suites (partial edit) + `run-speckit-update.sh` (full delete)
- **Relationship**: Each guardrail suite tests two independent subjects (a surviving `scripts/guardrails/*.sh` script and a deleted `.claude/hooks/*.sh` wrapper) — only the wrapper-testing assertions are removed. `run-speckit-update.sh` has only one subject (a deleted file), so the whole suite is removed.

## Removal ordering

Single atomic change (all edits land together in one commit, as with spec-024), so no cross-file ordering constraint applies at commit time. If done incrementally: settings.json wiring removal → hook file deletion → install.sh edits → README/AGENTS.md rewrites → test edits/deletion → grep verification, mirroring spec-024's pattern (docs and tests follow the deletion, verification comes last).
