#!/usr/bin/env python3
"""Prepares a round of the assurance review (references/reviewer.md).

check   finds, before the reviewer starts, the record errors a program can
        find: a reviewed_commit that is no commit behind HEAD, a commit after
        it that changes anything outside the record directory, and evidence
        files the manifest cites that are missing, untracked, or ignored.
bundle  writes what the reviewer reads into a new directory outside the
        repository: the change's diff without the record directory's data
        files, the graph and its diff, the manifest (the implementer's
        claims), copies of the evidence files it cites, the names of the
        record files left out, and the
        round's scope, which --previous decides: the whole diff from --base
        when the requirements graph changed beyond its text fields, the
        problem card changed, or the risk class changed, and the fix diff
        from --previous otherwise.

The record directory (--records) is the one directory that holds the
change's records, verification-manifest.json among them. Its records are
data files (RECORD_SUFFIXES); any other file there, such as a script that
makes evidence, is part of the change and is reviewed with it.

Contract: runs git with read-only subcommands only (rev-parse, merge-base,
diff, show, log, ls-files, check-ignore); opens no network connection, so a
URL in the evidence is never opened; writes only under --out. Needs Python
3.9 or later and git.

Exit codes: 0 no violation (check) or bundle written; 1 violations (check);
2 input that cannot be used (bad arguments, no repository, no manifest, an
--out that is inside the repository or not empty).
"""

from __future__ import annotations

import argparse
import copy
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, NoReturn, Optional, Tuple

EXIT_OK, EXIT_VIOLATIONS, EXIT_INPUT_ERROR = 0, 1, 2
URL = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*://")
MANIFEST, GRAPH, CARD = "verification-manifest.json", "requirements-graph.json", "problem-card.json"
# The graph fields a fix round may change without a whole review: words, not
# structure. Everything else (ids, decomposition, children, levels, stages,
# origins, which children a selection names) counts as structure.
TEXT_FIELDS = ("statement", "assumptions", "counterexamples")
CRITERION_TEXT_FIELDS = ("description",)
# Records are data. A file of the record directory with another suffix (a
# script that makes evidence, for example) is part of the change: the
# bundle's change.diff keeps it, and check reports it changed after the review.
RECORD_SUFFIXES = (".json", ".md", ".txt", ".xml", ".csv", ".yaml", ".yml", ".html", ".log")


def is_record(path: str, records: str) -> bool:
    return (path + "/").startswith(records + "/") and Path(path).suffix.lower() in RECORD_SUFFIXES


# The records written before implementation go in with the change, so the
# reviewed commit carries the requirements it was built to; a later commit
# may not change them.
REQUIREMENT_RECORDS = (CARD, GRAPH, "challenge-report.json")


def is_plain(ref: str) -> bool:
    """A relative path inside the repository with no "..", "." or empty part."""
    parts = ref.split("/")
    return not ref.startswith("/") and "\\" not in ref and all(part not in ("", ".", "..") for part in parts)


class InputError(Exception):
    """The input cannot be used; exit code 2."""


class Repository:
    def __init__(self) -> None:
        proc = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, timeout=60)
        if proc.returncode != 0:
            raise InputError("not inside a git repository")
        self.root = Path(proc.stdout.strip()).resolve()

    def git(self, *args: str, ok: Tuple[int, ...] = (0,)) -> subprocess.CompletedProcess:
        proc = subprocess.run(["git", "-C", str(self.root), *args], capture_output=True, text=True, timeout=120)
        if proc.returncode not in ok:
            raise InputError(f"git {args[0]} failed: {proc.stderr.strip()}")
        return proc

    def commit(self, rev: str) -> Optional[str]:
        proc = self.git("rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}", ok=(0, 1, 128))
        return proc.stdout.strip() if proc.returncode == 0 else None

    def is_ancestor(self, older: str, newer: str) -> bool:
        return self.git("merge-base", "--is-ancestor", older, newer, ok=(0, 1)).returncode == 0

    def show(self, rev: str, path: str) -> Optional[str]:
        proc = self.git("show", f"{rev}:{path}", ok=(0, 128))
        return proc.stdout if proc.returncode == 0 else None

    def show_bytes(self, rev: str, path: str) -> Optional[bytes]:
        proc = subprocess.run(["git", "-C", str(self.root), "show", f"{rev}:{path}"], capture_output=True, timeout=120)
        return proc.stdout if proc.returncode == 0 else None

    def committed(self, path: str) -> bool:
        return bool(self.git("ls-tree", "--name-only", "HEAD", "--", path).stdout.strip())

    def relative(self, path: str) -> str:
        resolved = Path(path).resolve()
        if resolved != self.root and self.root not in resolved.parents:
            raise InputError(f"{path} is not inside the repository")
        return resolved.relative_to(self.root).as_posix()


def load_json(text: str, what: str) -> Any:
    try:
        return json.loads(text)
    except ValueError as exc:
        raise InputError(f"{what} is not valid JSON: {exc}") from None


def current_manifest(repo: Repository, records: str) -> Dict[str, Any]:
    """The manifest as committed at HEAD: the review reads committed records only."""
    text = repo.show("HEAD", f"{records}/{MANIFEST}")
    if text is None:
        raise InputError(f"{records}/{MANIFEST} is not committed at HEAD; commit the records first")
    body = load_json(text, f"{records}/{MANIFEST}").get("verification_manifest")
    if not isinstance(body, dict) or not isinstance(body.get("reviewed_commit"), str):
        raise InputError(f"{records}/{MANIFEST} has no verification_manifest with a reviewed_commit")
    return body


def repository_refs(body: Dict[str, Any]) -> List[str]:
    """The evidence references that name a file of the repository."""
    refs = []
    for entry in body.get("checks") or []:
        evidence = entry.get("evidence") if isinstance(entry, dict) else None
        ref = evidence.get("ref") if isinstance(evidence, dict) else None
        if isinstance(ref, str) and ref and not URL.match(ref) and ref not in refs:
            refs.append(ref)
    return refs


# --- check ---------------------------------------------------------------------


def run_check(repo: Repository, records: str) -> List[Tuple[str, str, str]]:
    body = current_manifest(repo, records)
    violations: List[Tuple[str, str, str]] = []
    reviewed = repo.commit(body["reviewed_commit"])
    if reviewed is None:
        violations.append(("P-01", body["reviewed_commit"], "reviewed_commit is not a commit of this repository"))
    elif not repo.is_ancestor(reviewed, "HEAD"):
        violations.append(("P-01", reviewed, "reviewed_commit is not behind HEAD"))
    else:
        # --no-renames: a file moved into the record directory shows as the
        # deletion it is, not only as its new, record-looking name.
        changed = repo.git("diff", "--name-only", "--no-renames", reviewed, "HEAD").stdout.split("\n")
        requirement_records = {f"{records}/{name}" for name in REQUIREMENT_RECORDS}
        for path in (p for p in changed if p):
            if path in requirement_records:
                violations.append(("P-02", path, "changed after reviewed_commit; a record written before implementation goes in with the change"))
            elif not is_record(path, records):
                violations.append(("P-02", path, "changed after reviewed_commit, and is not a record (a data file of the record directory)"))
    # The gate reads these from the working tree, so each must be as committed.
    requirement_files = [f"{records}/{name}" for name in REQUIREMENT_RECORDS
                         if repo.committed(f"{records}/{name}") or (repo.root / records / name).exists()]
    for ref in [f"{records}/{MANIFEST}"] + requirement_files + repository_refs(body):
        problem = evidence_problem(repo, ref)
        if problem:
            violations.append(("P-03", ref, problem))
    return violations


def evidence_problem(repo: Repository, ref: str) -> Optional[str]:
    """Why a record file the review will read is not as committed, or None."""
    if not is_plain(ref):
        return "is not a plain path inside the repository"
    target = repo.root / ref
    if not repo.committed(ref):
        if not target.is_file():
            return "does not exist"
        ignored = repo.git("check-ignore", "-v", "--", ref, ok=(0, 1)).stdout.strip()
        if ignored:
            return f"is ignored by git ({ignored.split(chr(9))[0]})"
        if repo.git("ls-files", "--error-unmatch", "--", ref, ok=(0, 1)).returncode == 0:
            return "is staged but not committed"
        return "is not tracked"
    if not target.is_file() or repo.git("diff", "--quiet", "HEAD", "--", ref, ok=(0, 1)).returncode != 0:
        return "differs from its committed version"
    return None


# --- bundle ----------------------------------------------------------------------


def structure(graph: Any) -> Any:
    """The graph without its text fields, in a fixed order, so that only a
    change of structure makes two graphs differ."""
    doc = copy.deepcopy(graph)
    if not isinstance(doc, dict) or not isinstance(doc.get("requirements"), list):
        return doc
    nodes = []
    for node in doc["requirements"]:
        if isinstance(node, dict):
            for field in TEXT_FIELDS:
                node.pop(field, None)
            if isinstance(node.get("children"), list):
                node["children"] = sorted(map(str, node["children"]))
            if isinstance(node.get("selection"), dict):
                node["selection"] = sorted(node["selection"])
            if isinstance(node.get("acceptance"), list):
                for entry in node["acceptance"]:
                    if isinstance(entry, dict):
                        for field in CRITERION_TEXT_FIELDS:
                            entry.pop(field, None)
                node["acceptance"] = sorted(node["acceptance"], key=lambda e: json.dumps(e, sort_keys=True))
        nodes.append(node)
    doc["requirements"] = sorted(nodes, key=lambda n: json.dumps(n.get("id") if isinstance(n, dict) else n))
    return doc


def graph_reasons(before: Any, after: Any) -> List[str]:
    a, b = structure(before), structure(after)
    if a == b:
        return []
    reasons = []
    ids = lambda doc: {n.get("id"): n for n in doc.get("requirements", []) if isinstance(n, dict)} if isinstance(doc, dict) else {}
    na, nb = ids(a), ids(b)
    reasons += [f"requirement {i} added" for i in sorted(set(nb) - set(na), key=str)]
    reasons += [f"requirement {i} removed" for i in sorted(set(na) - set(nb), key=str)]
    reasons += [f"requirement {i} changed beyond its text fields" for i in sorted(set(na) & set(nb), key=str) if na[i] != nb[i]]
    if {k: v for k, v in a.items() if k != "requirements"} != {k: v for k, v in b.items() if k != "requirements"}:
        reasons.append("the graph's top level changed")
    return reasons or ["the requirements graph changed beyond its text fields"]


def manifest_naming(repo: Repository, records: str, commit: str) -> Optional[Dict[str, Any]]:
    """The newest committed manifest whose reviewed_commit is ``commit``."""
    history = repo.git("log", "--format=%H", "HEAD", "--", f"{records}/{MANIFEST}").stdout.split()
    for rev in history:
        text = repo.show(rev, f"{records}/{MANIFEST}")
        try:
            body = json.loads(text).get("verification_manifest") if text else None
        except ValueError:
            continue
        if isinstance(body, dict) and isinstance(body.get("reviewed_commit"), str) and repo.commit(body["reviewed_commit"]) == commit:
            return body
    return None


def decide_scope(repo: Repository, records: str, previous: str, reviewed: str, body: Dict[str, Any]) -> List[str]:
    """The reasons the round must read the whole diff; none means a fix round."""
    reasons: List[str] = []
    graphs = [repo.show(rev, f"{records}/{GRAPH}") for rev in (previous, reviewed)]
    if None in graphs:
        reasons.append(f"no {GRAPH} at {'the previous reviewed commit' if graphs[0] is None else 'the reviewed commit'}")
    else:
        reasons += graph_reasons(load_json(graphs[0], "the previous graph"), load_json(graphs[1], "the graph"))
    cards = [repo.show(rev, f"{records}/{CARD}") for rev in (previous, reviewed)]
    if None in cards:
        reasons.append(f"no {CARD} at {'the previous reviewed commit' if cards[0] is None else 'the reviewed commit'}")
    elif load_json(cards[0], "the previous problem card") != load_json(cards[1], "the problem card"):
        reasons.append("the problem card changed")
    before = manifest_naming(repo, records, previous)
    if before is None:
        reasons.append("no committed manifest names the previous reviewed commit, so its risk class is unknown")
    else:
        old = (before.get("risk") or {}).get("class")
        new = (body.get("risk") or {}).get("class")
        if old != new:
            reasons.append(f"the risk class changed from {old} to {new}")
    return reasons


def run_bundle(repo: Repository, records: str, base: str, out: Path, previous: Optional[str],
               previous_review: Optional[str]) -> Dict[str, Any]:
    out = out.resolve()
    if out == repo.root or repo.root in out.parents:
        raise InputError(f"--out {out} is inside the repository; give a directory outside it, so the bundle is never committed")
    if out.exists() and (not out.is_dir() or any(out.iterdir())):
        raise InputError(f"--out {out} exists and is not an empty directory")
    body = current_manifest(repo, records)
    reviewed = repo.commit(body["reviewed_commit"])
    base_sha = repo.commit(base)
    if reviewed is None or base_sha is None:
        raise InputError("the manifest's reviewed_commit and --base must both be commits of this repository")
    if not repo.is_ancestor(base_sha, reviewed):
        raise InputError("--base is not behind the reviewed commit")
    reasons = ["the first round"]
    start = base_sha
    prev_sha = None
    if previous is not None:
        prev_sha = repo.commit(previous)
        if prev_sha is None or not repo.is_ancestor(prev_sha, reviewed):
            raise InputError("--previous must be a commit behind the reviewed commit")
        reasons = decide_scope(repo, records, prev_sha, reviewed, body)
        if not reasons:
            start = prev_sha
    if previous_review is not None and not Path(previous_review).is_file():
        raise InputError(f"--previous-review {previous_review} is not a file")
    out.mkdir(parents=True, exist_ok=True)
    write = lambda name, text: (out / name).write_text(text, encoding="utf-8")
    excluded = [f":(exclude,glob){records}/**/*{suffix}" for suffix in RECORD_SUFFIXES]
    write("change.diff", repo.git("diff", "--no-color", "--no-ext-diff", start, reviewed, "--", ".", *excluded).stdout)
    write("graph.diff", repo.git("diff", "--no-color", "--no-ext-diff", start, reviewed, "--", f"{records}/{GRAPH}").stdout)
    write(GRAPH, repo.show(reviewed, f"{records}/{GRAPH}") or "")
    write("manifest.json", repo.show("HEAD", f"{records}/{MANIFEST}") or "")
    names = repo.git("diff", "--name-only", "--no-renames", start, reviewed, "--", records).stdout.split("\n")
    write("excluded.txt", "".join(f"{name}\n" for name in names if name and is_record(name, records)))
    copied = []
    for ref in repository_refs(body):
        # Only a plain path, read as committed at HEAD, so a copy can neither
        # leave --out nor show what was never committed; check reports the rest.
        content = repo.show_bytes("HEAD", ref) if is_plain(ref) else None
        if content is not None:
            target = out / "evidence" / ref
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
            copied.append(ref)
    if previous_review is not None:
        shutil.copyfile(previous_review, out / "previous-review.json")
    scope = {"scope": "fixes" if start == prev_sha else "whole", "range": [start, reviewed], "base": base_sha,
             "previous": prev_sha, "reasons": [] if start == prev_sha else reasons, "evidence": copied}
    write("scope.json", json.dumps(scope, indent=2, ensure_ascii=False) + "\n")
    return scope


# --- command line ----------------------------------------------------------------


class _Parser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        self.print_usage(sys.stderr)
        print(f"error: invalid arguments: {message}", file=sys.stderr)
        sys.exit(EXIT_INPUT_ERROR)


def main(argv: Optional[List[str]] = None) -> int:
    parser = _Parser(prog="review_prep.py", description="Prepare a round of the assurance review (git read-only).")
    commands = parser.add_subparsers(dest="command", required=True)
    check = commands.add_parser("check", help="find record errors before the review")
    check.add_argument("--records", required=True, help="the record directory of the change")
    bundle = commands.add_parser("bundle", help="write the reviewer's inputs into a new directory outside the repository")
    bundle.add_argument("--records", required=True, help="the record directory of the change")
    bundle.add_argument("--base", required=True, help="the commit the change started from")
    bundle.add_argument("--out", required=True, help="a new or empty directory outside the repository")
    bundle.add_argument("--previous", help="the previous round's reviewed commit")
    bundle.add_argument("--previous-review", help="the previous round's review record, copied into the bundle")
    args = parser.parse_args(argv)
    try:
        repo = Repository()
        records = repo.relative(args.records)
        if args.command == "check":
            violations = run_check(repo, records)
            for rule, where, message in violations:
                print(f"{rule} {where}: {message}")
            print(f"Result: {'failed' if violations else 'passed'} ({len(violations)} violations; checked P-01 P-02 P-03)")
            return EXIT_VIOLATIONS if violations else EXIT_OK
        scope = run_bundle(repo, records, args.base, Path(args.out), args.previous, args.previous_review)
    except InputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_INPUT_ERROR
    start, reviewed = scope["range"]
    print(f"scope: {scope['scope']} (range {start[:7]}..{reviewed[:7]})")
    for reason in scope["reasons"]:
        print(f"  - {reason}")
    print(f"bundle: {Path(args.out).resolve()} (change.diff, graph.diff, {GRAPH}, manifest.json, excluded.txt, "
          f"evidence/ with {len(scope['evidence'])} files{', previous-review.json' if args.previous_review else ''}, scope.json)")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
