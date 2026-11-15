import pathlib, re, sys
root = pathlib.Path(sys.argv[1])
skills = sorted(p.name for p in (root/'skills').iterdir() if (p/'SKILL.md').exists())
agents = sorted(p.stem for p in (root/'agents').glob('*.md'))
for s in skills:
    text = (root/'skills'/s/'SKILL.md').read_text()
    fm, body = text.split('---', 2)[1], text.split('---', 2)[2]
    meta = {}
    inmeta = False
    for line in fm.splitlines():
        if line.startswith('metadata:'): inmeta = True; continue
        if inmeta and line.startswith('  '):
            k, _, v = line.strip().partition(':'); meta[k] = v.strip()
        elif inmeta: inmeta = False
    print(f"## {s}  kind={meta.get('kind')} perm={meta.get('permission')} sandbox={meta.get('sandbox')}")
    for k in ('consumes', 'produces'):
        if k in meta: print(f"   {k}: {meta[k]}")
    m = re.search(r'^## Child skills\n(.*?)(?=^## )', body, re.S | re.M)
    if m: print('   CHILDREN:', re.findall(r'`([a-z-]+)`', m.group(1)))
    lines = body.splitlines()
    for name in skills + agents:
        if name == s: continue
        hits = [i+1+text[:text.index(body)].count('\n') for i, l in enumerate(lines) if re.search(r'(?<![a-z-])' + re.escape(name) + r'(?![a-z-])', l)]
        if hits: print(f"   refs {name}: lines {hits[:6]}")
