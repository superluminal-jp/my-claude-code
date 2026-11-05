# The bundled checker

`scripts/check_graph.py` reads one declaration, a skills directory, or the three records of the gate, and reports every rule it breaks. It reads its input and nothing else: it writes no file, opens no network connection, starts no process, and never executes input content. It needs Python 3.9 or later and its standard library only.

```sh
python3 <skill-dir>/scripts/check_graph.py [--format text|json] FILE
python3 <skill-dir>/scripts/check_graph.py [--format text|json] --skills-dir DIR
python3 <skill-dir>/scripts/check_graph.py [--format text|json] --gate CARD GRAPH [REPORT]
```

Give exactly one of the three. The kind of a `FILE` is read from its top-level key.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | no violation (for `--gate`: `ready`) |
| 1 | one or more violations (for `--gate`: `blocked`) |
| 2 | the input cannot be interpreted — bad arguments, a file that is unreadable, not a regular file, over 5 MiB, not UTF-8, invalid JSON, a repeated key, nesting too deep, or a wrong top level — or the checker itself failed |

With `--format json` the result is one object: `output_version`, `input_file`, `graph` (the kind), `status` (`passed`, `failed`, `error`), `rules_checked`, `violations` (`{rule_id, node_id, message}`), and `error`; the gate adds `decision`, `challenge` (`recorded` or `not_run`), and `reasons` (`{rule_id, message}`). `passed` means the structure follows the rules listed in `rules_checked`, nothing more.

## Declarations

Every declaration has `schema_version` and exactly one of the four keys below.

### Problem card — `problem_card` (object, `schema_version` 1)

Required: `id`, `ideal`, `current`, `gap`, `significance` (non-empty strings), `status` (`verified`, `unverified`, or `refuted`), and `evidence` (an array, possibly empty, of `{source, observation}`). Optional: `counter_evidence` (same shape), `hypotheses`, `proposed_solutions`, `out_of_scope` (arrays of strings), `status_rationale` (string).

| Rule | Passes when |
|---|---|
| C-00 | required fields are present, every value has the right type, and no field is undefined |
| C-01 | a `verified` card has at least one evidence entry |
| C-02 | any counter-evidence comes with a non-empty `status_rationale`, and a `refuted` card has counter-evidence |
| C-03 | `status` is one of the three values |

### Requirements graph — `requirements` (array)

Each node: `id`, `statement`, `decomposition` (`AND` — every child is needed; `OR` — one child is chosen by condition; `LEAF` — not decomposed), `acceptance` (at least one `{id, description, level}`, where `level` is `L1` for a leaf check, `L2` for a parent's integration check, `L3` for the whole system), and optionally `children`, `assumptions`, `counterexamples`, and, on an `OR` only, `selection` (`{child id: condition}` for every child). With `schema_version` 2 the top level also has `problem_id`, the id of the problem card the graph decomposes; the gate needs version 2.

### Skill composition graph — `skills` (array, `schema_version` 1)

Each node: `id`, `permission` (`read_only`, `workspace_write` — reversible changes inside the working tree, `external_effect` — effects on other systems or people), `role` (`orchestrator` applies its children in order, `worker` does the task, `auditor` is an independent AI reviewer, `checker` is a deterministic program), and optionally `children`.

### Challenge report — `challenge_report` (object, `schema_version` 1)

`problem_id`, `reviewer`, `context_given` (array of strings), and `findings`, each with `id`, `kind`, `target` (the problem card id or a requirement id), `severity` (`high`, `medium`, `low`), `statement`, `disposition` (`open`, `accepted`, `rejected`), and `resolution` (required unless `open`). The kinds are those in [challenger.md](challenger.md).

| Rule | Passes when |
|---|---|
| R-00 | required fields are present, every value has the right type, and no field is undefined |
| R-01 | finding ids are non-empty and unique; `kind`, `severity`, and `disposition` have defined values |
| R-02 | every `accepted` or `rejected` finding has a resolution |
| R-03 | (gate only) every target is the problem card or a node of the requirements graph |

## Graph rules

In the *Applies to* column, *declarations* means requirement and skill graph files, *compatibility mode* means `--skills-dir`, and *all* means both.

| Rule | Applies to | Passes when |
|---|---|---|
| S-00 | declarations | every node is an object with correctly typed fields and no undefined field |
| S-01 | declarations | every node has a non-empty, unique `id` |
| S-02 | all | every child is defined (a `SKILL.md` exists in compatibility mode) and listed once |
| S-03 | all | following children never returns to a node; a violation shows the cycle |
| S-04 | requirements | `LEAF` has no child; `AND` and `OR` have at least two |
| S-05 | requirements | an `OR` gives a non-empty condition for every child and names no id that is not its child; other nodes have no `selection` |
| S-06 | requirements | every node has at least one acceptance criterion |
| S-07 | requirements | acceptance ids are non-empty and unique across the graph; levels are `L1`–`L3` |
| S-08 | all | a child with several parents is legal (this rule never reports) |
| S-09 | skills | permission and role have defined values; an `auditor` or `checker`, and every skill reachable from it, is `read_only` |
| S-10 | compatibility mode | a declared child declares no children of its own: a `## Child skills` section may list skills that list none |
| S-11 | requirements | at most one node has no parent, so a forgotten child shows up as a second root |

## Gate rules

`--gate CARD GRAPH [REPORT]` is `ready` only when all four hold; otherwise it is `blocked` and `reasons` lists each one that failed.

| Rule | Holds when |
|---|---|
| G-01 | the problem card has no violation and its status is `verified` |
| G-02 | the requirements graph has no violation, is version 2, and its `problem_id` is the card's `id` |
| G-03 | if a report is given, it has no violation (including R-03) and is for the card's `id` |
| G-04 | no finding is `open` |

Without a report the gate can still be `ready`, and says `challenge: not_run`.

## Limits

- Statements are checked for presence, not meaning. A gap that names a solution, an OR whose conditions overlap, or a parent whose acceptance merely restates a child's passes every rule; finding those is the challenger's job.
- `permission` and `role` are self-declared; a skill that writes but declares `read_only` passes S-09.
- Declared skill ids are not compared with real `SKILL.md` files; only `--skills-dir` reads real skills, and it checks structure only, not how skills name each other in their text.
