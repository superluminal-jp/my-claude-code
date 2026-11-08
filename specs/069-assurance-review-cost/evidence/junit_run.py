#!/usr/bin/env python3
"""Runs one skill's unit tests and writes a JUnit XML report whose test cases
carry the spec 069 acceptance ids as acceptance_id properties, so that
assure.py collect-junit maps them. The mapping lives here, not in the
skills' tests, which are installed into ~/.claude and must not name this
repository's specs.

Usage: junit_run.py TESTS_DIR COMMIT OUT.xml. Exit 0 when every test passed.
"""

from __future__ import annotations

import sys
import unittest
from xml.sax.saxutils import quoteattr

# test id prefix (module.Class or module.Class.method) -> acceptance ids
MAPPING = {
    "test_review_prep.BundleTests": ["RA-A1"],
    "test_review_prep.ScopeTests": ["RB-A1"],
    "test_review_prep.CheckTests": ["RD-A1"],
}


def ids_for(test_id: str) -> list[str]:
    for prefix in sorted(MAPPING, key=len, reverse=True):
        if test_id == prefix or test_id.startswith(prefix + "."):
            return MAPPING[prefix]
    return []


class Collect(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.outcomes: dict[str, str] = {}

    def addSuccess(self, test):
        super().addSuccess(test)
        self.outcomes.setdefault(test.id(), "passed")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.outcomes[test.id()] = "failed"

    def addError(self, test, err):
        super().addError(test, err)
        self.outcomes[test.id()] = "failed"

    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        if err is not None:
            self.outcomes[test.id()] = "failed"

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.outcomes[test.id()] = "skipped"


def main(argv: list[str]) -> int:
    tests_dir, commit, out = argv[1], argv[2], argv[3]
    sys.path.insert(0, tests_dir)
    suite = unittest.defaultTestLoader.discover(tests_dir, top_level_dir=tests_dir)
    result = unittest.TextTestRunner(resultclass=Collect, verbosity=0, stream=sys.stderr).run(suite)
    failures = sum(1 for o in result.outcomes.values() if o == "failed")
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             f'<testsuite name={quoteattr(tests_dir)} tests="{len(result.outcomes)}" failures="{failures}">',
             f'  <properties><property name="commit" value={quoteattr(commit)}/></properties>']
    for test_id, outcome in sorted(result.outcomes.items()):
        classname, name = test_id.rsplit(".", 1)
        props = "".join(f'<property name="acceptance_id" value={quoteattr(i)}/>' for i in ids_for(test_id))
        body = (f"<properties>{props}</properties>" if props else "") + \
               {"passed": "", "failed": "<failure/>", "skipped": "<skipped/>"}[outcome]
        lines.append(f"  <testcase classname={quoteattr(classname)} name={quoteattr(name)}>{body}</testcase>")
    lines.append("</testsuite>")
    with open(out, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
