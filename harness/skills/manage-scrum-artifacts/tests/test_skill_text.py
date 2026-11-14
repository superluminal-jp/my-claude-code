"""The procedure text and the scripts must agree, and the rules the text exists for must be in it."""
from __future__ import annotations

import re
import unittest

from helpers import SKILL, TEMPLATES, run

SKILL_TEXT = (SKILL / "SKILL.md").read_text(encoding="utf-8")


class TheProcedureKeepsTheTeamsDecisionsWithTheTeam(unittest.TestCase):
    def test_it_forbids_deciding_each_value_the_scrum_team_owns(self) -> None:
        rule = re.search(r"^- Never decide or write these on your own:(.*)$", SKILL_TEXT, re.M)
        self.assertIsNotNone(rule)
        for value in (
            "the order of the Product Backlog", "the Product Goal", "the Sprint Goal",
            "the Definition of Done", "which items a Sprint selects",
        ):
            with self.subTest(value=value):
                self.assertIn(value, rule.group(1))

    def test_it_asks_when_the_product_folder_is_ambiguous(self) -> None:
        self.assertIn("Ask the person which folder when it is ambiguous", SKILL_TEXT)


class EveryCommandInTheProcedureIsAcceptedByItsScript(unittest.TestCase):
    def commands(self) -> list[tuple[str, list[str]]]:
        found = []
        for line in re.findall(r"^\s*`(python3 [^`]+)`\s*$", SKILL_TEXT, re.M):
            script = re.search(r"scripts/([a-z_]+\.py)", line).group(1)
            found.append((script, line.split(script + '"', 1)[1].split()))
        return found

    def test_the_procedure_shows_a_command_for_each_step_that_runs_one(self) -> None:
        scripts = [script for script, _ in self.commands()]
        self.assertEqual(scripts, ["scaffold.py", "scaffold.py", "check_artifacts.py"])

    def test_every_subcommand_and_option_is_in_the_scripts_help(self) -> None:
        for script, words in self.commands():
            subcommand = [w for w in words[:1] if not w.startswith("-")]
            help_text = run(script, *subcommand, "--help").stdout
            for option in [w for w in words if w.startswith("--")]:
                with self.subTest(script=script, option=option):
                    self.assertIn(option, help_text)

    def test_the_daily_option_named_in_the_text_exists(self) -> None:
        self.assertIn("`--daily`", SKILL_TEXT)
        self.assertIn("--daily", run("scaffold.py", "sprint", "--help").stdout)


class TheIndexTemplateSeparatesTheGuideFromConvention(unittest.TestCase):
    def test_it_has_one_heading_for_the_guide_and_one_for_convention(self) -> None:
        headings = re.findall(r"^## (.+)$", (TEMPLATES / "scrum-readme.md").read_text(encoding="utf-8"), re.M)
        self.assertEqual(headings, ["Scrum Guide が定めること", "このリポジトリでの運用上の決まり"])


if __name__ == "__main__":
    unittest.main()
