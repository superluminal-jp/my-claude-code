"""AC-DIAGRAM-3: the relations outside the role tree have their own page.

Checks, from the repository root:
- docs/harness/skill-map/04-components-relations.md has, in its Mermaid
  block, the 7 named relations: deliver-change to its 4 children,
  specify-requirements and verify-change to read-only-reviewer, and
  apply-scrum-guide to scrum-master-agent;
- that page has no role or branch node (no "[役割" or "[枝" label, no role_ id);
- the index docs/harness/skill-map/README.md lists the 5 pages in the order
  system context, containers, role tree, relations, dynamic.
Run: python3 -I specs/073-scrum-role-tree/evidence/check_skill_map.py
Exit 0 when every check holds, 1 otherwise. Reads files only.
"""
import pathlib
import re
import sys

DIR = pathlib.Path("docs/harness/skill-map")
EDGES = [
    ("deliver_change", "define_problem"), ("deliver_change", "specify_requirements"),
    ("deliver_change", "implement_change"), ("deliver_change", "verify_change"),
    ("specify_requirements", "read_only_reviewer"), ("verify_change", "read_only_reviewer"),
    ("apply_scrum_guide", "scrum_master_agent"),
]
ORDER = ["01-system-context.md", "02-containers.md", "03-role-tree.md", "04-components-relations.md", "05-dynamic-deliver-change.md"]

errors = []
page = (DIR / "04-components-relations.md").read_text(encoding="utf-8")
block = re.search(r"```mermaid\n(.*?)```", page, re.S)
mermaid = block.group(1) if block else ""
for a, b in EDGES:
    if not re.search(rf"^\s*{a}\s*-->\|\"[^\"]+\"\|\s*{b}\s*$", mermaid, re.M):
        errors.append(f"relations page lacks the edge {a} --> {b}")
if re.search(r"\[役割|\[枝|\brole_[a-z_]+\[", mermaid):
    errors.append("relations page has a role or branch node")
index = (DIR / "README.md").read_text(encoding="utf-8")
listed = re.findall(r"^\| [0-9] \| \[[^\]]+\]\(([^)]+)\)", index, re.M)
if listed != ORDER:
    errors.append(f"index lists {listed}, not {ORDER}")
for e in errors:
    print(f"FAIL {e}")
print(f"skill-map: {len(EDGES)} edges, {len(ORDER)} pages, {len(errors)} failures")
sys.exit(1 if errors else 0)
