#!/usr/bin/env python3
"""Reproduce the dry run of AC-ROOT-1: build a documentation tree in a fixture, then keep it.

Follows the "Build a documentation tree" procedure of sync-docs/SKILL.md on a throwaway Git
repository with two products and two feature folders each and no README, then adds a feature
folder and applies the Check step of the procedure for every change. Prints every command
with its raw output and exit code, and ends with RESULT: every expectation held (exit 0) or
the expectations that did not (exit 1).

The person who confirms the declaration in step 1 of the procedure is stood in for by whoever
runs this script: a fixture has nobody to confirm it. Each fact written into a README comes
with its source, a file and line of the fixture or a command and its output, in FACTS below.

Usage: python3 -B dryrun.py --skill <sync-docs directory> --work <new directory under $TMPDIR>
                            [--snapshot <directory to copy the final fixture into, as data files>]
Writes only under --work and --snapshot. Standard library only; no network.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

U = "TODO(unfilled): "
FIXTURE = {
    "package.json": '{\n  "name": "acme-platform",\n  "private": true,\n  "workspaces": ["products/*"],\n'
                    '  "scripts": {\n    "test": "vitest run"\n  }\n}\n',
    "products/shop/package.json": '{\n  "name": "@acme/shop",\n  "description": "Customer-facing web shop.",\n'
                                  '  "scripts": {\n    "build": "vite build",\n    "test": "vitest run"\n  }\n}\n',
    "products/admin/package.json": '{\n  "name": "@acme/admin",\n  "description": "Internal console for staff.",\n'
                                   '  "scripts": {\n    "build": "vite build",\n    "test": "vitest run"\n  }\n}\n',
    "products/shop/src/features/cart/cart.ts":
        "// Keeps the items a customer intends to buy, in the browser session only.\n"
        "export function addItem(cart: string[], sku: string): string[] {\n  return [...cart, sku];\n}\n",
    "products/shop/src/features/cart/cart.test.ts":
        'import { addItem } from "./cart";\ntest("adding an item keeps earlier items", () => {\n'
        '  expect(addItem(["a"], "b")).toEqual(["a", "b"]);\n});\n',
    "products/shop/src/features/checkout/checkout.ts":
        "// Turns a cart into an order. Payment is handled by an external provider.\n"
        "export function placeOrder(cart: string[]): { items: string[] } {\n"
        '  if (cart.length === 0) throw new Error("empty cart");\n  return { items: cart };\n}\n',
    "products/admin/src/features/users/users.ts": "export function listUsers(): string[] {\n  return [];\n}\n",
    "products/admin/src/features/audit-log/audit.ts":
        "// Records staff actions for later review. Entries are never edited after they are written.\n"
        "export function record(action: string): string {\n  return `${new Date().toISOString()} ${action}`;\n}\n",
}
COUPON = ("products/shop/src/features/coupon/coupon.ts",
          "// Applies a discount code to an order total. A code can be used once per order.\n"
          "export function applyCoupon(total: number, percent: number): number {\n"
          "  return total * (1 - percent / 100);\n}\n")

failures: list[str] = []


def show(title: str) -> None:
    print(f"\n## {title}")


def run(cmd: list[str], cwd: Path, expect: int | None = None) -> subprocess.CompletedProcess:
    proc = subprocess.run(cmd, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    shown = [Path(c).name if c == sys.executable or "/" in c and c.endswith(".py") else c for c in cmd]
    print("$ " + " ".join(shown))
    print(proc.stdout.rstrip("\n"))
    print(f"exit={proc.returncode}")
    if expect is not None and proc.returncode != expect:
        failures.append(f"{' '.join(shown)}: exit {proc.returncode}, expected {expect}")
    return proc


def expect(condition: bool, what: str) -> None:
    print(("ok: " if condition else "NOT AS EXPECTED: ") + what)
    if not condition:
        failures.append(what)


def write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def rel_readme(frm: str, to: str) -> str:
    return os.path.relpath(os.path.join(to or ".", "README.md"), frm or ".").replace(os.sep, "/")


def render(templates: Path, kind: str, node: str, title: str, parent: str | None, parent_title: str | None,
           children: list[tuple[str, str, str]], fills: list[tuple[str, str]]) -> str:
    """Fill the template of a node's kind, as step 2 of the procedure says."""
    text = (templates / f"readme-{kind}.md").read_text(encoding="utf-8").replace("{{title}}", title)
    if parent is not None:
        text = text.replace("{{parent_title}}", parent_title).replace("replace:parent-readme", rel_readme(node, parent))
    lines = []
    for line in text.split("\n"):
        if "replace:child-readme" in line:  # repeat the child line once per child node
            lines += [line.replace("{{child_title}}", c_title).replace("replace:child-readme", rel_readme(node, c_path))
                      .replace(U + "one line on what it is for.", c_line) for c_path, c_title, c_line in children]
            continue
        lines.append(line)
    text = "\n".join(lines)
    if not children:  # drop a list of children that would stay empty
        text = re.sub(r"## (Parts|Features|Contents)\n\n(?=\n|## )", "", text)
    for old, new in fills:
        if old not in text:
            failures.append(f"{node or '.'}: template text not found: {old}")
        text = text.replace(old, new, 1)
    return text


def walk_down(root: Path) -> set[str]:
    """Folders reached from the root README by following relative links downward only.

    Deliberately independent of check_tree.py: a plain regular expression over the raw text.
    """
    reached, queue = {""}, [""]
    while queue:
        here = queue.pop()
        text = (root / here / "README.md").read_text(encoding="utf-8")
        for target in re.findall(r"\]\(([^)\s#]+)\)", text):
            resolved = os.path.normpath(os.path.join(here or ".", target)).replace(os.sep, "/")
            folder = os.path.dirname(resolved) if resolved.endswith("README.md") else resolved
            folder = "" if folder == "." else folder
            downward = folder.startswith(here + "/") if here else not folder.startswith("..") and folder != ""
            if downward and folder not in reached and (root / folder / "README.md").is_file():
                reached.add(folder)
                queue.append(folder)
    return reached


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--skill", required=True)
    parser.add_argument("--work", required=True)
    parser.add_argument("--snapshot")
    args = parser.parse_args()
    skill = Path(args.skill).resolve()
    scripts, templates = skill / "scripts", skill / "templates"
    root = Path(args.work).resolve()
    if root.exists() and any(root.iterdir()):
        print(f"error: --work must be new or empty: {root}", file=sys.stderr)
        return 2
    py = [sys.executable, "-B"]
    tree = lambda *a, expect=None: run(py + [str(scripts / "check_tree.py"), "--root", str(root), *a], root, expect)

    show("fixture: two products with two feature folders each, and no README")
    for rel, text in FIXTURE.items():
        write(root, rel, text)
    for cmd in (["git", "init", "-q"], ["git", "config", "user.email", "dryrun@example.invalid"],
                ["git", "config", "user.name", "dryrun"], ["git", "config", "commit.gpgsign", "false"]):
        subprocess.run(cmd, cwd=root, check=True)
    run(["git", "add", "-A"], root, 0)
    run(["git", "commit", "-qm", "fixture without READMEs"], root, 0)
    base = run(["git", "rev-parse", "--short", "HEAD"], root, 0).stdout.strip()
    run(["git", "ls-files"], root, 0)

    show("procedure step 1, Declare: candidates without a declaration")
    tree(expect=0)
    candidates = json.loads(tree("--json", expect=0).stdout)["candidates"]
    expect(candidates == {"products": ["products/*"], "features": ["products/*/src/features/*"]},
           f"the candidates are products/* and products/*/src/features/* (got {candidates})")
    print("confirmation: the person who runs this script stands in for the person; a fixture has nobody to confirm it")
    write(root, ".living-documentation.json", json.dumps({"tree": candidates}, indent=2) + "\n")
    run(["cat", ".living-documentation.json"], root, 0)
    result = json.loads(tree("--json", expect=1).stdout)
    tree(expect=1)
    expect(sorted(e["kind"] for e in result["errors"]) == ["missing-readme"] * 7, "seven missing-readme errors")

    show("procedure steps 2 and 3, Create and Fill: READMEs from the templates, verified facts only")
    shop, admin = "products/shop", "products/admin"
    f = "src/features"
    readmes = {
        "": render(templates, "repository", "", "acme-platform", None, None,
                   [(shop, "@acme/shop", "Customer-facing web shop."), (admin, "@acme/admin", "Internal console for staff.")],
                   [(U + "the prerequisites and the shortest path to a first result, such as one command to build and test.",
                     "The root `test` script runs `vitest run`. " + U + "the prerequisites (runtime and package manager versions).")]),
        shop: render(templates, "product", shop, "@acme/shop", "", "acme-platform",
                     [(f"{shop}/{f}/cart", "cart", "Keeps the items a customer intends to buy, in the browser session only."),
                      (f"{shop}/{f}/checkout", "checkout", "Turns a cart into an order.")],
                     [(U + "what this product does and for whom, in one to three sentences.", "Customer-facing web shop."),
                      (U + "how to build, run, and test this product, with the commands.",
                       "Build with `vite build` and test with `vitest run` (the `build` and `test` scripts). " + U + "how to run it locally.")]),
        admin: render(templates, "product", admin, "@acme/admin", "", "acme-platform",
                      [(f"{admin}/{f}/users", "users", U + "one line on what it is for."),
                       (f"{admin}/{f}/audit-log", "audit-log", "Records staff actions for later review.")],
                      [(U + "what this product does and for whom, in one to three sentences.", "Internal console for staff."),
                       (U + "how to build, run, and test this product, with the commands.",
                        "Build with `vite build` and test with `vitest run` (the `build` and `test` scripts). " + U + "how to run it locally.")]),
    }
    purpose = U + "what this feature does for its users, in one to three sentences."
    invariant = "- " + U + "a rule this feature must keep. Checked by: " + U + "the test or lint rule that enforces it, or \"not checked\"."
    start = U + "the files to read first, as relative links, for example `[handler.ts](api/handler.ts)`."
    verified = U + "the commit at which this README was last compared with the code (`git rev-parse --short HEAD`)."
    features = {
        "cart": (shop, [(purpose, "Keeps the items a customer intends to buy, in the browser session only."),
                        (invariant, "- Adding an item keeps the items already in the cart. Checked by: the test \"adding an item keeps earlier items\" in [cart.test.ts](cart.test.ts)."),
                        (start, "[cart.ts](cart.ts)"), (verified, base)]),
        "checkout": (shop, [(purpose, "Turns a cart into an order."),
                            (U + "what this feature deliberately does not handle, and where that is handled instead.",
                             "Payment, which an external provider handles. " + U + "which provider, and where the integration lives."),
                            (invariant, "- An empty cart is never turned into an order. Checked by: not checked (no test covers it)."),
                            (start, "[checkout.ts](checkout.ts)"), (verified, base)]),
        "users": (admin, [(start, "[users.ts](users.ts)"), (verified, base)]),
        "audit-log": (admin, [(purpose, "Records staff actions for later review."),
                              (invariant, "- Entries are never edited after they are written. Checked by: not checked (no test covers it)."),
                              (start, "[audit.ts](audit.ts)"), (verified, base)]),
    }
    for name, (product, fills) in features.items():
        readmes[f"{product}/{f}/{name}"] = render(templates, "feature", f"{product}/{f}/{name}", name, product,
                                                  "@acme/shop" if product == shop else "@acme/admin", [], fills)
    for node, text in readmes.items():
        write(root, f"{node}/README.md" if node else "README.md", text)
    print("facts written, with their sources (a file and line of the fixture, or a command and its output above):")
    for readme, fact, source in FACTS:
        print(f"- {readme}: {fact} <- {source.replace('<base>', base)}")
    for node in sorted(readmes):
        run(["cat", f"{node}/README.md" if node else "README.md"], root, 0)

    show("procedure step 4, Check")
    tree(expect=0)
    run(py + [str(scripts / "check_links.py"), "--root", str(root)], root, 0)
    leftover = run(["grep", "-rn", "-e", "{{", "-e", "replace:", "--include=README.md", "."], root, 1)
    expect(leftover.stdout.strip() == "", "no {{ and no replace: is left in any README")
    reached = walk_down(root)
    declared = {str(p.relative_to(root)) for p in root.glob("products/*/src/features/*") if p.is_dir()}
    print(f"reached by downward links (independent walk): {sorted(reached)}")
    expect(declared <= reached and len(declared) == 4, "every feature folder README is reached from the root README by downward links")
    run(["git", "add", "-A"], root, 0)
    run(["git", "commit", "-qm", "build the documentation tree"], root, 0)
    run(["git", "log", "--oneline"], root, 0)

    show("a later change: one feature folder added, then the Check step of the procedure for every change")
    write(root, *COUPON)
    run(py + [str(scripts / "find_related.py"), "--root", str(root)], root, 0)
    result = json.loads(tree("--json", expect=1).stdout)
    tree(expect=1)
    expect(sorted((e["node"], e["kind"]) for e in result["errors"]) ==
           [(shop, "missing-child-link"), (f"{shop}/{f}/coupon", "missing-readme")],
           "the tree check names the missing README and the missing link from the parent")
    coupon = f"{shop}/{f}/coupon"
    write(root, f"{coupon}/README.md", render(templates, "feature", coupon, "coupon", shop, "@acme/shop", [], [
        (purpose, "Applies a discount code to an order total."),
        (invariant, "- A code can be used once per order. Checked by: not checked (no test covers it, and `applyCoupon` does not enforce it)."),
        (start, "[coupon.ts](coupon.ts)"),
        (verified, f"{run(['git', 'rev-parse', '--short', 'HEAD'], root, 0).stdout.strip()} plus the uncommitted coupon change")]))
    shop_readme = root / shop / "README.md"
    line = "- [checkout](src/features/checkout/README.md): Turns a cart into an order.\n"
    shop_readme.write_text(shop_readme.read_text(encoding="utf-8").replace(
        line, line + "- [coupon](src/features/coupon/README.md): Applies a discount code to an order total.\n"), encoding="utf-8")
    tree(expect=0)
    run(py + [str(scripts / "check_links.py"), "--root", str(root), "--changed"], root, 0)
    run(["git", "status", "--short", "--untracked-files=all"], root, 0)
    run(["cat", f"{coupon}/README.md"], root, 0)

    if args.snapshot:
        snapshot = Path(args.snapshot)
        listed = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=root,
                                text=True, stdout=subprocess.PIPE, check=True).stdout.split()
        for rel in listed:  # a record directory holds data files only, so code gets a .txt suffix
            target = snapshot / (rel + ".txt" if rel.endswith(".ts") else rel)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(root / rel, target)
        print(f"\nsnapshot of the fixture: {len(listed)} files")

    print("\nRESULT: " + ("every expectation held" if not failures else "NOT AS EXPECTED:\n- " + "\n- ".join(failures)))
    return 0 if not failures else 1


FACTS = [
    ("README.md", "the title acme-platform", "package.json:2"),
    ("README.md", "the root test script runs vitest run", "package.json:6"),
    ("README.md", "@acme/shop: Customer-facing web shop.", "products/shop/package.json:2-3"),
    ("README.md", "@acme/admin: Internal console for staff.", "products/admin/package.json:2-3"),
    ("products/shop/README.md", "the title @acme/shop and its purpose Customer-facing web shop.", "products/shop/package.json:2-3"),
    ("products/shop/README.md", "build with vite build, test with vitest run", "products/shop/package.json:5-6"),
    ("products/shop/README.md", "cart: Keeps the items a customer intends to buy, in the browser session only.", "products/shop/src/features/cart/cart.ts:1"),
    ("products/shop/README.md", "checkout: Turns a cart into an order.", "products/shop/src/features/checkout/checkout.ts:1"),
    ("products/shop/README.md", "coupon: Applies a discount code to an order total. (the later change)", "products/shop/src/features/coupon/coupon.ts:1"),
    ("products/admin/README.md", "the title @acme/admin and its purpose Internal console for staff.", "products/admin/package.json:2-3"),
    ("products/admin/README.md", "build with vite build, test with vitest run", "products/admin/package.json:5-6"),
    ("products/admin/README.md", "audit-log: Records staff actions for later review.", "products/admin/src/features/audit-log/audit.ts:1"),
    ("cart/README.md", "purpose", "cart.ts:1"),
    ("cart/README.md", "invariant: adding an item keeps the items already in the cart, checked by a test", "cart.test.ts:2-3"),
    ("cart/README.md", "start with cart.ts; last compared at <base>", "git ls-files and git rev-parse --short HEAD above"),
    ("checkout/README.md", "purpose", "checkout.ts:1"),
    ("checkout/README.md", "out of scope: payment, handled by an external provider", "checkout.ts:1"),
    ("checkout/README.md", "invariant: an empty cart is never turned into an order; no test", "checkout.ts:3; git ls-files above lists no test in the folder"),
    ("checkout/README.md", "start with checkout.ts; last compared at <base>", "git ls-files and git rev-parse --short HEAD above"),
    ("users/README.md", "start with users.ts; last compared at <base>", "git ls-files and git rev-parse --short HEAD above"),
    ("audit-log/README.md", "purpose", "audit.ts:1"),
    ("audit-log/README.md", "invariant: entries are never edited after they are written; no test", "audit.ts:1; git ls-files above lists no test in the folder"),
    ("audit-log/README.md", "start with audit.ts; last compared at <base>", "git ls-files and git rev-parse --short HEAD above"),
    ("coupon/README.md", "purpose", "coupon.ts:1"),
    ("coupon/README.md", "invariant: a code can be used once per order; no test, and applyCoupon does not enforce it", "coupon.ts:1-3; git status --short below lists no test in the folder"),
    ("coupon/README.md", "start with coupon.ts; last compared at the second git rev-parse plus the uncommitted change", "git rev-parse --short HEAD and git status --short below"),
]

if __name__ == "__main__":
    raise SystemExit(main())
