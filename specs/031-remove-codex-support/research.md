# Research: Remove Codex CLI Support and All Codex References

## R1 — `AGENTS.md` deletion and its dangling-reference inventory

**Finding**: `AGENTS.md` (90 lines) is a flat, non-`@`-importing guidance file Codex CLI reads natively. It is referenced by path from four other files: `README.md` (bullet + tree row + prose links), `README.ja.md` (same, in Japanese), `tests/run-subagent-delegation.sh` (`AGENTS_MD` variable + one check), and `tests/run-digital-agency-frontend-skill.sh` (one check). No other file under `.claude/`, `docs/`, or the repository root references it (confirmed by `grep -rl "AGENTS.md" --exclude-dir=.git --exclude-dir=specs .`).

**Decision**: Delete `AGENTS.md` outright; update all four referencing files in the same change so no dangling path reference survives (FR-001, FR-002, FR-005, FR-006).

## R2 — `README.md` edit map (verified by direct read, all line numbers as of this research pass)

| Location | Current content | Action |
|---|---|---|
| Lines 13-17 | `` `install.sh` synchronizes ... It does not deploy\nCodex CLI configuration; see [Codex CLI support](#codex-cli-support) for the\nofficial import flow. `` | Rewrite to end the sentence after "preserving unrelated user files." — drop the Codex clause entirely. |
| Lines 44-46 | `AGENTS.md` bullet under "What this provides" | Delete the bullet. |
| Lines 48-192 | Entire `## Codex CLI support` section (heading through "...same tool-agnostic script pattern.") | Delete the whole block, including its trailing blank line, leaving exactly one blank line before `## Install as user configuration`. |
| Lines 208-211 | "Re-running is safe... This repository no longer ships any hooks to import into Codex — see [Codex CLI support](#codex-cli-support) for what Codex enforces on its own, independent of anything here." | Rewrite to end after "upserts MCP servers." — drop the Codex sentence. |
| Lines 222-225 (bullet in "Important" list) | "**Nothing under `~/.codex` or `~/.agents` is touched.** Codex configuration is yours to manage via `/import`; see [Codex CLI support](#codex-cli-support), including how to clean up files an earlier version of this repository left behind." | Delete the bullet entirely (the three preceding bullets in the same list stand on their own). |
| Line 241 | `` ├── AGENTS.md                       # Project-only Codex guidance for this repository `` | Delete the tree row. |
| Lines 277-278 | `` ./tests/run-codex-references.sh `` / `` ./tests/run-codex-drift.sh `` | Delete both lines from the Verification command block. |
| Line 369 | `` # specify init --here --force --integration codex `` | Delete the line (the `claude` and `cursor-agent` example lines stand on their own). |
| Line 381 | "e.g. `.agents/skills/` for `codex`, `.cursor/skills/` for `cursor-agent`" | Reword to drop the `codex` example, e.g. "e.g. `.cursor/skills/` for `cursor-agent`". |

**Decision**: Apply all ten edits in one pass over `README.md`. This is the complete set of "codex" occurrences confirmed by `grep -ni codex README.md` at the start of this feature — no other location exists.

## R3 — `README.ja.md` edit map (mirrors R2)

| Location (line numbers as of this research pass) | Current content | Action |
|---|---|---|
| Line 9 | Standalone paragraph: "**Codex CLI 向けの移植物はこのリポジトリでは配布しません。** ... [ADR-0004](docs/adr/0004-adopt-official-codex-import.md) を参照してください。" | Delete the entire paragraph (and the blank line that isolates it, so line 6's sync description flows directly into "英語版" link). |
| Lines 25-28 (bullet, within the `.claude/skills/` list) | "Spec Kit の `speckit-*` スキルは...`--integration` が指す各エージェントのディレクトリ（`.claude/skills/`、`.agents/skills/`、`.cursor/skills/`）配下に生成される..." | Keep the bullet (it does not name "codex" — only the generic `.agents/skills/` path), no edit needed here. |
| Line 40 | "**Codex 側には何も展開しません** — `~/.codex` と `~/.agents` はユーザーの所有物として一切触れません。" | Delete the sentence; keep the rest of the paragraph (install requirements) intact. |
| Lines 59-146 | Entire `## Codex CLI サポート` section (heading through "測定日を更新してください。") | Delete the whole block, leaving one blank line before `## 代替: \`CLAUDE.md\` から import`. |
| Line 163 | `` ├── AGENTS.md                        # Codex CLI がそのまま読む平坦な指針（@ import 不可） `` | Delete the tree row. |
| Lines 180-181 | `` ./tests/run-codex-references.sh `` / `` ./tests/run-codex-drift.sh `` | Delete both lines from the Verification command block. |
| Line 243 | `` # specify init --here --force --integration codex `` | Delete the line. |
| Lines 254-255 | "指定した `--integration` に対応するパス。例: `codex` なら `.agents/skills/`、`cursor-agent` なら `.cursor/skills/`）" | Reword to drop the `codex` example, keeping the `cursor-agent` example, e.g. "指定した `--integration` に対応するパス。例: `cursor-agent` なら `.cursor/skills/`）". |

**Decision**: Apply all eight edits in one pass over `README.ja.md`, confirmed against `grep -ni codex README.ja.md`'s full output — no other location exists. Note line 27's `.agents/skills/` mention is the *generic* example-path segment (shared with `claude`/`cursor-agent`), not a Codex-specific claim — left as-is, matching R2's decision to leave README.md's equivalent generic wording alone.

## R4 — `install.sh` header comment rewrite

Current (lines 1-10):
```bash
#!/usr/bin/env bash
# Synchronize the managed .claude/ configuration into the user's ~/.claude/,
# upsert the repository's MCP servers, and install its required Claude Code
# plugins. Re-running is idempotent.
#
# Claude Code only. This installer deploys NO Codex CLI configuration and never
# touches ~/.codex or ~/.agents — Codex configuration is produced by the
# developer with OpenAI's official /import flow. See README.md § "Codex CLI
# support" and docs/adr/0004-adopt-official-codex-import.md.
# Requires: claude CLI, uvx. Optional: GOOGLE_DEV_KNOWLEDGE_API_KEY.
```

**Finding**: Lines 6-9 exist to disclaim Codex deployment and point to a README section that this feature deletes (R2) and to an ADR that this feature supersedes (R9). Once both targets are gone/changed, the pointer is stale by definition.

**Decision**: Delete lines 6-8 (the Codex-specific disclaimer and citations) outright — the file's own behavior (it only touches `.claude/` and MCP registration) is self-evident from the rest of the header and does not need a negative disclaimer about a product this repository no longer discusses. New header:
```bash
#!/usr/bin/env bash
# Synchronize the managed .claude/ configuration into the user's ~/.claude/,
# upsert the repository's MCP servers, and install its required Claude Code
# plugins. Re-running is idempotent.
#
# Requires: claude CLI, uvx. Optional: GOOGLE_DEV_KNOWLEDGE_API_KEY.
```

**Alternatives considered**: Rewording the disclaimer to remain generic ("this installer does not deploy configuration for any agent other than Claude Code") — rejected as unrequested scope creep; the file's own action (`.claude/` → `~/.claude/` only) is already unambiguous without a negative-space disclaimer naming a specific competitor product.

## R5 — Delete `tests/run-codex-references.sh` and `tests/run-codex-drift.sh`

**Finding**: `tests/run-codex-references.sh` (`RULE-01`…`RULE-10`) verifies `AGENTS.md` has no dangling references and that generated Codex paths stay gitignored. `tests/run-codex-drift.sh` (`DRIFT-01`…`DRIFT-06`) re-derives the live upstream facts backing the README's Codex section. Both suites currently pass on `main` (confirmed: R12 baseline). Neither is invoked by any other script — `grep -rl "run-codex-references\|run-codex-drift" --exclude-dir=.git .` outside `specs/`, `docs/adr/`, and the two READMEs (all edited in R2/R3/R9) returns no other caller.

**Decision**: Delete both files outright (FR-004). Their subject — `AGENTS.md`'s sync state and the README's Codex section's factual currency — no longer exists once R1/R2/R3 land, so there is nothing left for either suite to verify.

## R6 — `tests/run-subagent-delegation.sh`: remove the R5 cross-agent-parity block

Current (lines 19, 131-141):
```bash
AGENTS_MD="$REPO_ROOT/AGENTS.md"
```
```bash
# --- R5: cross-agent parity -------------------------------------------------

# Feature 021 retired the deployment map (.codex/README.md) along with the rest
# of the hand-maintained Codex port. The cross-agent question it answered —
# "is the subagent-delegation rule ported to Codex?" — is now answered in the
# root AGENTS.md, which is what Codex actually reads. ADR-0004 records why the
# exclusion still stands: Codex custom agents set defaults rather than
# isolating context from the parent turn.
grep -Fq 'subagent' "$AGENTS_MD" 2>/dev/null && c=1 || c=0
check "root AGENTS.md addresses delegation for Codex" "$c"

```

**Finding**: This is the file's entire "R5" section — one comment block plus one check, with nothing else under that heading (confirmed by reading the full file: the next section, "Always-loaded size discipline," starts immediately after). `$AGENTS_MD` (line 19) is used nowhere else in the file. There is no other "cross-agent" target left to check once Codex support is dropped — this isn't a check that can be rewritten to test something else meaningful; its entire premise (a second agent reads a ported file) no longer applies to this repository.

**Decision**: Delete the `AGENTS_MD` variable declaration (line 19) and the entire R5 block (lines 131-141, comment + check + trailing blank line) outright, per FR-005. This mirrors R5's reasoning for the two whole-file deletions: a check with no remaining subject is removed, not rewritten to check something arbitrary.

**Pre-existing, out-of-scope finding**: This suite already fails on `main` before this edit — its `RULE="$REPO_ROOT/.claude/rules/subagent-delegation.md"` target does not exist (spec 030 removed the rule file but left this test's cleanup incomplete; confirmed via `ls .claude/rules/` and `git log` showing spec 030 already merged). This failure is unrelated to Codex and is explicitly out of scope for this feature (spec.md FR-008, SC-003) — fixing it would be drive-by scope creep onto a different, already-merged spec's incomplete work.

## R7 — `tests/run-digital-agency-frontend-skill.sh`: remove the SYNC-SKILL-06 check

Current (lines 96-109, `run_sync_contract` function):
```bash
run_sync_contract() {
  # Feature 021 removed this repository's Codex port: the `.agents/skills/`
  # symlinks, the installer's CUSTOM_SKILLS registration, `.codex/AGENTS.md`,
  # `.codex/README.md`, and the codex-sync suite are gone, so SYNC-SKILL-01…04,
  # 06, 07 and 10 no longer describe anything that exists. Codex now discovers
  # this skill through `/import`, which generates `.agents/skills/` locally
  # from `.claude/skills/` — the authored source below is what must stay true.
  check "SYNC-SKILL-02: authored skill exists at the source of truth" "$([ -e "$REPO_ROOT/.claude/skills/digital-agency-frontend/SKILL.md" ] && echo 1 || echo 0)"
  check_contains "SYNC-SKILL-05: Claude routing lists the skill" "$REPO_ROOT/.claude/CLAUDE.md" 'digital-agency-frontend'
  check_contains "SYNC-SKILL-05A: canonical Claude routing composes the skill" "$REPO_ROOT/.claude/rules/skill-routing.md" 'coder.*digital-agency-frontend|digital-agency-frontend.*coder'
  check_contains "SYNC-SKILL-06: Codex routing lists the skill" "$REPO_ROOT/AGENTS.md" 'digital-agency-frontend'
  check_contains "SYNC-SKILL-08: English README lists the skill" "$REPO_ROOT/README.md" 'digital-agency-frontend'
  check_contains "SYNC-SKILL-09: Japanese README lists the skill" "$REPO_ROOT/README.ja.md" 'digital-agency-frontend'
}
```

**Finding**: `SYNC-SKILL-06` is the only line in this function asserting against `AGENTS.md`/Codex. The function's own comment already explains that `SYNC-SKILL-01…04, 06, 07, 10` describe artifacts that no longer exist as of feature 021 — `06` was kept only because `AGENTS.md` itself still existed at the time. Once `AGENTS.md` is deleted (R1), `06` joins that already-acknowledged list of retired numbers.

**Decision**: Delete the `SYNC-SKILL-06` check line and extend the existing comment's retired-number list to include `06` explicitly moving from "kept" to "retired," per FR-006. The four remaining checks (`02`, `05`, `05A`, `08`, `09`) are unaffected and continue to verify real, current sync obligations.

## R8 — `tests/run-mcp-startup.sh`: reword one comment

Current (lines 4-6):
```bash
# Closing stdin lets a healthy MCP server initialize and then exit cleanly on
# EOF. Import-time dependency failures instead produce a non-zero exit, which
# catches packages that Codex would report as a failed MCP handshake.
```

**Finding**: "Codex" here is used only as an illustrative example of "a client that would treat this as a handshake failure" — it names no Codex-specific behavior this repository supports or documents, and removing the word does not change what the check verifies (the assertion below only checks exit codes from `uvx`-run packages, per the rest of the file).

**Decision**: Reword to drop the Codex-specific framing while keeping the same point, per FR-007:
```bash
# Closing stdin lets a healthy MCP server initialize and then exit cleanly on
# EOF. Import-time dependency failures instead produce a non-zero exit, which
# is exactly what a client would see as a failed MCP handshake.
```

## R9 — New ADR: supersede ADR-0004

**Finding**: ADR-0004 ("Replace the hand-maintained Codex port with OpenAI's official import flow") has frontmatter `status: Proposed` — it was never formally moved to `Accepted` despite being the decision spec 021 actually implemented and despite ADR-0002 already pointing to it ("Superseded by 0004"). ADR-0002 itself is untouched by this feature (already Superseded, body unaffected). The next available ADR number is `0010` (`0001`-`0009` exist).

**Decision**: Add `docs/adr/0010-remove-codex-cli-support.md`, Status: Accepted, per the `adr` skill's MADR format (matching the structure of ADR-0001/0004-0009). Its "More information" section states "Supersedes ADR-0004" and its Context section explains ADR-0004's actual Proposed-but-implemented status plus ADR-0002's existing Superseded status, rather than assuming either was formally Accepted. Change ADR-0004's frontmatter `status:` line from `Proposed` to `Superseded by 0010` — no other line in ADR-0004's body is touched (FR-010). ADR-0002 is not edited at all (already accurate).

**Alternatives considered**: First correcting ADR-0004's status to `Accepted` before marking it `Superseded` — rejected as an unnecessary two-step edit to a file this feature is only supposed to touch on its Status line (FR-010); the new ADR's own Context section is the right place to note the historical Proposed-but-implemented discrepancy, not a second edit to ADR-0004's frontmatter.

## R10 — `.gitignore`: reword the Codex-directory comment, keep the ignore rules

Current (lines 76-80):
```gitignore
# Codex configuration is generated locally by OpenAI's official tooling
# (`/import`, or migrate-to-codex) and is never committed — see
# specs/021-codex-official-import/ and docs/adr/0004-*.
.codex/
.agents/
```

**Finding**: The ignore rules themselves (`.codex/`, `.agents/`) still serve a real purpose after this feature — a developer can still run `/import` or `migrate-to-codex` on their own initiative even though this repository no longer documents or supports that workflow, and those tools still write to `.codex/`/`.agents/` by their own external convention. The comment's existing citations are `specs/021-codex-official-import/` and `docs/adr/0004-*` — but both path *names* themselves contain the substring "codex" (the external tool's own naming, same as the directories being ignored), so keeping either citation would leave "codex" inside the comment's prose, contradicting the "drop the word from prose" resolution in spec.md's Edge Cases. There is no way to cite a specific artifact explaining this decision without its name containing "codex."

**Decision**: Keep both ignore lines unchanged. Reword the comment to describe the directories generically and drop the citations entirely rather than cite an artifact whose own name defeats the purpose of the rewording:
```gitignore
# May be written locally by external developer tooling this repository does
# not generate, deploy, or manage.
.codex/
.agents/
```

## R11 — `.specify/integrations/codex.manifest.json` and `.specify/extensions/.registry`: confirmed untouched

**Finding**: Both are Spec Kit's own machine-generated bookkeeping for its `specify init --integration codex` multi-agent-integration feature (tracks hashes of gitignored `.agents/skills/speckit-*` files this repository does not vendor). Neither is hand-authored documentation of this repository's own former Codex CLI guardrail-parity effort — that is a separate, orthogonal use of the string "codex" as a Spec Kit integration identifier.

**Decision**: No edit (FR-012, SC-005). Regenerating or removing Spec Kit's own integration bookkeeping is the `specify` CLI's job via its own commands, not a hand edit made as a side effect of an unrelated documentation-removal feature.

## R12 — Pre-change test-suite baseline (all `tests/run-*.sh`, captured before any edit in this feature)

| Suite | Result before this feature | Cause |
|---|---|---|
| `tests/run-codex-drift.sh` | 6 passed, 0 failed | N/A (deleted by this feature — R5) |
| `tests/run-codex-references.sh` | 9 passed, 0 failed | N/A (deleted by this feature — R5) |
| `tests/run-digital-agency-frontend-skill.sh` | 47 passed, 0 failed | N/A (edited by this feature — R7) |
| `tests/run-install.sh` | **FAIL** (`retired hooks are removed`) | Pre-existing, unrelated to Codex — not touched by this feature |
| `tests/run-mcp-startup.sh` | pass (3/3 packages) | N/A (edited by this feature — R8) |
| `tests/run-subagent-delegation.sh` | **FAIL** (rule file `.claude/rules/subagent-delegation.md` missing) | Pre-existing, spec 030's incomplete cleanup — unrelated to Codex; edited by this feature (R6) for its Codex-specific check only, but will keep failing overall for the pre-existing reason |

**Decision**: Use this table as the literal pre/post comparison baseline for tasks.md's verification steps (spec.md FR-008, SC-003) — a suite that already failed for an unrelated reason is not a regression this feature introduced, and is explicitly out of scope to fix (no drive-by repair of spec 030's incomplete work).
