"""Package-level tests for the minto-pyramid plugin."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True


def require(path: str) -> Path:
    p = ROOT / path
    assert p.exists(), f"missing: {path}"
    return p


class PackageTests(unittest.TestCase):
    def test_manifest(self):
        manifest = json.loads(require('.claude-plugin/plugin.json').read_text())
        self.assertEqual(manifest['name'], 'minto-pyramid')
        self.assertTrue(manifest['version'])

    def test_stop_hook(self):
        hooks = json.loads(require('hooks/hooks.json').read_text())
        self.assertIn('Stop', hooks['hooks'])
        stop_handlers = hooks['hooks']['Stop'][0]['hooks']
        self.assertTrue(any(h.get('type') == 'prompt' for h in stop_handlers))

    def test_skill(self):
        skill = require('SKILL.md').read_text()
        self.assertIn('Do not reveal private chain-of-thought', skill)
        self.assertIn('rules/completion-check.md', skill)

    def test_resources_exist(self):
        for path in [
            'rules/core.md',
            'rules/completion-check.md',
            'templates/answer.md',
            'templates/decision.md',
            'templates/document.md',
            'references/minto-source.md',
            'references/bibliography.bib',
            'README.md',
        ]:
            require(path)

    def test_eval_cases(self):
        cases = sorted((ROOT / 'evals').glob('*/case.yaml'))
        self.assertGreaterEqual(len(cases), 3)
        for case in cases:
            self.assertTrue((case.parent / 'prompt.md').exists(), case)
            self.assertTrue(list((case.parent / 'graders').glob('*.md')), case)


if __name__ == '__main__':
    unittest.main()
