"""AC-COMPAT-1: the bodies of every SKILL.md and agent definition are unchanged.

For each harness/skills/*/SKILL.md and harness/agents/*.md, compare the text
after the closing '---' of the frontmatter at BASE (default main) with the
same file at HEAD of the working tree (or at the commit given as the second
argument). Every file must exist on both sides (REQ-FORM renamed or converted
nothing) and its body must be byte-identical.
Run: python3 -I specs/073-scrum-role-tree/evidence/frontmatter_only.py [BASE [COMMIT]]
Exit 0 when every body is unchanged, 1 otherwise. Runs read-only git commands.
"""
import pathlib
import re
import subprocess
import sys

base = sys.argv[1] if len(sys.argv) > 1 else "main"
commit = sys.argv[2] if len(sys.argv) > 2 else None


def git_show(rev, rel):
    proc = subprocess.run(["git", "show", f"{rev}:{rel}"], capture_output=True, text=True)
    return proc.stdout if proc.returncode == 0 else None


def body(text):
    match = re.match(r"^---\n.*?\n---\n", text, re.S)
    return text[match.end():] if match else None


def files(rev):
    if rev is None:
        found = [str(p) for p in pathlib.Path("harness/skills").glob("*/SKILL.md")]
        found += [str(p) for p in pathlib.Path("harness/agents").glob("*.md")]
        return sorted(found)
    out = subprocess.run(["git", "ls-tree", "-r", "--name-only", rev, "harness/skills", "harness/agents"],
                         capture_output=True, text=True, check=True).stdout.split()
    return sorted(f for f in out if re.fullmatch(r"harness/skills/[^/]+/SKILL\.md|harness/agents/[^/]+\.md", f))


errors = []
old_files, new_files = files(base), files(commit)
if old_files != new_files:
    errors.append(f"file sets differ: only at {base} {sorted(set(old_files) - set(new_files))}, only now {sorted(set(new_files) - set(old_files))}")
for rel in sorted(set(old_files) & set(new_files)):
    old = git_show(base, rel)
    new = git_show(commit, rel) if commit else pathlib.Path(rel).read_text(encoding="utf-8")
    if body(old) is None or body(new) is None:
        errors.append(f"{rel}: no frontmatter on one side")
    elif body(old) != body(new):
        errors.append(f"{rel}: the body after the frontmatter changed")
for e in errors:
    print(f"FAIL {e}")
print(f"frontmatter-only: {len(new_files)} files compared with {base}, {len(errors)} failures")
sys.exit(1 if errors else 0)
