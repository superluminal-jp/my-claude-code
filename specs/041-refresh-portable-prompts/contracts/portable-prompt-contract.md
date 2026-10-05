# Contract: Portable prompt files

Interface: text a human pastes into a vendor settings field. Verified by `quickstart.md`.

| ID | Assertion |
|---|---|
| PP-01 | Each paste block's character count (`len()` of the fenced content) ≤ its budget in [data-model.md](../data-model.md), and the stated count equals the measured count |
| PP-02 | Placement text matches [research.md](../research.md) R1 / R3 exactly (field labels, menu path) |
| PP-03 | Every fact about limits, memory, models, or features is listed under "Verified facts" with an official URL and date; no unlisted service claim appears |
| PP-04 | Paste blocks contain no model names, no `.claude`/`rules/`/`skills/` paths, no slash commands, no authored skill names |
| PP-05 | Paste blocks convey: accuracy/uncertainty marking, authorization boundary, clarification with defaults, answer-first structure, reasoning completeness, brevity |
| PP-06 | Each omission in [research.md](../research.md) R6 appears under "Not ported" with its reason |
| PP-07 | No ALL-CAPS emphasis words (MUST, NEVER, CRITICAL, ALWAYS) in paste blocks |
