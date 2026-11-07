#!/usr/bin/env python3
"""R0-A5: checks that this change's own records follow the procedure spec 068
added to verified-delivery:

1. every commit after reviewed_commit changes only the record directory;
2. every evidence file the manifest cites is tracked by git and not ignored;
3. every finding statement of the given assurance review records is written
   in Japanese, the language of the records (it contains kana or kanji);
4. the given red and mutation observations (mutations.sh's output) show
   every red as assertion failures with no error, every mutation caught by an
   assertion, and the script's own result as expected.

Usage: records_check.py MUTATIONS_TXT REVIEW_RECORD... (run from anywhere in
the repository). Reads only; runs git read-only. Exit 0 when all four hold.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

RECORDS = Path(__file__).resolve().parent.parent
REPO = RECORDS.parent.parent
PREFIX = str(RECORDS.relative_to(REPO)) + "/"
JAPANESE = re.compile(r"[぀-ヿ一-鿿]")


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True, timeout=60)


def main(argv: list[str]) -> int:
    manifest = json.loads((RECORDS / "verification-manifest.json").read_text(encoding="utf-8"))["verification_manifest"]
    reviewed = manifest["reviewed_commit"]
    ok = True

    changed = git("diff", "--name-only", reviewed, "HEAD").stdout.split()
    outside = [p for p in changed if not p.startswith(PREFIX)]
    head = git("rev-parse", "HEAD").stdout.strip()
    print(f"1. {len(changed)} files changed from {reviewed[:7]} to HEAD {head[:7]}; outside {PREFIX}: {outside or 'none'}")
    ok &= not outside

    refs = sorted({c["evidence"]["ref"] for c in manifest["checks"] if isinstance(c.get("evidence"), dict)
                   and c["evidence"]["ref"].startswith(PREFIX)})
    for ref in refs:
        tracked = git("ls-files", "--error-unmatch", ref).returncode == 0
        ignored = git("check-ignore", "-q", ref).returncode == 0
        print(f"2. {ref}: {'tracked' if tracked else 'NOT TRACKED'}, {'IGNORED' if ignored else 'not ignored'}")
        ok &= tracked and not ignored

    for path in argv[2:]:
        findings = json.loads(Path(path).read_text(encoding="utf-8"))["assurance_review"]["findings"]
        english = [f["id"] for f in findings if not JAPANESE.search(f.get("statement", ""))]
        print(f"3. {Path(path).name}: {len(findings)} findings, statements without Japanese: {english or 'none'}")
        ok &= not english

    lines = Path(argv[1]).read_text(encoding="utf-8").splitlines()
    observed = [line for line in lines if line.startswith(("red ", "mutation "))]
    errors = [line for line in observed if re.search(r"\sERROR\s", line)]
    coverage = next((re.match(r"coverage: (\d+) of (\d+) ", line) for line in lines if line.startswith("coverage: ")), None)
    complete = coverage is not None and coverage.group(1) == coverage.group(2) and int(coverage.group(2)) > 0
    expected = "result: every observation as expected" in lines
    print(f"4. {Path(argv[1]).name}: {len(observed)} observations, {len(errors)} errors, "
          f"coverage {coverage.group(0).strip() if coverage else 'missing'}, script result {'as expected' if expected else 'NOT as expected'}")
    ok &= bool(observed) and not errors and complete and expected

    print("result:", "all hold" if ok else "SOMETHING DOES NOT HOLD")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
