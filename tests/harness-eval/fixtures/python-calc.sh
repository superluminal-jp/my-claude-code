#!/usr/bin/env bash
# A function whose documented contract (empty list -> 0.0) is broken, with one
# existing test that does not cover the broken case.
set -euo pipefail
[ -z "$(ls -A .)" ] || { echo "fixture: run me in an empty directory" >&2; exit 1; }
cat > calc.py <<'PY'
def mean(values):
    """Return the arithmetic mean of values."""
    return sum(values) / len(values)
PY
cat > test_calc.py <<'PY'
import unittest

from calc import mean


class MeanTest(unittest.TestCase):
    def test_mean_of_three_numbers(self):
        self.assertEqual(mean([1, 2, 3]), 2)


if __name__ == "__main__":
    unittest.main()
PY
printf '# calc\n\nmean() は数のリストの平均を返す。空のリストには 0.0 を返す。\n' > README.md
git init -q
git checkout -q -b main
git -c user.email=eval@example.invalid -c user.name=eval add -A
git -c user.email=eval@example.invalid -c user.name=eval -c commit.gpgsign=false commit -qm "initial"
