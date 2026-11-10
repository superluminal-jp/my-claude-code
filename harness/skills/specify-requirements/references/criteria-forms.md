# Forms for requirements and acceptance criteria

Read when writing an acceptance criterion or a requirement sentence. Use a form only when it removes an ambiguity that is actually there; do not run every sentence through every form.

## Ambiguity to remove first

| Pattern | Example | Replace with |
|---|---|---|
| Vague quantifier | "fast", "many", "soon", "robust", "scalable", "user-friendly" | A number and a unit |
| Undefined pronoun or scope | "it", "the system", "everything" | The named target |
| Hidden compound | A statement joined by "and/or" that bundles several requirements | One statement per requirement |
| Implicit actor or trigger | "when needed", "automatically" | The actor, the event, and the precondition |
| Implementation in a requirement | A solution dictated before the need is agreed | What is needed, kept apart from how |
| Negation without a positive | "should not be slow" | A measurable positive, such as "p95 below 200 ms" |

## Forms

| Form | Source | Use it to |
|---|---|---|
| Given/When/Then | Cucumber, Gherkin reference: <https://cucumber.io/docs/gherkin/> | Make the completion condition executable as a scenario |
| EARS | Mavin et al., *RE'09* (17th IEEE International Requirements Engineering Conference), IEEE, 2009, pp. 317-322 | Fit a requirement sentence into one of its syntactic templates |
| Volere fit criterion | Robertson & Robertson, *Mastering the Requirements Process* | Attach a quantified condition that decides whether the requirement is met |
| Planguage | Gilb, *Competitive Engineering*, Butterworth-Heinemann, 2005 | Quantify a quality requirement as Scale, Meter, Must, and Plan |
| SMART | Doran, "There's a S.M.A.R.T. Way to Write Management's Goals and Objectives," *Management Review* 70(11): 35-36, 1981 | Make a goal measurable |
| 5W2H | - | Enumerate the dimensions not yet captured |
| INVEST | Wake, "INVEST in Good Stories, and SMART Tasks," 2003: <https://xp123.com/invest-in-good-stories-and-smart-tasks/> | Judge the size and independence of a user story |
| MoSCoW | Clegg & Barker, *Case Method Fast-Track: A RAD Approach*, Addison-Wesley, 1994 | Rank scope into must, should, could, and won't |
| FURPS+ | Grady, *Practical Software Metrics for Project Management and Process Improvement*, Prentice Hall, 1992 | Detect missing non-functional dimensions |
| ISO/IEC/IEEE 29148:2018 | *Systems and software engineering - Life cycle processes - Requirements engineering*: <https://www.iso.org/standard/72089.html> | Judge the quality of the requirement statement itself |

Business analysis practice more broadly: IIBA, *A Guide to the Business Analysis Body of Knowledge (BABOK Guide)*, v3, 2015.

## Before a requirement goes into the graph

Each requirement is unambiguous, feasible, verifiable, free of conflict with the others, and small enough to estimate. If a failing check cannot be written from its acceptance criterion, the criterion is still ambiguous.

Never invent an acceptance criterion the person did not agree to. When a criterion needs a value only the person holds, record it as an open point with a proposed default, the alternative, and what the choice changes.
