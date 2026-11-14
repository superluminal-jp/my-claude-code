"""AC-FORM-1: check the table in specs/073-scrum-role-tree/form-and-name-review.md.

Rules:
- the element names in the table are exactly the skills under harness/skills/
  and the agent definitions under harness/agents/;
- the form verdict is エージェント exactly when (a) and (b) are both はい;
- the form cell says 変える exactly when the verdict differs from the current
  form, and the current form of an unchanged element is where it is now;
- the name cell is 変えない, or 変える: <new name>.

Run from the repository root:
  python3 -I specs/073-scrum-role-tree/evidence/check_form_review.py
Exit 0 when every rule holds, 1 when the table is missing or a rule fails.
Reads files only.
"""
from __future__ import annotations

import pathlib
import re
import sys

TABLE = pathlib.Path("specs/073-scrum-role-tree/form-and-name-review.md")
HEADER = ["要素", "現在の形", "(a)", "(b)", "形の判定", "名前の判定", "理由"]
FORMS = {"スキル", "エージェント"}
YES_NO = {"はい", "いいえ"}


def elements() -> dict[str, str]:
    found = {p.name: "スキル" for p in pathlib.Path("harness/skills").iterdir() if (p / "SKILL.md").is_file()}
    found.update({p.stem: "エージェント" for p in pathlib.Path("harness/agents").glob("*.md")})
    return found


def rows(text: str) -> tuple[list[str], list[list[str]]]:
    lines = [line for line in text.splitlines() if line.startswith("|")]
    cells = [[c.strip() for c in line.strip().strip("|").split("|")] for line in lines]
    if len(cells) < 2:
        return [], []
    return cells[0], [c for c in cells[2:]]


def main() -> int:
    if not TABLE.is_file():
        print(f"FAIL {TABLE} does not exist")
        return 1
    header, body = rows(TABLE.read_text(encoding="utf-8"))
    errors: list[str] = []
    if header != HEADER:
        errors.append(f"header must be {HEADER}, not {header}")
    actual = elements()
    names = []
    for cells in body:
        if len(cells) != len(HEADER):
            errors.append(f"row has {len(cells)} cells, not {len(HEADER)}: {cells}")
            continue
        name, current, a, b, verdict_cell, name_cell, reason = cells
        name = name.strip("`")
        names.append(name)
        verdict = re.sub(r"（.*?）", "", verdict_cell).strip()
        if current not in FORMS or verdict not in FORMS:
            errors.append(f"{name}: forms must be one of {sorted(FORMS)}")
        if a not in YES_NO or b not in YES_NO:
            errors.append(f"{name}: (a) and (b) must be one of {sorted(YES_NO)}")
        want = "エージェント" if (a == "はい" and b == "はい") else "スキル"
        if verdict != want:
            errors.append(f"{name}: (a)={a} (b)={b} gives {want}, but the verdict is {verdict}")
        changes = "変える" in verdict_cell
        if changes != (verdict != current):
            errors.append(f"{name}: the form cell says change={changes} while verdict {verdict} vs current {current}")
        if not changes and actual.get(name) not in (None, current):
            errors.append(f"{name}: current form {current} differs from where it is ({actual.get(name)})")
        if name_cell != "変えない" and not re.fullmatch(r"変える: [a-z0-9]+(-[a-z0-9]+)*", name_cell):
            errors.append(f"{name}: name cell must be 変えない or '変える: <new-name>', not {name_cell!r}")
        if not reason:
            errors.append(f"{name}: the reason is empty")
    if len(names) != len(set(names)):
        errors.append("an element appears in more than one row")
    if set(names) != set(actual):
        errors.append(f"table names differ from harness: missing {sorted(set(actual) - set(names))}, extra {sorted(set(names) - set(actual))}")
    for error in errors:
        print(f"FAIL {error}")
    print(f"form-review: {len(names)} rows, {len(errors)} failures")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
