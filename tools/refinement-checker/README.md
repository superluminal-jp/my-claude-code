# refinement-checker

日本語版: [README.ja.md](README.ja.md)

`check_graph.py` reads a declared requirement graph or skill composition graph
and reports every structural rule it breaks, without changing anything. A
pass means only that the declaration follows the rules listed in the result;
it does not show that a decomposition is sufficient, that an implementation
is secure, or that any test was run. The contract is
[spec 059](../../specs/059-refinement-graph-checker/spec.md); the exact
arguments, output, and exit codes are in its
[CLI contract](../../specs/059-refinement-graph-checker/contracts/cli.md).

Terms used below:

- **Skill**: a Claude Code skill, a directory with a `SKILL.md` playbook that
  Claude loads when a task matches it. This repository's skills are under
  `.claude/skills/`.
- **Spec 058**: [`specs/058-parent-skill-references/spec.md`](../../specs/058-parent-skill-references/spec.md).
  It lets a parent skill list, in a `## Child skills` section of its
  `SKILL.md`, the skills it applies in order, one `` - `name` `` line each, and
  allows one level only: a child skill may not list children of its own.
- **Levels L1, L2, L3**: what an acceptance criterion verifies. L1 checks a
  single leaf requirement, L2 checks a parent by integrating its children,
  and L3 checks the whole system.
- **Phases**: spec 059 is Phase 1 of five. Phase 2 adds problem definition and
  decomposition skills, Phase 3 independent verification at every level with
  recorded evidence (which test ran on which commit, with what result),
  Phase 4 a review card for the human decision, and Phase 5 a comparison
  experiment of review time and quality.

## Purpose, who runs it, and where it is distributed

- **Purpose**: Phase 1 of a plan to let people review AI-made changes by their
  requirements and evidence rather than by rereading every diff. It gives
  requirement decompositions and skill compositions a declared form that a
  machine can check before later phases write parent skills (none exists
  yet) or independent auditor agents.
- **Who runs it**: the GitHub Actions job `test` in `.github/workflows/ci.yml`
  (through `tests/run-refinement-checker.sh`),
  and the maintainer or Claude by hand.
- **Distribution**: none. It lives outside `.claude/`, so `install.sh` does not
  copy it to `~/.claude/`. Whether it moves into a skill under
  `.claude/skills/` is decided in Phase 2.

## Usage

Python 3.9 or later; the standard library only; no network access.

```sh
python3 tools/refinement-checker/check_graph.py FILE
python3 tools/refinement-checker/check_graph.py --format json FILE
python3 tools/refinement-checker/check_graph.py --skills-dir .claude/skills
```

`FILE` is one declaration (JSON). `--skills-dir DIR` is compatibility mode: it
reads the `## Child skills` section of every `DIR/*/SKILL.md` the way spec 058
defines it. Give exactly one of the two.

## Declaration format

A declaration has `"schema_version": 1` and exactly one of `requirements` or
`skills`, an array of nodes. See [`examples/`](examples/) for one of each, and
the [data model](../../specs/059-refinement-graph-checker/data-model.md) for
every field and the rule a missing or wrong field breaks.

- **Requirement node**: `id`, `statement`, `decomposition` (`AND`, `OR`, or
  `LEAF`), `acceptance` (at least one `{id, description, level}`, level `L1`,
  `L2`, or `L3`), and optionally `children`, `assumptions`, `counterexamples`,
  and, on an OR node only, `selection` (a condition for every child).
- **Skill node**: `id`, `permission` (`read_only`, `workspace_write`, or
  `external_effect`), `role` (`orchestrator`, `worker`, `auditor`, or
  `checker`), and optionally `children`.

## Rules

In the `Applies to` column, *declarations* means both kinds of declaration
file, *requirements* and *skills* mean that kind only, *compatibility mode*
means `--skills-dir`, and *all* means every input.

| Rule | Applies to | Passes when |
|---|---|---|
| S-00 | declarations | every node is an object with correctly typed fields and no undefined field |
| S-01 | declarations | every node has a non-empty, unique `id` |
| S-02 | all | every child is defined (a `SKILL.md` exists in compatibility mode) and listed once |
| S-03 | all | following children never returns to a node; a violation shows the cycle |
| S-04 | requirements | `LEAF` has no child; `AND` and `OR` have at least two |
| S-05 | requirements | an `OR` gives a non-empty condition for every child and names no other id; other nodes have no `selection` |
| S-06 | requirements | every node has at least one acceptance criterion |
| S-07 | requirements | acceptance ids are non-empty and unique across the graph; levels are `L1`–`L3` |
| S-08 | all | a child with several parents is legal (never reported) |
| S-09 | skills | permission and role are known values; an `auditor` or `checker`, and every skill it can reach, is `read_only` |
| S-10 | compatibility mode | a declared child declares no children of its own (spec 058's one level) |
| S-11 | requirements | at most one node has no parent, so a forgotten child shows up as a second root |

## Exit codes

| Code | Meaning |
|---|---|
| 0 | no violation |
| 1 | one or more rule violations |
| 2 | the input cannot be interpreted (bad arguments, unreadable or over 5 MiB, not UTF-8, invalid JSON, a repeated key, nesting too deep, a wrong top level), or the checker itself failed |

## Limits

- `permission` and `role` are declared, not enforced. A skill that writes
  files but declares `permission: read_only`, or an auditor declared as
  `role: worker`, passes S-09. Enforcement belongs to Claude Code's permission
  settings and the environment that runs the skill.
- Declared skill ids are not compared with the real `SKILL.md` files; only
  compatibility mode reads real skills.
- Compatibility mode checks the structural rules of spec 058 only. Whether a
  declared child is in the `authored_skills` list (the skills this repository
  authors, listed at the top of `tests/run-config-pyramid.sh`), and how skills name each
  other in their text, stay with `tests/run-config-pyramid.sh`.
- OR conditions are checked for presence, not for being exclusive or covering
  every case. Whether a parent's acceptance criteria really verify the parent
  is a judgment for a reviewer.

## Tests

```sh
bash tests/run-refinement-checker.sh
```

It runs the acceptance tests in [`tests/`](tests/), checks both examples, and
reads this repository's `.claude/skills/` in compatibility mode. Four tests
that need Phase 3's evidence records are printed as `NOT RUN` and never
counted as passed: T-04 (a failed parent check keeps the change incomplete),
T-05 (a completion claim without evidence is not accepted), T-06 (evidence for
another commit is rejected as stale), and T-10 (an unknown risk class stops
the flow instead of counting as low risk).
