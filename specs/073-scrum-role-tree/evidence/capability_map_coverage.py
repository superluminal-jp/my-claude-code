"""List, for every skill and agent under harness/, whether docs/harness/capability-map.json
names it as a component and which branches its stages carry. Read-only. Run from the
repository root: python3 -I specs/073-scrum-role-tree/evidence/capability_map_coverage.py"""
import json
import pathlib

m = json.load(open("docs/harness/capability-map.json", encoding="utf-8"))
comps = {c["id"] for c in m["components"]}
skills = sorted(p.name for p in pathlib.Path("harness/skills").iterdir() if (p / "SKILL.md").exists())
agents = sorted(p.name for p in pathlib.Path("harness/agents").glob("*.md"))
ids = [f"skill:{s}" for s in skills] + [f"agent:{a}" for a in agents]
for i in ids:
    stages = [s for s in m["stages"] if i in s.get("owners", [])]
    branches = sorted({s["branch"] for s in stages})
    print(f"{i:36s} component={'yes' if i in comps else 'NO'} branches={','.join(branches) or '-'} stages={','.join(s['id'] for s in stages)}")
print(f"elements={len(ids)} missing={sum(i not in comps for i in ids)} multi_branch={sum(len({s['branch'] for s in m['stages'] if i in s.get('owners', [])}) > 1 for i in ids)}")
