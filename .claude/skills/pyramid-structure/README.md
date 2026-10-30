# pyramid-structure

Always-applied skill that structures every substantive answer, plan, decision, review and document as a Minto pyramid, and checks the structure mechanically before the output is sent.

## What it does

- **Applies on every substantive task.** The description tells Claude to use it for every substantive task, and excludes single facts, short direct answers and raw machine output.
- **Checks each substantive draft with a script.** `scripts/check.py md -` reads the draft from standard input and reports heading, list and opening-sentence findings (rules S1–S8). Errors must be fixed before sending; warnings are fixed unless deliberate.
- **Reviews documents in depth on request.** `scripts/check.py tree` checks a claim tree written as JSON (rules T1–T12): tree integrity, group order, the 4-point and 2-"therefore" limits of a deductive group, propositional entailment by truth table with a countermodel on failure, and overlap and coverage of declared scopes.

The script verifies form, not truth. Whether a sentence is a claim, whether a child answers its parent, and whether the claim tree is faithful to the text stay with Claude's judgment (J1–J6 in `SKILL.md`).

## Layout

- `SKILL.md` — entry point (always loaded when the skill triggers; kept short).
- `scripts/check.py` — the checker; Python 3.10+, standard library only. Executed, never read into context.
- `references/` — loaded on demand: `templates.md` (answer, decision, long document), `genres.md` (apex location and key line by genre, IMRaD), `tree-schema.md` (claim-tree JSON).
- `.claude-plugin/plugin.json` — plugin manifest; the folder is also an authored skills-directory plugin. It declares no hooks.
- `tests/` — unit tests for the checker (`test_check.py`) and the package (`test_package.py`: manifest, eval-suite shape, and `claude plugin validate --strict` when the CLI is installed).
- `evals/` — behavior cases for `claude plugin eval`.

## Use as a plugin

`install.sh` already syncs this folder to `~/.claude/skills/`. To load it on its own for one session, point Claude Code at the folder:

```bash
claude --plugin-dir /path/to/pyramid-structure
```

## Tests

```bash
python3 -B -m unittest discover -s tests -v
```

## Evals

Each case grades the reply with `llm` rubrics and adds two zero-cost `tool_used` graders: `skill-fired` (the skill was invoked) and `checker-ran` (`check.py` ran; plugin arm only, so it does not count against the no-plugin baseline). Run from this folder:

```bash
claude plugin eval . --allow-tools "Bash(python3 *)" --model <model you work with> --judge-model haiku
```

- **Judge: Haiku.** The `llm` graders check short, concrete statements about the reply, so the small model suffices; it is also the CLI's default `--judge-model`. If `skill-fired` passes but the score difference to the baseline is negative, suspect the judge first and re-run with `--judge-model sonnet`.
- **Model under test: the one you work with, not Haiku by default.** The suite measures whether that model follows this always-on skill, including running the checker on every substantive draft. No case pins `model`, so `--model haiku` remains a cheap smoke run, but its score says nothing about the model you use.
- **Bash grant.** `Bash` is removed from eval runs unless granted; the grant above allows only `python3` commands, which is all the checker needs.
- Every run is a billed model call. Add `--runs 1 --ablation none` while iterating on graders, and `--max-cost-usd` as a ceiling.
- Unverified: eval runs execute Bash in an OS sandbox that cannot read the home directory. If this folder sits under your home directory, `checker-ran` may fail because the script cannot be read; run the suite from a copy outside it to tell the two apart.

## Provenance

This skill replaces the vendored `minto-pyramid` plugin (archived under `archive/minto-pyramid/`; see spec 055). Its completion check and answer, decision and document templates were carried over in condensed form. Its rule against revealing chain-of-thought was reversed into a reasoning-disclosure rule: the skill shows how each answer was reached as a structured, checkable account, and marks any account of its internal process as a reconstruction. Three of its eval cases (`lead-with-answer`, `avoid-topic-only-headings`, `respect-user-format`) were copied with `Bash` added to their allowed tools so the checker can run; the fourth, `no-chain-of-thought`, became `explains-reasoning` with graders for the reversed rule. `review-finds-structure-gaps` is new.

Sources for the rules: Minto, *The Minto Pyramid Principle* (1987/2009); Mensh & Kording 2017, *PLoS Comput Biol* 13(9):e1005619; Gopen & Swan 1990, *American Scientist* 78(6):550–558; ICMJE Recommendations; Swales 1990; Hopewell et al. 2025 (CONSORT 2025).
