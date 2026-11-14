from __future__ import annotations

import shutil
import unittest

from helpers import TempRepo, snapshot


class Placed(TempRepo):
    """A product at the root with one sprint, as the scaffold leaves it."""

    def setUp(self) -> None:
        super().setUp()
        self.scaffold("init")
        self.scaffold("sprint", "--start", "2026-11-16")
        self.scrum = self.root / "scrum"
        self.sprint = self.scrum / "sprints" / "001-2026-11-16"

    def one_error(self, rule: str, path: str) -> None:
        code, result = self.check_json()
        self.assertEqual(code, 1, result)
        self.assertEqual([(e["rule"], e["path"]) for e in result["errors"]], [(rule, path)])


class ShapeErrorsAreReportedOneByOne(Placed):
    def test_a_missing_product_backlog_is_an_error(self) -> None:
        (self.scrum / "product-backlog.md").unlink()
        self.one_error("SA-01", "scrum/product-backlog.md")

    def test_a_missing_definition_of_done_is_an_error(self) -> None:
        (self.scrum / "definition-of-done.md").unlink()
        self.one_error("SA-02", "scrum/definition-of-done.md")

    def test_a_second_product_backlog_is_an_error(self) -> None:
        shutil.copy(self.scrum / "product-backlog.md", self.sprint / "product-backlog.md")
        self.one_error("SA-03", "scrum/sprints/001-2026-11-16/product-backlog.md")

    def test_a_second_definition_of_done_is_an_error(self) -> None:
        shutil.copy(self.scrum / "definition-of-done.md", self.sprint / "definition-of-done.md")
        self.one_error("SA-03", "scrum/sprints/001-2026-11-16/definition-of-done.md")

    def test_a_sprint_folder_with_a_malformed_name_is_an_error(self) -> None:
        for name in ("sprint-2", "2-2026-11-30", "002-2026-13-01"):
            with self.subTest(name=name):
                folder = self.scrum / "sprints" / name
                shutil.copytree(self.sprint, folder)
                self.one_error("SA-04", f"scrum/sprints/{name}")
                shutil.rmtree(folder)

    def test_two_sprint_folders_with_one_number_are_an_error(self) -> None:
        shutil.copytree(self.sprint, self.scrum / "sprints" / "001-2026-11-30")
        self.one_error("SA-05", "scrum/sprints/001-2026-11-30")

    def test_a_sprint_without_its_sprint_backlog_is_an_error(self) -> None:
        (self.sprint / "sprint-backlog.md").unlink()
        self.one_error("SA-06", "scrum/sprints/001-2026-11-16/sprint-backlog.md")

    def test_numbers_and_start_dates_in_different_orders_are_an_error(self) -> None:
        shutil.copytree(self.sprint, self.scrum / "sprints" / "002-2026-11-02")
        self.one_error("SA-07", "scrum/sprints/002-2026-11-02")


class ACleanProductPasses(Placed):
    def test_the_scaffolded_product_has_no_error(self) -> None:
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_json_output_is_one_object_with_product_errors_and_warnings(self) -> None:
        code, result = self.check_json()
        self.assertEqual(code, 0)
        self.assertEqual(sorted(result), ["errors", "product", "warnings"])
        self.assertEqual(result["product"], ".")
        self.assertEqual(result["errors"], [])

    def test_a_product_without_scrum_cannot_be_checked(self) -> None:
        (self.root / "other").mkdir()
        result = self.check("--product", "other")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)

    def test_checking_changes_nothing(self) -> None:
        before = snapshot(self.root)
        self.check()
        self.check("--format", "json")
        self.assertEqual(snapshot(self.root), before)


class UnsetCommitmentsAreWarned(Placed):
    def warnings(self) -> list[tuple[str, str]]:
        code, result = self.check_json()
        self.assertEqual(code, 0, result)
        return [(w["rule"], w["path"]) for w in result["warnings"]]

    def test_a_fresh_product_warns_once_for_each_commitment(self) -> None:
        self.assertEqual(self.warnings(), [
            ("SW-01", "scrum/product-backlog.md"),
            ("SW-02", "scrum/definition-of-done.md"),
            ("SW-03", "scrum/sprints/001-2026-11-16/sprint-backlog.md"),
        ])

    def test_commitments_that_are_written_are_not_warned(self) -> None:
        def fill(path, field, value):
            text = path.read_text(encoding="utf-8")
            marker = f"- **{field}**："
            self.assertIn(marker, text)
            path.write_text(text.replace(marker, marker + value, 1), encoding="utf-8")

        fill(self.scrum / "product-backlog.md", "Product Goal", "受注から出荷までを1日にする")
        fill(self.scrum / "definition-of-done.md", "Definition of Done", "\n  - テストが通る\n  - レビュー済み")
        fill(self.sprint / "sprint-backlog.md", "Sprint Goal", "出荷指示を自動で出す")
        self.assertEqual(self.warnings(), [])


if __name__ == "__main__":
    unittest.main()
