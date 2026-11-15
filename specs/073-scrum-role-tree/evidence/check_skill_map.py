"""AC-DIAGRAM-3: the relations outside the role tree have their own page.

Checks, from the repository root:
- docs/harness/skill-map/04-components-relations.md has, in its Mermaid
  block, the 7 named relations: deliver-change to its 4 children,
  specify-requirements and verify-change to read-only-reviewer, and
  apply-scrum-guide to scrum-master-agent;
- that page has no role or branch node (no "[役割" or "[枝" label, no role_ id);
- the index docs/harness/skill-map/README.md lists the 5 pages in the order
  system context, containers, role tree, relations, dynamic;
- every `...SKILL.md`:N citation in pages 01, 02, 04, and 05 names a line that
  exists, and the citations below still point at the line that says what the
  page claims (AR-04 of the first assurance review: the frontmatter grew).
With REV, the pages are read as committed at REV (git show), the skills from
the working tree.
Run: python3 -I specs/073-scrum-role-tree/evidence/check_skill_map.py [REV]
Exit 0 when every check holds, 1 otherwise. Reads files only.
"""
import pathlib
import re
import subprocess
import sys

REV = sys.argv[1] if len(sys.argv) > 1 else None


def page_text(name):
    rel = f"docs/harness/skill-map/{name}"
    if REV:
        return subprocess.run(["git", "show", f"{REV}:{rel}"], capture_output=True, text=True, check=True).stdout
    return pathlib.Path(rel).read_text(encoding="utf-8")


# (page, skill, line, text the line must contain)
ANCHORS = [
    ("01-system-context.md", "manage-git", 10, "network-hosts:"),
    ("01-system-context.md", "apply-dads-frontend", 10, "network-hosts:"),
    ("01-system-context.md", "build-dads-slides", 10, "network-hosts:"),
    ("02-containers.md", "specify-requirements", 38, "read-only-reviewer"),
    ("02-containers.md", "verify-change", 32, "read-only-reviewer"),
    ("02-containers.md", "apply-scrum-guide", 55, "scrum-master-agent"),
    ("04-components-relations.md", "deliver-change", 17, "## Child skills"),
    ("04-components-relations.md", "apply-scrum-guide", 15, "それぞれを扱う能力と併用し"),
    ("04-components-relations.md", "apply-secure-logging", 15, "adds its criteria"),
    ("04-components-relations.md", "apply-dads-frontend", 16, "adds its criteria"),
    ("05-dynamic-deliver-change.md", "deliver-change", 26, "define-problem"),
    ("05-dynamic-deliver-change.md", "deliver-change", 27, "specify-requirements"),
    ("05-dynamic-deliver-change.md", "deliver-change", 28, "implement-change"),
    ("05-dynamic-deliver-change.md", "deliver-change", 35, "Stop and ask"),
    ("05-dynamic-deliver-change.md", "verify-change", 22, "Commit the change first"),
    ("05-dynamic-deliver-change.md", "implement-change", 20, "When the change has a requirements graph"),
    ("05-dynamic-deliver-change.md", "implement-change", 28, "Synchronize"),
    ("05-dynamic-deliver-change.md", "apply-scrum-guide", 43, "作成物を読む"),
    ("05-dynamic-deliver-change.md", "apply-scrum-guide", 48, "完了を判定する"),
    ("05-dynamic-deliver-change.md", "apply-scrum-guide", 57, "開発でファイルを変えた作業"),
]
CITE = re.compile(r"`(?:harness/)?(?:skills/)?([a-z0-9-]+)/SKILL\.md`:([0-9](?:[0-9, -]*[0-9])?)")

DIR = pathlib.Path("docs/harness/skill-map")
EDGES = [
    ("deliver_change", "define_problem"), ("deliver_change", "specify_requirements"),
    ("deliver_change", "implement_change"), ("deliver_change", "verify_change"),
    ("specify_requirements", "read_only_reviewer"), ("verify_change", "read_only_reviewer"),
    ("apply_scrum_guide", "scrum_master_agent"),
]
ORDER = ["01-system-context.md", "02-containers.md", "03-role-tree.md", "04-components-relations.md", "05-dynamic-deliver-change.md"]

errors = []
page = page_text("04-components-relations.md")
block = re.search(r"```mermaid\n(.*?)```", page, re.S)
mermaid = block.group(1) if block else ""
for a, b in EDGES:
    if not re.search(rf"^\s*{a}\s*-->\|\"[^\"]+\"\|\s*{b}\s*$", mermaid, re.M):
        errors.append(f"relations page lacks the edge {a} --> {b}")
if re.search(r"\[役割|\[枝|\brole_[a-z_]+\[", mermaid):
    errors.append("relations page has a role or branch node")
index = page_text("README.md")
listed = re.findall(r"^\| [0-9] \| \[[^\]]+\]\(([^)]+)\)", index, re.M)
if listed != ORDER:
    errors.append(f"index lists {listed}, not {ORDER}")
cited = 0
for name in ("01-system-context.md", "02-containers.md", "04-components-relations.md", "05-dynamic-deliver-change.md"):
    text = page_text(name)
    for skill, spec in CITE.findall(text):
        size = len(pathlib.Path(f"harness/skills/{skill}/SKILL.md").read_text(encoding="utf-8").split("\n"))
        for n in re.findall(r"[0-9]+", spec):
            cited += 1
            if int(n) > size:
                errors.append(f"{name}: {skill}/SKILL.md:{n} is past the end ({size} lines)")
    for page, skill, n, want in ANCHORS:
        if page == name and f"{skill}/SKILL.md`:" in text:
            line = pathlib.Path(f"harness/skills/{skill}/SKILL.md").read_text(encoding="utf-8").split("\n")[n - 1]
            cites_n = any(n in [int(x) for x in re.findall(r"[0-9]+", s)] or any(int(a) <= n <= int(b) for a, b in re.findall(r"([0-9]+)-([0-9]+)", s))
                          for k, s in CITE.findall(text) if k == skill)
            if want not in line:
                errors.append(f"{skill}/SKILL.md:{n} does not contain {want!r}")
            if not cites_n:
                errors.append(f"{name} does not cite {skill}/SKILL.md:{n}, where {want!r} is")
for e in errors:
    print(f"FAIL {e}")
print(f"skill-map: {len(EDGES)} edges, {len(ORDER)} pages, {cited} line citations, {len(ANCHORS)} anchors, {len(errors)} failures")
sys.exit(1 if errors else 0)
