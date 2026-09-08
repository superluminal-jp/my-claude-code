# Applied inventory — frameworks named to the user

These are the frameworks the criteria come from. Name one to the user **only** when it
actually produced the judgement being shown, and only attached to that judgement — never
as a standalone explanation.

Selection is by group, not by scanning this list. The kind of gap decides the group; within
the group, take the entry that most directly generates a criterion. At most two names per
presentation.

## Group A — Confirming grounding

*Use when the question is how to tell that understanding actually matched.*

| Framework | Source | Criterion it generates |
|---|---|---|
| Grounding criterion | Clark, *Using Language*, Cambridge University Press, 1996; Clark & Brennan, "Grounding in Communication," in Resnick, Levine & Teasley (Eds.), *Perspectives on Socially Shared Cognition*, APA, 1991, Ch. 7, pp. 127–149 | Fix the depth of grounding sufficient for the current purpose — no more, no less |
| Read-back / hear-back | ICAO Doc 9432, *Manual of Radiotelephony*, 4th ed., 2007 | Close the loop: the receiver repeats, the sender confirms |
| Back-brief | US Army ADP 6-0, *Mission Command: Command and Control of Army Forces*, July 2019 | The receiver restates the task in their own words before acting |
| Teach-back | AHRQ, *Health Literacy Universal Precautions Toolkit* | Reverse the direction — have the requester restate, to test the explanation rather than the listener |
| I-PASS / SBAR | Starmer et al., *NEJM* 371, 2014 (medical error rate 24.5 → 18.8 per 100 admissions); SBAR, Kaiser Permanente | Structure a handoff into fixed slots so omissions become visible |

## Group B — Conveying intent

*Use when the question is how to transfer what is wanted without dictating the steps.*

| Framework | Source | Criterion it generates |
|---|---|---|
| Commander's Intent | US Army ADP 6-0, 2019 | State purpose and end state, not the procedure |
| Example Mapping | Wynne, "Introducing Example Mapping," Cucumber blog, 8 December 2015 | Separate rules, examples, and open questions structurally |
| Specification by Example | Adzic, *Specification by Example*, Manning, 2011 | Use concrete examples to illustrate a rule; the rule, not the example, is the specification |
| Ubiquitous language | Evans, *Domain-Driven Design*, Addison-Wesley, 2003 | Use the agreed vocabulary strictly, in conversation and in the artifact alike |

## Group C — Locating the divergence

*Use when understanding has already diverged and the point of divergence must be found.*

| Framework | Source | Criterion it generates |
|---|---|---|
| Ladder of inference | Originates with Argyris, *Overcoming Organizational Defenses*, Allyn & Bacon, 1990, p. 88; the seven-rung form in circulation is Ross, in Senge et al., *The Fifth Discipline Fieldbook*, Doubleday, 1994, pp. 242–246 | Identify which rung — data, selection, meaning, assumption, conclusion — the readings parted at |
| Balancing advocacy and inquiry | Argyris; Senge, *The Fifth Discipline*, Doubleday, 1990 | Match each assertion with a question, rather than stacking assertions |
| Toulmin model of argument | Toulmin, *The Uses of Argument*, Cambridge University Press, 1958 | Expose the unstated warrant connecting evidence to claim |
| Premortem | Klein, "Performing a Project Premortem," *Harvard Business Review* 85(9): 18–19, September 2007 | Assume failure has occurred, to surface assumptions never put into words |

## Group D — Writing and verifying requirements

*Use when intent is agreed and must become something testable.*

| Framework | Source | Criterion it generates |
|---|---|---|
| Ambiguity pattern catalogue | Carried forward from the prior form of this capability | Detect vague quantifiers, undefined pronouns, hidden compounds, implicit actors, implementation leakage, negation without a positive |
| 5W2H | — | Enumerate the dimensions not yet captured |
| SMART | Doran, "There's a S.M.A.R.T. Way to Write Management's Goals and Objectives," *Management Review* 70(11): 35–36, 1981 | Make a goal measurable |
| Given/When/Then | Cucumber, Gherkin reference — <https://cucumber.io/docs/gherkin/> | Make the completion condition executable as a scenario |
| EARS | Mavin et al., *RE'09* (17th IEEE International Requirements Engineering Conference), IEEE, 2009, pp. 317–322 | Fit each requirement sentence into one of six syntactic templates |
| Volere fit criterion | Robertson & Robertson, *Mastering the Requirements Process* | Attach a quantified condition that decides whether the requirement is met |
| Planguage | Gilb, *Competitive Engineering*, Butterworth-Heinemann, 2005 | Quantify a quality requirement as Scale / Meter / Must / Plan |
| INVEST | Wake, "INVEST in Good Stories, and SMART Tasks," 2003 — <https://xp123.com/invest-in-good-stories-and-smart-tasks/> | Judge the size and independence of a user story |
| MoSCoW | Clegg & Barker, *Case Method Fast-Track: A RAD Approach*, Addison-Wesley, 1994; stewarded by the DSDM / Agile Business Consortium | Rank scope into must / should / could / won't |
| FURPS+ | Grady, *Practical Software Metrics for Project Management and Process Improvement*, Prentice Hall, 1992 | Detect missing non-functional dimensions |
| ISO/IEC/IEEE 29148:2018 | *Systems and software engineering — Life cycle processes — Requirements engineering* — <https://www.iso.org/standard/72089.html> | Judge the quality of the requirement statement itself |

Business analysis practice more broadly: IIBA, *A Guide to the Business Analysis Body of
Knowledge (BABOK Guide)*, v3, 2015 — <https://www.iiba.org/>.

## What stays out of this inventory

There is no cap on how many frameworks this inventory holds. Only two conditions exclude one.

1. **Domain-specific standards** — security, accessibility, cloud-provider guidance, and the
   like. A separately matching capability owns those; duplicating them here would create a
   second, weaker copy.
2. **Practices that presuppose co-presence or simultaneous speech** — Event Storming, Three
   Amigos, Impact Mapping, and Collaborative Requirements Modelling among them. They depend on
   the copresence, simultaneity, and co-temporality constraints Clark & Brennan (1991) identify
   as properties of the medium. In one-to-one text they can be cited but not performed, so they
   are not stocked here.
