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
- `tests/` — unit tests for the checker.
- `evals/` — behavior cases for `claude plugin eval`.

## Tests

```bash
python3 -B -m unittest discover -s tests -v
```

## Provenance

This skill replaces the vendored `minto-pyramid` plugin (archived under `archive/minto-pyramid/`; see spec 055). Its completion check and answer, decision and document templates were carried over in condensed form. Its rule against revealing chain-of-thought was reversed into a reasoning-disclosure rule: the skill shows how each answer was reached as a structured, checkable account, and marks any account of its internal process as a reconstruction. Three of its eval cases (`lead-with-answer`, `avoid-topic-only-headings`, `respect-user-format`) were copied with `Bash` added to their allowed tools so the checker can run; the fourth, `no-chain-of-thought`, became `explains-reasoning` with graders for the reversed rule. `review-finds-structure-gaps` is new.

Sources for the rules: Minto, *The Minto Pyramid Principle* (1987/2009); Mensh & Kording 2017, *PLoS Comput Biol* 13(9):e1005619; Gopen & Swan 1990, *American Scientist* 78(6):550–558; ICMJE Recommendations; Swales 1990; Hopewell et al. 2025 (CONSORT 2025).
